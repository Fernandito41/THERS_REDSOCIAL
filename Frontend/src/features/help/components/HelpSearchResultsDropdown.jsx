import { Link } from "react-router-dom";
import { IoDocumentTextOutline } from "react-icons/io5";
import { getCategoryById } from "../data/categories";
import HighlightMatch from "./HighlightMatch";

export default function HelpSearchResultsDropdown({
  id,
  query,
  articles,
  faqs,
  isLoading,
  onNavigate,
  onSeeAll,
}) {
  const hasResults = articles.length > 0 || faqs.length > 0;

  return (
    <div
      id={id}
      role="listbox"
      className="absolute left-0 right-0 top-full mt-2 z-20 bg-surface dark:bg-surface-dark border border-line dark:border-line-dark rounded-2xl shadow-lift overflow-hidden animate-float-in"
    >
      {isLoading ? (
        <div className="p-4 space-y-3" aria-live="polite" aria-label="Buscando">
          {[0, 1, 2].map((i) => (
            <div key={i} className="h-4 rounded-full bg-line dark:bg-line-dark animate-pulse" />
          ))}
        </div>
      ) : !hasResults ? (
        <div className="p-5 text-center">
          <p className="text-sm text-ink dark:text-ink-dark font-medium">
            No encontramos resultados para "{query}"
          </p>
          <p className="text-xs text-muted dark:text-muted-dark mt-1">
            Probá con otra palabra o explorá las categorías del Centro de Ayuda.
          </p>
        </div>
      ) : (
        <>
          <ul className="max-h-96 overflow-y-auto py-2">
            {articles.map((article) => {
              const category = getCategoryById(article.categoryId);
              return (
                <li key={article.slug} role="option" aria-selected="false">
                  <Link
                    to={`/help/article/${article.slug}`}
                    onClick={onNavigate}
                    onMouseDown={(e) => e.preventDefault()}
                    className="flex items-start gap-3 px-4 py-2.5 hover:bg-canvas dark:hover:bg-canvas-dark transition-colors"
                  >
                    <IoDocumentTextOutline size={16} className="mt-0.5 shrink-0 text-pulse-500" aria-hidden="true" />
                    <span className="min-w-0">
                      <span className="block text-xs font-semibold uppercase tracking-wide text-pulse-600 dark:text-pulse-300">
                        {category?.title}
                      </span>
                      <span className="block text-sm text-ink dark:text-ink-dark truncate">
                        <HighlightMatch text={article.title} query={query} />
                      </span>
                    </span>
                  </Link>
                </li>
              );
            })}
          </ul>

          <button
            type="button"
            onMouseDown={(e) => e.preventDefault()}
            onClick={onSeeAll}
            className="w-full text-left px-4 py-3 text-sm font-semibold text-pulse-600 dark:text-pulse-300 border-t border-line dark:border-line-dark hover:bg-canvas dark:hover:bg-canvas-dark transition-colors"
          >
            Ver todos los resultados para "{query}"
          </button>
        </>
      )}
    </div>
  );
}
