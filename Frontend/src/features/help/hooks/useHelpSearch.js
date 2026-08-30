import { useEffect, useMemo, useState } from "react";
import { useDebouncedValue } from "./useDebouncedValue";
import { searchArticles, searchFaqs } from "../lib/searchHelp";

// Búsqueda local con debounce -- no hay backend de búsqueda todavía
// (API_CONTRACT.md solo documenta /login y /register), así que "loading"
// refleja el propio debounce, no una llamada de red real.
export function useHelpSearch(query, { categoryId, limit } = {}) {
  const debouncedQuery = useDebouncedValue(query, 300);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!query.trim()) {
      setIsLoading(false);
      return;
    }
    setIsLoading(true);
  }, [query]);

  useEffect(() => {
    setIsLoading(false);
  }, [debouncedQuery]);

  const articles = useMemo(
    () => searchArticles(debouncedQuery, { categoryId, limit }),
    [debouncedQuery, categoryId, limit]
  );

  const faqs = useMemo(() => searchFaqs(debouncedQuery, 4), [debouncedQuery]);

  return {
    query: debouncedQuery,
    articles,
    faqs,
    isLoading,
    hasQuery: debouncedQuery.trim().length > 0,
    hasResults: articles.length > 0 || faqs.length > 0,
  };
}
