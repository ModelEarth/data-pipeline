import { useState, useEffect, useRef } from 'react';

export default function NodesList({ onNodeSelect, className = '', onNodeClick, highlightedNode, onHighlightReceived }) {
  const [nodes, setNodes] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [loading, setLoading] = useState(true);
  const listRef = useRef(null);

  useEffect(() => {
    loadNodes();
  }, []);

  useEffect(() => {
    if (highlightedNode && onHighlightReceived) {
      onHighlightReceived(highlightedNode);
      // Scroll to highlighted node
      const nodeElement = document.querySelector(`[data-node-id="${highlightedNode.node_id}"]`);
      if (nodeElement && listRef.current) {
        nodeElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }
  }, [highlightedNode, onHighlightReceived]);

  const parseCSVLine = (line) => {
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
  };

  const loadNodes = async () => {
    try {
      // For production/static mode, load from CSV directly
      const basePath = process.env.NODE_ENV === 'production' ? '/data-pipeline' : '';
      const csvResponse = await fetch(`${basePath}/nodes.csv`);
      
      if (csvResponse.ok) {
        const csvText = await csvResponse.text();
        const lines = csvText.split('\n').filter(line => line.trim());
        const headers = parseCSVLine(lines[0]);
        const csvNodes = [];
        
        for (let i = 1; i < lines.length; i++) {
          const values = parseCSVLine(lines[i]);
          if (values.length >= headers.length - 1) { // Allow for some flexibility
            const node = {};
            headers.forEach((header, index) => {
              node[header.trim()] = values[index] ? values[index].trim() : '';
            });
            csvNodes.push(node);
          }
        }
        setNodes(csvNodes);
      } else {
        // Fallback to API for development
        const apiResponse = await fetch(`${process.env.NODE_ENV === 'production' ? '/data-pipeline/admin' : ''}/api/nodes`);
        if (apiResponse.ok) {
          const data = await apiResponse.json();
          setNodes(data);
        } else {
          setNodes(generateSampleNodes());
        }
      }
    } catch (error) {
      console.error('Failed to load nodes:', error);
      setNodes(generateSampleNodes());
    } finally {
      setLoading(false);
    }
  };

  const generateSampleNodes = () => {
    return [
      {
        node_id: 'eco_001',
        name: 'Economic Data Fetcher',
        description: 'Fetches economic data from USEEIO API',
        type: 'data_fetcher',
        order: 1,
        processing_time_est: 'medium',
        folder_size: '207M'
      },
      {
        node_id: 'zip_001',
        name: 'Zipcode Metrics Generator',
        description: 'Generates zipcode metrics from Census ZBP API',
        type: 'data_processor',
        order: 2,
        processing_time_est: 'fast',
        folder_size: '24K'
      },
      {
        node_id: 'naics_001',
        name: 'NAICS Timeline Aggregator',
        description: 'Aggregates NAICS data across years (2017-2020)',
        type: 'data_aggregator',
        order: 5,
        processing_time_est: 'medium',
        folder_size: '20K'
      },
      {
        node_id: 'ml_001',
        name: 'Random Forest Automator',
        description: 'Automates random forest analysis for poverty prediction',
        type: 'ml_processor',
        order: 9,
        processing_time_est: 'slow',
        folder_size: '375M'
      },
      {
        node_id: 'trade_001',
        name: 'Comtrade Data Fetcher',
        description: 'Fetches trade data from UN Comtrade API',
        type: 'api_fetcher',
        order: 20,
        processing_time_est: 'medium',
        folder_size: '15M'
      }
    ];
  };

  const handleNodeClick = (e, node) => {
    // Prevent click if text is selected
    const selection = window.getSelection();
    if (selection && selection.toString().length > 0) {
      return;
    }
    
    setSelectedNode(node);
    onNodeSelect?.(node);
    onNodeClick?.(); // Bring Node Details to front
  };

  const getTypeColor = (type) => {
    const colors = {
      'data_fetcher': 'text-blue-400',
      'data_processor': 'text-cyan-400',
      'data_aggregator': 'text-emerald-400',
      'ml_processor': 'text-orange-400',
      'api_fetcher': 'text-blue-400'
    };
    return colors[type] || 'text-gray-400';
  };

  const getProcessingIcon = (time) => {
    const icons = {
      'fast': '⚡',
      'medium': '⏱️',
      'slow': '🐌',
      'very_slow': '🔄'
    };
    return icons[time] || '⏱️';
  };

  if (loading) {
    return (
      <div className={`panel p-6 ${className}`}>
        <div className="animate-pulse">
          <div className="h-4 bg-dark-panel-alt rounded mb-4"></div>
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-12 bg-dark-panel-alt rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`panel p-4 ${className}`}>
      <h2 className="text-xl mb-3 text-gray-100 light:text-gray-900">Nodes</h2>
      
      <div className="space-y-2" ref={listRef}>
        {nodes.map((node) => (
          <div
            key={node.node_id}
            data-node-id={node.node_id}
            className={`p-3 rounded-lg cursor-pointer transition-all duration-200 border select-text ${
              highlightedNode?.node_id === node.node_id
                ? 'bg-yellow-500/20 border-yellow-500/50 animate-pulse'
                : selectedNode?.node_id === node.node_id
                ? 'bg-blue-500/10 border-blue-500/30'
                : 'bg-gray-700 hover:bg-gray-600 border-gray-600 hover:border-cyan-400/30 light:bg-gray-100 light:hover:bg-gray-50 light:border-gray-300 light:hover:border-cyan-500/30'
            }`}
            onClick={(e) => handleNodeClick(e, node)}
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="text-sm font-mono text-gray-400">
                  {node.node_id}
                </span>
              </div>
              <span className="text-xs text-gray-400">
                {node.folder_size}
              </span>
            </div>
            
            <h3 className="font-semibold text-sm mb-1 text-gray-100 light:text-gray-900">
              {node.name}
            </h3>
            
            <p className="text-xs text-muted mb-2 line-clamp-2">
              {node.description}
            </p>
            
            <div className="flex items-center justify-between">
              <span className={`text-xs font-medium ${getTypeColor(node.type)}`}>
                {node.type.replace('_', ' ')}
              </span>
              <span className="text-xs text-gray-400">
                #{node.order}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}