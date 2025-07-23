import { useState, useRef, useEffect } from 'react';
import NodesList from './NodesList';
import EdgeResizeHandle from './EdgeResizeHandle';
import CornerResizeHandle from './CornerResizeHandle';

export default function DraggableModal({ onClose, onNodeSelect, onFocus, onNodeClick, hideTitle = false, highlightedNode, onHighlightReceived }) {
  const [position, setPosition] = useState({ x: 100, y: 100 });
  const [size, setSize] = useState({ width: 320, height: 384 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const modalRef = useRef(null);

  // Calculate floating layout position: 1/3 width, 1/2 height, upper left
  const getFloatingPosition = () => {
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight - 81; // Subtract top bar height
    return {
      x: 20,
      y: 100,
      width: Math.floor(viewportWidth / 3) - 40,
      height: Math.floor(viewportHeight / 2) - 20
    };
  };

  const handleMouseDown = (e) => {
    // Bring to front when clicked
    onFocus?.();
    
    // Only start dragging if clicking on the header area
    if (e.target.closest('.drag-handle')) {
      setIsDragging(true);
      setDragStart({
        x: e.clientX - position.x,
        y: e.clientY - position.y
      });
    }
  };

  const handleMouseMove = (e) => {
    if (isDragging) {
      setPosition({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y
      });
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isDragging, dragStart, position]);

  useEffect(() => {
    const handleReset = () => {
      const floatingPos = getFloatingPosition();
      setPosition({ x: floatingPos.x, y: floatingPos.y });
      setSize({ width: floatingPos.width, height: floatingPos.height });
    };
    
    window.addEventListener('resetFloatingPositions', handleReset);
    return () => window.removeEventListener('resetFloatingPositions', handleReset);
  }, []);

  return (
    <div
      ref={modalRef}
      data-resizable
      className="absolute bg-gray-800 border border-gray-700 rounded-3xl shadow-2xl overflow-hidden light:bg-gray-200 light:border-gray-400"
      style={{
        left: `${position.x}px`,
        top: `${position.y}px`,
        width: `${size.width}px`,
        height: `${size.height}px`,
        zIndex: 50
      }}
      onMouseDown={handleMouseDown}
      onClick={() => onFocus?.()}
    >
      {/* Draggable Header */}
      <div className="drag-handle flex items-center justify-between p-4 bg-gray-700 border-b border-gray-600 cursor-move light:bg-gray-300 light:border-gray-400">
        <h2 className="text-lg font-semibold text-gray-100 light:text-gray-900 select-none">
          Nodes
        </h2>
        <button
          onClick={onClose}
          className="w-8 h-8 rounded-full bg-gray-600 hover:bg-red-600 flex items-center justify-center transition-colors duration-200 light:bg-gray-400 light:hover:bg-red-500"
        >
          <span className="text-gray-100 text-xl font-bold light:text-gray-900">×</span>
        </button>
      </div>

      {/* Content */}
      <div className="p-4 overflow-y-auto" style={{ height: 'calc(100% - 60px)' }}>
        <NodesList 
          onNodeSelect={onNodeSelect}
          onNodeClick={onNodeClick}
          highlightedNode={highlightedNode}
          onHighlightReceived={onHighlightReceived}
          className="bg-transparent border-none p-0"
        />
      </div>
      
      {/* Edge and Corner Resize Handles */}
      <EdgeResizeHandle edge="top" onResize={setSize} />
      <EdgeResizeHandle edge="bottom" onResize={setSize} />
      <EdgeResizeHandle edge="left" onResize={setSize} />
      <EdgeResizeHandle edge="right" onResize={setSize} />
      <CornerResizeHandle corner="top-left" onResize={setSize} />
      <CornerResizeHandle corner="top-right" onResize={setSize} />
      <CornerResizeHandle corner="bottom-left" onResize={setSize} />
      <CornerResizeHandle corner="bottom-right" onResize={setSize} />
    </div>
  );
}