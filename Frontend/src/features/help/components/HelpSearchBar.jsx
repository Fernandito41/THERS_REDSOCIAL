import { useId, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { IoSearchOutline, IoCloseOutline } from "react-icons/io5";
import { useHelpSearch } from "../hooks/useHelpSearch";
import HelpSearchResultsDropdown from "./HelpSearchResultsDropdown";

// Buscador central del Centro de Ayuda -- reutilizado en el hero de /help y
// en la barra persistente de HelpLayout. `autoFocus`/`size` permiten variar
// su presentación sin duplicar el componente (§6 de la tarea: un único
// elemento de búsqueda con resultados dinámicos y debounce).
export default function HelpSearchBar({
  autoFocus = false,
  size = "lg",
  placeholder = "Buscar artículos de ayuda...",
  onSubmitQuery,
}) {
  const navigate = useNavigate();
  const listboxId = useId();
  const inputRef = useRef(null);

  const [value, setValue] = useState("");
  const [isOpen, setIsOpen] = useState(false);

  const { articles, faqs, isLoading, hasQuery } = useHelpSearch(value, { limit: 6 });

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = value.trim();
    if (!trimmed) return;
    setIsOpen(false);
    inputRef.current?.blur();
    if (onSubmitQuery) {
      onSubmitQuery(trimmed);
    } else {
      navigate(`/help/search?q=${encodeURIComponent(trimmed)}`);
    }
  };

  const handleClear = () => {
    setValue("");
    inputRef.current?.focus();
  };

  const heightClass = size === "lg" ? "py-3.5 text-base" : "py-2.5 text-sm";

  return (
    <div className="relative w-full">
      <form role="search" onSubmit={handleSubmit}>
        <label htmlFor={listboxId} className="sr-only">
          Buscar en el Centro de Ayuda
        </label>
        <div className="relative">
          <IoSearchOutline
            className="absolute left-4 top-1/2 -translate-y-1/2 text-muted dark:text-muted-dark"
            size={size === "lg" ? 20 : 18}
            aria-hidden="true"
          />
          <input
            id={listboxId}
            ref={inputRef}
            type="search"
            role="combobox"
            aria-expanded={isOpen && hasQuery}
            aria-controls={`${listboxId}-results`}
            aria-autocomplete="list"
            autoFocus={autoFocus}
            value={value}
            onChange={(e) => {
              setValue(e.target.value);
              setIsOpen(true);
            }}
            onFocus={() => setIsOpen(true)}
            onBlur={() => setTimeout(() => setIsOpen(false), 120)}
            placeholder={placeholder}
            className={`w-full bg-surface dark:bg-surface-dark border border-line dark:border-line-dark rounded-full pl-11 pr-10 ${heightClass} text-ink dark:text-ink-dark placeholder-muted focus:outline-none focus:ring-2 focus:ring-pulse-500 transition`}
          />
          {value && (
            <button
              type="button"
              onClick={handleClear}
              aria-label="Borrar búsqueda"
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted hover:text-ink dark:hover:text-ink-dark p-1 rounded-full"
            >
              <IoCloseOutline size={18} />
            </button>
          )}
        </div>
      </form>

      {isOpen && hasQuery && (
        <HelpSearchResultsDropdown
          id={`${listboxId}-results`}
          query={value}
          articles={articles}
          faqs={faqs}
          isLoading={isLoading}
          onNavigate={() => setIsOpen(false)}
          onSeeAll={() => {
            setIsOpen(false);
            navigate(`/help/search?q=${encodeURIComponent(value.trim())}`);
          }}
        />
      )}
    </div>
  );
}
