import { useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getCategoryById } from "../data/categories";
import { getArticlesByCategory } from "../data/articles";
import { sortArticles } from "../lib/searchHelp";
import { getCategoryIcon } from "../components/helpIcons";
import HelpBreadcrumbs from "../components/HelpBreadcrumbs";
import HelpFilters from "../components/HelpFilters";
import HelpArticleList from "../components/HelpArticleList";
import HelpEmptyState from "../components/HelpEmptyState";

export default function HelpCategoryPage() {
  const { categoryId } = useParams();
  const category = getCategoryById(categoryId);
  const [sortBy, setSortBy] = useState("title");

  const articles = useMemo(() => {
    if (!category) return [];
    return sortArticles(getArticlesByCategory(category.id), sortBy);
  }, [category, sortBy]);

  if (!category) {
    return (
      <HelpEmptyState
        title="No encontramos esta categoría."
        description="Puede que el enlace esté roto o que la categoría haya cambiado de nombre."
        action={
          <Link
            to="/help"
            className="inline-flex text-sm font-semibold px-4 py-2 rounded-full bg-pulse-600 hover:bg-pulse-700 text-white transition"
          >
            Volver al Centro de Ayuda
          </Link>
        }
      />
    );
  }

  const Icon = getCategoryIcon(category.icon);

  return (
    <div className="space-y-6">
      <HelpBreadcrumbs items={[{ label: "Centro de Ayuda", to: "/help" }, { label: category.title }]} />

      <div className="flex items-center gap-3">
        <span className="flex items-center justify-center w-11 h-11 rounded-full bg-pulse-50 dark:bg-pulse-900/30 text-pulse-600 dark:text-pulse-300 shrink-0">
          <Icon size={20} aria-hidden="true" />
        </span>
        <div>
          <h2 className="text-xl font-extrabold tracking-tight text-ink dark:text-ink-dark">{category.title}</h2>
          <p className="text-sm text-muted dark:text-muted-dark">{category.description}</p>
        </div>
      </div>

      <div className="flex items-start gap-6">
        <HelpFilters
          showCategory={false}
          sortBy={sortBy}
          onSortChange={setSortBy}
        />

        <div className="flex-1 min-w-0">
          <HelpArticleList
            articles={articles}
            emptyState={
              <HelpEmptyState description="Todavía no hay artículos publicados en esta categoría." />
            }
          />
        </div>
      </div>
    </div>
  );
}
