import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import HelpSearchBar from "../components/HelpSearchBar";
import HelpFilters from "../components/HelpFilters";
import HelpArticleList from "../components/HelpArticleList";
import HelpEmptyState from "../components/HelpEmptyState";
import HelpFeaturedTopics from "../components/HelpFeaturedTopics";
import { useHelpSearch } from "../hooks/useHelpSearch";
import { sortArticles } from "../lib/searchHelp";

export default function HelpSearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const query = searchParams.get("q") || "";

  const [categoryId, setCategoryId] = useState("all");
  const [sortBy, setSortBy] = useState("relevance");

  const { articles, isLoading, hasQuery } = useHelpSearch(query, { categoryId });

  const sortedArticles = useMemo(() => {
    if (sortBy === "relevance") return articles;
    return sortArticles(articles, sortBy);
  }, [articles, sortBy]);

  useEffect(() => {
    setCategoryId("all");
    setSortBy("relevance");
  }, [query]);

  const handleSubmitQuery = (value) => {
    setSearchParams({ q: value });
  };

  return (
    <div className="space-y-6">
      <div className="max-w-xl">
        <HelpSearchBar
          size="sm"
          autoFocus={!query}
          placeholder="Buscar artículos de ayuda..."
          onSubmitQuery={handleSubmitQuery}
        />
      </div>

      {!hasQuery ? (
        <HelpEmptyState
          title="Buscá en el Centro de Ayuda"
          description="Escribí una palabra clave arriba para encontrar artículos, o explorá alguno de estos temas."
          action={<HelpFeaturedTopics />}
        />
      ) : (
        <>
          <h1 className="text-lg font-bold text-ink dark:text-ink-dark">
            Resultados para "{query}"
          </h1>

          <div className="flex items-start gap-6">
            <HelpFilters
              categoryId={categoryId}
              onCategoryChange={setCategoryId}
              sortBy={sortBy}
              onSortChange={setSortBy}
              showRelevance
            />

            <div className="flex-1 min-w-0">
              <HelpArticleList
                articles={sortedArticles}
                query={query}
                isLoading={isLoading}
                emptyState={
                  <HelpEmptyState
                    description="Probá con otra palabra, revisá la ortografía o explorá las categorías del Centro de Ayuda."
                    action={
                      <Link
                        to="/help"
                        className="inline-flex text-sm font-semibold px-4 py-2 rounded-full bg-pulse-600 hover:bg-pulse-700 text-white transition"
                      >
                        Ver todas las categorías
                      </Link>
                    }
                  />
                }
              />
            </div>
          </div>
        </>
      )}
    </div>
  );
}
