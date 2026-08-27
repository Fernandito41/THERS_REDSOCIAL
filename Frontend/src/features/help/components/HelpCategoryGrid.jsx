import { Link } from "react-router-dom";
import { HELP_CATEGORIES } from "../data/categories";
import { getCategoryIcon } from "./helpIcons";

export default function HelpCategoryGrid() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
      {HELP_CATEGORIES.map((category) => {
        const Icon = getCategoryIcon(category.icon);
        return (
          <Link
            key={category.id}
            to={`/help/category/${category.id}`}
            className="group flex items-start gap-3 rounded-2xl border border-line dark:border-line-dark bg-surface dark:bg-surface-dark p-4 hover:shadow-soft hover:border-pulse-300 dark:hover:border-pulse-700 transition"
          >
            <span className="shrink-0 flex items-center justify-center w-10 h-10 rounded-full bg-pulse-50 dark:bg-pulse-900/30 text-pulse-600 dark:text-pulse-300 group-hover:scale-105 transition-transform">
              <Icon size={18} aria-hidden="true" />
            </span>
            <span className="min-w-0">
              <span className="block text-sm font-semibold text-ink dark:text-ink-dark">{category.title}</span>
              <span className="block text-xs text-muted dark:text-muted-dark mt-0.5">{category.description}</span>
            </span>
          </Link>
        );
      })}
    </div>
  );
}
