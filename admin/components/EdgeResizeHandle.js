import { useState, useRef, useEffect } from 'react';

export default function EdgeResizeHandle({ onResize, edge, className = '', onDoubleClick }) {
  const [isResizing, setIsResizing] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [startPos, setStartPos] = useState({ x: 0, y: 0 });
  const [startSize, setStartSize] = useState({ width: 0, height: 0 });

  const getHandleStyles = () => {
    const baseStyles = {
      position: 'absolute',
      backgroundColor: 'rgba(156, 163, 175, 0.1)',
      transition: 'background-color 0.2s',
    };

    switch (edge) {
      case 'top':
        return {
          ...baseStyles,
          top: '0',
          left: '8px',
          right: '8px',
          height: '1px',
          cursor: 'n-resize',
        };
      case 'bottom':
        return {
          ...baseStyles,
          bottom: '0',
          left: '8px',
          right: '8px',
          height: '1px',
          cursor: 's-resize',
        };
      case 'left':
        return {
          ...baseStyles,
          left: '0',
          top: '8px',
          bottom: '8px',
          width: '1px',
          cursor: 'w-resize',
        };
      case 'right':
        return {
          ...baseStyles,
          right: '0',
          top: '8px',
          bottom: '8px',
          width: '1px',
          cursor: 'e-resize',
        };
      default:
        return baseStyles;
    }
  };

  const getArrowIcon = () => {
    switch (edge) {
      case 'top': return '↑';
      case 'bottom': return '↓';
      case 'left': return '←';
      case 'right': return '→';
      default: return '';
    }
  };

  const getArrowPosition = () => {
    const baseStyles = {
      position: 'absolute',
      fontSize: '12px',
      color: 'rgba(156, 163, 175, 0.8)',
      pointerEvents: 'none',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
    };

    switch (edge) {
      case 'top':
      case 'bottom':
        return {
          ...baseStyles,
          left: '50%',
          transform: 'translateX(-50%)',
          width: '20px',
          height: '4px',
        };
      case 'left':
      case 'right':
        return {
          ...baseStyles,
          top: '50%',
          transform: 'translateY(-50%)',
          width: '4px',
          height: '20px',
          writingMode: 'vertical-rl',
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
      className={`hover:bg-gray-400 hover:bg-opacity-50 ${className}`}
      style={getHandleStyles()}
      onMouseDown={handleMouseDown}
    >
      <div style={getArrowPosition()}>
        {getArrowIcon()}
      </div>
    </div>
  );
}