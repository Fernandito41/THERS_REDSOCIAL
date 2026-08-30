import HelpSearchBar from "../components/HelpSearchBar";
import HelpFeaturedTopics from "../components/HelpFeaturedTopics";
import HelpCategoryGrid from "../components/HelpCategoryGrid";
import HelpArticleList from "../components/HelpArticleList";
import HelpFAQ from "../components/HelpFAQ";
import { HELP_ARTICLES } from "../data/articles";
import { HELP_FAQS } from "../data/faqs";

const POPULAR_SLUGS = [
  "crear-una-cuenta",
  "recuperar-cuenta",
  "editar-perfil",
  "reportar-una-publicacion",
  "apariencia-modo-oscuro",
  "quien-puede-ver-tu-perfil",
];

const popularArticles = POPULAR_SLUGS.map((slug) => HELP_ARTICLES.find((a) => a.slug === slug)).filter(Boolean);

export default function HelpCenter() {
  return (
    <div className="space-y-14">
      <section className="text-center py-6 sm:py-10">
        <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-ink dark:text-ink-dark">
          ¿En qué podemos ayudarte?
        </h2>
        <p className="mt-2 text-sm sm:text-base text-muted dark:text-muted-dark max-w-lg mx-auto">
          Buscá una respuesta o explorá por categoría: cuenta, seguridad, privacidad, publicaciones y más.
        </p>
        <div className="mt-6 max-w-xl mx-auto">
          <HelpSearchBar />
        </div>
      </section>

      <section aria-labelledby="help-topics-heading">
        <h2 id="help-topics-heading" className="text-lg font-bold tracking-tight text-ink dark:text-ink-dark mb-4">
          Temas destacados
        </h2>
        <HelpFeaturedTopics />
      </section>

      <section aria-labelledby="help-categories-heading">
        <h2 id="help-categories-heading" className="text-lg font-bold tracking-tight text-ink dark:text-ink-dark mb-4">
          Categorías
        </h2>
        <HelpCategoryGrid />
      </section>

      <section aria-labelledby="help-popular-heading">
        <h2 id="help-popular-heading" className="text-lg font-bold tracking-tight text-ink dark:text-ink-dark mb-4">
          Artículos populares
        </h2>
        <HelpArticleList articles={popularArticles} />
      </section>

      <HelpFAQ faqs={HELP_FAQS.slice(0, 6)} />
    </div>
  );
}
