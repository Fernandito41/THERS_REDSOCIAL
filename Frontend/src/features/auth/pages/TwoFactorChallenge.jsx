import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { IoInformationCircleOutline, IoKeyOutline } from "react-icons/io5";
import { useToast } from "@shared/components/Toast";
import { useLanguage } from "@shared/i18n";
import Spinner from "@shared/components/Spinner";
import { getErrorMessage } from "@shared/lib/api";
import AuthCard from "../components/AuthCard";
import { useAuth } from "../context/AuthContext";

// Segundo paso del login cuando la cuenta tiene 2FA
// (POST /api/2fa/verify, ADR-022-two-factor-authentication.md).
//
// El `two_factor_token` llega por router state desde Login.jsx / AuthPage.jsx /
// Register.jsx (los tres caminos que pueden iniciar un login). **No se guarda en
// localStorage a propósito**: no es una sesión, vive cinco minutos y no sirve
// para ningún endpoint protegido. Si se pierde (F5, navegación directa a esta
// URL), el único camino correcto es volver a iniciar sesión -- no hay nada que
// recuperar.
//
// No se usa OtpCodeInput (el de seis casillas de ADR-010/ADR-011) porque este
// campo acepta DOS formatos: un TOTP de 6 dígitos o un código de recuperación
// de 11 caracteres con guion. Un input de longitud fija dejaría fuera el
// segundo, que es justamente el que se usa cuando alguien perdió el teléfono.
export default function TwoFactorChallenge() {
  const navigate = useNavigate();
  const location = useLocation();
  const toast = useToast();
  const { t } = useLanguage();
  const { verifyTwoFactor } = useAuth();

  const twoFactorToken = location.state?.twoFactorToken;

  const [code, setCode] = useState("");
  const [isSubmitting, setSubmitting] = useState(false);

  if (!twoFactorToken) {
    return (
      <AuthCard title="Verificación en dos pasos">
        <div className="flex items-start gap-3 rounded-2xl border border-line dark:border-line-dark bg-canvas dark:bg-canvas-dark p-4">
          <IoInformationCircleOutline className="mt-0.5 shrink-0 text-muted" size={20} />
          <p className="text-sm text-muted">
            Esta verificación caducó o se abrió directamente. Volvé a iniciar sesión para recibir
            un código nuevo.
          </p>
        </div>
        <Link
          to="/login"
          className="mt-4 block w-full rounded-full bg-pulse-600 py-3 text-center text-sm font-bold text-white transition hover:bg-pulse-700"
        >
          Volver a iniciar sesión
        </Link>
      </AuthCard>
    );
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    const value = code.trim();
    if (!value || isSubmitting) return;

    setSubmitting(true);
    try {
      const result = await verifyTwoFactor(twoFactorToken, value);

      if (result.usedRecoveryCode) {
        // Avisar es importante: un código de recuperación se gasta, y si nadie
        // lo dice la persona se queda sin ellos sin enterarse.
        toast.info(
          `Entraste con un código de recuperación. Te quedan ${result.recoveryCodesRemaining}. ` +
            "Podés generar códigos nuevos en Configuración › Seguridad."
        );
      }

      navigate(result.user.profile_completed ? "/feed" : "/complete-profile");
    } catch (error) {
      if (error.response?.status === 401) {
        // El backend no distingue "TOTP incorrecto" de "código de recuperación
        // inválido o ya usado" a propósito (ADR-022 §Seguridad), así que acá
        // tampoco se adivina cuál de los dos falló.
        toast.error("El código no es válido. Revisá que la hora de tu teléfono esté bien.");
        setCode("");
        return;
      }
      console.error(error);
      toast.error(getErrorMessage(error, t));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AuthCard title="Verificación en dos pasos">
      <p className="mb-5 text-sm text-muted">
        Abrí tu app autenticadora y escribí el código de 6 dígitos. También podés usar uno de tus
        códigos de recuperación.
      </p>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div>
          <label
            htmlFor="two-factor-code"
            className="mb-1.5 block text-xs font-semibold text-ink dark:text-ink-dark"
          >
            Código
          </label>
          <input
            id="two-factor-code"
            type="text"
            inputMode="text"
            autoComplete="one-time-code"
            autoFocus
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="123456  o  ABCDE-FGHJK"
            maxLength={20}
            disabled={isSubmitting}
            className="w-full rounded-2xl border border-line dark:border-line-dark bg-canvas dark:bg-canvas-dark px-4 py-3 text-center font-mono text-lg tracking-widest text-ink dark:text-ink-dark placeholder:text-sm placeholder:tracking-normal placeholder-muted focus:outline-none focus:ring-2 focus:ring-pulse-500 disabled:opacity-60"
          />
        </div>

        <button
          type="submit"
          disabled={!code.trim() || isSubmitting}
          className="flex w-full items-center justify-center gap-2 rounded-full bg-pulse-600 py-3 text-sm font-bold text-white transition hover:bg-pulse-700 disabled:opacity-50"
        >
          {isSubmitting ? <Spinner size={16} /> : <IoKeyOutline size={16} />}
          Verificar
        </button>
      </form>

      <Link
        to="/login"
        className="mt-5 block text-center text-xs font-semibold text-muted hover:text-ink dark:hover:text-ink-dark"
      >
        Cancelar y volver a iniciar sesión
      </Link>
    </AuthCard>
  );
}
