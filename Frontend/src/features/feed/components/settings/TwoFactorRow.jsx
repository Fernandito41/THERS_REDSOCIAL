import { useEffect, useRef, useState } from "react";
import QRCode from "qrcode";
import Icon from "@shared/components/Icon";
import Spinner from "@shared/components/Spinner";
import { api, getErrorMessage } from "@shared/lib/api";
import { getStoredToken } from "@features/auth";
import { useToast } from "@shared/components/Toast";
import { useLanguage } from "@shared/i18n";

// Verificación en dos pasos con TOTP
// (GET /api/2fa, POST /api/2fa/setup, /confirm, /disable, /recovery-codes --
// ADR-022-two-factor-authentication.md).
//
// El alta tiene DOS pasos, igual que en el backend: pedir el QR no activa
// nada, y recién un código válido de la app autenticadora lo confirma. Es lo
// que evita que alguien escanee, cierre la pantalla y quede con la cuenta
// exigiendo un código que su app no puede generar (ADR-022 §Decisión).
//
// El QR se genera **en el navegador** a partir del `otpauth://` que devuelve el
// servidor: el secreto no tiene por qué pasar por un servicio de imágenes
// externo, y el backend no necesita una dependencia de generación de PNG.

function authHeaders() {
  return { Authorization: `Bearer ${getStoredToken()}` };
}

