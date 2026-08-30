import { HELP_ARTICLES } from "../data/articles";
import { HELP_FAQS } from "../data/faqs";
import { getCategoryById } from "../data/categories";

function normalize(value) {
  return (value || "")
    .toString()
    .normalize("NFD")
    .replace(new RegExp("[\\u0300-\\u036f]", "g"), "")
    .toLowerCase();
}

function articleSearchScore(article, query) {
  const q = normalize(query);
  const title = normalize(article.title);
  const description = normalize(article.description);
  const category = getCategoryById(article.categoryId);
  const categoryTitle = normalize(category?.title);
  const tags = article.tags.map(normalize);
  const body = normalize(
    article.sections
      .map((s) => [s.heading, s.text, ...(s.items || [])].filter(Boolean).join(" "))
      .join(" ")
  );

  if (title === q) return 100;
  if (title.startsWith(q)) return 90;
  if (title.includes(q)) return 80;
  if (tags.some((tag) => tag.includes(q))) return 65;
  if (description.includes(q)) return 55;
  if (categoryTitle.includes(q)) return 40;
  if (body.includes(q)) return 30;
  return 0;
}

// Búsqueda local por coincidencia de texto (sin backend de búsqueda todavía) --
// puntúa título > tags > descripción > categoría > contenido, y ordena de
// mayor a menor relevancia. Coincide con lo que el buscador visualmente
// promete ("por título", "por contenido", "por categoría").
export function searchArticles(query, { categoryId, limit } = {}) {
  const trimmed = (query || "").trim();
  if (!trimmed) return [];

  let results = HELP_ARTICLES.map((article) => ({
    article,
    score: articleSearchScore(article, trimmed),
  })).filter((r) => r.score > 0);

  if (categoryId && categoryId !== "all") {
    results = results.filter((r) => r.article.categoryId === categoryId);
  }

  results.sort((a, b) => b.score - a.score);

  const articles = results.map((r) => r.article);
  return typeof limit === "number" ? articles.slice(0, limit) : articles;
}

export function searchFaqs(query, limit = 4) {
  const q = normalize((query || "").trim());
  if (!q) return [];

  return HELP_FAQS.filter(
    (faq) => normalize(faq.question).includes(q) || normalize(faq.answer).includes(q)
  ).slice(0, limit);
}

export function sortArticles(articles, sortBy) {
  const list = [...articles];
  if (sortBy === "recent") {
    return list.sort((a, b) => (a.updatedAt < b.updatedAt ? 1 : -1));
  }
  return list.sort((a, b) => a.title.localeCompare(b.title, "es"));
}
