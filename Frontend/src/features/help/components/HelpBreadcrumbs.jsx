import { Link } from "react-router-dom";
import { IoChevronForward } from "react-icons/io5";

// `items`: [{ label, to? }] -- el último ítem (sin `to`) es la página actual.
export default function HelpBreadcrumbs({ items }) {
  return (
    <nav aria-label="Ruta de navegación" className="flex items-center flex-wrap gap-1.5 text-sm">
      {items.map((item, index) => {
        const isLast = index === items.length - 1;
        return (
          <span key={`${item.label}-${index}`} className="flex items-center gap-1.5">
            {index > 0 && <IoChevronForward size={12} className="text-muted dark:text-muted-dark" aria-hidden="true" />}
            {isLast || !item.to ? (
              <span aria-current={isLast ? "page" : undefined} className="text-ink dark:text-ink-dark font-medium">
                {item.label}
              </span>
            ) : (
              <Link to={item.to} className="text-muted dark:text-muted-dark hover:text-pulse-600 dark:hover:text-pulse-300 transition-colors">
                {item.label}
              </Link>
            )}
          </span>
        );
      })}
    </nav>
  );
}
