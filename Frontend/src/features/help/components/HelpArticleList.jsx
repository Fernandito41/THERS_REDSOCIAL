import HelpArticleCard from "./HelpArticleCard";
import HelpEmptyState from "./HelpEmptyState";
import { HelpArticleListSkeleton } from "./HelpSkeleton";

export default function HelpArticleList({ articles, query = "", isLoading = false, emptyState }) {
  if (isLoading) return <HelpArticleListSkeleton />;

  if (articles.length === 0) {
    return emptyState || <HelpEmptyState />;
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
      {articles.map((article) => (
        <HelpArticleCard key={article.slug} article={article} query={query} />
      ))}
    </div>
  );
}
