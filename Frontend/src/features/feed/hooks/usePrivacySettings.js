import { useCallback, useEffect, useState } from "react";
import { api, getErrorMessage } from "@shared/lib/api";
import { getStoredToken } from "@features/auth";
import { useToast } from "@shared/components/Toast";
import { useLanguage } from "@shared/i18n";

// Preferencias de privacidad REALES, contra el servidor
// (GET/PATCH /api/users/me/privacy -- ADR-018-private-accounts.md,
// ADR-019-mentions.md, ADR-020-content-filters-and-privacy-preferences.md).
//
// A diferencia de `settingsStorage.js`, que guarda preferencias en este
// navegador porque no hay endpoint que las aplique, estas siete sí se aplican
// en el servidor: filtran consultas, deciden permisos y ocultan datos. Por eso
// NO pasan por localStorage -- guardarlas ahí sería exactamente el problema que
// settingsStorage.js documenta ("una preferencia local no es una regla
// aplicada").
//
// Actualización optimista con rollback, mismo patrón que handleToggleLike en
// AppShell.jsx (ADR-005): el interruptor responde al instante y vuelve atrás si
// la petición falla. Importa especialmente acá -- un control de privacidad que
// parece tardar invita a tocarlo dos veces.

function authHeaders() {
  return { Authorization: `Bearer ${getStoredToken()}` };
}

export function usePrivacySettings() {
  const toast = useToast();
  const { t } = useLanguage();

  const [privacy, setPrivacy] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const res = await api.get("/users/me/privacy", { headers: authHeaders() });
        if (!cancelled) setPrivacy(res.data.privacy);
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

  const update = useCallback(
    async (field, value) => {
      const previous = privacy;
      setPrivacy((current) => ({ ...current, [field]: value }));

      try {
        const res = await api.patch(
          "/users/me/privacy",
          { [field]: value },
          { headers: authHeaders() }
        );
        // Se reemplaza con la respuesta del servidor, no con el valor que
        // mandamos: así `pending_follow_requests_count` queda al día sin otra
        // petición.
        setPrivacy(res.data.privacy);
      } catch (error) {
        setPrivacy(previous);
        toast.error(getErrorMessage(error, t));
      }
    },
    [privacy, toast, t]
  );

  // Las solicitudes pendientes se responden desde esta misma pantalla, así que
  // el contador vive acá y se baja localmente al aceptar/rechazar -- sin volver
  // a pedir todo el objeto de privacidad.
  const decrementPendingRequests = useCallback(() => {
    setPrivacy((current) =>
      current
        ? {
            ...current,
            pending_follow_requests_count: Math.max(
              0,
              current.pending_follow_requests_count - 1
            ),
          }
        : current
    );
  }, []);

  return { privacy, loading, update, decrementPendingRequests };
}
