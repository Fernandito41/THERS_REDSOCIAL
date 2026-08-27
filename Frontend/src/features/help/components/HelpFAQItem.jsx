import { useId } from "react";
import { Link } from "react-router-dom";
import { IoChevronDown } from "react-icons/io5";

export default function HelpFAQItem({ faq, isOpen, onToggle }) {
  const panelId = useId();

  return (
    <div className="border-b border-line dark:border-line-dark last:border-b-0">
      <h3>
        <button
          type="button"
          onClick={onToggle}
          aria-expanded={isOpen}
          aria-controls={panelId}
          className="w-full flex items-center justify-between gap-4 py-4 text-left text-sm font-medium text-ink dark:text-ink-dark hover:text-pulse-700 dark:hover:text-pulse-300 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-pulse-500 rounded-sm"
        >
          {faq.question}
          <IoChevronDown
            size={16}
            className={`shrink-0 transition-transform duration-200 motion-reduce:transition-none ${isOpen ? "rotate-180" : ""}`}
            aria-hidden="true"
          />
        </button>
      </h3>

      {isOpen && (
        <div id={panelId} role="region" className="pb-4 -mt-1 animate-float-in">
          <p className="text-sm text-muted dark:text-muted-dark">{faq.answer}</p>
          {faq.articleSlug && (
            <Link
              to={`/help/article/${faq.articleSlug}`}
              className="inline-block mt-2 text-sm font-semibold text-pulse-600 dark:text-pulse-300 hover:underline"
            >
              Leer el artículo completo
            </Link>
          )}
        </div>
      )}
    </div>
  );
}
