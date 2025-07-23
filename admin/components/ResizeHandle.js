import { useState, useRef, useEffect } from 'react';

export default function ResizeHandle({ onResize, className = '' }) {
  const [isResizing, setIsResizing] = useState(false);
  const [startPos, setStartPos] = useState({ x: 0, y: 0 });
  const [startSize, setStartSize] = useState({ width: 0, height: 0 });

  const handleMouseDown = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    setIsResizing(true);
    setStartPos({ x: e.clientX, y: e.clientY });
    
    // Get current size from parent
    const parent = e.target.closest('[data-resizable]');
    if (parent) {
      const rect = parent.getBoundingClientRect();
      setStartSize({ width: rect.width, height: rect.height });
    }
  };

  const handleMouseMove = (e) => {
    if (isResizing && onResize) {
      const deltaX = e.clientX - startPos.x;
      const deltaY = e.clientY - startPos.y;
      
      onResize({
        width: startSize.width + deltaX,
        height: startSize.height + deltaY
      });
    }
  };

  const handleMouseUp = () => {
    setIsResizing(false);
  };

  useEffect(() => {
    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isResizing, startPos, startSize]);

  return (
    <div
      className={`absolute bottom-0 right-0 w-4 h-4 cursor-se-resize ${className}`}
      onMouseDown={handleMouseDown}
      style={{
        background: 'linear-gradient(-45deg, transparent 40%, rgba(156, 163, 175, 0.5) 40%, rgba(156, 163, 175, 0.5) 60%, transparent 60%)',
        borderBottomRightRadius: '4px'
      }}
    />
  );
}