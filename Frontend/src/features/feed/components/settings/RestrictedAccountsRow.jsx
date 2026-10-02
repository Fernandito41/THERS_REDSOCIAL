import { useEffect, useState } from "react";
import Icon from "@shared/components/Icon";
import Spinner from "@shared/components/Spinner";
import { api, getErrorMessage } from "@shared/lib/api";
import { getStoredToken } from "@features/auth";
import { useToast } from "@shared/components/Toast";
import { useLanguage } from "@shared/i18n";

// Cuentas bloqueadas y restringidas
// (GET/POST /api/users/me/blocks y DELETE /api/users/me/blocks/<id>;
// GET/POST /api/users/me/restrictions y DELETE /api/users/me/restrictions/<id> --
// ADR-025-blocked-and-restricted-accounts.md).
//
// Antes de ese ADR estos controles eran `pending` ("Requiere comprobación de
// acceso en el servidor, que no existe"). Ahora el servidor corta el acceso
// de verdad: este componente solo administra las dos listas.
//
// Un único componente para los dos tipos (`kind="block" | "restrict"`): la
// diferencia es el texto y la ruta, no la mecánica -- mismo criterio de
// reutilización que SettingsSectionPage.

const COPY = {
  block: {
    path: "/users/me/blocks",
    listKey: "blocks",
    title: "Cuentas bloqueadas",
    description:
      "Una cuenta bloqueada deja de ver tu contenido y de poder interactuar contigo: tus publicaciones, comentarios, likes, seguimiento y mensajes. Tampoco ves lo suyo. Bloquear a alguien deja de seguirlo y de ser seguido.",
    placeholder: "@usuario a bloquear",
    add: "Bloquear",
    remove: "Desbloquear",
    empty: "No tienes ninguna cuenta bloqueada.",
    added: "Cuenta bloqueada",
    removed: "Cuenta desbloqueada",
  },
  restrict: {
    path: "/users/me/restrictions",
    listKey: "restrictions",
    title: "Cuentas restringidas",
    description:
      "Una cuenta restringida sigue viendo tu perfil y puede interactuar, pero sus comentarios en tus publicaciones quedan ocultos para los demás. Ella no se entera. Tú sí los ves, para poder moderarlos.",
    placeholder: "@usuario a restringir",
    add: "Restringir",
    remove: "Quitar restricción",
    empty: "No tienes ninguna cuenta restringida.",
    added: "Cuenta restringida",
    removed: "Restricción quitada",
  },
};

function authHeaders() {
  return { Authorization: `Bearer ${getStoredToken()}` };
}

export default function RestrictedAccountsRow({ kind }) {
  const copy = COPY[kind];
  const toast = useToast();
  const { t } = useLanguage();

  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [draft, setDraft] = useState("");
  const [saving, setSaving] = useState(false);
  const [removingId, setRemovingId] = useState(null);

  async function load() {
    const res = await api.get(copy.path, { headers: authHeaders() });
    return res.data[copy.listKey];
  }

  useEffect(() => {
    let cancelled = false;

    async function init() {
      try {
        const loaded = await load();
        if (!cancelled) setItems(loaded);
      } catch (error) {
        if (!cancelled) toast.error(getErrorMessage(error, t));
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    init();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [kind]);

  async function handleAdd(event) {
    event.preventDefault();
    const username = draft.trim();
    if (!username || saving) return;

    setSaving(true);
    try {
      await api.post(copy.path, { username }, { headers: authHeaders() });
      setItems(await load());
      setDraft("");
      toast.success(copy.added);
    } catch (error) {
      toast.error(getErrorMessage(error, t));
    } finally {
      setSaving(false);
    }
  }

  async function handleRemove(item) {
    if (removingId) return;
    setRemovingId(item.user.id);

    try {
      await api.delete(`${copy.path}/${item.user.id}`, { headers: authHeaders() });
      setItems((previous) => previous.filter((i) => i.user.id !== item.user.id));
      toast.success(copy.removed);
    } catch (error) {
      toast.error(getErrorMessage(error, t));
    } finally {
      setRemovingId(null);
    }
  }

  const inputId = `restricted-input-${kind}`;

  return (
    <div className="flex flex-col gap-3 py-4 first:pt-0 last:pb-0">
      <div className="flex flex-col gap-1">
        <span className="text-label-lg font-semibold text-th-fg-strong">
          {copy.title} ({items.length})
        </span>
        <p className="text-body-sm text-th-fg-muted">{copy.description}</p>
        <p className="text-body-sm text-th-fg-subtle">Se aplica en el servidor.</p>
      </div>

      <form onSubmit={handleAdd} className="flex items-center gap-2">
        <label htmlFor={inputId} className="sr-only">
          {copy.placeholder}
        </label>
        <input
          id={inputId}
          type="text"
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          placeholder={copy.placeholder}
          maxLength={40}
          disabled={saving}
          autoComplete="off"
          className="min-h-[44px] flex-1 rounded-th-input border border-th-border bg-th-surface px-3.5 py-2 text-body-sm text-th-fg placeholder:text-th-fg-muted th-focus-ring disabled:opacity-60"
        />
        <button
          type="submit"
          disabled={!draft.trim() || saving}
          className="inline-flex min-h-[44px] shrink-0 items-center gap-2 rounded-th-input bg-th-brand px-4 py-2 text-label-lg font-bold text-th-on-brand transition-colors th-focus-ring hover:bg-th-brand-hover disabled:opacity-40"
        >
          {saving ? <Spinner size={16} /> : copy.add}
        </button>
      </form>

      {loading ? (
        <div className="flex items-center gap-2 text-th-fg-muted" role="status">
          <Spinner size={16} />
          <span className="text-body-sm">Cargando...</span>
        </div>
      ) : items.length === 0 ? (
        <p className="text-body-sm text-th-fg-muted">{copy.empty}</p>
      ) : (
        <ul className="flex flex-col gap-2">
          {items.map((item) => (
            <li
              key={item.user.id}
              className="flex items-center gap-3 rounded-th-card bg-th-surface-subtle px-3 py-2.5"
            >
              <Icon
                name={kind === "block" ? "block" : "visibility_off"}
                size={20}
                className="shrink-0 text-th-fg-muted"
              />
              <div className="min-w-0 flex-1">
                <p className="truncate text-label-md font-bold text-th-fg-strong">
                  {item.user.name}
                </p>
                <p className="truncate text-body-sm text-th-fg-muted">@{item.user.username}</p>
              </div>
              <button
                type="button"
                onClick={() => handleRemove(item)}
                disabled={removingId === item.user.id}
                aria-label={`${copy.remove} a @${item.user.username}`}
                className="flex h-9 shrink-0 items-center gap-1.5 rounded-th-pill border border-th-border px-3 text-label-md font-bold text-th-fg transition-colors th-focus-ring hover:bg-th-surface disabled:opacity-40"
              >
                {removingId === item.user.id ? <Spinner size={14} /> : copy.remove}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
