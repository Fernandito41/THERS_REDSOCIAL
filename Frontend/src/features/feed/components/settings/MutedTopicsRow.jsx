import { useEffect, useState } from "react";
import Icon from "@shared/components/Icon";
import Spinner from "@shared/components/Spinner";
import { api, getErrorMessage } from "@shared/lib/api";
import { getStoredToken } from "@features/auth";
import { useToast } from "@shared/components/Toast";
import { useLanguage } from "@shared/i18n";

// Editor de temas silenciados
// (GET/POST/DELETE /api/users/me/muted-topics -- ADR-030-content-preferences.md).
//
// Un tema es un hashtag: silenciar `viajes` oculta del feed las publicaciones
// que contienen `#viajes` (la etiqueta completa, no `#viajes2`). Mismo reparto
// que MutedKeywordsRow: el servidor devuelve la lista completa en cada
// respuesta y acá solo se reemplaza el estado con lo que llegó.
//
// El tema va en el body también en el DELETE (igual que las palabras
// ocultas, ADR-024): puede llevar acentos y no hay motivo para percent-encoding.

const MAX_TOPIC_LENGTH = 50;

function authHeaders() {
  return { Authorization: `Bearer ${getStoredToken()}` };
}

export default function MutedTopicsRow() {
  const toast = useToast();
  const { t } = useLanguage();

  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [draft, setDraft] = useState("");
  const [saving, setSaving] = useState(false);
  const [removingTopic, setRemovingTopic] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const res = await api.get("/users/me/muted-topics", { headers: authHeaders() });
        if (!cancelled) setTopics(res.data.muted_topics);
      } catch (error) {
        if (!cancelled) toast.error(getErrorMessage(error, t));
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleAdd(event) {
    event.preventDefault();
    const topic = draft.trim();
    if (!topic || saving) return;

    setSaving(true);
    try {
      const res = await api.post("/users/me/muted-topics", { topic }, { headers: authHeaders() });
      setTopics(res.data.muted_topics);
      setDraft("");
    } catch (error) {
      toast.error(getErrorMessage(error, t));
    } finally {
      setSaving(false);
    }
  }

  async function handleRemove(topic) {
    if (removingTopic) return;
    setRemovingTopic(topic);

    try {
      const res = await api.delete("/users/me/muted-topics", {
        headers: authHeaders(),
        data: { topic },
      });
      setTopics(res.data.muted_topics);
    } catch (error) {
      toast.error(getErrorMessage(error, t));
    } finally {
      setRemovingTopic(null);
    }
  }

  return (
    <div className="flex flex-col gap-3 py-4">
      <div className="flex flex-col gap-1">
        <span className="text-label-lg font-semibold text-th-fg-strong">Temas silenciados</span>
        <p className="text-body-sm text-th-fg-muted">
          Las publicaciones que incluyan estas etiquetas no te aparecerán en el feed. Silenciar{" "}
          <span className="font-semibold">viajes</span> oculta <span className="font-semibold">#viajes</span>,
          pero no <span className="font-semibold">#viajes2</span>. Solo afecta a lo que ves tú, y tus
          propias publicaciones nunca se te ocultan.
        </p>
        <p className="text-body-sm text-th-fg-subtle">Se guarda en el servidor y se aplica a cada consulta.</p>
      </div>

      <form onSubmit={handleAdd} className="flex items-center gap-2">
        <label htmlFor="muted-topic-input" className="sr-only">
          Silenciar un tema
        </label>
        <input
          id="muted-topic-input"
          type="text"
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          placeholder="Ej: #viajes"
          maxLength={MAX_TOPIC_LENGTH + 1}
          disabled={saving}
          autoComplete="off"
          className="min-h-[44px] flex-1 rounded-th-input border border-th-border bg-th-surface px-3.5 py-2 text-body-sm text-th-fg placeholder:text-th-fg-muted th-focus-ring disabled:opacity-60"
        />
        <button
          type="submit"
          disabled={!draft.trim() || saving}
          className="inline-flex min-h-[44px] shrink-0 items-center gap-2 rounded-th-input bg-th-brand px-4 py-2 text-label-lg font-bold text-th-on-brand transition-colors th-focus-ring hover:bg-th-brand-hover disabled:opacity-40"
        >
          {saving ? <Spinner size={16} /> : "Silenciar"}
        </button>
      </form>

      {loading ? (
        <div className="flex items-center gap-2 text-th-fg-muted" role="status">
          <Spinner size={16} />
          <span className="text-body-sm">Cargando temas...</span>
        </div>
      ) : topics.length === 0 ? (
        <p className="text-body-sm text-th-fg-muted">Todavía no silenciaste ningún tema.</p>
      ) : (
        <ul className="flex flex-wrap gap-2">
          {topics.map((topic) => (
            <li key={topic}>
              <span className="inline-flex items-center gap-1.5 rounded-th-pill border border-th-border bg-th-surface-subtle py-1 pl-3 pr-1.5 text-label-md text-th-fg">
                #{topic}
                <button
                  type="button"
                  onClick={() => handleRemove(topic)}
                  disabled={removingTopic === topic}
                  aria-label={`Dejar de silenciar #${topic}`}
                  className="flex h-6 w-6 items-center justify-center rounded-th-pill text-th-fg-muted transition-colors th-focus-ring hover:bg-th-danger-surface hover:text-th-danger-accent disabled:opacity-40"
                >
                  {removingTopic === topic ? <Spinner size={12} /> : <Icon name="close" size={14} />}
                </button>
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
