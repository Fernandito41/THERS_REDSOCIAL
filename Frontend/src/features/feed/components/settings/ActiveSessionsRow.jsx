import { useEffect, useState } from "react";
import Icon from "@shared/components/Icon";
import Spinner from "@shared/components/Spinner";
import ConfirmDialog from "@shared/components/ConfirmDialog";
import { api, getErrorMessage } from "@shared/lib/api";
import { getStoredToken } from "@features/auth";
import { useToast } from "@shared/components/Toast";
import { useLanguage } from "@shared/i18n";
import { formatRelativeTime } from "../../lib/formatRelativeTime";
import { describeUserAgent } from "../../lib/describeUserAgent";

// Sesiones activas (GET /api/sessions, DELETE /api/sessions/<id>,
// DELETE /api/sessions -- ADR-021-session-registry.md).
//
// Antes de ese ADR este control era `pending` con el motivo "El JWT no se
// registra por dispositivo, así que no hay nada que listar ni revocar de
// verdad". Ahora cada token tiene una fila y cerrarla invalida ese token de
// inmediato.
//
// Cerrar la sesión propia SÍ está permitido (el backend lo informa con
// `was_current`): es lo mismo que cerrar sesión, y bloquearlo obligaría a
// explicar una excepción sin ganar nada. Lo que se hace es avisar antes, porque
// el efecto es salir de la aplicación.

function authHeaders() {
  return { Authorization: `Bearer ${getStoredToken()}` };
}

export default function ActiveSessionsRow() {
  const toast = useToast();
  const { t } = useLanguage();

  const [sessions, setSessions] = useState(null);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState(null);
  // Sesión propia pendiente de confirmar para cerrar (`null` = diálogo cerrado).
  // Solo la propia pide confirmación: cerrar otra es reversible volviendo a
  // entrar en ese dispositivo; cerrar la propia te saca de acá.
  const [pendingCurrent, setPendingCurrent] = useState(null);
  const [closingOthers, setClosingOthers] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const res = await api.get("/sessions", { headers: authHeaders() });
        if (!cancelled) setSessions(res.data.sessions);
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

  async function revoke(session) {
    if (busyId) return;
    setBusyId(session.id);

    try {
      const res = await api.delete(`/sessions/${session.id}`, { headers: authHeaders() });
      if (res.data.was_current) {
        // El token con el que se hizo esta petición ya no sirve. Se avisa y se
        // manda a /login con una recarga completa, para que no quede estado en
        // memoria de una sesión que ya no existe.
        toast.info("Cerraste esta sesión. Tenés que iniciar sesión de nuevo.");
        window.location.assign("/login");
        return;
      }
      setSessions((previous) => previous.filter((s) => s.id !== session.id));
      toast.success("Sesión cerrada en ese dispositivo");
    } catch (error) {
      toast.error(getErrorMessage(error, t));
    } finally {
      setBusyId(null);
    }
  }

  async function closeOthers() {
    if (closingOthers) return;
    setClosingOthers(true);

    try {
      const res = await api.delete("/sessions", { headers: authHeaders() });
      setSessions((previous) => previous.filter((s) => s.is_current));
      toast.success(
        res.data.revoked_count === 1
          ? "Se cerró 1 sesión"
          : `Se cerraron ${res.data.revoked_count} sesiones`
      );
    } catch (error) {
      toast.error(getErrorMessage(error, t));
    } finally {
      setClosingOthers(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center gap-2 py-4 text-th-fg-muted" role="status">
        <Spinner size={16} />
        <span className="text-body-sm">Cargando sesiones...</span>
      </div>
    );
  }

  const others = (sessions ?? []).filter((s) => !s.is_current);

  return (
    <div className="flex flex-col gap-3 py-4">
      <div className="flex flex-col gap-1">
        <span className="text-label-lg font-semibold text-th-fg-strong">
          Sesiones activas ({sessions?.length ?? 0})
        </span>
        <p className="text-body-sm text-th-fg-muted">
          Dispositivos con la sesión abierta. Al cerrar una, su token deja de valer de inmediato.
        </p>
        <p className="text-body-sm text-th-fg-subtle">Se aplica en el servidor.</p>
      </div>

      <ul className="flex flex-col gap-2">
        {(sessions ?? []).map((session) => (
          <li
            key={session.id}
            className="flex flex-wrap items-center gap-3 rounded-th-card bg-th-surface-subtle px-3 py-2.5"
          >
            <Icon
              name={session.is_current ? "verified_user" : "devices"}
              size={20}
              className="shrink-0 text-th-fg-muted"
            />
            <div className="min-w-0 flex-1">
              <p className="truncate text-label-md font-bold text-th-fg-strong">
                {describeUserAgent(session.user_agent)}
                {session.is_current && (
                  <span className="ml-2 rounded-th-pill bg-th-brand px-2 py-0.5 text-label-md font-bold text-th-on-brand">
                    Este dispositivo
                  </span>
                )}
              </p>
              <p className="truncate text-body-sm text-th-fg-muted">
                {session.ip_address || "IP desconocida"} · activa{" "}
                {formatRelativeTime(session.last_used_at || session.created_at)}
              </p>
            </div>

            <button
              type="button"
              onClick={() =>
                session.is_current ? setPendingCurrent(session) : revoke(session)
              }
              disabled={busyId === session.id}
              aria-label={`Cerrar la sesión de ${describeUserAgent(session.user_agent)}`}
              className="flex h-9 shrink-0 items-center gap-1.5 rounded-th-pill border border-th-border px-3 text-label-md font-bold text-th-fg-muted transition-colors th-focus-ring hover:bg-th-danger-surface hover:text-th-danger-accent disabled:opacity-40"
            >
              {busyId === session.id ? <Spinner size={14} /> : "Cerrar"}
            </button>
          </li>
        ))}
      </ul>

      {others.length > 0 && (
        <button
          type="button"
          onClick={closeOthers}
          disabled={closingOthers}
          className="inline-flex min-h-[44px] w-fit items-center gap-2 rounded-th-input border border-th-border px-4 py-2 text-label-lg font-bold text-th-fg transition-colors th-focus-ring hover:bg-th-surface-subtle disabled:opacity-40"
        >
          {closingOthers && <Spinner size={16} />}
          Cerrar las demás sesiones ({others.length})
        </button>
      )}

      <ConfirmDialog
        open={pendingCurrent !== null}
        icon="logout"
        destructive
        title="¿Cerrar esta sesión?"
        description="Vas a salir de THERS en este dispositivo y tendrás que iniciar sesión de nuevo."
        confirmLabel="Cerrar sesión"
        onConfirm={() => {
          const session = pendingCurrent;
          setPendingCurrent(null);
          if (session) revoke(session);
        }}
        onCancel={() => setPendingCurrent(null)}
      />
    </div>
  );
}
