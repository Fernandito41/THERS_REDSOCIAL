import { NavLink } from "react-router-dom";
import { HELP_CATEGORIES } from "../data/categories";
import { getCategoryIcon } from "./helpIcons";

// Navegación por categorías en desktop -- oculta en mobile/tablet, donde
// HelpMobileCategoryNav cubre el mismo rol como fila de chips.
export default function HelpSidebar() {
  return (
    <nav aria-label="Categorías del Centro de Ayuda" className="hidden lg:block w-60 shrink-0">
      <ul className="sticky top-24 space-y-1">
        <li>
          <NavLink
            to="/help"
            end
            className={({ isActive }) =>
              `block px-3 py-2 rounded-xl text-sm font-semibold transition-colors ${
                isActive
                  ? "bg-pulse-50 dark:bg-pulse-900/30 text-pulse-700 dark:text-pulse-300"
                  : "text-ink dark:text-ink-dark hover:bg-canvas dark:hover:bg-canvas-dark"
              }`
            }
          >
            Todas las categorías
          </NavLink>
        </li>

        {HELP_CATEGORIES.map((category) => {
          const Icon = getCategoryIcon(category.icon);
          return (
            <li key={category.id}>
              <NavLink
                to={`/help/category/${category.id}`}
                className={({ isActive }) =>
                  `flex items-center gap-2.5 px-3 py-2 rounded-xl text-sm transition-colors ${
                    isActive
                      ? "bg-pulse-50 dark:bg-pulse-900/30 text-pulse-700 dark:text-pulse-300 font-semibold"
                      : "text-muted dark:text-muted-dark hover:bg-canvas dark:hover:bg-canvas-dark hover:text-ink dark:hover:text-ink-dark"
                  }`
                }
              >
                <Icon size={17} aria-hidden="true" />
                {category.title}
              </NavLink>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
