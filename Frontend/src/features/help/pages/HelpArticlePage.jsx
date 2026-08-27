import { Link, useParams } from "react-router-dom";
import { IoTimeOutline, IoConstructOutline, IoArrowBack, IoArrowForward } from "react-icons/io5";
import { getArticleBySlug, getArticlesByCategory, getRelatedArticles } from "../data/articles";
import { getCategoryById } from "../data/categories";
import { formatHelpDate } from "../lib/formatDate";
import HelpBreadcrumbs from "../components/HelpBreadcrumbs";
import HelpArticleContent, { getTableOfContents } from "../components/HelpArticleContent";
import HelpFeedback from "../components/HelpFeedback";
import HelpRelatedArticles from "../components/HelpRelatedArticles";
import HelpEmptyState from "../components/HelpEmptyState";

export default function HelpArticlePage() {
  const { slug } = useParams();
  const article = getArticleBySlug(slug);

  if (!article) {
    return (
      <HelpEmptyState
        title="No encontramos este artículo."
        description="Puede que el enlace esté roto o que el artículo haya cambiado de dirección."
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

  const category = getCategoryById(article.categoryId);
  const related = getRelatedArticles(article);
  const toc = getTableOfContents(article.sections);

  const categoryArticles = getArticlesByCategory(article.categoryId);
  const currentIndex = categoryArticles.findIndex((a) => a.slug === article.slug);
  const prevArticle = currentIndex > 0 ? categoryArticles[currentIndex - 1] : null;
  const nextArticle = currentIndex < categoryArticles.length - 1 ? categoryArticles[currentIndex + 1] : null;

  return (
    <div className="max-w-3xl space-y-8">
      <HelpBreadcrumbs
        items={[
          { label: "Centro de Ayuda", to: "/help" },
          { label: category?.title, to: `/help/category/${article.categoryId}` },
          { label: article.title },
        ]}
      />

      <header>
        <span className="text-xs font-semibold uppercase tracking-wide text-pulse-600 dark:text-pulse-300">
          {category?.title}
        </span>
        <h1 className="mt-1.5 text-2xl sm:text-3xl font-extrabold tracking-tight text-ink dark:text-ink-dark">
          {article.title}
        </h1>
        <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-muted dark:text-muted-dark">
          <span>Última actualización: {formatHelpDate(article.updatedAt)}</span>
          <span className="flex items-center gap-1">
            <IoTimeOutline size={13} aria-hidden="true" />
            {article.readTimeMinutes} min de lectura
          </span>
        </div>
      </header>

      {article.status === "in-progress" && (
        <div className="flex items-start gap-2.5 rounded-xl bg-warning-50 dark:bg-warning-500/10 border border-warning-300/60 dark:border-warning-500/30 px-4 py-3 text-sm text-ink dark:text-ink-dark">
          <IoConstructOutline size={17} className="shrink-0 mt-0.5 text-warning-600 dark:text-warning-400" aria-hidden="true" />
          <p>Esta función todavía está en desarrollo en THERS. El artículo explica cómo va a funcionar y qué podés hacer hoy mientras tanto.</p>
        </div>
      )}

      {toc.length >= 3 && (
        <nav aria-label="Tabla de contenidos" className="rounded-2xl border border-line dark:border-line-dark bg-canvas dark:bg-canvas-dark p-4">
          <p className="text-xs font-semibold uppercase tracking-wide text-muted dark:text-muted-dark mb-2">
            En este artículo
          </p>
          <ul className="space-y-1">
            {toc.map((entry) => (
              <li key={entry.id}>
                <a href={`#${entry.id}`} className="text-sm text-pulse-600 dark:text-pulse-300 hover:underline">
                  {entry.heading}
                </a>
              </li>
            ))}
          </ul>
        </nav>
      )}

      <HelpArticleContent sections={article.sections} />

      <HelpFeedback slug={article.slug} />

      {(prevArticle || nextArticle) && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
          {prevArticle ? (
            <Link
              to={`/help/article/${prevArticle.slug}`}
              className="flex items-center gap-2 rounded-xl border border-line dark:border-line-dark px-4 py-3 hover:bg-canvas dark:hover:bg-canvas-dark transition-colors"
            >
              <IoArrowBack size={15} className="shrink-0 text-muted dark:text-muted-dark" aria-hidden="true" />
              <span className="min-w-0">
                <span className="block text-[11px] text-muted dark:text-muted-dark">Anterior</span>
                <span className="block text-sm text-ink dark:text-ink-dark truncate">{prevArticle.title}</span>
              </span>
            </Link>
          ) : (
            <span />
          )}

          {nextArticle && (
            <Link
              to={`/help/article/${nextArticle.slug}`}
              className="flex items-center justify-end gap-2 rounded-xl border border-line dark:border-line-dark px-4 py-3 text-right hover:bg-canvas dark:hover:bg-canvas-dark transition-colors sm:col-start-2"
            >
              <span className="min-w-0">
                <span className="block text-[11px] text-muted dark:text-muted-dark">Siguiente</span>
                <span className="block text-sm text-ink dark:text-ink-dark truncate">{nextArticle.title}</span>
              </span>
              <IoArrowForward size={15} className="shrink-0 text-muted dark:text-muted-dark" aria-hidden="true" />
            </Link>
          )}
        </div>
      )}

      <HelpRelatedArticles articles={related} />
    </div>
  );
}
