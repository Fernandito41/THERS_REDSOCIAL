import { useCallback, useEffect, useState } from "react";
import { api, getErrorMessage } from "@shared/lib/api";
import { getStoredToken } from "@features/auth";
import { useToast } from "@shared/components/Toast";
import { useLanguage } from "@shared/i18n";

// Preferencias de seguridad REALES, contra el servidor
// (GET/PATCH /api/users/me/security -- ADR-025-session-registry.md).
//
// Endpoint separado del de privacidad a propósito, igual que en el backend:
// privacidad es "quién ve qué", seguridad es "quién puede entrar". Comparten
// pantalla de Configuración pero no dominio.
//
// Mismo patrón que usePrivacySettings: actualización optimista con rollback, y
// NADA en localStorage -- estas preferencias se aplican en el servidor, así que
// guardarlas localmente sería afirmar una protección que el servidor no conoce.

function authHeaders() {
  return { Authorization: `Bearer ${getStoredToken()}` };
}

export function useSecuritySettings() {
  const toast = useToast();
  const { t } = useLanguage();

  const [security, setSecurity] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const res = await api.get("/users/me/security", { headers: authHeaders() });
        if (!cancelled) setSecurity(res.data.security);
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
      const previous = security;
      setSecurity((current) => ({ ...current, [field]: value }));

      try {
        const res = await api.patch(
          "/users/me/security",
          { [field]: value },
          { headers: authHeaders() }
        );
        setSecurity(res.data.security);
      } catch (error) {
        setSecurity(previous);
        toast.error(getErrorMessage(error, t));
      }
    },
    [security, toast, t]
  );

  return { security, loading, update };
}
