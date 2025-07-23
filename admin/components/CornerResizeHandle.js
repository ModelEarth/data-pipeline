import { useState, useRef, useEffect } from 'react';

export default function CornerResizeHandle({ onResize, corner, className = '' }) {
  const [isResizing, setIsResizing] = useState(false);
  const [startPos, setStartPos] = useState({ x: 0, y: 0 });
  const [startSize, setStartSize] = useState({ width: 0, height: 0 });

  const getHandleStyles = () => {
    const baseStyles = {
      position: 'absolute',
      width: '16px',
      height: '16px',
      backgroundColor: 'transparent',
    };

    switch (corner) {
      case 'top-left':
        return {
          ...baseStyles,
          top: '0',
          left: '0',
          cursor: 'nw-resize',
        };
      case 'top-right':
        return {
          ...baseStyles,
          top: '0',
          right: '0',
          cursor: 'ne-resize',
        };
      case 'bottom-left':
        return {
          ...baseStyles,
          bottom: '0',
          left: '0',
          cursor: 'sw-resize',
        };
      case 'bottom-right':
        return {
          ...baseStyles,
          bottom: '0',
          right: '0',
          cursor: 'se-resize',
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

      switch (corner) {
        case 'top-left':
          newWidth = startSize.width - deltaX;
          newHeight = startSize.height - deltaY;
          break;
        case 'top-right':
          newWidth = startSize.width + deltaX;
          newHeight = startSize.height - deltaY;
          break;
        case 'bottom-left':
          newWidth = startSize.width - deltaX;
          newHeight = startSize.height + deltaY;
          break;
        case 'bottom-right':
          newWidth = startSize.width + deltaX;
          newHeight = startSize.height + deltaY;
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