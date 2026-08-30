import { Link } from "react-router-dom";
import { IoArrowForward } from "react-icons/io5";

export default function HelpRelatedArticles({ articles }) {
  if (!articles || articles.length === 0) return null;

  return (
    <section aria-labelledby="help-related-heading">
      <h2 id="help-related-heading" className="text-sm font-semibold text-ink dark:text-ink-dark mb-3">
        Artículos relacionados
      </h2>
      <ul className="space-y-2">
        {articles.map((article) => (
          <li key={article.slug}>
            <Link
              to={`/help/article/${article.slug}`}
              className="group flex items-center gap-2 text-sm text-muted dark:text-muted-dark hover:text-pulse-600 dark:hover:text-pulse-300 transition-colors"
            >
              <IoArrowForward size={14} className="shrink-0 group-hover:translate-x-0.5 transition-transform" aria-hidden="true" />
              {article.title}
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}
