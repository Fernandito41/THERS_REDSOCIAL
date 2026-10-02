import { useEffect, useState } from "react";
import Avatar from "@shared/components/Avatar";
import Icon from "@shared/components/Icon";
import Spinner from "@shared/components/Spinner";
import { api, getErrorMessage } from "@shared/lib/api";
import { getStoredToken } from "@features/auth";
import { useToast } from "@shared/components/Toast";
import { useLanguage } from "@shared/i18n";
import { formatRelativeTime } from "../../lib/formatRelativeTime";

// Bandeja de solicitudes de seguimiento
// (GET /api/follow-requests, POST /api/follow-requests/<id>/accept,
// DELETE /api/follow-requests/<id> -- ADR-018-private-accounts.md).
//
// Vive dentro de Configuración › Privacidad, junto al interruptor que las
// produce: una cuenta pública nunca genera solicitudes, así que no tenía
// sentido darles un lugar propio en la navegación principal. Si el equipo
// decide después que merecen su propia pantalla, el componente ya es
// autónomo.
//
// Se monta aunque la cuenta sea pública: volver a pública NO borra lo que
// quedó pendiente (ADR-018 §Decisión), así que esconder la bandeja dejaría
// solicitudes irrespondibles.

function authHeaders() {
  return { Authorization: `Bearer ${getStoredToken()}` };
}

export default function FollowRequestsRow({ onResolved }) {
  const toast = useToast();
  const { t } = useLanguage();

  const [requests, setRequests] = useState(null);
  const [loading, setLoading] = useState(true);
  // Id de la persona cuya solicitud tiene una petición en vuelo, para
  // deshabilitar sus dos botones sin bloquear el resto de la lista.
  const [busyId, setBusyId] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const res = await api.get("/follow-requests", { headers: authHeaders() });
        if (!cancelled) setRequests(res.data.follow_requests);
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

  // Aceptar y rechazar comparten todo salvo el verbo y el mensaje, así que
  // comparten handler -- duplicarlo invitaría a que divergieran.
  async function respond(userId, accept) {
    if (busyId) return;
    setBusyId(userId);

    try {
      if (accept) {
        await api.post(`/follow-requests/${userId}/accept`, null, { headers: authHeaders() });
      } else {
        await api.delete(`/follow-requests/${userId}`, { headers: authHeaders() });
      }
      // Sin actualización optimista: la solicitud sale de la lista cuando el
      // servidor confirma. Es una decisión que afecta a quién ve tu contenido
      // -- mostrarla como resuelta antes de que lo esté sería afirmar un
      // permiso que todavía no existe.
      setRequests((previous) => previous.filter((request) => request.user.id !== userId));
      onResolved?.();
      toast.success(accept ? "Solicitud aceptada" : "Solicitud rechazada");
    } catch (error) {
      toast.error(getErrorMessage(error, t));
    } finally {
      setBusyId(null);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center gap-2 py-4 text-th-fg-muted" role="status">
        <Spinner size={16} />
        <span className="text-body-sm">Cargando solicitudes...</span>
      </div>
    );
  }

  if (!requests || requests.length === 0) {
    return (
      <div className="flex flex-col gap-1 py-4">
        <span className="text-label-lg font-semibold text-th-fg-strong">
          Solicitudes de seguimiento
        </span>
        <p className="text-body-sm text-th-fg-muted">
          No tienes solicitudes pendientes. Cuando tu cuenta es privada, quien quiera seguirte
          aparecerá acá para que lo apruebes.
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3 py-4">
      <div className="flex flex-col gap-1">
        <span className="text-label-lg font-semibold text-th-fg-strong">
          Solicitudes de seguimiento ({requests.length})
        </span>
        <p className="text-body-sm text-th-fg-muted">
          Al aprobar, esta persona podrá ver tus cápsulas. Si la rechazas no se le avisa, y podrá
          volver a pedirlo más adelante.
        </p>
      </div>

      <ul className="flex flex-col gap-2">
        {requests.map(({ user, requested_at }) => (
          <li
            key={user.id}
            className="flex flex-wrap items-center gap-3 rounded-th-card bg-th-surface-subtle px-3 py-2.5"
          >
            <Avatar name={user.name} size="w-9 h-9" />
            <div className="min-w-0 flex-1">
              <p className="truncate text-label-md font-bold text-th-fg-strong">{user.name}</p>
              <p className="truncate text-body-sm text-th-fg-muted">
                @{user.username} · {formatRelativeTime(requested_at)}
              </p>
            </div>

            <div className="flex shrink-0 items-center gap-2">
              <button
                type="button"
                onClick={() => respond(user.id, false)}
                disabled={busyId === user.id}
                aria-label={`Rechazar la solicitud de ${user.name}`}
                className="flex h-9 w-9 items-center justify-center rounded-th-pill border border-th-border text-th-fg-muted transition-colors th-focus-ring hover:bg-th-danger-surface hover:text-th-danger-accent disabled:opacity-40"
              >
                <Icon name="close" size={18} />
              </button>
              <button
                type="button"
                onClick={() => respond(user.id, true)}
                disabled={busyId === user.id}
                aria-label={`Aceptar la solicitud de ${user.name}`}
                className="inline-flex min-h-[36px] items-center gap-1.5 rounded-th-pill bg-th-brand px-3.5 py-1.5 text-label-md font-bold text-th-on-brand transition-colors th-focus-ring hover:bg-th-brand-hover disabled:opacity-40"
              >
                {busyId === user.id ? <Spinner size={14} /> : "Aprobar"}
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
