import { Link } from "react-router-dom";
import { IoTimeOutline } from "react-icons/io5";
import { getCategoryById } from "../data/categories";
import HighlightMatch from "./HighlightMatch";

export default function HelpArticleCard({ article, query = "" }) {
  const category = getCategoryById(article.categoryId);

  return (
    <Link
      to={`/help/article/${article.slug}`}
      className="group flex flex-col rounded-2xl border border-line dark:border-line-dark bg-surface dark:bg-surface-dark p-5 hover:shadow-soft hover:border-pulse-300 dark:hover:border-pulse-700 transition"
    >
      <div className="flex items-center justify-between gap-2">
        <span className="text-xs font-semibold uppercase tracking-wide text-pulse-600 dark:text-pulse-300">
          {category?.title}
        </span>
        {article.status === "in-progress" && (
          <span className="text-[10px] font-semibold uppercase tracking-wide text-warning-600 dark:text-warning-400 bg-warning-50 dark:bg-warning-500/10 rounded-full px-2 py-0.5">
            En desarrollo
          </span>
        )}
      </div>

      <h3 className="mt-2 text-sm font-semibold text-ink dark:text-ink-dark leading-snug group-hover:text-pulse-700 dark:group-hover:text-pulse-300 transition-colors">
        <HighlightMatch text={article.title} query={query} />
      </h3>

      <p className="mt-1.5 text-xs text-muted dark:text-muted-dark line-clamp-2">
        <HighlightMatch text={article.description} query={query} />
      </p>

      <div className="mt-3 flex items-center gap-1 text-[11px] text-muted dark:text-muted-dark">
        <IoTimeOutline size={12} aria-hidden="true" />
        {article.readTimeMinutes} min de lectura
      </div>
    </Link>
  );
}
