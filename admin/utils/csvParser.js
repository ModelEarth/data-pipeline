// Standalone CSV parser that can be embedded as a widget
export class NodesCSVParser {
  constructor(csvContent) {
    this.csvContent = csvContent;
    this.nodes = [];
    this.parse();
  }

  parse() {
    const lines = this.csvContent.split('\n').filter(line => line.trim());
    if (lines.length === 0) return;

    const headers = this.parseCSVLine(lines[0]);
    
    for (let i = 1; i < lines.length; i++) {
      const values = this.parseCSVLine(lines[i]);
      if (values.length === headers.length) {
        const node = {};
        headers.forEach((header, index) => {
          node[header] = values[index];
        });
        this.nodes.push(node);
      }
    }
  }

  parseCSVLine(line) {
    const result = [];
    let current = '';
    let inQuotes = false;
    
    for (let i = 0; i < line.length; i++) {
      const char = line[i];
      
      if (char === '"' && (i === 0 || line[i-1] === ',')) {
        inQuotes = true;
      } else if (char === '"' && inQuotes && (i === line.length - 1 || line[i+1] === ',')) {
        inQuotes = false;
      } else if (char === ',' && !inQuotes) {
        result.push(current.trim());
        current = '';
      } else {
        current += char;
      }
    }
    
    result.push(current.trim());
    return result;
  }

  getNodes() {
    return this.nodes;
  }

  getNodeById(nodeId) {
    return this.nodes.find(node => node.node_id === nodeId);
  }

  getNodesByType(type) {
    return this.nodes.filter(node => node.type === type);
  }

  getSortedByOrder() {
    return [...this.nodes].sort((a, b) => parseInt(a.order) - parseInt(b.order));
  }

  // Generate embeddable widget HTML
  generateWidget(containerId = 'nodes-widget', options = {}) {
    const {
      showSearch = true,
      showFilters = true,
      theme = 'dark',
      maxHeight = '600px'
    } = options;

    return `
      <div id="${containerId}" class="nodes-widget nodes-widget-${theme}">
        <style>
          .nodes-widget {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            border-radius: 12px;
            overflow: hidden;
            max-height: ${maxHeight};
            border: 1px solid #2a2a2a;
          }
          
          .nodes-widget-dark {
            background: #1a1a1a;
            color: #e5e5e5;
          }
          
          .nodes-widget-light {
            background: #ffffff;
            color: #1a1a1a;
          }
          
          .widget-header {
            padding: 16px;
            border-bottom: 1px solid #2a2a2a;
            background: #0f0f0f;
          }
          
          .widget-search {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #2a2a2a;
            border-radius: 8px;
            background: #242424;
            color: #e5e5e5;
            font-size: 14px;
          }
          
          .widget-filters {
            display: flex;
            gap: 8px;
            margin-top: 12px;
            flex-wrap: wrap;
          }
          
          .filter-tag {
            padding: 4px 8px;
            border-radius: 16px;
            font-size: 12px;
            cursor: pointer;
            border: 1px solid #3b82f6;
            color: #3b82f6;
            background: transparent;
          }
          
          .filter-tag.active {
            background: #3b82f6;
            color: white;
          }
          
          .widget-list {
            max-height: calc(${maxHeight} - 120px);
            overflow-y: auto;
          }
          
          .node-item {
            padding: 12px 16px;
            border-bottom: 1px solid #2a2a2a;
            cursor: pointer;
            transition: background-color 0.2s;
          }
          
          .node-item:hover {
            background: #242424;
          }
          
          .node-header {
            display: flex;
            justify-content: between;
            align-items: center;
            margin-bottom: 4px;
          }
          
          .node-id {
            font-family: monospace;
            font-size: 12px;
            color: #06b6d4;
          }
          
          .node-name {
            font-weight: 600;
            margin-bottom: 4px;
          }
          
          .node-description {
            font-size: 13px;
            color: #a0a0a0;
            margin-bottom: 8px;
          }
          
          .node-meta {
            display: flex;
            gap: 12px;
            font-size: 11px;
          }
          
          .node-type {
            color: #10b981;
          }
          
          .node-size {
            color: #f59e0b;
          }
        </style>
        
        ${showSearch ? `
          <div class="widget-header">
            <input 
              type="text" 
              class="widget-search" 
              placeholder="Search nodes..."
              oninput="filterNodes(this.value)"
            >
            ${showFilters ? `
              <div class="widget-filters">
                <button class="filter-tag" onclick="filterByType('')">All</button>
                <button class="filter-tag" onclick="filterByType('data_fetcher')">Fetchers</button>
                <button class="filter-tag" onclick="filterByType('ml_processor')">ML</button>
                <button class="filter-tag" onclick="filterByType('data_processor')">Processors</button>
              </div>
            ` : ''}
          </div>
        ` : ''}
        
        <div class="widget-list">
          ${this.nodes.map(node => `
            <div class="node-item" data-node-id="${node.node_id}" data-type="${node.type}">
              <div class="node-header">
                <span class="node-id">${node.node_id}</span>
              </div>
              <div class="node-name">${node.name}</div>
              <div class="node-description">${node.description}</div>
              <div class="node-meta">
                <span class="node-type">${node.type}</span>
                <span class="node-size">${node.folder_size}</span>
                <span>Order: ${node.order}</span>
              </div>
            </div>
          `).join('')}
        </div>
        
        <script>
          function filterNodes(searchTerm) {
            const items = document.querySelectorAll('#${containerId} .node-item');
            items.forEach(item => {
              const text = item.textContent.toLowerCase();
              item.style.display = text.includes(searchTerm.toLowerCase()) ? 'block' : 'none';
            });
          }
          
          function filterByType(type) {
            const items = document.querySelectorAll('#${containerId} .node-item');
            const tags = document.querySelectorAll('#${containerId} .filter-tag');
            
            tags.forEach(tag => tag.classList.remove('active'));
            event.target.classList.add('active');
            
            items.forEach(item => {
              if (!type || item.dataset.type === type) {
                item.style.display = 'block';
              } else {
                item.style.display = 'none';
              }
            });
          }
          
          // Add click handlers for node selection
          document.querySelectorAll('#${containerId} .node-item').forEach(item => {
            item.addEventListener('click', function() {
              const nodeId = this.dataset.nodeId;
              // Dispatch custom event that parent applications can listen to
              document.dispatchEvent(new CustomEvent('nodeSelected', {
                detail: { nodeId, element: this }
              }));
            });
          });
        </script>
      </div>
    `;
  }
}

// Export for use in browser environments
if (typeof window !== 'undefined') {
  window.NodesCSVParser = NodesCSVParser;
}