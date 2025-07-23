import { useState, useRef, useEffect } from 'react';

export default function EdgeResizeHandle({ onResize, edge, className = '', onDoubleClick }) {
  const [isResizing, setIsResizing] = useState(false);
  const [startPos, setStartPos] = useState({ x: 0, y: 0 });
  const [startSize, setStartSize] = useState({ width: 0, height: 0 });

  const getHandleStyles = () => {
    const baseStyles = {
      position: 'absolute',
      backgroundColor: 'transparent',
    };

    switch (edge) {
      case 'top':
        return {
          ...baseStyles,
          top: '0',
          left: '8px',
          right: '8px',
          height: '4px',
          cursor: 'n-resize',
        };
      case 'bottom':
        return {
          ...baseStyles,
          bottom: '0',
          left: '8px',
          right: '8px',
          height: '4px',
          cursor: 's-resize',
        };
      case 'left':
        return {
          ...baseStyles,
          left: '0',
          top: '8px',
          bottom: '8px',
          width: '4px',
          cursor: 'w-resize',
        };
      case 'right':
        return {
          ...baseStyles,
          right: '0',
          top: '8px',
          bottom: '8px',
          width: '4px',
          cursor: 'e-resize',
        };
      default:
        return baseStyles;
    }
  };


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
      
      let newWidth = startSize.width;
      let newHeight = startSize.height;

      switch (edge) {
        case 'top':
          newHeight = startSize.height - deltaY;
          break;
        case 'bottom':
          newHeight = startSize.height + deltaY;
          break;
        case 'left':
          newWidth = startSize.width - deltaX;
          break;
        case 'right':
          newWidth = startSize.width + deltaX;
          break;
      }

      onResize({
        width: Math.max(200, newWidth),
        height: Math.max(150, newHeight)
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
      className={className}
      style={getHandleStyles()}
      onMouseDown={handleMouseDown}
    />
  );
}