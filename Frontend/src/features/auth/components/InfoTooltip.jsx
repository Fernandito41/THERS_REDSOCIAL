import { useEffect, useId, useRef, useState } from "react";
import { IoHelpCircleOutline } from "react-icons/io5";

// "?" interactivo genérico -- botón + popover con click-afuera/Escape para
// cerrar, mismo patrón que el popover de BirthDateField. `children` es
// contenido libre (texto + enlaces), así no depende de react-router-dom por
// sí mismo.
export default function InfoTooltip({ label = "Más información", children }) {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef(null);
  const popoverId = useId();

  useEffect(() => {
    function handlePointerDown(e) {
      if (containerRef.current && !containerRef.current.contains(e.target)) setIsOpen(false);
    }
    function handleKeyDown(e) {
      if (e.key === "Escape") setIsOpen(false);
    }
    document.addEventListener("mousedown", handlePointerDown);
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("mousedown", handlePointerDown);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, []);

  return (
    <span ref={containerRef} className="relative inline-flex">
      <button
        type="button"
        onClick={() => setIsOpen((v) => !v)}
        aria-expanded={isOpen}
        aria-controls={popoverId}
        aria-label={label}
        className="text-muted-dark hover:text-ink-dark focus:outline-none focus:ring-2 focus:ring-pulse-500 rounded-full"
      >
        <IoHelpCircleOutline size={15} />
      </button>

      {isOpen && (
        <div
          id={popoverId}
          role="tooltip"
          className="absolute z-30 top-full left-0 mt-2 w-64 bg-surface-dark border border-line-dark rounded-xl shadow-lift p-3 text-xs leading-relaxed text-muted-dark animate-float-in"
        >
          {children}
        </div>
      )}
    </span>
  );
}
