(function () {
  const NODES_CSV = '../nodes.csv';
  const CONFIG_FILENAME = 'config.yaml';
  const FLASK_SERVER_URL = 'http://localhost:5001';
  const FLASK_HEALTH_ENDPOINT = `${FLASK_SERVER_URL}/health`;
  const FLASK_RUN_ENDPOINT = `${FLASK_SERVER_URL}/api/nodes/run`;
  const FLASK_SAVE_CONFIG_ENDPOINT = `${FLASK_SERVER_URL}/api/config/save`;
  const LOCAL_API_BASE = './api';
  const INPUT_TABS = {
    overview: { name: 'Overview' },
    fields: { name: 'Fields' },
    yaml: { name: 'Yaml' },
    notes: { name: 'Notes' },
    all: { name: 'All' },
  };

  const state = {
    nodes: [],
    filtered: [],
    activeId: null,
    configValues: {},
    configSchema: [],
    generalConfigSchema: [],
    generalSectionSchemas: [],
    nodeSpecificConfigSchema: [],
    rawConfigText: '',
    rawConfigOriginalText: '',
    rawConfigValid: true,
    rawConfigSaveMessage: '',
    rawConfigSaveIsSuccess: false,
    commandBase: '',
    adminNotePath: '',
    flaskAvailable: null,
    localApiAvailable: null,
    isRunning: false,
    flowVisible: false,
    viewMode: 'both',
    inputMode: 'overview',
    requiredFieldKeys: [],
    hashNodeId: '',
    hashSourcePython: '',
  };

  let flaskCheckPromise = null;
  let localApiCheckPromise = null;

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

  function safeGoHash(update) {
    if (typeof goHash === 'function') {
      goHash(update);
      return;
    }
    const hash = safeGetHash();
    Object.assign(hash, update);
    const next = Object.keys(hash)
      .filter((key) => hash[key] !== undefined && hash[key] !== null && hash[key] !== '')
      .map((key) => `${key}=${encodeURIComponent(hash[key])}`)
      .join('&');
    window.location.hash = next;
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
    } else {
      safeGoHash(update);
    }
  }

  function resolveInputMode(inputValue) {
    if (!inputValue) return 'overview';
    const normalized = String(inputValue).trim().toLowerCase();
    if (Object.prototype.hasOwnProperty.call(INPUT_TABS, normalized)) {
      return normalized;
    }
    return 'all';
  }

  function normalizeYamlForCompare(text) {
    return String(text || '')
      .replace(/\r\n/g, '\n')
      .trim();
  }

  function hasUnsavedRawConfigChanges() {
    return (
      normalizeYamlForCompare(state.rawConfigText) !==
      normalizeYamlForCompare(state.rawConfigOriginalText)
    );
  }

  function renderRawSaveStatus() {
    const statusEl = document.getElementById('rawConfigSaveStatus');
    if (!statusEl) return;
    statusEl.textContent = state.rawConfigSaveMessage || '';
    statusEl.classList.remove('status-success', 'status-error');
    if (state.rawConfigSaveMessage) {
      statusEl.classList.add(state.rawConfigSaveIsSuccess ? 'status-success' : 'status-error');
    }
  }

  function clearSavedStatusWhenDirty() {
    if (hasUnsavedRawConfigChanges() && state.rawConfigSaveMessage === 'Saved config.yaml') {
      state.rawConfigSaveMessage = '';
      state.rawConfigSaveIsSuccess = false;
      renderRawSaveStatus();
    }
  }

  function renderInputTabs() {
    const container = document.getElementById('inputTabsContainer');
    if (!container) return;
    const hash = safeGetHash();
    const mode = resolveInputMode(hash.input);
    state.inputMode = mode;

    const tabsHtml = [
      '<div class="page-tab-container">',
      ...Object.keys(INPUT_TABS).map((key) => {
        const isActive = key === mode ? ' active' : '';
        return `<button class="page-tab${isActive}" id="input-${key}-tab" type="button" data-input="${key}">${INPUT_TABS[key].name}</button>`;
      }),
      '</div>',
      '<div class="page-tab-line"></div>',
    ].join('');
    container.innerHTML = tabsHtml;

    container.querySelectorAll('.page-tab[data-input]').forEach((tab) => {
      tab.addEventListener('click', () => {
        const value = tab.getAttribute('data-input') || 'overview';
        safeGoHash({ input: value });
      });
    });
  }

  function applyInputSectionVisibility() {
    const sections = {
      overview: document.getElementById('overviewSection'),
      fields: document.getElementById('detailConfig'),
      yaml: document.getElementById('rawConfigSection'),
      notes: document.getElementById('adminNoteSection'),
      save: document.getElementById('rawConfigSaveSection'),
    };
    const mode = state.inputMode || 'overview';
    const showAll = mode === 'all';
    const hasRawYaml = Boolean((state.rawConfigText || '').trim());
    const hasAdminNote = Boolean((state.adminNotePath || '').trim());
    const showOverview = showAll || mode === 'overview';
    const showFields = showAll || mode === 'fields';
    const showYaml = hasRawYaml && (showAll || mode === 'yaml');
    const showNotes = hasAdminNote && (showAll || mode === 'notes');
    const inSaveViews = showAll || mode === 'fields' || mode === 'yaml';
    const isDirty = hasUnsavedRawConfigChanges();
    const showSavedMessageOnly = !isDirty && state.rawConfigSaveMessage === 'Saved config.yaml';
    const showSaveSection = inSaveViews && (isDirty || showSavedMessageOnly);
    const showSaveButton = inSaveViews && isDirty;

    if (sections.overview) sections.overview.classList.toggle('is-hidden', !showOverview);
    if (sections.fields) sections.fields.classList.toggle('is-hidden', !showFields);
    if (sections.yaml) sections.yaml.classList.toggle('is-hidden', !showYaml);
    if (sections.notes) sections.notes.classList.toggle('is-hidden', !showNotes);
    if (sections.save) sections.save.classList.toggle('is-hidden', !showSaveSection);
    const saveBtn = document.getElementById('saveRawConfig');
    if (saveBtn) {
      saveBtn.classList.toggle('is-hidden', !showSaveButton);
    }
    renderRawSaveStatus();
  }

  function normalizeNodeLink(link) {
    if (!link) return '';
    return String(link)
      .trim()
      .replace(/^(\.\.\/)+/, '')
      .replace(/^\/+/, '');
  }

  function buildNodeUrl(link) {
    const raw = String(link || '').trim().replace(/^(\.\.\/)+/, '').replace(/^\/+/, '');
    if (!raw) return '';

    if (raw.startsWith('data-pipeline/')) {
      return `../${raw.replace(/^data-pipeline\//, '')}`;
    }

    if (raw.startsWith('exiobase/')) {
      return `../../${raw}`;
    }

    const normalized = normalizeNodeLink(link);
    return normalized ? `../${normalized}` : '';
  }

  function buildConfigGithubUrl(nodeLink) {
    const raw = String(nodeLink || '').trim().replace(/^(\.\.\/)+/, '').replace(/^\/+/, '');
    const normalized = normalizeNodeLink(nodeLink);
    if (!raw && !normalized) return '';

    if (raw.startsWith('data-pipeline/')) {
      const repoPath = raw.replace(/^data-pipeline\//, '');
      return `https://github.com/ModelEarth/data-pipeline/blob/main/${repoPath}/${CONFIG_FILENAME}`;
    }

    if (raw.startsWith('exiobase/')) {
      const repoPath = raw.replace(/^exiobase\//, '');
      return `https://github.com/ModelEarth/exiobase/blob/main/${repoPath}/${CONFIG_FILENAME}`;
    }

    if (normalized.startsWith('exiobase/')) {
      const repoPath = normalized.replace(/^exiobase\//, '');
      return `https://github.com/ModelEarth/exiobase/blob/main/${repoPath}/${CONFIG_FILENAME}`;
    }

    if (normalized) {
      return `https://github.com/ModelEarth/data-pipeline/blob/main/${normalized}/${CONFIG_FILENAME}`;
    }

    return '';
  }

  function buildNodeGithubFolderUrl(nodeLink) {
    const raw = String(nodeLink || '').trim().replace(/^(\.\.\/)+/, '').replace(/^\/+/, '');
    const normalized = normalizeNodeLink(nodeLink);
    if (!raw && !normalized) return '';

    if (raw.startsWith('data-pipeline/')) {
      const repoPath = raw.replace(/^data-pipeline\//, '');
      return `https://github.com/ModelEarth/data-pipeline/tree/main/${repoPath}`;
    }

    if (raw.startsWith('exiobase/')) {
      const repoPath = raw.replace(/^exiobase\//, '');
      return `https://github.com/ModelEarth/exiobase/tree/main/${repoPath}`;
    }

    if (normalized.startsWith('exiobase/')) {
      const repoPath = normalized.replace(/^exiobase\//, '');
      return `https://github.com/ModelEarth/exiobase/tree/main/${repoPath}`;
    }

    if (normalized) {
      return `https://github.com/ModelEarth/data-pipeline/tree/main/${normalized}`;
    }

    return '';
  }

  function setConfigGithubLink(node) {
    const linkEl = document.getElementById('configGithubLink');
    const popupLinkEl = document.getElementById('configYamlGithubLink');
    const folderPathEl = document.getElementById('pythonFolderGithubLink');
    const href = buildConfigGithubUrl(node && node.link ? node.link : '');
    const folderHref = buildNodeGithubFolderUrl(node && node.link ? node.link : '');
    const displayPath = normalizeNodeLink(node && node.link ? node.link : '') || 'Details path';
    if (!href) {
      if (linkEl) {
        linkEl.classList.add('is-hidden');
        linkEl.removeAttribute('href');
      }
      if (popupLinkEl) {
        popupLinkEl.removeAttribute('href');
        popupLinkEl.setAttribute('aria-disabled', 'true');
        popupLinkEl.classList.add('is-disabled-link');
      }
      if (folderPathEl) {
        if (folderHref) {
          folderPathEl.href = folderHref;
          folderPathEl.textContent = displayPath;
          folderPathEl.removeAttribute('aria-disabled');
          folderPathEl.classList.remove('is-disabled-link');
        } else {
          folderPathEl.removeAttribute('href');
          folderPathEl.textContent = 'Details path';
          folderPathEl.setAttribute('aria-disabled', 'true');
          folderPathEl.classList.add('is-disabled-link');
        }
      }
      return;
    }
    if (linkEl) {
      linkEl.href = href;
      linkEl.classList.remove('is-hidden');
    }
    if (popupLinkEl) {
      popupLinkEl.href = href;
      popupLinkEl.removeAttribute('aria-disabled');
      popupLinkEl.classList.remove('is-disabled-link');
    }
    if (folderPathEl) {
      if (folderHref) {
        folderPathEl.href = folderHref;
        folderPathEl.textContent = displayPath;
        folderPathEl.removeAttribute('aria-disabled');
        folderPathEl.classList.remove('is-disabled-link');
      } else {
        folderPathEl.removeAttribute('href');
        folderPathEl.textContent = 'Details path';
        folderPathEl.setAttribute('aria-disabled', 'true');
        folderPathEl.classList.add('is-disabled-link');
      }
    }
  }

  function resetFlaskAvailability() {
    state.flaskAvailable = null;
    flaskCheckPromise = null;
  }

  function checkFlaskAvailability() {
    if (state.flaskAvailable !== null) {
      return Promise.resolve(state.flaskAvailable);
    }
    if (flaskCheckPromise) {
      return flaskCheckPromise;
    }
    flaskCheckPromise = fetch(FLASK_HEALTH_ENDPOINT, {
      method: 'GET',
      mode: 'cors',
      cache: 'no-cache',
      signal: AbortSignal.timeout(2000),
    })
      .then((response) => {
        state.flaskAvailable = response.ok;
        return response.ok;
      })
      .catch(() => {
        state.flaskAvailable = false;
        return false;
      })
      .finally(() => {
        flaskCheckPromise = null;
      });
    return flaskCheckPromise;
  }

  function resetLocalApiAvailability() {
    state.localApiAvailable = null;
    localApiCheckPromise = null;
  }

  function checkLocalApiAvailability() {
    if (state.localApiAvailable !== null) {
      return Promise.resolve(state.localApiAvailable);
    }
    if (localApiCheckPromise) {
      return localApiCheckPromise;
    }
    localApiCheckPromise = fetch(`${LOCAL_API_BASE}/nodes/run`, {
      method: 'GET',
      cache: 'no-store',
      signal: AbortSignal.timeout(2000),
    })
      .then((response) => {
        state.localApiAvailable = response.status !== 404 && response.status !== 501;
        return state.localApiAvailable;
      })
      .catch(() => {
        state.localApiAvailable = false;
        return false;
      })
      .finally(() => {
        localApiCheckPromise = null;
      });
    return localApiCheckPromise;
  }

  function updateFlaskBanner() {
    const banner = document.getElementById('flaskBanner');
    if (!banner) return;
    if (state.flaskAvailable === false) {
      banner.classList.remove('is-hidden');
    } else {
      banner.classList.add('is-hidden');
    }
  }

  function updateFlaskFallback() {
    const fallback = document.getElementById('flaskFallback');
    const flaskReady = document.getElementById('runFlaskReady');
    const bannerText = document.getElementById('runBannerText');
    if (!fallback || !flaskReady) return;
    if (state.flaskAvailable === false) {
      fallback.classList.remove('is-hidden');
      if (bannerText) {
        const port =
          window.location.port ||
          (window.location.protocol === 'https:' ? '443' : '80');
        bannerText.textContent =
          state.localApiAvailable === true
            ? `Flask server not available. Using Next.js API fallback (port ${port}).`
            : 'Flask server not available. Next.js API fallback unavailable.';
      }
      flaskReady.classList.add('is-hidden');
    } else if (state.flaskAvailable === true) {
      fallback.classList.add('is-hidden');
      flaskReady.classList.remove('is-hidden');
    } else {
      fallback.classList.add('is-hidden');
      flaskReady.classList.add('is-hidden');
    }
  }

  function parseCsvRows(csvText) {
    const rows = [];
    let current = '';
    let row = [];
    let inQuotes = false;

    for (let i = 0; i < csvText.length; i++) {
      const char = csvText[i];
      const next = csvText[i + 1];
      if (char === '"') {
        if (inQuotes && next === '"') {
          current += '"';
          i++;
        } else {
          inQuotes = !inQuotes;
        }
        continue;
      }
      if (!inQuotes && char === ',') {
        row.push(current);
        current = '';
        continue;
      }
      if (!inQuotes && char === '\n') {
        row.push(current);
        rows.push(row);
        row = [];
        current = '';
        continue;
      }
      if (char === '\r') {
        continue;
      }
      current += char;
    }
    if (current.length || row.length) {
      row.push(current);
      rows.push(row);
    }
    return rows;
  }

  async function loadNodes() {
    const response = await fetch(NODES_CSV);
    const text = await response.text();
    const rows = parseCsvRows(text);
    const headers = rows.shift();
    state.nodes = rows
      .filter((row) => row.length && row[0])
      .map((row) => {
        const obj = {};
        headers.forEach((header, idx) => {
          obj[header] = row[idx] || '';
        });
        return obj;
      });
    state.filtered = [...state.nodes];
  }

  function selectNode(nodeId, updateHash = true) {
    if (!nodeId) return;
    state.activeId = nodeId;
    window.currentPipelineNodeId = nodeId;
    if (updateHash) {
      goNodeHashOnly(nodeId);
    }
    renderList();
    renderDetail();
    const panelFlow = document.getElementById('panelFlow');
    if (panelFlow && !panelFlow.classList.contains('is-hidden') && typeof renderFlowchart === 'function') {
      renderFlowchart('flowchart');
    }
  }

  function renderList() {
    const list = document.getElementById('nodeList');
    const count = document.getElementById('nodeCount');
    if (!list) return;
    list.innerHTML = '';
    count.textContent = `${state.filtered.length} nodes`;

    state.filtered.forEach((node) => {
      const card = document.createElement('div');
      card.className = `node-card${node.node_id === state.activeId ? ' active' : ''}`;
      card.dataset.nodeId = node.node_id;

      const name = document.createElement('div');
      name.className = 'node-name';
      name.textContent = node.name || node.node_id;

      const meta = document.createElement('div');
      meta.className = 'node-meta';
      const speed = (node.processing_time_est || '').trim();
      meta.textContent = speed ? `${node.type || 'node'} · ${speed}` : `${node.type || 'node'}`;

      card.appendChild(name);
      card.appendChild(meta);
      card.addEventListener('click', () => selectNode(node.node_id));
      list.appendChild(card);
    });
  }

  function setDetailSummary(node) {
    const summary = document.getElementById('detailSummary');
    const title = document.getElementById('detailTitle');
    const meta = document.getElementById('detailMeta');
    if (!summary || !title || !meta) return;

    if (!node) {
      title.textContent = 'Select a node';
      meta.textContent = '';
      summary.innerHTML = '<div class="panel-meta">Choose a node from the list to view details.</div>';
      return;
    }

    title.textContent = node.name || node.node_id;
    meta.textContent = node.description || '';

    const rawLink = String(node.link || '')
      .trim()
      .replace(/^(\.\.\/)+/, '')
      .replace(/^\/+/, '');
    const normalizedLink = normalizeNodeLink(node.link);
    const detailsUrl = buildNodeUrl(node.link);
    const displayPath = normalizedLink
      ? (() => {
          const parts = normalizedLink.split('/').filter(Boolean);
          if (parts.length > 3) {
            return `${parts.slice(0, 3).join('/')}/...`;
          }
          return parts.join('/');
        })()
      : '';
    const pythonPath = (() => {
      if (!node.python_cmds) return '';
      const parts = String(node.python_cmds).trim().split(/\s+/);
      if (!parts.length) return '';
      if (parts[0].toLowerCase().startsWith('python')) {
        return parts[1] || '';
      }
      return parts[0] || '';
    })();
    const sourcePythonForAddNode = (() => {
      if (!rawLink || !pythonPath) return '';
      return `../../../${rawLink}/${pythonPath}`.replace(/\/{2,}/g, '/');
    })();
    const dependenciesMarkup = node.dependencies
      ? `<div class="tag-list">${String(node.dependencies)
          .split(',')
          .map((item) => item.trim())
          .filter(Boolean)
          .map((item) => `<div class="tag">${item}</div>`)
          .join('')}</div>`
      : '';

    const leftRows = [
      ['ID', node.node_id],
      ['Type', node.type],
      ['Order', node.order, 'detail-kv--order is-hidden'],
      ['Output Info', node.output_info],
      ['Processing Time', node.processing_time_est],
    ].filter(Boolean);

    const rightRows = [
      detailsUrl
        ? [
            'Details',
            `<a href="${detailsUrl}" target="_blank" rel="noopener">${displayPath}</a>`,
          ]
        : null,
      ['Python Path', pythonPath],
      ['Data Sources', node.data_sources],
      ['Dependencies', dependenciesMarkup],
    ].filter(Boolean);

    const formatLabel = (label) => String(label || '').replace(/_/g, ' ');
    const renderRows = (rows) =>
      rows
        .map(
          ([label, value, extraClass]) =>
            `<div class="detail-kv${extraClass ? ` ${extraClass}` : ''}"><span class="key-label">${formatLabel(
              label
            )}</span><div>${
              value === undefined || value === null || value === ''
                ? blankPlaceholderHtml()
                : value
            }</div></div>`
        )
        .join('');

    summary.innerHTML = `
      <div class="detail-columns-row">
        <div class="detail-columns">
          <div class="detail-col">
            ${renderRows(leftRows)}
            <div class="local">
              <button class="btn btn-sm btn-outline" type="button" id="showNodeOrder">row order</button>
              <button class="btn btn-sm btn-outline" type="button" id="updateNodeFromDetails">update row</button>
            </div>
          </div>
          <div class="detail-col">${renderRows(rightRows)}</div>
        </div>
        <button class="detail-info-btn" id="detailMetaInfoBtn" type="button" aria-label="Metadata info" title="Metadata info">i</button>
      </div>
      <div id="inputTabsContainer"></div>
    `;

    const nodeOrderBtn = summary.querySelector('#showNodeOrder');
    if (nodeOrderBtn) {
      nodeOrderBtn.addEventListener('click', () => {
        const orderRow = summary.querySelector('.detail-kv--order');
        if (orderRow) {
          orderRow.classList.remove('is-hidden');
          nodeOrderBtn.remove();
        }
      });
    }

    const updateNodeBtn = summary.querySelector('#updateNodeFromDetails');
    if (updateNodeBtn) {
      updateNodeBtn.addEventListener('click', () => {
        const hashUpdate = {
          node: 'add_node',
          node_id: node.node_id || '',
          source_python: sourcePythonForAddNode,
        };
        if (typeof goHash === 'function') {
          goHash(hashUpdate);
        } else {
          safeGoHash(hashUpdate);
        }
      });
    }

    const detailInfoBtn = summary.querySelector('#detailMetaInfoBtn');
    if (detailInfoBtn) {
      detailInfoBtn.addEventListener('click', () => {
        const popup = document.getElementById('metaInfoPopup');
        if (popup) popup.classList.remove('is-hidden');
      });
    }
  }

  function isApiKeyField(key) {
    const lower = key.toLowerCase();
    return lower.includes('api') && lower.includes('key');
  }

  function fieldIsShort(key) {
    const lower = key.toLowerCase();
    return ['year', 'level', 'state', 'scope'].some((token) => lower.includes(token));
  }

  function fieldShouldBeNarrow(key) {
    const lower = key.toLowerCase();
    return !['path', 'url', 'api'].some((token) => lower.includes(token));
  }

  function fieldIsRightColumn(key) {
    const lower = key.toLowerCase();
    return lower === 'source_python' || lower === 'output_path' || isApiKeyField(key);
  }

  function getNodeOptionsFromList() {
    const listCards = Array.from(document.querySelectorAll('#nodeList .node-card[data-node-id]'));
    const fromDom = listCards
      .map((card) => {
        const nodeId = String(card.getAttribute('data-node-id') || '').trim();
        const nameEl = card.querySelector('.node-name');
        const nodeName = String((nameEl && nameEl.textContent) || nodeId).trim();
        return nodeId ? { id: nodeId, name: nodeName } : null;
      })
      .filter(Boolean);
    if (fromDom.length) return fromDom;

    return (state.nodes || [])
      .map((node) => ({
        id: String(node.node_id || '').trim(),
        name: String(node.name || node.node_id || '').trim(),
      }))
      .filter((item) => item.id);
  }

  function normalizeConfigField(key, value, label = key) {
    if (String(value || '').toLowerCase() === 'required') {
      return {
        key,
        label,
        type: 'text',
        value: '',
        optional: false,
        required: true,
        isApiKey: isApiKeyField(key),
      };
    }

    if (
      value &&
      typeof value === 'object' &&
      String(value.type || '').toLowerCase() === 'flag'
    ) {
      return {
        key,
        label,
        type: 'flag',
        value: Boolean(value.selected),
        optional: true,
        required: Boolean(value.required),
        isApiKey: false,
      };
    }

    if (value && typeof value === 'object' && value.options) {
      const options = String(value.options)
        .split(',')
        .map((opt) => opt.trim())
        .filter(Boolean);
      return {
        key,
        label,
        type: 'select',
        options,
        value: value.selected || options[0] || '',
        optional: false,
        required: Boolean(value.required),
        isApiKey: isApiKeyField(key),
      };
    }

    const textValue = value === null || value === undefined ? '' : String(value);
    const optional = textValue.toLowerCase() === 'optional';

    return {
      key,
      label,
      type: 'text',
      value: optional || isApiKeyField(key) ? '' : textValue,
      optional,
      required: false,
      isApiKey: isApiKeyField(key),
    };
  }

  function toTitleCaseLabel(value) {
    return String(value || '')
      .replace(/_/g, ' ')
      .replace(/\s+/g, ' ')
      .trim()
      .split(' ')
      .filter(Boolean)
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ');
  }

  function isRunFieldValue(value) {
    if (value === null || value === undefined) return true;
    if (typeof value !== 'object') return true;
    return (
      Object.prototype.hasOwnProperty.call(value, 'type') ||
      Object.prototype.hasOwnProperty.call(value, 'options') ||
      Object.prototype.hasOwnProperty.call(value, 'selected')
    );
  }

  function guessScriptKeyFromNode(node) {
    if (!node || !node.python_cmds) return '';
    const parts = String(node.python_cmds).trim().split(/\s+/);
    const pyFile = parts.find((part) => /\.py$/i.test(part)) || '';
    if (!pyFile) return '';
    return pyFile
      .replace(/\.py$/i, '')
      .replace(/[^a-z0-9]+/gi, '_')
      .replace(/^_+|_+$/g, '')
      .toLowerCase();
  }

  function flattenConfigObject(source, prefix = '') {
    if (!source || typeof source !== 'object') return {};
    const out = {};
    Object.entries(source).forEach(([key, value]) => {
      const nextKey = prefix ? `${prefix}_${key}` : key;
      if (
        value &&
        typeof value === 'object' &&
        !Array.isArray(value) &&
        !isRunFieldValue(value)
      ) {
        Object.assign(out, flattenConfigObject(value, nextKey));
      } else {
        out[nextKey] = value;
      }
    });
    return out;
  }

  function findNodeConfigSection(nodesObj, node) {
    if (!nodesObj || typeof nodesObj !== 'object') return {};
    const nodeId = String((node && node.node_id) || '').trim();
    if (nodeId && nodesObj[nodeId] && typeof nodesObj[nodeId] === 'object') {
      return nodesObj[nodeId];
    }
    const scriptKey = guessScriptKeyFromNode(node);
    if (scriptKey && nodesObj[scriptKey] && typeof nodesObj[scriptKey] === 'object') {
      return nodesObj[scriptKey];
    }
    return {};
  }

  function collectConfigForNode(config, node) {
    if (!config || typeof config !== 'object') {
      return { general: {}, generalSections: {}, nodeSpecific: {} };
    }
    const general = {};
    const generalSections = {};

    Object.entries(config).forEach(([key, value]) => {
      if (key === 'NODES' || key === 'ADMIN_NOTE' || key === 'REQUIRED') return;
      if (
        value &&
        typeof value === 'object' &&
        !Array.isArray(value) &&
        !isRunFieldValue(value)
      ) {
        generalSections[key] = flattenConfigObject(value, key);
      } else {
        general[key] = value;
      }
    });

    const nodeConfigRaw = findNodeConfigSection(config.NODES, node) || {};
    const nodeConfig = { ...nodeConfigRaw };
    const requiredFromTop = parseRequiredSpec(config.REQUIRED);
    const requiredFromNode = parseRequiredSpec(nodeConfig.REQUIRED);
    if (Object.prototype.hasOwnProperty.call(nodeConfig, 'REQUIRED')) {
      delete nodeConfig.REQUIRED;
    }
    const nodeSpecific = flattenConfigObject(nodeConfig);

    return {
      general,
      generalSections,
      nodeSpecific,
      requiredKeys: [...requiredFromTop, ...requiredFromNode],
    };
  }

  function normalizeFieldKey(key) {
    return String(key || '')
      .trim()
      .toLowerCase()
      .replace(/[\s-]+/g, '_');
  }

  function parseRequiredSpec(requiredSpec) {
    if (!requiredSpec) return [];
    if (Array.isArray(requiredSpec)) {
      return requiredSpec
        .map((item) => normalizeFieldKey(item))
        .filter(Boolean);
    }
    if (typeof requiredSpec === 'string') {
      return requiredSpec
        .split(',')
        .map((item) => normalizeFieldKey(item))
        .filter(Boolean);
    }
    if (typeof requiredSpec === 'object') {
      return Object.keys(requiredSpec)
        .filter((key) => Boolean(requiredSpec[key]))
        .map((key) => normalizeFieldKey(key))
        .filter(Boolean);
    }
    return [];
  }

  function fieldMatchesRequired(fieldKey, requiredKey) {
    const fieldNorm = normalizeFieldKey(fieldKey);
    const reqNorm = normalizeFieldKey(requiredKey);
    return fieldNorm === reqNorm || fieldNorm.endsWith(`_${reqNorm}`);
  }

  function isFieldRequired(field) {
    if (!field) return false;
    if (field.required) return true;
    return state.requiredFieldKeys.some((requiredKey) =>
      fieldMatchesRequired(field.key, requiredKey)
    );
  }

  function isMissingRequiredValue(field, value) {
    if (field.type === 'flag') {
      return value !== true;
    }
    return value === undefined || value === null || String(value).trim() === '';
  }

  function clearRequiredFieldErrors() {
    document.querySelectorAll('.config-field.is-required-missing').forEach((el) => {
      el.classList.remove('is-required-missing');
    });
  }

  function markMissingRequiredFields(missingFields) {
    clearRequiredFieldErrors();
    missingFields.forEach((field) => {
      const el = document.querySelector(`.config-field[data-field-key="${field.key}"]`);
      if (el) el.classList.add('is-required-missing');
    });
  }

  function getMissingRequiredFields() {
    return state.configSchema.filter((field) => {
      if (!isFieldRequired(field)) return false;
      const value = state.configValues[field.key];
      return isMissingRequiredValue(field, value);
    });
  }

  function blankPlaceholderHtml() {
    return '<span class="blank-placeholder" aria-hidden="true">&nbsp;</span>';
  }

  function yamlStringifySafe(obj) {
    if (typeof YAML === 'undefined') return '';
    if (typeof YAML.stringify === 'function') return YAML.stringify(obj);
    if (typeof YAML.dump === 'function') return YAML.dump(obj);
    return '';
  }

  function findLeafPaths(obj, prefix = '', path = []) {
    if (!obj || typeof obj !== 'object' || Array.isArray(obj)) return [];
    const leaves = [];
    Object.entries(obj).forEach(([key, value]) => {
      const flatKey = prefix ? `${prefix}_${key}` : key;
      const nextPath = path.concat(key);
      if (
        value &&
        typeof value === 'object' &&
        !Array.isArray(value) &&
        !isRunFieldValue(value)
      ) {
        leaves.push(...findLeafPaths(value, flatKey, nextPath));
      } else {
        leaves.push({
          flatKey,
          normalizedKey: normalizeFieldKey(flatKey),
          path: nextPath,
          value,
        });
      }
    });
    return leaves;
  }

  function getValueAtPath(obj, path) {
    let current = obj;
    for (let i = 0; i < path.length; i++) {
      if (!current || typeof current !== 'object') return undefined;
      current = current[path[i]];
    }
    return current;
  }

  function setValueAtPath(obj, path, nextValue) {
    if (!obj || typeof obj !== 'object' || !path.length) return false;
    let current = obj;
    for (let i = 0; i < path.length - 1; i++) {
      const key = path[i];
      if (!current[key] || typeof current[key] !== 'object') return false;
      current = current[key];
    }
    current[path[path.length - 1]] = nextValue;
    return true;
  }

  function applyFieldValueToLeafValue(existingValue, field, value) {
    if (field.type === 'flag') {
      const boolVal = Boolean(value);
      if (
        existingValue &&
        typeof existingValue === 'object' &&
        !Array.isArray(existingValue) &&
        String(existingValue.type || '').toLowerCase() === 'flag'
      ) {
        return { ...existingValue, selected: boolVal };
      }
      return boolVal;
    }

    const textVal = value === undefined || value === null ? '' : String(value);
    if (
      existingValue &&
      typeof existingValue === 'object' &&
      !Array.isArray(existingValue) &&
      Object.prototype.hasOwnProperty.call(existingValue, 'options')
    ) {
      return { ...existingValue, selected: textVal };
    }
    return textVal;
  }

  function updateFieldInObject(targetObj, field, value) {
    if (!targetObj || typeof targetObj !== 'object') return false;
    const targetNorm = normalizeFieldKey(field.key);
    const leaves = findLeafPaths(targetObj);
    if (!leaves.length) return false;

    const exactMatch = leaves.find((leaf) => leaf.normalizedKey === targetNorm);
    const suffixMatch = leaves.find((leaf) => leaf.normalizedKey.endsWith(`_${targetNorm}`));
    const match = exactMatch || suffixMatch;
    if (!match) return false;

    const existingValue = getValueAtPath(targetObj, match.path);
    const nextValue = applyFieldValueToLeafValue(existingValue, field, value);
    return setValueAtPath(targetObj, match.path, nextValue);
  }

  function findNodeConfigContainer(config, node) {
    if (!config || typeof config !== 'object' || !config.NODES || typeof config.NODES !== 'object') {
      return null;
    }
    const nodeId = String((node && node.node_id) || '').trim();
    if (nodeId && config.NODES[nodeId] && typeof config.NODES[nodeId] === 'object') {
      return config.NODES[nodeId];
    }
    const scriptKey = guessScriptKeyFromNode(node);
    if (scriptKey && config.NODES[scriptKey] && typeof config.NODES[scriptKey] === 'object') {
      return config.NODES[scriptKey];
    }
    return null;
  }

  function syncRawConfigFromFieldChange(field, value) {
    if (!field) return;
    if (typeof YAML === 'undefined') return;
    const node = state.nodes.find((n) => n.node_id === state.activeId);
    const sourceText =
      state.rawConfigText ||
      (document.getElementById('rawConfigYaml') && document.getElementById('rawConfigYaml').value) ||
      '';
    if (!sourceText.trim()) return;

    let configObj;
    try {
      configObj = YAML.parse(sourceText) || {};
    } catch (err) {
      return;
    }

    let updated = false;
    const nodeContainer = findNodeConfigContainer(configObj, node);
    if (nodeContainer) {
      updated = updateFieldInObject(nodeContainer, field, value) || updated;
    }
    if (!updated) {
      updated = updateFieldInObject(configObj, field, value) || updated;
    }
    if (!updated) return;

    const nextYaml = yamlStringifySafe(configObj);
    if (!nextYaml) return;
    state.rawConfigText = nextYaml;
    state.rawConfigValid = true;

    const rawEl = document.getElementById('rawConfigYaml');
    if (rawEl) {
      rawEl.value = nextYaml;
      rawEl.classList.remove('invalid-yaml');
    }
    clearSavedStatusWhenDirty();
    applyInputSectionVisibility();
  }

  function buildCommand() {
    const pieces = [state.commandBase];
    state.configSchema.forEach((field) => {
      const value = state.configValues[field.key];
      if (field.type === 'flag') {
        if (value) {
          const flag = `--${field.key.toLowerCase().replace(/_/g, '-')}`;
          pieces.push(flag);
        }
        return;
      }
      if (field.isApiKey) {
        const lowered = String(value || '').toLowerCase();
        if (!value || lowered === 'optional' || String(value).length <= 8) {
          return;
        }
      }
      if (value === undefined || value === null || value === '') {
        return;
      }
      const flag = `--${field.key.toLowerCase().replace(/_/g, '-')}`;
      pieces.push(`${flag} ${value}`);
    });
    return pieces.join(' ').trim();
  }

  function renderConfigForm() {
    const formWrap = document.getElementById('configForm');
    const commandEl = document.getElementById('pythonCommand');
    if (!formWrap || !commandEl) return;

    const hasGeneral = state.generalConfigSchema.length > 0;
    const hasGeneralSections = state.generalSectionSchemas.some(
      (section) => section.fields && section.fields.length > 0
    );
    const hasNodeSpecific = state.nodeSpecificConfigSchema.length > 0;
    if (!hasGeneral && !hasGeneralSections && !hasNodeSpecific) {
      formWrap.innerHTML = '<div class="panel-meta">No config.yaml found for this node.</div>';
      commandEl.value = state.commandBase || '';
      renderOverviewSection();
      return;
    }

    const renderGrid = (fields) => {
      const grid = document.createElement('div');
      grid.className = 'config-grid';
      const leftCol = document.createElement('div');
      leftCol.className = 'config-column config-column-left';
      const rightCol = document.createElement('div');
      rightCol.className = 'config-column config-column-right';

      const preferredRight = fields.filter((field) => fieldIsRightColumn(field.key));
      const preferredLeft = fields.filter((field) => !fieldIsRightColumn(field.key));
      const splitIndex = Math.ceil(preferredLeft.length / 2);
      const leftFields = preferredLeft.slice(0, splitIndex);
      const rightFields = preferredRight.concat(preferredLeft.slice(splitIndex));

      const appendField = (field, col) => {
        const wrapper = document.createElement('div');
        wrapper.className = 'config-field';
        wrapper.setAttribute('data-field-key', field.key);
        if (fieldIsShort(field.key)) {
          wrapper.classList.add('short');
        }
        if (fieldShouldBeNarrow(field.key) && !fieldIsRightColumn(field.key)) {
          wrapper.classList.add('narrow');
        }

        const label = document.createElement('label');
        label.className = 'key-label';
        label.textContent = toTitleCaseLabel(field.label || field.key);

        if (isFieldRequired(field)) {
          const required = document.createElement('small');
          required.textContent = '(required)';
          label.appendChild(required);
        } else if (field.isApiKey && field.optional) {
          const optional = document.createElement('small');
          optional.textContent = '(optional)';
          label.appendChild(optional);
        }

        wrapper.appendChild(label);

        let input;
        const isNodeIdField = String(field.key || '').toLowerCase() === 'node_id';
        const currentValue = state.configValues[field.key] || field.value || '';
        const useNodeIdPicker =
          isNodeIdField && String(currentValue).trim().toLowerCase() === 'choose';

        if (useNodeIdPicker) {
          input = document.createElement('select');
          const chooseOption = document.createElement('option');
          chooseOption.value = 'choose';
          chooseOption.textContent = 'New or Existing Row...';
          input.appendChild(chooseOption);
          const newOption = document.createElement('option');
          newOption.value = 'new';
          newOption.textContent = 'Add new pipeline row';
          input.appendChild(newOption);
          getNodeOptionsFromList().forEach((item) => {
            const option = document.createElement('option');
            option.value = item.id;
            option.textContent = item.name;
            input.appendChild(option);
          });
          input.value = currentValue;

          const newNodeInput = document.createElement('input');
          newNodeInput.type = 'text';
          newNodeInput.placeholder = 'Enter new node_id';
          newNodeInput.className = 'node-id-new-input is-hidden';

          const syncPickerValue = () => {
            const selectedValue = String(input.value || '').trim();
            if (selectedValue === 'new') {
              newNodeInput.classList.remove('is-hidden');
              const typedNodeId = String(newNodeInput.value || '').trim();
              state.configValues[field.key] = typedNodeId;
              syncRawConfigFromFieldChange(field, typedNodeId);
            } else {
              newNodeInput.classList.add('is-hidden');
              state.configValues[field.key] = selectedValue;
              syncRawConfigFromFieldChange(field, selectedValue);
            }
            commandEl.value = buildCommand();
            renderOverviewSection();
            clearRequiredFieldErrors();
          };

          input.addEventListener('change', syncPickerValue);
          newNodeInput.addEventListener('input', syncPickerValue);
          newNodeInput.addEventListener('change', syncPickerValue);

          wrapper.appendChild(input);
          wrapper.appendChild(newNodeInput);
          col.appendChild(wrapper);
          return;
        } else if (field.type === 'select') {
          input = document.createElement('select');
          field.options.forEach((opt) => {
            const option = document.createElement('option');
            option.value = opt;
            option.textContent = opt;
            input.appendChild(option);
          });
          input.value = currentValue;
        } else {
          input = document.createElement('input');
          if (field.type === 'flag') {
            input.type = 'checkbox';
            input.checked = Boolean(state.configValues[field.key]);
          } else {
            input.type = 'text';
            input.value = currentValue;
          }
        }

        const onFieldChange = () => {
          const nextValue = field.type === 'flag' ? input.checked : input.value;
          state.configValues[field.key] = nextValue;
          syncRawConfigFromFieldChange(field, nextValue);
          commandEl.value = buildCommand();
          renderOverviewSection();
          clearRequiredFieldErrors();
        };
        input.addEventListener('input', onFieldChange);
        input.addEventListener('change', onFieldChange);

        wrapper.appendChild(input);
        col.appendChild(wrapper);
      };

      leftFields.forEach((field) => appendField(field, leftCol));
      rightFields.forEach((field) => appendField(field, rightCol));

      grid.appendChild(leftCol);
      grid.appendChild(rightCol);
      return grid;
    };

    formWrap.innerHTML = '';

    if (hasGeneral) {
      formWrap.appendChild(renderGrid(state.generalConfigSchema));
    }

    if (hasGeneralSections) {
      state.generalSectionSchemas.forEach((section) => {
        if (!section.fields || !section.fields.length) return;
        const divider = document.createElement('div');
        divider.className = 'config-divider';
        formWrap.appendChild(divider);

        const sectionTitle = document.createElement('div');
        sectionTitle.className = 'section-title settings-subtitle';
        sectionTitle.textContent = section.title;
        formWrap.appendChild(sectionTitle);

        formWrap.appendChild(renderGrid(section.fields));
      });
    }

    if ((hasGeneral || hasGeneralSections) && hasNodeSpecific) {
      const divider = document.createElement('div');
      divider.className = 'config-divider';
      formWrap.appendChild(divider);
    }

    if (hasNodeSpecific) {
      const nodeTitle = document.createElement('div');
      nodeTitle.className = 'section-title settings-subtitle';
      const nodeIdLabel = (state.activeId || 'node').trim();
      nodeTitle.textContent = `${nodeIdLabel} Settings`;
      formWrap.appendChild(nodeTitle);
      formWrap.appendChild(renderGrid(state.nodeSpecificConfigSchema));
    }

    commandEl.value = buildCommand();
    renderOverviewSection();
  }

  function renderOverviewSection() {
    const wrap = document.getElementById('overviewConfig');
    if (!wrap) return;

    const hasGeneral = state.generalConfigSchema.length > 0;
    const hasGeneralSections = state.generalSectionSchemas.some(
      (section) => section.fields && section.fields.length > 0
    );
    const hasNodeSpecific = state.nodeSpecificConfigSchema.length > 0;

    if (!hasGeneral && !hasGeneralSections && !hasNodeSpecific) {
      wrap.innerHTML = '<div class="panel-meta">No config values available for overview.</div>';
      return;
    }

    const renderOverviewGrid = (fields) => {
      const leftFields = [];
      const rightFields = [];
      const preferredRight = fields.filter((field) => fieldIsRightColumn(field.key));
      const preferredLeft = fields.filter((field) => !fieldIsRightColumn(field.key));
      const splitIndex = Math.ceil(preferredLeft.length / 2);
      leftFields.push(...preferredLeft.slice(0, splitIndex));
      rightFields.push(...preferredRight, ...preferredLeft.slice(splitIndex));

      const renderCol = (columnFields) =>
        columnFields
          .map((field) => {
            const rawValue = state.configValues[field.key];
            const value =
              field.type === 'flag'
                ? rawValue
                  ? 'True'
                  : 'False'
                : rawValue === null || rawValue === undefined || rawValue === ''
                  ? blankPlaceholderHtml()
                  : String(rawValue);
            return `<div class="detail-kv"><span class="key-label">${toTitleCaseLabel(
              field.label || field.key
            )}</span><div>${value}</div></div>`;
          })
          .join('');

      return `
        <div class="overview-grid">
          <div class="overview-column">${renderCol(leftFields)}</div>
          <div class="overview-column">${renderCol(rightFields)}</div>
        </div>
      `;
    };

    const blocks = [];
    if (hasGeneral) {
      blocks.push(renderOverviewGrid(state.generalConfigSchema));
    }
    if (hasGeneralSections) {
      state.generalSectionSchemas.forEach((section) => {
        if (!section.fields || !section.fields.length) return;
        blocks.push('<div class="config-divider"></div>');
        blocks.push(`<div class="section-title settings-subtitle">${section.title}</div>`);
        blocks.push(renderOverviewGrid(section.fields));
      });
    }
    if ((hasGeneral || hasGeneralSections) && hasNodeSpecific) {
      blocks.push('<div class="config-divider"></div>');
    }
    if (hasNodeSpecific) {
      const nodeIdLabel = (state.activeId || 'node').trim();
      blocks.push(`<div class="section-title settings-subtitle">${nodeIdLabel} Settings</div>`);
      blocks.push(renderOverviewGrid(state.nodeSpecificConfigSchema));
    }
    wrap.innerHTML = blocks.join('');
  }

  function renderRawConfig() {
    const section = document.getElementById('rawConfigSection');
    const textarea = document.getElementById('rawConfigYaml');
    if (!section || !textarea) return;
    const text = state.rawConfigText || '';
    textarea.value = text;
    textarea.classList.toggle('invalid-yaml', !state.rawConfigValid);
    renderRawSaveStatus();
    if (text.trim()) {
      section.classList.remove('is-hidden');
    } else {
      section.classList.add('is-hidden');
    }
  }

  function applyConfigObject(config, node) {
    state.adminNotePath =
      config && typeof config === 'object' && typeof config.ADMIN_NOTE === 'string'
        ? config.ADMIN_NOTE.trim()
        : '';

    const toSchema = (obj, stripPrefix = '', titleCase = false) =>
      Object.keys(obj).map((key) => {
        const label =
          stripPrefix && key.startsWith(`${stripPrefix}_`)
            ? key.slice(stripPrefix.length + 1)
            : key;
        return normalizeConfigField(key, obj[key], titleCase ? toTitleCaseLabel(label) : label);
      });

    const { general, generalSections, nodeSpecific, requiredKeys } = collectConfigForNode(
      config,
      node
    );
    state.generalConfigSchema = toSchema(general);
    state.generalSectionSchemas = Object.keys(generalSections).map((sectionKey) => ({
      title: sectionKey,
      fields: toSchema(generalSections[sectionKey], sectionKey, true),
    }));
    state.nodeSpecificConfigSchema = toSchema(nodeSpecific);
    state.configSchema = [
      ...state.generalConfigSchema,
      ...state.generalSectionSchemas.flatMap((section) => section.fields || []),
      ...state.nodeSpecificConfigSchema,
    ];
    state.requiredFieldKeys = requiredKeys || [];
    state.configValues = {};
    state.configSchema.forEach((field) => {
      state.configValues[field.key] = field.value;
    });
  }

  function setConfigValueCaseInsensitive(config, preferredKey, value) {
    if (!config || typeof config !== 'object') return;
    const match = Object.keys(config).find(
      (key) => String(key).toLowerCase() === String(preferredKey).toLowerCase()
    );
    config[match || preferredKey] = value;
  }

  function applyHashOverridesToConfig(config, node) {
    if (!node || String(node.node_id || '').trim() !== 'add_node') {
      return false;
    }
    const hash = safeGetHash();
    if (!hash || typeof hash !== 'object') return false;
    let changed = false;

    if (hash.node_id) {
      setConfigValueCaseInsensitive(config, 'NODE_ID', String(hash.node_id));
      changed = true;
    }

    if (hash.source_python) {
      setConfigValueCaseInsensitive(config, 'SOURCE_PYTHON', String(hash.source_python));
      changed = true;
    }

    return changed;
  }

  function renderAdminNote(nodeLink) {
    const section = document.getElementById('adminNoteSection');
    const adminDiv = document.getElementById('adminDiv');
    if (!section || !adminDiv) return;

    adminDiv.innerHTML = '';
    if (!state.adminNotePath) {
      section.classList.add('is-hidden');
      return;
    }

    let notePath = state.adminNotePath;
    if (!/^https?:\/\//i.test(notePath) && nodeLink) {
      notePath = `${nodeLink}/${notePath}`.replace(/\/{2,}/g, '/');
    }

    section.classList.remove('is-hidden');
    if (typeof loadMarkdown === 'function') {
      loadMarkdown(notePath, 'adminDiv', '_parent');
    } else {
      adminDiv.textContent = `Admin note: ${notePath}`;
    }
  }

  async function loadConfig(node) {
    state.configSchema = [];
    state.generalConfigSchema = [];
    state.generalSectionSchemas = [];
    state.nodeSpecificConfigSchema = [];
    state.configValues = {};
    state.adminNotePath = '';
    state.rawConfigText = '';
    state.rawConfigOriginalText = '';
    state.rawConfigValid = true;
    state.rawConfigSaveMessage = '';
    state.rawConfigSaveIsSuccess = false;

    if (!node || !node.link) {
      renderRawConfig();
      renderConfigForm();
      renderAdminNote('');
      return;
    }

    const link = buildNodeUrl(node.link);
    const configPath = link ? `${link}/${CONFIG_FILENAME}` : '';
    try {
      const response = await fetch(configPath);
      if (!response.ok) throw new Error('config missing');
      const yamlText = await response.text();
      state.rawConfigText = yamlText;
      state.rawConfigOriginalText = yamlText;
      state.rawConfigValid = true;
      state.rawConfigSaveMessage = '';
      state.rawConfigSaveIsSuccess = false;
      if (typeof YAML === 'undefined') {
        throw new Error('YAML parser unavailable');
      }
      const config = YAML.parse(yamlText) || {};
      const mergedFromHash = applyHashOverridesToConfig(config, node);
      if (mergedFromHash) {
        if (typeof YAML.stringify === 'function') {
          state.rawConfigText = YAML.stringify(config);
        } else if (typeof YAML.dump === 'function') {
          state.rawConfigText = YAML.dump(config);
        }
        state.rawConfigOriginalText = state.rawConfigText;
      }
      applyConfigObject(config, node);
    } catch (err) {
      state.configSchema = [];
      state.generalConfigSchema = [];
      state.generalSectionSchemas = [];
      state.nodeSpecificConfigSchema = [];
      state.adminNotePath = '';
      state.rawConfigText = '';
      state.rawConfigOriginalText = '';
      state.rawConfigValid = true;
      state.rawConfigSaveMessage = '';
      state.rawConfigSaveIsSuccess = false;
    }

    renderRawConfig();
    renderConfigForm();
    renderAdminNote(link);
    renderInputTabs();
    applyInputSectionVisibility();
  }

  function setCommandBase(node) {
    if (!node || !node.python_cmds) {
      state.commandBase = '';
      return;
    }
    const base = node.python_cmds.split(' --')[0];
    state.commandBase = base.trim();
  }

  async function renderDetail() {
    const node = state.nodes.find((n) => n.node_id === state.activeId);
    setDetailSummary(node);
    renderInputTabs();
    applyInputSectionVisibility();
    setCommandBase(node);
    setConfigGithubLink(node);

    const openBtn = document.getElementById('openNodeFolder');
    if (openBtn) {
      openBtn.disabled = !node || !node.link;
      openBtn.onclick = () => {
        if (!node || !node.link) return;
        const target = buildNodeUrl(node.link);
        if (target) {
          window.location.href = target;
        }
      };
    }

    const runBtn = document.getElementById('runProcess');
    const runStatus = document.getElementById('runStatus');
    const runResult = document.getElementById('runResult');
    const runResultText = document.getElementById('runResultText');
    if (runBtn) {
      const runDisabled =
        !node ||
        !node.python_cmds ||
        (node.run_process_available &&
          node.run_process_available.toLowerCase &&
          node.run_process_available.toLowerCase() === 'no');
      runBtn.disabled = runDisabled || state.isRunning;
      runBtn.textContent = state.isRunning ? '🔄 Running...' : '▶️ Run Process';
      runBtn.onclick = async () => {
        const missingRequiredFields = getMissingRequiredFields();
        if (missingRequiredFields.length) {
          markMissingRequiredFields(missingRequiredFields);
          if (runStatus) {
            runStatus.textContent = `Missing required fields: ${missingRequiredFields
              .map((field) => toTitleCaseLabel(field.label || field.key))
              .join(', ')}`;
          }
          return;
        }

        if (!node || !node.python_cmds) {
          if (runStatus) runStatus.textContent = 'No Python command available for this node';
          return;
        }
        const commandEl = document.getElementById('pythonCommand');
        const command = (commandEl && commandEl.value) || node.python_cmds;
        const apiUrl =
          state.flaskAvailable === true ? FLASK_RUN_ENDPOINT : `${LOCAL_API_BASE}/nodes/run`;
        state.isRunning = true;
        if (runStatus) runStatus.textContent = 'Running...';
        if (runResult) {
          runResult.classList.add('is-hidden');
          runResult.classList.remove('success', 'error');
        }
        renderDetail();
        try {
          const response = await fetch(apiUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              node_id: node.node_id,
              command,
              working_directory: normalizeNodeLink(node.link),
            }),
          });
          const result = await response.json();
          if (runResultText) {
            runResultText.textContent = result.output || result.stderr || result.error || '';
          }
          if (runResult) {
            runResult.classList.remove('is-hidden');
            runResult.classList.add(result.success ? 'success' : 'error');
          }
          if (runStatus) {
            runStatus.textContent = result.success ? '✅ Success' : '❌ Failed';
          }
        } catch (err) {
          if (runResultText) {
            runResultText.textContent = err.message || 'Failed to run process.';
          }
          if (runResult) {
            runResult.classList.remove('is-hidden');
            runResult.classList.add('error');
          }
          if (runStatus) {
            runStatus.textContent = '❌ Failed';
          }
        } finally {
          state.isRunning = false;
          if (runBtn) {
            runBtn.disabled = runDisabled;
            runBtn.textContent = '▶️ Run Process';
          }
        }
      };
    }

    updateFlaskFallback();

    await loadConfig(node);
  }

  function filterNodes(term) {
    const lower = term.toLowerCase();
    state.filtered = state.nodes.filter((node) => {
      return [node.node_id, node.name, node.description, node.type]
        .filter(Boolean)
        .some((value) => value.toLowerCase().includes(lower));
    });
    renderList();
  }

  function bindSearch() {
    const input = document.getElementById('nodeSearch');
    if (!input) return;
    input.addEventListener('input', () => filterNodes(input.value));
  }

  function bindCopy() {
    const btn = document.getElementById('copyCommand');
    const commandEl = document.getElementById('pythonCommand');
    if (!btn || !commandEl) return;
    btn.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(commandEl.value || '');
        btn.textContent = 'Copied';
        setTimeout(() => {
          btn.textContent = 'Copy';
        }, 1200);
      } catch (err) {
        btn.textContent = 'Copy failed';
      }
    });
  }

  function bindRawConfigEditor() {
    const textarea = document.getElementById('rawConfigYaml');
    if (!textarea) return;
    textarea.addEventListener('input', () => {
      state.rawConfigText = textarea.value || '';
      clearSavedStatusWhenDirty();
      const node = state.nodes.find((n) => n.node_id === state.activeId);
      const nodeLink = node ? buildNodeUrl(node.link) : '';
      if (!state.rawConfigText.trim()) {
        state.configSchema = [];
        state.generalConfigSchema = [];
        state.generalSectionSchemas = [];
        state.nodeSpecificConfigSchema = [];
        state.configValues = {};
        state.adminNotePath = '';
        state.rawConfigValid = true;
        clearSavedStatusWhenDirty();
        textarea.classList.remove('invalid-yaml');
        renderConfigForm();
        renderOverviewSection();
        renderAdminNote(nodeLink);
        applyInputSectionVisibility();
        return;
      }
      try {
        if (typeof YAML === 'undefined') {
          throw new Error('YAML parser unavailable');
        }
        const config = YAML.parse(state.rawConfigText) || {};
        applyConfigObject(config, node);
        state.rawConfigValid = true;
        clearSavedStatusWhenDirty();
        textarea.classList.remove('invalid-yaml');
        renderConfigForm();
        renderOverviewSection();
        renderAdminNote(nodeLink);
        applyInputSectionVisibility();
      } catch (err) {
        state.rawConfigValid = false;
        textarea.classList.add('invalid-yaml');
        applyInputSectionVisibility();
      }
    });
  }

  function setRawSaveStatus(message, isSuccess) {
    state.rawConfigSaveMessage = message || '';
    state.rawConfigSaveIsSuccess = Boolean(isSuccess);
    renderRawSaveStatus();
  }

  function bindRawConfigSave() {
    const saveBtn = document.getElementById('saveRawConfig');
    if (!saveBtn) return;
    saveBtn.addEventListener('click', async () => {
      const node = state.nodes.find((n) => n.node_id === state.activeId);
      if (!node || !node.link) {
        setRawSaveStatus('Save failed: no node selected', false);
        return;
      }
      if (!state.rawConfigText || !state.rawConfigText.trim()) {
        setRawSaveStatus('Save failed: config is empty', false);
        return;
      }

      try {
        if (typeof YAML === 'undefined') {
          throw new Error('YAML parser unavailable');
        }
        YAML.parse(state.rawConfigText);
        state.rawConfigValid = true;
      } catch (err) {
        state.rawConfigValid = false;
        const rawEl = document.getElementById('rawConfigYaml');
        if (rawEl) rawEl.classList.add('invalid-yaml');
        setRawSaveStatus('Save failed: invalid YAML', false);
        return;
      }

      saveBtn.disabled = true;
      setRawSaveStatus('Saving...', true);
      const apiUrl =
        state.flaskAvailable === true
          ? FLASK_SAVE_CONFIG_ENDPOINT
          : `${LOCAL_API_BASE}/config/save`;
      try {
        const response = await fetch(apiUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            working_directory: node.link,
            filename: CONFIG_FILENAME,
            content: state.rawConfigText,
          }),
        });
        const result = await response.json().catch(() => ({}));
        if (!response.ok || !result.success) {
          const message = result.error || `HTTP ${response.status}`;
          throw new Error(message);
        }
        state.rawConfigOriginalText = state.rawConfigText;
        setRawSaveStatus('Saved config.yaml', true);
        applyInputSectionVisibility();
      } catch (err) {
        setRawSaveStatus(`Save failed: ${err.message || 'unknown error'}`, false);
      } finally {
        saveBtn.disabled = false;
      }
    });
  }

  function bindTextareaResizeHandles() {
    const grips = document.querySelectorAll('.textarea-resize-grip[data-target]');
    grips.forEach((grip) => {
      grip.addEventListener('pointerdown', (event) => {
        const targetId = grip.getAttribute('data-target');
        const textarea = targetId ? document.getElementById(targetId) : null;
        if (!textarea) return;

        const startY = event.clientY;
        const startHeight = textarea.offsetHeight;
        const minHeight = 56;

        document.body.classList.add('is-resizing-textarea');

        const onMove = (moveEvent) => {
          const delta = moveEvent.clientY - startY;
          const nextHeight = Math.max(minHeight, startHeight + delta);
          textarea.style.height = `${nextHeight}px`;
        };

        const onUp = () => {
          window.removeEventListener('pointermove', onMove);
          window.removeEventListener('pointerup', onUp);
          document.body.classList.remove('is-resizing-textarea');
        };

        window.addEventListener('pointermove', onMove);
        window.addEventListener('pointerup', onUp);
        event.preventDefault();
      });
    });
  }

  function bindPanelToggles() {
    const setViewMode = (mode, syncHash = true) => {
      const flowBtn = document.getElementById('btnViewFlowchart');
      const adminBtn = document.getElementById('btnViewAdmin');
      const bothBtn = document.getElementById('btnViewBoth');
      const panelList = document.getElementById('panelList');
      const panelDetail = document.getElementById('panelDetail');
      const panelFlow = document.getElementById('panelFlow');
      if (!flowBtn || !adminBtn || !bothBtn || !panelList || !panelDetail || !panelFlow) return;

      let resolvedMode = mode;
      if (!['flowchart', 'admin', 'both'].includes(resolvedMode)) {
        resolvedMode = 'both';
      }
      state.viewMode = resolvedMode;

      const showFlow = resolvedMode !== 'admin';
      const showMain = resolvedMode !== 'flowchart';
      state.flowVisible = showFlow;

      panelFlow.classList.toggle('is-hidden', !showFlow);
      panelList.classList.toggle('is-hidden', !showMain);
      panelDetail.classList.toggle('is-hidden', !showMain);

      flowBtn.classList.toggle('btn-primary', resolvedMode === 'flowchart');
      adminBtn.classList.toggle('btn-primary', resolvedMode === 'admin');
      bothBtn.classList.toggle('is-hidden', resolvedMode === 'both');

      if (showFlow && typeof renderFlowchart === 'function') {
        renderFlowchart('flowchart');
      }
      if (syncHash) {
        const viewValue =
          resolvedMode === 'flowchart' ? 'flowchart' : resolvedMode === 'admin' ? 'admin' : '';
        safeGoHash({ view: viewValue });
      }
    };

    const flowBtn = document.getElementById('btnViewFlowchart');
    const adminBtn = document.getElementById('btnViewAdmin');
    const bothBtn = document.getElementById('btnViewBoth');
    if (!flowBtn || !adminBtn || !bothBtn) return;

    flowBtn.addEventListener('click', () => {
      setViewMode('flowchart', true);
    });
    adminBtn.addEventListener('click', () => {
      setViewMode('admin', true);
    });
    bothBtn.addEventListener('click', () => {
      setViewMode('both', true);
    });

    state.setViewMode = setViewMode;
    window.setPipelineFlowVisible = (visible) => setViewMode(visible ? 'flowchart' : 'admin', true);
  }

  function bindFlaskActivatePopup() {
    const activateBtn = document.getElementById('flaskActivate');
    const popup = document.getElementById('flaskActivatePopup');
    const copyBtn = document.getElementById('flaskPopupCopy');
    const closeBtn = document.getElementById('flaskPopupClose');
    const runCommandsLink = document.getElementById('flaskRunCommands');
    if (!activateBtn || !popup || !closeBtn) return;

    activateBtn.addEventListener('click', (event) => {
      event.preventDefault();
      popup.classList.remove('is-hidden');
    });

    closeBtn.addEventListener('click', () => {
      popup.classList.add('is-hidden');
    });

    if (copyBtn) {
      copyBtn.addEventListener('click', async () => {
        try {
          await navigator.clipboard.writeText('start pipeline');
          popup.classList.add('is-hidden');
        } catch (err) {
          copyBtn.textContent = 'Copy failed';
        }
      });
    }

    if (runCommandsLink) {
      runCommandsLink.addEventListener('click', () => {
        popup.classList.add('is-hidden');
      });
    }

    popup.addEventListener('click', (event) => {
      if (event.target === popup) {
        popup.classList.add('is-hidden');
      }
    });
  }

  function bindMetaInfoPopup() {
    const popup = document.getElementById('metaInfoPopup');
    const closeIconBtn = document.getElementById('metaInfoPopupCloseIcon');
    if (!popup) return;
    if (closeIconBtn) {
      closeIconBtn.addEventListener('click', () => {
        popup.classList.add('is-hidden');
      });
    }

    popup.addEventListener('click', (event) => {
      if (event.target === popup) {
        popup.classList.add('is-hidden');
      }
    });
  }

  function handleHashChange() {
    const hash = safeGetHash();
    const nextInputMode = resolveInputMode(hash.input);
    if (nextInputMode !== state.inputMode) {
      state.inputMode = nextInputMode;
      renderInputTabs();
      applyInputSectionVisibility();
    } else {
      renderInputTabs();
      applyInputSectionVisibility();
    }

    if (typeof state.setViewMode === 'function') {
      if (!Object.prototype.hasOwnProperty.call(hash, 'view') || !hash.view) {
        state.setViewMode('both', false);
      } else if (hash.view === 'flowchart') {
        state.setViewMode('flowchart', false);
      } else if (hash.view === 'admin') {
        state.setViewMode('admin', false);
      } else {
        state.setViewMode('both', false);
      }
    }
    let nodeChanged = false;
    if (hash.node && hash.node !== state.activeId) {
      selectNode(hash.node, false);
      nodeChanged = true;
    }

    const nextHashNodeId = String(hash.node_id || '');
    const nextHashSourcePython = String(hash.source_python || '');
    const configHashChanged =
      nextHashNodeId !== state.hashNodeId || nextHashSourcePython !== state.hashSourcePython;
    if (configHashChanged) {
      state.hashNodeId = nextHashNodeId;
      state.hashSourcePython = nextHashSourcePython;
    }

    if (!nodeChanged && state.activeId === 'add_node' && configHashChanged) {
      renderDetail();
    }
  }

  async function init() {
    await loadNodes();
    bindSearch();
    bindCopy();
    bindRawConfigEditor();
    bindRawConfigSave();
    bindTextareaResizeHandles();
    bindPanelToggles();
    bindFlaskActivatePopup();
    bindMetaInfoPopup();

    renderList();

    const hash = safeGetHash();
    if (hash.node) {
      selectNode(hash.node, false);
    } else if (state.nodes[0]) {
      selectNode(state.nodes[0].node_id, false);
    }
    handleHashChange();

    if (typeof renderFlowchart === 'function') {
      renderFlowchart('flowchart');
    }

    document.addEventListener('hashChangeEvent', handleHashChange);
    window.addEventListener('hashchange', handleHashChange);

    const flaskRetry = document.getElementById('flaskRetry');
    if (flaskRetry) {
      flaskRetry.addEventListener('click', async () => {
        resetFlaskAvailability();
        resetLocalApiAvailability();
        state.flaskAvailable = await checkFlaskAvailability();
        state.localApiAvailable = await checkLocalApiAvailability();
        updateFlaskBanner();
        updateFlaskFallback();
      });
    }

    state.flaskAvailable = await checkFlaskAvailability();
    state.localApiAvailable = await checkLocalApiAvailability();
    updateFlaskBanner();
    updateFlaskFallback();

    setInterval(async () => {
      state.flaskAvailable = await checkFlaskAvailability();
      state.localApiAvailable = await checkLocalApiAvailability();
      updateFlaskBanner();
      updateFlaskFallback();
    }, 30000);
  }

  if (typeof waitForElm === 'function') {
    waitForElm('#nodeList').then(init);
  } else {
    document.addEventListener('DOMContentLoaded', init);
  }
})();
