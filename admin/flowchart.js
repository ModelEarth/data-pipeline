(function () {
  const NODES_JSON = '../nodes.json';
  const BOX_WIDTH = 180;
  let cachedFlowData = null;
  let resizeRaf = null;

  function scalePositions(nodes, width, height) {
    const positions = nodes
      .map((node) => node.position)
      .filter((pos) => Array.isArray(pos) && pos.length === 2);

    if (!positions.length) return nodes;

    const xs = positions.map((p) => p[0]);
    const ys = positions.map((p) => p[1]);
    const minX = Math.min(...xs);
    const maxX = Math.max(...xs);
    const minY = Math.min(...ys);
    const maxY = Math.max(...ys);

    const pad = 40;
    const scaleX = (width - pad * 2) / (maxX - minX || 1);
    const scaleY = (height - pad * 2) / (maxY - minY || 1);
    const scale = Math.min(scaleX, scaleY, 1.2);

    return nodes.map((node) => {
      const pos = node.position || [0, 0];
      return {
        ...node,
        scaled: [
          pad + (pos[0] - minX) * scale,
          pad + (pos[1] - minY) * scale,
        ],
      };
    });
  }

  function safeGetHash() {
    if (typeof getHash === 'function') {
      return getHash();
    }
    const hash = window.location.hash.replace(/^#/, '');
    return hash.split('&').reduce((acc, pair) => {
      const [key, val] = pair.split('=');
      if (key) acc[key] = decodeURIComponent(val || '');
      return acc;
    }, {});
  }

  function goNodeHashOnly(nodeId) {
    const current = safeGetHash();
    const update = { node: nodeId };
    Object.keys(current || {}).forEach((key) => {
      if (key !== 'node') {
        update[key] = '';
      }
    });
    if (typeof goHash === 'function') {
      goHash(update);
      return;
    }
    const next = Object.keys(update)
      .filter((key) => update[key] !== undefined && update[key] !== null && update[key] !== '')
      .map((key) => `${key}=${encodeURIComponent(update[key])}`)
      .join('&');
    window.location.hash = next;
  }

  function buildConnectionPairs(data, nodes) {
    const pairs = [];
    const byName = new Map();
    const byId = new Map();
    nodes.forEach((node) => {
      if (node && node.name) byName.set(String(node.name), node);
      if (node && node.id) byId.set(String(node.id), node);
    });

    const connections = data && typeof data === 'object' ? data.connections || {} : {};
    Object.entries(connections).forEach(([parentKey, value]) => {
      const parent = byName.get(parentKey) || byId.get(parentKey);
      if (!parent || !value || typeof value !== 'object') return;
      const lanes = Array.isArray(value.main) ? value.main : [];
      lanes.forEach((lane) => {
        if (!Array.isArray(lane)) return;
        lane.forEach((entry) => {
          if (!entry || typeof entry !== 'object') return;
          const childKey = entry.node || entry.id;
          const child = byName.get(String(childKey || '')) || byId.get(String(childKey || ''));
          if (!child) return;
          pairs.push([parent, child]);
        });
      });
    });

    return pairs;
  }

  function buildConnectionGroups(data, nodes) {
    const groups = [];
    const byName = new Map();
    const byId = new Map();
    nodes.forEach((node) => {
      if (node && node.name) byName.set(String(node.name), node);
      if (node && node.id) byId.set(String(node.id), node);
    });

    const connections = data && typeof data === 'object' ? data.connections || {} : {};
    Object.entries(connections).forEach(([parentKey, value]) => {
      const parent = byName.get(parentKey) || byId.get(parentKey);
      if (!parent || !value || typeof value !== 'object') return;
      const lanes = Array.isArray(value.main) ? value.main : [];
      const children = [];
      lanes.forEach((lane) => {
        if (!Array.isArray(lane)) return;
        lane.forEach((entry) => {
          if (!entry || typeof entry !== 'object') return;
          const childKey = entry.node || entry.id;
          const child = byName.get(String(childKey || '')) || byId.get(String(childKey || ''));
          if (child) children.push(child);
        });
      });
      if (children.length) {
        groups.push({ parent, children });
      }
    });
    return groups;
  }

  function applyParentChildLayout(data, nodes, width) {
    const groups = buildConnectionGroups(data, nodes);
    if (!groups.length) return nodes;

    const yGap = 100;
    const xGap = 210;
    const minX = 24;
    const maxX = Math.max(minX, width - 210);

    groups.forEach(({ parent, children }) => {
      const parentX = parent.scaled?.[0] || 0;
      const parentY = parent.scaled?.[1] || 0;
      const count = children.length;
      const startX = parentX - ((count - 1) * xGap) / 2;
      children.forEach((child, idx) => {
        const nextX = Math.max(minX, Math.min(maxX, startX + idx * xGap));
        const nextY = parentY + yGap;
        child.scaled = [nextX, nextY];
      });
    });

    return nodes;
  }

  function applyNarrowStackLayout(nodes, width) {
    if (width > 640) {
      return nodes;
    }
    const x = Math.max(20, (width - BOX_WIDTH) / 2);
    const yStart = 24;
    const yGap = 92;
    nodes.forEach((node, index) => {
      node.scaled = [x, yStart + index * yGap];
    });
    return nodes;
  }

  function drawConnections(container, data, nodes, nodeElements, width, height) {
    const pairs = buildConnectionPairs(data, nodes);
    if (!pairs.length) return;

    const ns = 'http://www.w3.org/2000/svg';
    const svg = document.createElementNS(ns, 'svg');
    svg.setAttribute('class', 'flow-links');
    svg.setAttribute('width', String(width));
    svg.setAttribute('height', String(height));
    svg.setAttribute('viewBox', `0 0 ${width} ${height}`);

    pairs.forEach(([fromNode, toNode]) => {
      const fromEl = nodeElements.get(String(fromNode.id || ''));
      const toEl = nodeElements.get(String(toNode.id || ''));
      const startX = fromEl
        ? fromEl.offsetLeft + fromEl.offsetWidth / 2
        : (fromNode.scaled?.[0] || 0) + BOX_WIDTH / 2;
      const startY = fromEl
        ? fromEl.offsetTop + fromEl.offsetHeight
        : fromNode.scaled?.[1] || 0;
      const endX = toEl
        ? toEl.offsetLeft + toEl.offsetWidth / 2
        : (toNode.scaled?.[0] || 0) + BOX_WIDTH / 2;
      const endY = toEl ? toEl.offsetTop : toNode.scaled?.[1] || 0;
      const bend = Math.max(36, Math.abs(endY - startY) * 0.45);
      const path = document.createElementNS(ns, 'path');
      path.setAttribute(
        'd',
        `M ${startX} ${startY} C ${startX} ${startY + bend}, ${endX} ${endY - bend}, ${endX} ${endY}`
      );
      svg.appendChild(path);
    });

    container.insertBefore(svg, container.firstChild || null);
  }

  function renderFlowchartFromData(targetId, data) {
    const container = document.getElementById(targetId);
    if (!container || !data) return;
    container.innerHTML = '';
    const nodes = (data.nodes || []).filter((node) => node.id !== 'trigger');

    const width = container.clientWidth || 800;
    const height = container.clientHeight || 1;

    const scaledNodes = scalePositions(nodes, width, height);
    applyNarrowStackLayout(scaledNodes, width);
    applyParentChildLayout(data, scaledNodes, width);
    const nodeElements = new Map();
    const hash = safeGetHash();
    const activeNodeId = String(hash.node || window.currentPipelineNodeId || '').trim();

    scaledNodes.forEach((node) => {
      const box = document.createElement('div');
      box.className = 'flow-node';
      box.dataset.nodeId = node.id || '';
      if (activeNodeId && String(node.id || '') === activeNodeId) {
        box.classList.add('flow-node--active');
      }
      const [x, y] = node.scaled || [0, 0];
      box.style.left = `${x}px`;
      box.style.top = `${y}px`;

      const link = document.createElement('a');
      link.className = 'flow-node-link';
      link.href = `#node=${encodeURIComponent(node.id || '')}`;
      link.addEventListener('click', (event) => {
        event.preventDefault();
        const nodeId = node.id || '';
        if (!nodeId) return;
        goNodeHashOnly(nodeId);
      });

      const title = document.createElement('h4');
      title.textContent = node.name || node.id;
      const meta = document.createElement('p');
      meta.textContent = node.type || '';

      link.appendChild(title);
      link.appendChild(meta);
      box.appendChild(link);
      container.appendChild(box);
      if (node.id) {
        nodeElements.set(String(node.id), box);
      }
    });

    let contentBottom = 0;
    nodeElements.forEach((el) => {
      const bottom = el.offsetTop + el.offsetHeight;
      if (bottom > contentBottom) {
        contentBottom = bottom;
      }
    });
    const renderHeight = Math.max(1, contentBottom + 28);
    container.style.height = `${renderHeight}px`;

    drawConnections(container, data, scaledNodes, nodeElements, width, renderHeight);
  }

  async function renderFlowchart(targetId) {
    if (!cachedFlowData) {
      const response = await fetch(NODES_JSON);
      cachedFlowData = await response.json();
    }
    renderFlowchartFromData(targetId, cachedFlowData);
  }

  window.renderFlowchart = renderFlowchart;

  window.addEventListener('resize', () => {
    const panelFlow = document.getElementById('panelFlow');
    if (panelFlow && panelFlow.classList.contains('is-hidden')) {
      return;
    }
    if (resizeRaf) {
      cancelAnimationFrame(resizeRaf);
    }
    resizeRaf = requestAnimationFrame(() => {
      resizeRaf = null;
      renderFlowchart('flowchart');
    });
  });
})();