export default function TwoFactorRow() {
  const toast = useToast();
  const { t } = useLanguage();

  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  // Alta en curso: { secret, provisioning_uri }. `null` = no se está dando de alta.
  const [setup, setSetup] = useState(null);
  const [code, setCode] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  // Códigos recién generados. Es la ÚNICA vez que existen en claro, así que se
  // muestran hasta que la persona los cierre explícitamente.
  const [recoveryCodes, setRecoveryCodes] = useState(null);
  const [mode, setMode] = useState(null); // null | "disable" | "regenerate"
  const canvasRef = useRef(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const res = await api.get("/2fa", { headers: authHeaders() });
        if (!cancelled) setStatus(res.data.two_factor);
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

  // Dibuja el QR cuando hay un alta en curso. Depende del canvas, así que corre
  // después del render que lo monta.
  useEffect(() => {
    if (!setup || !canvasRef.current) return;
    QRCode.toCanvas(canvasRef.current, setup.provisioning_uri, { width: 180, margin: 1 }).catch(
      () => {
        // Si el QR no se puede dibujar, el alta sigue siendo posible con el
        // secreto en texto, que se muestra siempre debajo.
      }
    );
  }, [setup]);

  async function handleStartSetup() {
    setBusy(true);
    try {
      const res = await api.post("/2fa/setup", null, { headers: authHeaders() });
      setSetup(res.data.two_factor_setup);
      setCode("");
    } catch (error) {
      toast.error(getErrorMessage(error, t));
    } finally {
      setBusy(false);
    }
  }

  async function handleConfirm(e) {
    e.preventDefault();
    if (!code.trim() || busy) return;

    setBusy(true);
    try {
      const res = await api.post(
        "/2fa/confirm",
        { code: code.trim() },
        { headers: authHeaders() }
      );
      setRecoveryCodes(res.data.recovery_codes);
      setSetup(null);
      setCode("");
      setStatus({ enabled: true, setup_pending: false, recovery_codes_remaining: 10 });
      toast.success("Verificación en dos pasos activada");
    } catch (error) {
      // 400 = el código no coincide. El mensaje del backend ya explica qué
      // revisar (la hora del teléfono), así que se muestra tal cual.
      toast.error(getErrorMessage(error, t));
    } finally {
      setBusy(false);
    }
  }

  async function handlePasswordAction(e) {
    e.preventDefault();
    if (!password || busy) return;

    const isDisable = mode === "disable";
    setBusy(true);
    try {
      if (isDisable) {
        await api.post("/2fa/disable", { password }, { headers: authHeaders() });
        // Desactivar cierra TODAS las sesiones, incluida esta (ADR-022
        // §Decisión): el token actual ya no sirve, así que hay que volver a
        // entrar. Se avisa antes de que el próximo fetch falle con un 401.
        toast.info(
          "Verificación en dos pasos desactivada. Por seguridad se cerraron todas tus sesiones: vas a tener que iniciar sesión de nuevo."
        );
        setStatus({ enabled: false, setup_pending: false, recovery_codes_remaining: 0 });
      } else {
        const res = await api.post(
          "/2fa/recovery-codes",
          { password },
          { headers: authHeaders() }
        );
        setRecoveryCodes(res.data.recovery_codes);
        setStatus((current) => ({ ...current, recovery_codes_remaining: 10 }));
        toast.success("Códigos de recuperación nuevos generados");
      }
      setMode(null);
      setPassword("");
    } catch (error) {
      toast.error(getErrorMessage(error, t));
    } finally {
      setBusy(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center gap-2 py-4 text-th-fg-muted" role="status">
        <Spinner size={16} />
        <span className="text-body-sm">Cargando estado del 2FA...</span>
      </div>
    );
  }

  // Los códigos tapan el resto: son lo único que importa en ese momento y no se
  // pueden volver a consultar.
  if (recoveryCodes) {
    return (
      <div className="flex flex-col gap-3 py-4">
        <div className="flex flex-col gap-1">
          <span className="text-label-lg font-semibold text-th-fg-strong">
            Guardá tus códigos de recuperación
          </span>
          <p className="text-body-sm text-th-fg-muted">
            Son tu única forma de entrar si perdés el teléfono. Cada uno sirve una sola vez.{" "}
            <strong>No vamos a poder mostrártelos otra vez</strong> — guardalos en un lugar seguro
            antes de cerrar esto.
          </p>
        </div>

        <ul className="grid grid-cols-2 gap-2 rounded-th-card bg-th-surface-subtle p-3 font-mono text-body-sm text-th-fg">
          {recoveryCodes.map((recoveryCode) => (
            <li key={recoveryCode}>{recoveryCode}</li>
          ))}
        </ul>

        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={() => navigator.clipboard?.writeText(recoveryCodes.join("\n"))}
            className="inline-flex min-h-[44px] items-center gap-2 rounded-th-input border border-th-border px-4 py-2 text-label-lg font-bold text-th-fg transition-colors th-focus-ring hover:bg-th-surface-subtle"
          >
            <Icon name="content_copy" size={18} />
            Copiar
          </button>
          <button
            type="button"
            onClick={() => setRecoveryCodes(null)}
            className="min-h-[44px] rounded-th-input bg-th-brand px-4 py-2 text-label-lg font-bold text-th-on-brand transition-colors th-focus-ring hover:bg-th-brand-hover"
          >
            Ya los guardé
          </button>
        </div>
      </div>
    );
  }

  // Alta en curso: QR + secreto + confirmación.
  if (setup) {
    return (
      <form onSubmit={handleConfirm} className="flex flex-col gap-3 py-4">
        <div className="flex flex-col gap-1">
          <span className="text-label-lg font-semibold text-th-fg-strong">
            Vinculá tu app autenticadora
          </span>
          <p className="text-body-sm text-th-fg-muted">
            Escaneá este código con Google Authenticator, Authy o la app que uses. Si no podés
            escanear, cargá el código de abajo a mano.
          </p>
        </div>

        <div className="flex flex-wrap items-start gap-4">
          <canvas
            ref={canvasRef}
            aria-label="Código QR para vincular tu app autenticadora"
            className="shrink-0 rounded-th-card bg-white p-2"
          />
          <div className="flex min-w-0 flex-col gap-1">
            <span className="text-label-md font-semibold text-th-fg-strong">
              Código para carga manual
            </span>
            <code className="break-all rounded-th-input bg-th-surface-subtle px-2.5 py-1.5 font-mono text-body-sm text-th-fg">
              {setup.secret}
            </code>
          </div>
        </div>

        <div>
          <label
            htmlFor="two-factor-setup-code"
            className="mb-1.5 block text-label-md font-semibold text-th-fg-strong"
          >
            Escribí el código de 6 dígitos que muestra la app
          </label>
          <input
            id="two-factor-setup-code"
            type="text"
            inputMode="numeric"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="123456"
            maxLength={6}
            disabled={busy}
            className="min-h-[44px] w-40 rounded-th-input border border-th-border bg-th-surface px-3.5 py-2 text-center font-mono text-body-lg tracking-widest text-th-fg th-focus-ring disabled:opacity-60"
          />
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            type="submit"
            disabled={!code.trim() || busy}
            className="inline-flex min-h-[44px] items-center gap-2 rounded-th-input bg-th-brand px-4 py-2 text-label-lg font-bold text-th-on-brand transition-colors th-focus-ring hover:bg-th-brand-hover disabled:opacity-40"
          >
            {busy && <Spinner size={16} />}
            Activar
          </button>
          <button
            type="button"
            onClick={() => setSetup(null)}
            disabled={busy}
            className="min-h-[44px] rounded-th-input px-4 py-2 text-label-lg text-th-fg-muted transition-colors th-focus-ring hover:bg-th-surface-subtle disabled:opacity-40"
          >
            Cancelar
          </button>
        </div>
      </form>
    );
  }

  // Confirmación con contraseña (desactivar o regenerar códigos).
  if (mode) {
    return (
      <form onSubmit={handlePasswordAction} className="flex flex-col gap-3 py-4">
        <div className="flex flex-col gap-1">
          <span className="text-label-lg font-semibold text-th-fg-strong">
            {mode === "disable"
              ? "Confirmá con tu contraseña para desactivar el 2FA"
              : "Confirmá con tu contraseña para generar códigos nuevos"}
          </span>
          <p className="text-body-sm text-th-fg-muted">
            {mode === "disable"
              ? "Se van a borrar tus códigos de recuperación y se cerrarán todas tus sesiones, incluida esta."
              : "Los códigos que tengas anotados dejarán de servir en cuanto generes los nuevos."}
          </p>
        </div>

        <input
          type="password"
          autoComplete="current-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Tu contraseña"
          disabled={busy}
          className="min-h-[44px] max-w-xs rounded-th-input border border-th-border bg-th-surface px-3.5 py-2 text-body-sm text-th-fg th-focus-ring disabled:opacity-60"
        />

        <div className="flex flex-wrap items-center gap-2">
          <button
            type="submit"
            disabled={!password || busy}
            className={`inline-flex min-h-[44px] items-center gap-2 rounded-th-input px-4 py-2 text-label-lg font-bold transition-colors th-focus-ring disabled:opacity-40 ${
              mode === "disable"
                ? "bg-th-danger-accent text-white hover:opacity-90"
                : "bg-th-brand text-th-on-brand hover:bg-th-brand-hover"
            }`}
          >
            {busy && <Spinner size={16} />}
            {mode === "disable" ? "Desactivar" : "Generar"}
          </button>
          <button
            type="button"
            onClick={() => {
              setMode(null);
              setPassword("");
            }}
            disabled={busy}
            className="min-h-[44px] rounded-th-input px-4 py-2 text-label-lg text-th-fg-muted transition-colors th-focus-ring hover:bg-th-surface-subtle disabled:opacity-40"
          >
            Cancelar
          </button>
        </div>
      </form>
    );
  }

  // Estado base.
  return (
    <div className="flex flex-wrap items-start justify-between gap-4 py-4">
      <div className="flex min-w-0 flex-1 flex-col gap-1">
        <span className="text-label-lg font-semibold text-th-fg-strong">
          Autenticación en dos pasos (2FA)
        </span>
        <p className="text-body-sm text-th-fg-muted">
          Un segundo factor además de la contraseña al iniciar sesión, con una app autenticadora
          (Google Authenticator, Authy u otra).
        </p>
        {status?.enabled ? (
          <p className="text-body-sm text-th-fg-muted">
            <strong className="text-th-fg-strong">Activada.</strong> Te quedan{" "}
            {status.recovery_codes_remaining} códigos de recuperación.
          </p>
        ) : status?.setup_pending ? (
          <p className="text-body-sm text-th-fg-muted">
            Dejaste una configuración a medias. Volvé a empezar para obtener un código QR nuevo.
          </p>
        ) : null}
        <p className="text-body-sm text-th-fg-subtle">Se aplica en el servidor.</p>
      </div>

      <div className="flex shrink-0 flex-wrap items-center gap-2">
        {status?.enabled ? (
          <>
            <button
              type="button"
              onClick={() => setMode("regenerate")}
              className="min-h-[44px] rounded-th-input border border-th-border px-4 py-2 text-label-lg font-bold text-th-fg transition-colors th-focus-ring hover:bg-th-surface-subtle"
            >
              Códigos nuevos
            </button>
            <button
              type="button"
              onClick={() => setMode("disable")}
              className="min-h-[44px] rounded-th-input px-4 py-2 text-label-lg font-bold text-th-danger-accent transition-colors th-focus-ring hover:bg-th-danger-surface"
            >
              Desactivar
            </button>
          </>
        ) : (
          <button
            type="button"
            onClick={handleStartSetup}
            disabled={busy}
            className="inline-flex min-h-[44px] items-center gap-2 rounded-th-input bg-th-brand px-4 py-2 text-label-lg font-bold text-th-on-brand transition-colors th-focus-ring hover:bg-th-brand-hover disabled:opacity-40"
          >
            {busy && <Spinner size={16} />}
            {status?.setup_pending ? "Volver a configurar" : "Activar 2FA"}
          </button>
        )}
      </div>
    </div>
  );
}
