import { useEffect, useRef } from "react";
import "./FloatingWidget.css";

type Props = {
  onClick: () => void;
  loading: boolean;
};

const FloatingWidget = ({ onClick, loading }: Props) => {
  const widgetRef = useRef<HTMLButtonElement>(null);
  const isDraggingRef = useRef(false);
  const dragStartRef = useRef({ x: 0, y: 0 });
  const hasMovedRef = useRef(false);

  useEffect(() => {
    const widget = widgetRef.current;
    if (!widget) return;

    // Handle drag start - use Alt+Click or right-click to drag
    const handleMouseDown = (e: MouseEvent) => {
      // Right-click or Alt+Left-click to drag
      if (e.button === 2 || (e.button === 0 && e.altKey)) {
        isDraggingRef.current = true;
        hasMovedRef.current = false;
        dragStartRef.current = {
          x: e.clientX,
          y: e.clientY,
        };
        e.preventDefault();
        e.stopPropagation();
      }
    };

    // Handle dragging
    const handleMouseMove = (e: MouseEvent) => {
      if (isDraggingRef.current) {
        const deltaX = e.clientX - dragStartRef.current.x;
        const deltaY = e.clientY - dragStartRef.current.y;
        
        // Check if we've moved enough to consider it a drag
        if (Math.abs(deltaX) > 3 || Math.abs(deltaY) > 3) {
          hasMovedRef.current = true;
        }
        
        if (window.electron?.moveWindow) {
          window.electron.moveWindow(deltaX, deltaY);
        }
        
        dragStartRef.current = {
          x: e.clientX,
          y: e.clientY,
        };
      }
    };

    // Handle drag end
    const handleMouseUp = (e: MouseEvent) => {
      if (isDraggingRef.current) {
        isDraggingRef.current = false;
        // If we dragged, prevent click
        if (hasMovedRef.current) {
          e.preventDefault();
          e.stopPropagation();
        }
        hasMovedRef.current = false;
      }
    };

    // Prevent context menu on right-click (we use it for dragging)
    const handleContextMenu = (e: MouseEvent) => {
      e.preventDefault();
    };

    widget.addEventListener("mousedown", handleMouseDown);
    document.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("mouseup", handleMouseUp);
    widget.addEventListener("contextmenu", handleContextMenu);

    return () => {
      widget.removeEventListener("mousedown", handleMouseDown);
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
      widget.removeEventListener("contextmenu", handleContextMenu);
    };
  }, []);

  const handleClick = (e: React.MouseEvent) => {
    // Only trigger click if we didn't drag
    if (!hasMovedRef.current && !isDraggingRef.current) {
      onClick();
    }
    isDraggingRef.current = false;
    hasMovedRef.current = false;
  };

  return (
    <button
      ref={widgetRef}
      className="floating-widget"
      onClick={handleClick}
      disabled={loading}
      title="Click to scan | Right-click or Alt+Click and drag to move"
      aria-busy={loading}
      style={{ cursor: loading ? "progress" : "pointer" }}
    >
      {loading ? "Scanning..." : "Scan"}
    </button>
  );
};

export default FloatingWidget;

