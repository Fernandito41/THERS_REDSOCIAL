import { useId, useState } from "react";
import { IoOptionsOutline, IoClose } from "react-icons/io5";
import { HELP_CATEGORIES } from "../data/categories";

// Filtros de categoría + orden. En desktop se muestran inline; en mobile se
// colapsan en un drawer accesible (§9 de la tarea). `showCategory` se apaga
// en HelpCategoryPage, donde la categoría ya está fija por la ruta.
export default function HelpFilters({
  categoryId = "all",
  onCategoryChange,
  sortBy,
  onSortChange,
  showCategory = true,
  showRelevance = false,
}) {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const panelId = useId();

  const sortOptions = [
    ...(showRelevance ? [{ value: "relevance", label: "Relevancia" }] : []),
    { value: "recent", label: "Más recientes" },
    { value: "title", label: "Título (A-Z)" },
  ];

  const content = (
    <div className="space-y-6">
      {showCategory && (
        <fieldset>
          <legend className="text-xs font-semibold uppercase tracking-wide text-muted dark:text-muted-dark mb-2">
            Categoría
          </legend>
          <div className="space-y-1.5">
            <label className="flex items-center gap-2 text-sm text-ink dark:text-ink-dark cursor-pointer">
              <input
                type="radio"
                name="help-filter-category"
                checked={categoryId === "all"}
                onChange={() => onCategoryChange("all")}
                className="accent-pulse-600"
              />
              Todas
            </label>
            {HELP_CATEGORIES.map((category) => (
              <label key={category.id} className="flex items-center gap-2 text-sm text-ink dark:text-ink-dark cursor-pointer">
                <input
                  type="radio"
                  name="help-filter-category"
                  checked={categoryId === category.id}
                  onChange={() => onCategoryChange(category.id)}
                  className="accent-pulse-600"
                />
                {category.title}
              </label>
            ))}
          </div>
        </fieldset>
      )}

      <fieldset>
        <legend className="text-xs font-semibold uppercase tracking-wide text-muted dark:text-muted-dark mb-2">
          Ordenar por
        </legend>
        <div className="space-y-1.5">
          {sortOptions.map((option) => (
            <label key={option.value} className="flex items-center gap-2 text-sm text-ink dark:text-ink-dark cursor-pointer">
              <input
                type="radio"
                name="help-filter-sort"
                checked={sortBy === option.value}
                onChange={() => onSortChange(option.value)}
                className="accent-pulse-600"
              />
              {option.label}
            </label>
          ))}
        </div>
      </fieldset>
    </div>
  );

  return (
    <>
      {/* Desktop / tablet ancho: filtros inline en una tarjeta */}
      <div className="hidden md:block rounded-2xl border border-line dark:border-line-dark bg-surface dark:bg-surface-dark p-5 w-56 shrink-0 h-fit">
        {content}
      </div>

      {/* Mobile: botón que abre un drawer accesible */}
      <div className="md:hidden">
        <button
          type="button"
          onClick={() => setDrawerOpen(true)}
          aria-haspopup="dialog"
          aria-expanded={drawerOpen}
          aria-controls={panelId}
          className="inline-flex items-center gap-2 text-sm font-semibold px-4 py-2 rounded-full border border-line dark:border-line-dark text-ink dark:text-ink-dark hover:bg-canvas dark:hover:bg-canvas-dark transition"
        >
          <IoOptionsOutline size={16} aria-hidden="true" />
          Filtros
        </button>

        {drawerOpen && (
          <div className="fixed inset-0 z-50 flex items-end">
            <div
              className="absolute inset-0 bg-black/40"
              onClick={() => setDrawerOpen(false)}
              aria-hidden="true"
            />
            <div
              id={panelId}
              role="dialog"
              aria-modal="true"
              aria-label="Filtros de búsqueda"
              className="relative w-full bg-surface dark:bg-surface-dark rounded-t-3xl p-5 pb-8 max-h-[80vh] overflow-y-auto animate-float-in"
            >
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-base font-semibold text-ink dark:text-ink-dark">Filtros</h2>
                <button
                  type="button"
                  onClick={() => setDrawerOpen(false)}
                  aria-label="Cerrar filtros"
                  className="p-2 rounded-full hover:bg-canvas dark:hover:bg-canvas-dark text-muted dark:text-muted-dark"
                >
                  <IoClose size={18} />
                </button>
              </div>
              {content}
              <button
                type="button"
                onClick={() => setDrawerOpen(false)}
                className="mt-6 w-full py-3 rounded-full font-semibold bg-pulse-600 hover:bg-pulse-700 text-white transition"
              >
                Aplicar filtros
              </button>
            </div>
          </div>
        )}
      </div>
    </>
  );
}
