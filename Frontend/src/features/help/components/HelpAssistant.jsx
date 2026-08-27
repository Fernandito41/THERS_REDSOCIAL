import { useId, useState } from "react";
import { Link } from "react-router-dom";
import { IoChatbubbleEllipsesOutline, IoClose, IoSearchOutline, IoArrowForward } from "react-icons/io5";
import { HELP_FAQS } from "../data/faqs";
import { useHelpSearch } from "../hooks/useHelpSearch";

const QUICK_QUESTIONS = HELP_FAQS.slice(0, 5);

// Asistente de ayuda de THERS -- Fase 1: basado en búsqueda local sobre
// artículos/FAQ + preguntas sugeridas, sin ninguna IA conectada (el backend
// de THERS no expone hoy ningún servicio de ese tipo -- API_CONTRACT.md solo
// documenta /login y /register). No se simulan respuestas generadas: cada
// resultado es un artículo real del Centro de Ayuda. Cuando THERS incorpore
// un servicio de IA real, este es el único punto que debería reemplazarse
// (la búsqueda de useHelpSearch) por una llamada a ese servicio.
function AssistantBody({ onNavigate }) {
  const [query, setQuery] = useState("");
  const { articles, hasQuery } = useHelpSearch(query, { limit: 4 });
  const inputId = useId();

  return (
    <div className="flex flex-col h-full">
      <div className="px-5 pt-5 pb-4 border-b border-line dark:border-line-dark">
        <p className="text-sm font-bold text-ink dark:text-ink-dark">Asistente THERS</p>
        <p className="text-xs text-muted dark:text-muted-dark mt-0.5">
          Respuestas basadas en los artículos del Centro de Ayuda.
        </p>
      </div>

      <div className="px-5 pt-4">
        <label htmlFor={inputId} className="sr-only">
          Escribí tu pregunta
        </label>
        <div className="relative">
          <IoSearchOutline className="absolute left-3.5 top-1/2 -translate-y-1/2 text-muted dark:text-muted-dark" size={16} />
          <input
            id={inputId}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Escribí tu pregunta..."
            className="w-full bg-canvas dark:bg-canvas-dark border border-line dark:border-line-dark rounded-full pl-10 pr-4 py-2.5 text-sm text-ink dark:text-ink-dark placeholder-muted focus:outline-none focus:ring-2 focus:ring-pulse-500"
          />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
        {hasQuery ? (
          articles.length > 0 ? (
            <ul className="space-y-1.5">
              {articles.map((article) => (
                <li key={article.slug}>
                  <Link
                    to={`/help/article/${article.slug}`}
                    onClick={onNavigate}
                    className="flex items-center gap-2 text-sm text-ink dark:text-ink-dark hover:text-pulse-600 dark:hover:text-pulse-300 py-1.5 transition-colors"
                  >
                    <IoArrowForward size={13} className="shrink-0 text-pulse-500" aria-hidden="true" />
                    {article.title}
                  </Link>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-muted dark:text-muted-dark">
              No encontramos coincidencias. Probá con otra palabra o explorá las categorías del Centro de Ayuda.
            </p>
          )
        ) : (
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-muted dark:text-muted-dark mb-2">
              Preguntas frecuentes
            </p>
            <ul className="space-y-1.5">
              {QUICK_QUESTIONS.map((faq) => (
                <li key={faq.id}>
                  <Link
                    to={`/help/article/${faq.articleSlug}`}
                    onClick={onNavigate}
                    className="flex items-center gap-2 text-sm text-ink dark:text-ink-dark hover:text-pulse-600 dark:hover:text-pulse-300 py-1.5 transition-colors"
                  >
                    <IoArrowForward size={13} className="shrink-0 text-pulse-500" aria-hidden="true" />
                    {faq.question}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

export function HelpAssistantPanel() {
  return (
    <aside
      aria-label="Asistente de ayuda de THERS"
      className="hidden lg:flex lg:flex-col w-72 shrink-0 h-fit sticky top-24 rounded-2xl border border-line dark:border-line-dark bg-surface dark:bg-surface-dark shadow-soft max-h-[calc(100vh-8rem)] overflow-hidden"
    >
      <AssistantBody />
    </aside>
  );
}

export function HelpAssistantFloatingButton() {
  const [open, setOpen] = useState(false);
  const panelId = useId();

  return (
    <div className="lg:hidden">
      <button
        type="button"
        onClick={() => setOpen(true)}
        aria-haspopup="dialog"
        aria-expanded={open}
        aria-controls={panelId}
        aria-label="Abrir asistente de ayuda"
        className="fixed bottom-5 right-5 z-40 w-14 h-14 rounded-full bg-gradient-to-br from-pulse-500 to-pulse-700 text-white shadow-lift flex items-center justify-center active:scale-95 transition-transform"
      >
        <IoChatbubbleEllipsesOutline size={24} />
      </button>

      {open && (
        <div className="fixed inset-0 z-50 flex items-end">
          <div className="absolute inset-0 bg-black/40" onClick={() => setOpen(false)} aria-hidden="true" />
          <div
            id={panelId}
            role="dialog"
            aria-modal="true"
            aria-label="Asistente de ayuda de THERS"
            className="relative w-full bg-surface dark:bg-surface-dark rounded-t-3xl h-[75vh] flex flex-col animate-float-in"
          >
            <button
              type="button"
              onClick={() => setOpen(false)}
              aria-label="Cerrar asistente"
              className="absolute top-4 right-4 z-10 p-2 rounded-full hover:bg-canvas dark:hover:bg-canvas-dark text-muted dark:text-muted-dark"
            >
              <IoClose size={18} />
            </button>
            <AssistantBody onNavigate={() => setOpen(false)} />
          </div>
        </div>
      )}
    </div>
  );
}
