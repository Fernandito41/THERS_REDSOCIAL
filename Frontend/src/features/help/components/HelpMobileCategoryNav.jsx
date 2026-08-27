import { NavLink } from "react-router-dom";
import { HELP_CATEGORIES } from "../data/categories";

export default function HelpMobileCategoryNav() {
  return (
    <nav aria-label="Categorías del Centro de Ayuda" className="lg:hidden -mx-4 px-4">
      <ul className="flex gap-2 overflow-x-auto pb-1">
        <li className="shrink-0">
          <NavLink
            to="/help"
            end
            className={({ isActive }) =>
              `block px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap border transition-colors ${
                isActive
                  ? "bg-pulse-600 border-pulse-600 text-white"
                  : "border-line dark:border-line-dark text-ink dark:text-ink-dark hover:bg-canvas dark:hover:bg-canvas-dark"
              }`
            }
          >
            Todas
          </NavLink>
        </li>
        {HELP_CATEGORIES.map((category) => (
          <li key={category.id} className="shrink-0">
            <NavLink
              to={`/help/category/${category.id}`}
              className={({ isActive }) =>
                `block px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap border transition-colors ${
                  isActive
                    ? "bg-pulse-600 border-pulse-600 text-white"
                    : "border-line dark:border-line-dark text-ink dark:text-ink-dark hover:bg-canvas dark:hover:bg-canvas-dark"
                }`
              }
            >
              {category.title}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  );
}
