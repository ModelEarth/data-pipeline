import { useState, useEffect, useRef } from 'react';

export default function FlowChart({ className = '', onNodeSelect, isFloating = false, hideTitle = false, onHighlightInList, focusedNode = null }) {
  const [nodes, setNodes] = useState([]);
  const [connections, setConnections] = useState([]);
  const [csvNodes, setCsvNodes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [draggedNode, setDraggedNode] = useState(null);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const [isDraggingChart, setIsDraggingChart] = useState(false);
  const [chartOffset, setChartOffset] = useState({ x: 0, y: 0 });
  const [clickStartPos, setClickStartPos] = useState({ x: 0, y: 0 });
  const [hoveredNode, setHoveredNode] = useState(null);
  const [showMenu, setShowMenu] = useState(null);
  const [expandedNode, setExpandedNode] = useState(null);
  const [menuPosition, setMenuPosition] = useState({ x: 0, y: 0 });
  const [originalNodes, setOriginalNodes] = useState([]);
  const svgRef = useRef(null);

  useEffect(() => {
    loadFlowData();
  }, []);

  // Reposition nodes when focusedNode changes
  useEffect(() => {
    if (!focusedNode || nodes.length === 0) return;

    const focusedNodeId = focusedNode.node_id;
    const focusedFlowNode = nodes.find(n => n.id === focusedNodeId);

    if (focusedFlowNode) {
      // Save original positions if not already saved
      if (originalNodes.length === 0) {
        setOriginalNodes(nodes.map(n => ({ ...n, position: [...n.position] })));
      }

      // Position focused node on the left
      const newNodes = nodes.map(node => {
        if (node.id === focusedNodeId) {
          return { ...node, position: [50, 200] };
        }
        // Position other nodes to the right
        const otherIndex = nodes.filter(n => n.id !== focusedNodeId).indexOf(node);
        if (otherIndex >= 0) {
          const row = Math.floor(otherIndex / 2);
          const col = otherIndex % 2;
          return {
            ...node,
            position: [300 + col * 250, 100 + row * 120]
          };
        }
        return node;
      });

      setNodes(newNodes);
    }
  }, [focusedNode?.node_id]);

  // Reset positions when focusedNode is cleared
  useEffect(() => {
    if (!focusedNode && originalNodes.length > 0) {
      setNodes(originalNodes);
      setOriginalNodes([]);
    }
  }, [focusedNode]);

  const loadFlowData = async () => {
    try {
      // Always use /data-pipeline path
      const basePath = '/data-pipeline';

      // Load CSV data for node details
      const csvResponse = await fetch(`${basePath}/nodes.csv`);
      if (csvResponse.ok) {
        const csvText = await csvResponse.text();
        const lines = csvText.split('\n').filter(line => line.trim());
        const headers = lines[0].split(',').map(h => h.trim());
        const csvData = [];
        
        for (let i = 1; i < lines.length; i++) {
          const values = lines[i].split(',');
          if (values.length >= headers.length - 1) {
            const node = {};
            headers.forEach((header, index) => {
              node[header.trim()] = values[index] ? values[index].trim() : '';
            });
            csvData.push(node);
          }
        }
        setCsvNodes(csvData);
      }
      
      // Load flow chart data
      const response = await fetch(`${basePath}/nodes.json`);
      if (response.ok) {
        const data = await response.json();
        setNodes(data.nodes || []);
        setConnections(data.connections || {});
      } else {
        // Fallback: generate sample flow data
        generateSampleFlow();
      }
    } catch (error) {
      console.error('Failed to load flow data:', error);
      generateSampleFlow();
    } finally {
      setLoading(false);
    }
  };

  const generateSampleFlow = () => {
    const sampleNodes = [
      {
        id: 'trigger',
        name: 'Start Pipeline',
        position: [100, 300],
        type: 'trigger'
      },
      {
        id: 'eco_001',
        name: 'Economic Data Fetcher',
        position: [300, 100],
        type: 'data_fetcher'
      },
      {
        id: 'zip_001',
        name: 'Zipcode Metrics',
        position: [500, 200],
        type: 'data_processor'
      },
      {
        id: 'naics_001',
        name: 'NAICS Timeline',
        position: [700, 300],
        type: 'data_aggregator'
      },
      {
        id: 'ml_001',
        name: 'ML Processor',
        position: [900, 400],
        type: 'ml_processor'
      }
    ];

    const sampleConnections = {
      'Start Pipeline': {
        main: [[{ node: 'Economic Data Fetcher', type: 'main', index: 0 }]]
      },
      'Economic Data Fetcher': {
        main: [[{ node: 'Zipcode Metrics', type: 'main', index: 0 }]]
      },
      'Zipcode Metrics': {
        main: [[{ node: 'NAICS Timeline', type: 'main', index: 0 }]]
      },
      'NAICS Timeline': {
        main: [[{ node: 'ML Processor', type: 'main', index: 0 }]]
      }
    };

    setNodes(sampleNodes);
    setConnections(sampleConnections);
  };

  const getNodeColor = (type) => {
    const colors = {
      'trigger': '#10b981',
      'data_fetcher': '#3b82f6',
      'data_processor': '#06b6d4',
      'data_aggregator': '#10b981',
      'ml_processor': '#f59e0b',
      'api_fetcher': '#8b5cf6'
    };
    return colors[type] || '#6b7280';
  };

  const handleNodeMouseDown = (e, node) => {
    e.preventDefault();
    e.stopPropagation();
    const svgRect = svgRef.current.getBoundingClientRect();
    const svgPoint = svgRef.current.createSVGPoint();
    svgPoint.x = e.clientX - svgRect.left;
    svgPoint.y = e.clientY - svgRect.top;
    const transformedPoint = svgPoint.matrixTransform(svgRef.current.getScreenCTM().inverse());
    
    // Store click start position to detect if it's a click or drag
    setClickStartPos({ x: e.clientX, y: e.clientY });
    
    setDraggedNode(node.id);
    setDragOffset({
      x: transformedPoint.x - node.position[0],
      y: transformedPoint.y - node.position[1]
    });
  };

  const handleChartMouseDown = (e) => {
    if (!isFloating || draggedNode) return;
    
    e.preventDefault();
    setIsDraggingChart(true);
    setChartOffset({
      x: e.clientX,
      y: e.clientY
    });
  };

  const handleNodeClick = (e, node) => {
    // Only trigger click if we didn't drag much
    const dragDistance = Math.sqrt(
      Math.pow(e.clientX - clickStartPos.x, 2) + 
      Math.pow(e.clientY - clickStartPos.y, 2)
    );
    
    if (dragDistance < 5 && onNodeSelect) {
      // Find the corresponding node data from CSV
      const csvNode = csvNodes.find(csvN => csvN.node_id === node.id);
      if (csvNode) {
        onNodeSelect(csvNode);
      } else {
        // Fallback to basic node data
        onNodeSelect({
          node_id: node.id,
          name: node.name,
          description: `Pipeline node: ${node.name}`,
          type: node.type
        });
      }
    }
  };

  const handleMouseMove = (e) => {
    if (draggedNode && svgRef.current) {
      const svgRect = svgRef.current.getBoundingClientRect();
      const svgPoint = svgRef.current.createSVGPoint();
      svgPoint.x = e.clientX - svgRect.left;
      svgPoint.y = e.clientY - svgRect.top;
      const transformedPoint = svgPoint.matrixTransform(svgRef.current.getScreenCTM().inverse());
      
      setNodes(prevNodes => 
        prevNodes.map(node => 
          node.id === draggedNode 
            ? { 
                ...node, 
                position: [
                  transformedPoint.x - dragOffset.x,
                  transformedPoint.y - dragOffset.y
                ]
              }
            : node
        )
      );
    } else if (isDraggingChart && isFloating) {
      const deltaX = e.clientX - chartOffset.x;
      const deltaY = e.clientY - chartOffset.y;
      
      // Move the entire chart by updating all node positions
      setNodes(prevNodes => 
        prevNodes.map(node => ({
          ...node,
          position: [
            node.position[0] + deltaX,
            node.position[1] + deltaY
          ]
        }))
      );
      
      setChartOffset({ x: e.clientX, y: e.clientY });
    }
  };

  const handleMouseUp = (e) => {
    if (draggedNode) {
      // Check if this was a click (minimal movement) vs drag
      const dragDistance = Math.sqrt(
        Math.pow(e.clientX - clickStartPos.x, 2) + 
        Math.pow(e.clientY - clickStartPos.y, 2)
      );
      
      if (dragDistance < 5) {
        // This was a click, find and select the node
        const clickedNode = nodes.find(n => n.id === draggedNode);
        if (clickedNode) {
          handleNodeClick(e, clickedNode);
        }
      }
    }
    
    setDraggedNode(null);
    setDragOffset({ x: 0, y: 0 });
    setIsDraggingChart(false);
  };

  useEffect(() => {
    if (draggedNode || isDraggingChart) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [draggedNode, dragOffset, isDraggingChart, chartOffset]);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (showMenu && !e.target.closest('.node-menu')) {
        setShowMenu(null);
      }
    };
    
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [showMenu]);

  const renderConnections = () => {
    const lines = [];
    
    Object.entries(connections).forEach(([fromNodeName, connectionData]) => {
      const fromNode = nodes.find(n => n.name === fromNodeName);
      if (!fromNode) return;

      connectionData.main?.[0]?.forEach((connection, index) => {
        const toNode = nodes.find(n => n.name === connection.node);
        if (!toNode) return;

        const fromX = fromNode.position[0] + 120; // node width offset
        const fromY = fromNode.position[1] + 25;  // node height center
        const toX = toNode.position[0];
        const toY = toNode.position[1] + 25;

        // Create curved connection
        const midX = (fromX + toX) / 2;
        const pathData = `M ${fromX} ${fromY} Q ${midX} ${fromY} ${toX} ${toY}`;

        lines.push(
          <g key={`${fromNodeName}-${connection.node}-${index}`}>
            <path
              d={pathData}
              fill="none"
              className="flow-connection"
              markerEnd="url(#arrowhead)"
            />
          </g>
        );
      });
    });

    return lines;
  };

  if (loading) {
    return (
      <div className={`panel p-8 ${className}`}>
        <div className="flex items-center justify-center h-96">
          <div className="animate-spin rounded-full h-12 w-12 border-2 border-accent-cyan border-t-transparent"></div>
        </div>
      </div>
    );
  }

  return (
    <div className={`panel p-6 ${className}`}>
      {!hideTitle && (
        <h2 className="text-xl mb-6 text-gray-100 light:text-gray-900">Pipeline Flow</h2>
      )}
      
      <div 
        className={`relative overflow-auto bg-gray-700 light:bg-gray-300 rounded-lg ${isFloating ? 'cursor-grab' : ''}`} 
        style={{ height: hideTitle ? 'calc(100% - 24px)' : '600px', overflowX: 'auto', overflowY: 'auto' }}
        onMouseDown={handleChartMouseDown}
      >
        <svg
          ref={svgRef}
          className="w-full h-full"
          viewBox="0 0 1200 800"
          style={{ minWidth: '1200px', minHeight: '800px' }}
        >
          {/* Arrow marker definition */}
          <defs>
            <marker
              id="arrowhead"
              markerWidth="10"
              markerHeight="7"
              refX="9"
              refY="3.5"
              orient="auto"
            >
              <polygon
                points="0 0, 10 3.5, 0 7"
                fill="#06b6d4"
              />
            </marker>
          </defs>

          {/* Render connections */}
          {renderConnections()}

          {/* Render nodes */}
          {nodes
            .sort((a, b) => draggedNode === b.id ? 1 : draggedNode === a.id ? -1 : 0)
            .map((node) => (
            <g key={node.id} style={{ opacity: expandedNode === node.id ? 1 : 0.9 }}>
              <rect
                x={node.position[0]}
                y={node.position[1]}
                width="200"
                height={expandedNode === node.id ? "120" : "50"}
                rx="8"
                ry="8"
                fill={getNodeColor(node.type)}
                fillOpacity="0.1"
                stroke={getNodeColor(node.type)}
                strokeWidth="2"
                className={`hover:fill-opacity-20 transition-all duration-200 ${
                  draggedNode === node.id ? 'fill-opacity-30 cursor-grabbing' : 'cursor-pointer'
                }`}
                onMouseDown={(e) => handleNodeMouseDown(e, node)}
                onMouseEnter={() => setHoveredNode(node.id)}
                onMouseLeave={() => setHoveredNode(null)}
                style={{ cursor: draggedNode === node.id ? 'grabbing' : hoveredNode === node.id ? 'grab' : 'pointer' }}
              />
              <text
                x={node.position[0] + 100}
                y={node.position[1] + (expandedNode === node.id ? 20 : 30)}
                textAnchor="middle"
                className="text-sm font-medium fill-current text-gray-100 pointer-events-none select-none"
                onMouseDown={(e) => handleNodeMouseDown(e, node)}
              >
                {node.name}
              </text>
              
              {/* Expanded node details */}
              {expandedNode === node.id && (
                <g>
                  <text
                    x={node.position[0] + 10}
                    y={node.position[1] + 40}
                    className="text-xs fill-current text-gray-200 pointer-events-none select-none"
                  >
                    ID: {node.id}
                  </text>
                  <text
                    x={node.position[0] + 10}
                    y={node.position[1] + 55}
                    className="text-xs fill-current text-gray-200 pointer-events-none select-none"
                  >
                    Type: {node.type?.replace('_', ' ')}
                  </text>
                  <text
                    x={node.position[0] + 10}
                    y={node.position[1] + 70}
                    className="text-xs fill-current text-gray-200 pointer-events-none select-none"
                  >
                    Status: Active
                  </text>
                  {csvNodes.find(n => n.node_id === node.id)?.description && (
                    <text
                      x={node.position[0] + 10}
                      y={node.position[1] + 85}
                      className="text-xs fill-current text-gray-200 pointer-events-none select-none"
                    >
                      {csvNodes.find(n => n.node_id === node.id)?.description.substring(0, 30)}...
                    </text>
                  )}
                </g>
              )}
              
              {/* 3-dot menu */}
              <g className="node-menu">
                <circle
                  cx={node.position[0] + 185}
                  cy={node.position[1] + 15}
                  r="12"
                  fill="rgba(0,0,0,0.1)"
                  className="hover:fill-opacity-20 cursor-pointer"
                  onClick={(e) => {
                    e.stopPropagation();
                    const rect = svgRef.current.getBoundingClientRect();
                    setMenuPosition({
                      x: e.clientX - rect.left,
                      y: e.clientY - rect.top
                    });
                    setShowMenu(showMenu === node.id ? null : node.id);
                  }}
                />
                <text
                  x={node.position[0] + 185}
                  y={node.position[1] + 20}
                  textAnchor="middle"
                  className="text-xs fill-current text-gray-300 pointer-events-none select-none"
                  style={{ fontSize: '10px' }}
                >
                  ⋮
                </text>
              </g>
            </g>
          ))}
        </svg>
        
        {/* Context Menu */}
        {showMenu && (
          <div
            className="absolute bg-gray-800 border border-gray-600 rounded-lg shadow-lg py-2 z-50 light:bg-gray-200 light:border-gray-400"
            style={{
              left: `${menuPosition.x}px`,
              top: `${menuPosition.y}px`
            }}
          >
            <button
              className="w-full px-4 py-2 text-left text-sm text-gray-100 hover:bg-gray-700 light:text-gray-900 light:hover:bg-gray-100"
              onClick={() => {
                const csvNode = csvNodes.find(n => n.node_id === showMenu);
                if (csvNode && onHighlightInList) {
                  onHighlightInList(csvNode);
                }
                setShowMenu(null);
              }}
            >
              Select in list
            </button>
            <button
              className="w-full px-4 py-2 text-left text-sm text-gray-100 hover:bg-gray-700 light:text-gray-900 light:hover:bg-gray-100"
              onClick={() => {
                setExpandedNode(expandedNode === showMenu ? null : showMenu);
                setShowMenu(null);
              }}
            >
              {expandedNode === showMenu ? 'Collapse Node' : 'Expand Node'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}