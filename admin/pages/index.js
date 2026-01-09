import { useState, useEffect } from 'react';
import Head from 'next/head';
import DarkModeToggle from '../components/DarkModeToggle';
import NodesList from '../components/NodesList';
import FlowChart from '../components/FlowChart';
import NodeDetailPanel from '../components/NodeDetailPanel';
import DraggableModal from '../components/DraggableModal';
import FloatingDetailPanel from '../components/FloatingDetailPanel';
import DraggableFlowChart from '../components/DraggableFlowChart';
import { checkFlaskAvailability, resetFlaskAvailability } from '../utils/flaskCheck';

export default function Home() {
  const [mounted, setMounted] = useState(false);
  const [selectedNode, setSelectedNode] = useState(null);
  const [listPosition, setListPosition] = useState('column'); // 'column', 'full-width', 'floating'
  const [showFloatingList, setShowFloatingList] = useState(false);
  const [showFloatingDetail, setShowFloatingDetail] = useState(false);
  const [showFloatingChart, setShowFloatingChart] = useState(false);
  const [panelZIndex, setPanelZIndex] = useState({ list: 40, chart: 41, detail: 42 });
  const [highlightedNode, setHighlightedNode] = useState(null);
  const [flaskAvailable, setFlaskAvailable] = useState(null); // null = checking, true = available, false = unavailable

  // Ensure hydration completes before rendering client-specific content
  useEffect(() => {
    setMounted(true);
  }, []);

  const handleNodeSelect = (node) => {
    setSelectedNode(node);
    setShowFloatingDetail(true);
  };

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
    // Reset positions for floating layout
    setTimeout(() => {
      window.dispatchEvent(new CustomEvent('resetFloatingPositions'));
    }, 100);
  };

  const handleHighlightInList = (node) => {
    setHighlightedNode(node);
    bringToFront('detail');
    // Clear highlight after 3 seconds
    setTimeout(() => setHighlightedNode(null), 3000);
  };

  // Check Flask availability on mount
  useEffect(() => {
    const checkFlask = async () => {
      const available = await checkFlaskAvailability();
      setFlaskAvailable(available);
    };
    checkFlask();
    
    // Re-check every 30 seconds
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

      <div className={`min-h-screen bg-gray-900 light:bg-yellow-50 ${listPosition === 'floating' ? 'overflow-auto' : ''}`} style={listPosition === 'floating' ? { height: '100vh' } : {}}>
        {/* Flask Availability Banner - only render after mount to avoid hydration mismatch */}
        {mounted && flaskAvailable === false && (
          <div className="bg-orange-500/20 border-b border-orange-500/50 px-6 py-3 flex items-center justify-between relative z-50">
            <div className="flex items-center gap-3">
              <span className="text-orange-400">⚠️</span>
              <span className="text-orange-300 light:text-orange-700">
                Flask Server is not running on port 5001
              </span>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={handleRetryFlaskCheck}
                className="text-sm px-3 py-1 bg-orange-500/30 hover:bg-orange-500/50 rounded border border-orange-500/50 text-orange-200 light:text-orange-800"
              >
                Retry Check
              </button>
              <a
                href="../flask"
                target="_blank"
                className="text-sm px-3 py-1 bg-blue-500/30 hover:bg-blue-500/50 rounded border border-blue-500/50 text-blue-200 light:text-blue-800"
              >
                Activate Flask Server
              </a>
            </div>
          </div>
        )}
        
        {/* Top Bar */}
        <div className="flex items-center justify-between p-6 border-b border-gray-700 light:border-gray-400 relative z-50">
          <div className="flex gap-2">
            <button
              onClick={() => setListPosition('column')}
              className={`btn text-sm px-3 py-2 ${listPosition === 'column' ? 'btn-primary' : ''}`}
              title="Column Layout"
            >
              ▦
            </button>
            <button
              onClick={() => {
                setListPosition('full-width');
                setShowFloatingList(true);
              }}
              className={`btn text-sm px-3 py-2 ${listPosition === 'full-width' ? 'btn-primary' : ''}`}
              title="Full Width Layout"
            >
              ▬
            </button>
            <button
              onClick={() => {
                setListPosition('floating');
                setShowFloatingList(true);
                setShowFloatingChart(true);
                // Reset positions for floating layout
                window.dispatchEvent(new CustomEvent('resetFloatingPositions'));
              }}
              className={`btn text-sm px-3 py-2 ${listPosition === 'floating' ? 'btn-primary' : ''}`}
              title="Floating Layout"
            >
              ⧉
            </button>
          </div>
          
          <DarkModeToggle />
        </div>

        {/* Main Layout */}
        <div className={`flex ${listPosition === 'floating' ? 'h-auto min-h-[calc(100vh-81px)]' : 'h-[calc(100vh-81px)]'}`}>
          {/* Column Layout */}
          {listPosition === 'column' && (
            <div className="w-[30%] border-r border-gray-700 light:border-gray-400 p-6 overflow-y-auto">
              <NodesList 
                onNodeSelect={handleNodeSelect}
                onNodeClick={() => bringToFront('detail')}
                highlightedNode={highlightedNode}
                onHighlightReceived={setSelectedNode}
                className="h-auto"
              />
            </div>
          )}

          {/* Main Content Area */}
          <div className={`flex-1 ${listPosition === 'column' ? 'w-[70%]' : 'w-full'}`}>
            <div className="h-full">
              {/* Flow Chart - only show when not in floating mode */}
              {listPosition !== 'floating' && (
                <div className="h-full p-6">
                  <FlowChart 
                    className="h-full" 
                    onNodeSelect={handleNodeSelect}
                    isFloating={false}
                    onHighlightInList={handleHighlightInList}
                  />
                  
                  {/* Full Width List - now floating */}
                </div>
              )}
              
              {/* Empty state for floating mode */}
              {listPosition === 'floating' && (
                <div className="h-full flex items-center justify-center p-6">
                  <div className="text-center">
                    <button 
                      onClick={openAllFloatingPanels}
                      className="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-700 flex items-center justify-center light:bg-gray-300 hover:bg-gray-600 light:hover:bg-gray-400 transition-colors duration-200 cursor-pointer"
                    >
                      <span className="text-2xl">⧉</span>
                    </button>
                    <h3 className="text-lg font-medium text-gray-100 mb-2 light:text-gray-900">Floating Mode Active</h3>
                    <p className="text-muted">Click the icon above to open floating panels</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Floating List Popup */}
        {(listPosition === 'floating' || listPosition === 'full-width') && showFloatingList && (
          <div 
            className="fixed inset-0 pointer-events-none"
            id="listPopup"
            style={{ zIndex: panelZIndex.list }}
          >
            <div className="pointer-events-auto">
              <DraggableModal 
                onClose={() => setShowFloatingList(false)}
                onNodeSelect={(node) => {
                  handleNodeSelect(node);
                }}
                onFocus={() => bringToFront('list')}
                onNodeClick={() => bringToFront('detail')}
                highlightedNode={highlightedNode}
                onHighlightReceived={setSelectedNode}
                hideTitle={listPosition === 'floating'}
              />
            </div>
          </div>
        )}

        {/* Floating Chart Popup */}
        {(listPosition === 'floating' || listPosition === 'full-width') && showFloatingChart && (
          <div 
            className="fixed inset-0 pointer-events-none"
            style={{ zIndex: panelZIndex.chart }}
          >
            <div className="pointer-events-auto">
              <DraggableFlowChart
                onNodeSelect={handleNodeSelect}
                onClose={() => setShowFloatingChart(false)}
                onFocus={() => bringToFront('chart')}
                isFullWidth={listPosition === 'full-width'}
                hideTitle={listPosition === 'floating'}
                onHighlightInList={handleHighlightInList}
              />
            </div>
          </div>
        )}

        {/* Floating Detail Panel */}
        {showFloatingDetail && selectedNode && (
          <div 
            className="fixed inset-0 pointer-events-none"
            style={{ zIndex: panelZIndex.detail }}
          >
            <div className="pointer-events-auto">
              <FloatingDetailPanel
                node={selectedNode}
                onClose={() => setShowFloatingDetail(false)}
                onUpdateNode={handleUpdateNode}
                onRunNode={handleRunNode}
                onFocus={() => bringToFront('detail')}
                flaskAvailable={flaskAvailable}
              />
            </div>
          </div>
        )}
      </div>
    </>
  );
}