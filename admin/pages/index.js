import { useState, useEffect, useCallback } from 'react';
import Head from 'next/head';
import DarkModeToggle from '../components/DarkModeToggle';
import NodesList from '../components/NodesList';
import FlowChart from '../components/FlowChart';
import NodeDetailPanel from '../components/NodeDetailPanel';
import DraggableModal from '../components/DraggableModal';
import FloatingDetailPanel from '../components/FloatingDetailPanel';
import DraggableFlowChart from '../components/DraggableFlowChart';
import { checkFlaskAvailability, resetFlaskAvailability } from '../utils/flaskCheck';
import { getHash, goHash, saveState, loadState, initializeState, onHashChange } from '../utils/stateManager';

export default function Home() {
  const [mounted, setMounted] = useState(false);
  const [nodes, setNodes] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [listPosition, setListPosition] = useState('column');
  const [showFloatingList, setShowFloatingList] = useState(false);
  const [showFloatingDetail, setShowFloatingDetail] = useState(false);
  const [showFloatingChart, setShowFloatingChart] = useState(false);
  const [panelZIndex, setPanelZIndex] = useState({ list: 40, chart: 41, detail: 42 });
  const [highlightedNode, setHighlightedNode] = useState(null);
  const [flaskAvailable, setFlaskAvailable] = useState(null);

  // Initialize from hash/localStorage after mount
  useEffect(() => {
    setMounted(true);
    const initial = initializeState();
    setListPosition(initial.view);

    // Set up floating states based on view
    if (initial.view === 'floating') {
      setShowFloatingList(true);
      setShowFloatingChart(true);
    } else if (initial.view === 'full') {
      setShowFloatingList(false);
      setShowFloatingChart(false);
    }
  }, []);

  // Load nodes and set initial selection
  useEffect(() => {
    if (!mounted) return;

    const loadNodes = async () => {
      try {
        // Always use /data-pipeline/nodes.csv path
        const response = await fetch('/data-pipeline/nodes.csv');
        if (response.ok) {
          const csvText = await response.text();
          const lines = csvText.split('\n').filter(line => line.trim());
          const headers = lines[0].split(',').map(h => h.trim());
          const csvNodes = [];

          for (let i = 1; i < lines.length; i++) {
            const values = parseCSVLine(lines[i]);
            if (values.length >= headers.length - 1) {
              const node = {};
              headers.forEach((header, index) => {
                node[header.trim()] = values[index] ? values[index].trim() : '';
              });
              csvNodes.push(node);
            }
          }
          setNodes(csvNodes);

          // Set initial node selection from hash or first node for full-width
          const hash = getHash();
          if (hash.node) {
            const node = csvNodes.find(n => n.node_id === hash.node);
            if (node) setSelectedNode(node);
          } else if (listPosition === 'full' && csvNodes.length > 0) {
            setSelectedNode(csvNodes[0]);
            goHash({ node: csvNodes[0].node_id });
          }
        }
      } catch (error) {
        console.error('Failed to load nodes:', error);
      }
    };

    loadNodes();
  }, [mounted]);

  // Parse CSV line handling quoted values
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

  // Listen for hash changes (browser back/forward, manual URL edit)
  useEffect(() => {
    if (!mounted) return;

    const cleanup = onHashChange((hash) => {
      if (hash.view && hash.view !== listPosition) {
        handleViewChange(hash.view, false);
      }
      if (hash.node && (!selectedNode || hash.node !== selectedNode.node_id)) {
        const node = nodes.find(n => n.node_id === hash.node);
        if (node) setSelectedNode(node);
      }
    });

    return cleanup;
  }, [mounted, listPosition, selectedNode, nodes]);

  // Handle view change
  const handleViewChange = useCallback((view, updateUrl = true) => {
    setListPosition(view);
    saveState({ view });

    if (updateUrl) {
      goHash({ view });
    }

    // Configure floating states based on view
    if (view === 'floating') {
      setShowFloatingList(true);
      setShowFloatingChart(true);
      setShowFloatingDetail(!!selectedNode);
      setTimeout(() => {
        window.dispatchEvent(new CustomEvent('resetFloatingPositions'));
      }, 100);
    } else {
      setShowFloatingList(false);
      setShowFloatingChart(false);
      setShowFloatingDetail(false);
    }
  }, [selectedNode]);

  // Handle node selection
  const handleNodeSelect = useCallback((node) => {
    setSelectedNode(node);
    saveState({ selectedNodeId: node?.node_id });
    goHash({ node: node?.node_id });

    if (listPosition === 'floating') {
      setShowFloatingDetail(true);
    }
  }, [listPosition]);

  const handleUpdateNode = (updatedNode) => {
    setSelectedNode(updatedNode);
  };

  const handleRunNode = (node, result) => {
    console.log('Node run result:', { node, result });
  };

  const bringToFront = (panelType) => {
    const maxZ = Math.max(...Object.values(panelZIndex));
    setPanelZIndex(prev => ({
      ...prev,
      [panelType]: maxZ + 1
    }));
  };

  const openAllFloatingPanels = () => {
    setShowFloatingList(true);
    setShowFloatingChart(true);
    setTimeout(() => {
      window.dispatchEvent(new CustomEvent('resetFloatingPositions'));
    }, 100);
  };

  const handleHighlightInList = (node) => {
    setHighlightedNode(node);
    bringToFront('detail');
    setTimeout(() => setHighlightedNode(null), 3000);
  };

  // Check Flask availability
  useEffect(() => {
    const checkFlask = async () => {
      const available = await checkFlaskAvailability();
      setFlaskAvailable(available);
    };
    checkFlask();
    const interval = setInterval(checkFlask, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleRetryFlaskCheck = async () => {
    resetFlaskAvailability();
    const available = await checkFlaskAvailability();
    setFlaskAvailable(available);
  };

  return (
    <>
      <Head>
        <title>Data Pipeline Admin</title>
        <meta name="description" content="Data Pipeline Administration Interface" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="admin-container">
        {/* Flask Availability Banner */}
        {mounted && flaskAvailable === false && (
          <div className="flask-banner">
            <div className="flask-banner-content">
              <span className="flask-banner-icon">⚠️</span>
              <span className="flask-banner-text">
                Flask Server is not running on port 5001
              </span>
            </div>
            <div className="flask-banner-actions">
              <button onClick={handleRetryFlaskCheck} className="flask-banner-btn retry">
                Retry Check
              </button>
              <a href="../flask" target="_blank" className="flask-banner-btn activate">
                Activate Flask Server
              </a>
            </div>
          </div>
        )}

        {/* Top Bar */}
        <div className="top-bar">
          <div className="layout-buttons">
            <button
              onClick={() => handleViewChange('column')}
              className={`btn btn-layout ${listPosition === 'column' ? 'btn-primary' : ''}`}
              title="Column Layout"
            >
              <svg className="layout-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="2" y="3" width="6" height="18" rx="1" />
                <rect x="10" y="3" width="12" height="18" rx="1" />
              </svg>
            </button>
            <button
              onClick={() => handleViewChange('full')}
              className={`btn btn-layout ${listPosition === 'full' ? 'btn-primary' : ''}`}
              title="Full Width Layout"
            >
              <svg className="layout-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="2" y="3" width="20" height="8" rx="1" />
                <rect x="2" y="13" width="20" height="8" rx="1" />
              </svg>
            </button>
            <button
              onClick={() => handleViewChange('floating')}
              className={`btn btn-layout ${listPosition === 'floating' ? 'btn-primary' : ''}`}
              title="Floating Layout"
            >
              <span className="layout-icon">⧉</span>
            </button>
          </div>

          <DarkModeToggle />
        </div>

        {/* Column Layout */}
        {listPosition === 'column' && (
          <div className="layout-column">
            <div className="column-sidebar">
              <NodesList
                onNodeSelect={handleNodeSelect}
                onNodeClick={() => bringToFront('detail')}
                highlightedNode={highlightedNode}
                onHighlightReceived={setSelectedNode}
                selectedNode={selectedNode}
              />
            </div>
            <div className="column-main">
              {selectedNode && (
                <div className="column-detail-section">
                  <div className="column-detail-panel">
                    <div className="column-detail-header">
                      <h2>Node Details</h2>
                      <button
                        onClick={() => {
                          setSelectedNode(null);
                          goHash({ node: null });
                        }}
                        className="close-btn"
                      >
                        ×
                      </button>
                    </div>
                    <div className="column-detail-content">
                      <NodeDetailPanel
                        node={selectedNode}
                        onUpdateNode={handleUpdateNode}
                        onRunNode={handleRunNode}
                        flaskAvailable={flaskAvailable}
                      />
                    </div>
                  </div>
                </div>
              )}
              <div className="column-flow-section">
                <FlowChart
                  onNodeSelect={handleNodeSelect}
                  isFloating={false}
                  onHighlightInList={handleHighlightInList}
                  focusedNode={selectedNode}
                />
              </div>
            </div>
          </div>
        )}

        {/* Full Width Layout */}
        {listPosition === 'full' && (
          <div className="layout-fullwidth">
            <div className="fullwidth-top">
              <div className="fullwidth-list">
                <NodesList
                  onNodeSelect={handleNodeSelect}
                  onNodeClick={() => {}}
                  highlightedNode={highlightedNode}
                  onHighlightReceived={setSelectedNode}
                  selectedNode={selectedNode}
                  compact={true}
                />
              </div>
              {selectedNode && (
                <div className="fullwidth-detail">
                  <div className="fullwidth-detail-header">
                    <h2>Node Details</h2>
                    <button
                      onClick={() => {
                        setSelectedNode(null);
                        goHash({ node: null });
                      }}
                      className="close-btn"
                    >
                      ×
                    </button>
                  </div>
                  <div className="fullwidth-detail-content">
                    <NodeDetailPanel
                      node={selectedNode}
                      onUpdateNode={handleUpdateNode}
                      onRunNode={handleRunNode}
                      flaskAvailable={flaskAvailable}
                    />
                  </div>
                </div>
              )}
            </div>
            <div className="fullwidth-bottom">
              <FlowChart
                onNodeSelect={handleNodeSelect}
                isFloating={false}
                onHighlightInList={handleHighlightInList}
              />
            </div>
          </div>
        )}

        {/* Floating Layout */}
        {listPosition === 'floating' && (
          <div className="layout-floating">
            {!showFloatingList && !showFloatingChart && (
              <div className="floating-empty">
                <button onClick={openAllFloatingPanels} className="floating-open-btn">
                  <span>⧉</span>
                </button>
                <h3>Floating Mode Active</h3>
                <p className="text-muted">Click the icon above to open floating panels</p>
              </div>
            )}
          </div>
        )}

        {/* Floating Panels (only in floating mode) */}
        {listPosition === 'floating' && showFloatingList && (
          <div className="floating-wrapper" style={{ zIndex: panelZIndex.list }}>
            <DraggableModal
              onClose={() => setShowFloatingList(false)}
              onNodeSelect={handleNodeSelect}
              onFocus={() => bringToFront('list')}
              onNodeClick={() => bringToFront('detail')}
              highlightedNode={highlightedNode}
              onHighlightReceived={setSelectedNode}
              hideTitle={true}
            />
          </div>
        )}

        {listPosition === 'floating' && showFloatingChart && (
          <div className="floating-wrapper" style={{ zIndex: panelZIndex.chart }}>
            <DraggableFlowChart
              onNodeSelect={handleNodeSelect}
              onClose={() => setShowFloatingChart(false)}
              onFocus={() => bringToFront('chart')}
              isFullWidth={false}
              hideTitle={true}
              onHighlightInList={handleHighlightInList}
            />
          </div>
        )}

        {listPosition === 'floating' && showFloatingDetail && selectedNode && (
          <div className="floating-wrapper" style={{ zIndex: panelZIndex.detail }}>
            <FloatingDetailPanel
              node={selectedNode}
              onClose={() => setShowFloatingDetail(false)}
              onUpdateNode={handleUpdateNode}
              onRunNode={handleRunNode}
              onFocus={() => bringToFront('detail')}
              flaskAvailable={flaskAvailable}
            />
          </div>
        )}
      </div>
    </>
  );
}
