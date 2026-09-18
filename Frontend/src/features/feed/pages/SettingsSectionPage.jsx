import { useCallback, useEffect, useState } from "react";
import { Link, useOutletContext, useParams } from "react-router-dom";
import Icon from "@shared/components/Icon";
import { useToast } from "@shared/components/Toast";
import { useLanguage } from "@shared/i18n";
import { api, getErrorMessage } from "@shared/lib/api";
import { getStoredToken } from "@features/auth";
import { SETTINGS_CONTENT } from "../data/settingsSections";
import { loadSettings, saveSetting } from "../lib/settingsStorage";
import {
  ActionRow,
  ChoiceRow,
  InfoRow,
  PendingRow,
  ScopeNotice,
  SectionHeader,
  SettingGroup,
  SwitchRow,
} from "../components/settings/SettingsPrimitives";

/**
 * Renderiza una de las 12 secciones de Configuración a partir de su
 * descripción en `data/settingsSections.js`.
 *
 * Un único renderizador en vez de doce componentes casi idénticos: las
 * secciones se diferencian por contenido, no por maquetado (archivo maestro
 * §6, principio de reutilización).
 *
 * Filas con comportamiento REAL:
 *  · `passwordReset`     -> POST /api/forgot-password (ADR-009)
 *  · `emailVerification` -> POST /api/send-verification-email (ADR-009) +
 *                           `email_verified` de la sesión
 *  · `profileLink`       -> enlace a la edición de perfil ya existente
 *  · `switch` / `choice` -> preferencia guardada en este navegador
 */
export default function SettingsSectionPage() {
  const { section } = useParams();
  const { currentUser } = useOutletContext();
  const content = SETTINGS_CONTENT[section];

  const [prefs, setPrefs] = useState(() => loadSettings(currentUser.username));

  useEffect(() => {
    setPrefs(loadSettings(currentUser.username));
  }, [currentUser.username]);

  const setPref = useCallback(
    (key, value) => {
      setPrefs((previous) => ({ ...previous, [key]: value }));
      saveSetting(currentUser.username, key, value);
    },
    [currentUser.username]
  );

  if (!content) {
    return (
      <div className="flex flex-col items-center gap-2 rounded-th-card border border-dashed border-th-border bg-th-surface px-6 py-16 text-center">
        <Icon name="search_off" size={28} className="text-th-fg-subtle" />
        <p className="text-label-lg font-bold text-th-fg-strong">Sección no encontrada</p>
        <Link to="/settings" className="text-label-lg font-bold text-th-brand-fg hover:underline">
          Volver a Configuración
        </Link>
      </div>
    );
  }

  return (
    <>
      <SectionHeader title={content.title} description={content.description} />

      {content.notice && (
        <ScopeNotice tone={content.notice.tone}>{content.notice.text}</ScopeNotice>
      )}

      {content.groups.map((group) => (
        <SettingGroup
          key={group.title}
          title={group.title}
          description={group.description}
          index={group.index}
        >
          {group.rows.map((row, rowIndex) => (
            <SettingRowRenderer
              key={row.key || row.label || `${group.title}-${rowIndex}`}
              row={row}
              prefs={prefs}
              setPref={setPref}
              currentUser={currentUser}
            />
          ))}
        </SettingGroup>
      ))}
    </>
  );
}

function SettingRowRenderer({ row, prefs, setPref, currentUser }) {
  switch (row.type) {
    case "switch":
      return (
        <SwitchRow
          label={row.label}
          description={row.description}
          checked={prefs[row.key] ?? row.default ?? false}
          onChange={(value) => setPref(row.key, value)}
        />
      );

    case "choice":
      return (
        <ChoiceRow
          id={`setting-${row.key}`}
          label={row.label}
          description={row.description}
          value={prefs[row.key] ?? row.default ?? row.options[0]}
          options={row.options}
          onChange={(value) => setPref(row.key, value)}
        />
      );

    case "info":
      return <InfoRow label={row.label} description={row.description} value={row.value} />;

    case "profileLink":
      return <ProfileLinkRow currentUser={currentUser} />;

    case "passwordReset":
      return <PasswordResetRow currentUser={currentUser} />;

    case "emailVerification":
      return <EmailVerificationRow currentUser={currentUser} />;

    case "pending":
    default:
      return (
        <PendingRow
          label={row.label}
          description={row.description}
          action={row.action}
          reason={row.reason}
        />
      );
  }
}

/** Los campos de identidad se editan en el perfil, que ya tiene su formulario. */
function ProfileLinkRow({ currentUser }) {
  return (
    <div className="flex flex-wrap items-start justify-between gap-4 py-4 first:pt-0 last:pb-0">
      <div className="flex min-w-0 flex-1 flex-col gap-1">
        <span className="text-label-lg font-semibold text-th-fg-strong">
          {currentUser.name} · @{currentUser.username}
        </span>
        <p className="text-body-sm text-th-fg-muted">
          Nombre y usuario se guardan en el servidor. Biografía, ubicación, enlace y portada se
          guardan en este navegador.
        </p>
      </div>
      <Link
        to="/profile"
        className="min-h-[44px] shrink-0 rounded-th-input bg-th-brand px-4 py-2.5 text-label-lg font-bold text-th-on-brand transition-colors th-focus-ring hover:bg-th-brand-hover"
      >
        Editar perfil
      </Link>
    </div>
  );
}

/** POST /api/forgot-password — flujo real (ADR-009). */
function PasswordResetRow({ currentUser }) {
  const toast = useToast();
  const { t } = useLanguage();
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  async function handleRequest() {
    setLoading(true);
    try {
      await api.post("/forgot-password", { email: currentUser.email });
      setSent(true);
      // El contrato usa un mensaje neutro a propósito: no revela si el correo
      // está registrado (archivo maestro §10.1). No se afirma "correo enviado".
      toast.success("Si la dirección está registrada, recibirás instrucciones.");
    } catch (error) {
      toast.error(getErrorMessage(error, t));
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <ActionRow
        label="Cambiar contraseña"
        description="Te enviamos un enlace de restablecimiento a la dirección de tu cuenta."
        action={sent ? "Volver a enviar" : "Enviar enlace"}
        onAction={handleRequest}
        loading={loading}
        variant="primary"
      />
      {sent && (
        <p className="pb-4 text-body-sm text-th-fg-muted">
          El envío real de correo depende de que `RESEND_API_KEY` esté configurada en el servidor;
          sin ella el backend registra el intento pero no manda nada.
        </p>
      )}
    </>
  );
}

/** POST /api/send-verification-email + `email_verified` real de la sesión (ADR-009). */
function EmailVerificationRow({ currentUser }) {
  const toast = useToast();
  const { t } = useLanguage();
  const [loading, setLoading] = useState(false);

  async function handleSend() {
    setLoading(true);
    try {
      await api.post("/send-verification-email", null, {
        headers: { Authorization: `Bearer ${getStoredToken()}` },
      });
      toast.success("Si hace falta verificar, recibirás un correo con el enlace.");
    } catch (error) {
      toast.error(getErrorMessage(error, t));
    } finally {
      setLoading(false);
    }
  }

  if (currentUser.email_verified) {
    return (
      <InfoRow
        label="Correo verificado"
        description="Tu dirección ya está confirmada."
        value="Verificado"
      />
    );
  }

  return (
    <ActionRow
      label="Verificar correo"
      description="Tu dirección todavía no está confirmada."
      action="Enviar verificación"
      onAction={handleSend}
      loading={loading}
    />
  );
}
