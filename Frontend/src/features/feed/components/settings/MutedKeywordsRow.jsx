import { useEffect, useState } from "react";
import Icon from "@shared/components/Icon";
import Spinner from "@shared/components/Spinner";
import { api, getErrorMessage } from "@shared/lib/api";
import { getStoredToken } from "@features/auth";
import { useToast } from "@shared/components/Toast";
import { useLanguage } from "@shared/i18n";

// Editor de términos filtrados
// (GET/POST/DELETE /api/users/me/muted-keywords --
// ADR-020-content-filters-and-privacy-preferences.md).
//
// El servidor devuelve la lista completa en cada respuesta (incluido el POST y
// el DELETE), así que este componente nunca tiene que reconstruirla a mano ni
// volver a pedirla -- se reemplaza con lo que vino.
//
// El término se manda en el body también en el DELETE, no en la URL: puede
// llevar espacios, acentos y `/`, y meterlo en el path obligaría a
// percent-encoding en los dos lados para nada (ADR-020 §Contrato API).

const MAX_KEYWORD_LENGTH = 60;

function authHeaders() {
  return { Authorization: `Bearer ${getStoredToken()}` };
}

export default function MutedKeywordsRow() {
  const toast = useToast();
  const { t } = useLanguage();

  const [keywords, setKeywords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [draft, setDraft] = useState("");
  const [saving, setSaving] = useState(false);
  const [removingKeyword, setRemovingKeyword] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const res = await api.get("/users/me/muted-keywords", { headers: authHeaders() });
        if (!cancelled) setKeywords(res.data.muted_keywords);
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
    const keyword = draft.trim();
    if (!keyword || saving) return;

    setSaving(true);
    try {
      const res = await api.post(
        "/users/me/muted-keywords",
        { keyword },
        { headers: authHeaders() }
      );
      setKeywords(res.data.muted_keywords);
      setDraft("");
    } catch (error) {
      toast.error(getErrorMessage(error, t));
    } finally {
      setSaving(false);
    }
  }

  async function handleRemove(keyword) {
    if (removingKeyword) return;
    setRemovingKeyword(keyword);

    try {
      // axios manda body en DELETE con la clave `data`, no como segundo
      // argumento (a diferencia de post/patch).
      const res = await api.delete("/users/me/muted-keywords", {
        headers: authHeaders(),
        data: { keyword },
      });
      setKeywords(res.data.muted_keywords);
    } catch (error) {
      toast.error(getErrorMessage(error, t));
    } finally {
      setRemovingKeyword(null);
    }
  }

  return (
    <div className="flex flex-col gap-3 py-4">
      <div className="flex flex-col gap-1">
        <span className="text-label-lg font-semibold text-th-fg-strong">
          Filtros de palabras clave personalizadas
        </span>
        <p className="text-body-sm text-th-fg-muted">
          Las cápsulas y los comentarios que contengan alguno de estos términos no te aparecerán,
          en ningún hilo. Solo afecta a lo que ves tú: el resto de la gente los sigue viendo, y tus
          propias publicaciones nunca se te ocultan.
        </p>
        <p className="text-body-sm text-th-fg-subtle">Se guarda en el servidor y se aplica a cada consulta.</p>
      </div>

      <form onSubmit={handleAdd} className="flex items-center gap-2">
        <label htmlFor="muted-keyword-input" className="sr-only">
          Agregar un término a filtrar
        </label>
        <input
          id="muted-keyword-input"
          type="text"
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          placeholder="Ej: spoilers"
          maxLength={MAX_KEYWORD_LENGTH}
          disabled={saving}
          className="min-h-[44px] flex-1 rounded-th-input border border-th-border bg-th-surface px-3.5 py-2 text-body-sm text-th-fg placeholder:text-th-fg-muted th-focus-ring disabled:opacity-60"
        />
        <button
          type="submit"
          disabled={!draft.trim() || saving}
          className="inline-flex min-h-[44px] shrink-0 items-center gap-2 rounded-th-input bg-th-brand px-4 py-2 text-label-lg font-bold text-th-on-brand transition-colors th-focus-ring hover:bg-th-brand-hover disabled:opacity-40"
        >
          {saving ? <Spinner size={16} /> : "Agregar"}
        </button>
      </form>

      {loading ? (
        <div className="flex items-center gap-2 text-th-fg-muted" role="status">
          <Spinner size={16} />
          <span className="text-body-sm">Cargando términos...</span>
        </div>
      ) : keywords.length === 0 ? (
        <p className="text-body-sm text-th-fg-muted">Todavía no filtras ningún término.</p>
      ) : (
        <ul className="flex flex-wrap gap-2">
          {keywords.map((keyword) => (
            <li key={keyword}>
              <span className="inline-flex items-center gap-1.5 rounded-th-pill border border-th-border bg-th-surface-subtle py-1 pl-3 pr-1.5 text-label-md text-th-fg">
                {keyword}
                <button
                  type="button"
                  onClick={() => handleRemove(keyword)}
                  disabled={removingKeyword === keyword}
                  aria-label={`Dejar de filtrar "${keyword}"`}
                  className="flex h-6 w-6 items-center justify-center rounded-th-pill text-th-fg-muted transition-colors th-focus-ring hover:bg-th-danger-surface hover:text-th-danger-accent disabled:opacity-40"
                >
                  {removingKeyword === keyword ? <Spinner size={12} /> : <Icon name="close" size={14} />}
                </button>
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
