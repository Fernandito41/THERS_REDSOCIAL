import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import ConfirmDialog from "@shared/components/ConfirmDialog";
import Spinner from "@shared/components/Spinner";
import { api, getErrorMessage } from "@shared/lib/api";
import { useLanguage } from "@shared/i18n";
import { useAuth } from "@features/auth";

// Eliminación de cuenta (ADR-031-account-deletion.md). Página PÚBLICA a
// propósito: es el recurso web que Google Play exige para pedir la eliminación
// sin tener la app instalada, y también el camino de quien olvidó su contraseña.
// Con sesión abierta el correo viene precargado; el endpoint no cambia.
//
// Flujo (decisiones del equipo, ADR-031 §Decisiones del equipo):
//  1. Pedir un código al correo de la cuenta.
//  2. Introducir el código (y el de 2FA si la cuenta lo tiene).
//  3. Escribir el correo y la palabra DELETE a mano -- fricción deliberada.
//  4. Pulsar «Eliminar cuenta» y confirmar una última advertencia.
//
// La validación real es del servidor; las comprobaciones de aquí solo evitan
// pedir al servidor algo que ya se sabe incompleto.

const CONFIRM_WORD = "DELETE";
const RESEND_COOLDOWN_SECONDS = 60;

const inputClass =
  "w-full rounded-lg border border-line dark:border-line-dark bg-surface dark:bg-surface-dark " +
  "px-3 py-2.5 text-sm text-ink dark:text-ink-dark placeholder:text-muted dark:placeholder:text-muted-dark " +
  "focus:outline-none focus:ring-2 focus:ring-pulse-500";

function Field({ id, label, hint, children }) {
  return (
    <div>
      <label htmlFor={id} className="block text-sm font-semibold text-ink dark:text-ink-dark">
        {label}
      </label>
      {hint && <p className="mt-0.5 text-xs text-muted dark:text-muted-dark">{hint}</p>}
      <div className="mt-1.5">{children}</div>
    </div>
  );
}

export default function DeleteAccount() {
  const { t } = useLanguage();
  const { user, logout } = useAuth();

  const [step, setStep] = useState("email"); // email | confirm | done
  const [email, setEmail] = useState(user?.email ?? "");
  const [code, setCode] = useState("");
  const [confirmEmail, setConfirmEmail] = useState("");
  const [word, setWord] = useState("");
  const [twoFactorCode, setTwoFactorCode] = useState("");
  const [needsTwoFactor, setNeedsTwoFactor] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [askFinal, setAskFinal] = useState(false);
  const [cooldown, setCooldown] = useState(0);

  // Si la sesión carga después del primer render, se precarga el correo.
  useEffect(() => {
    if (user?.email && !email) setEmail(user.email);
  }, [user, email]);

  useEffect(() => {
    if (cooldown <= 0) return undefined;
    const timer = setTimeout(() => setCooldown((value) => value - 1), 1000);
    return () => clearTimeout(timer);
  }, [cooldown]);

  const requestCode = async (event) => {
    event?.preventDefault();
    setError("");
    if (!email.trim()) {
      setError("Escribe el correo de tu cuenta.");
      return;
    }
    setBusy(true);
    try {
      await api.post("/account-deletion/request", { email: email.trim() });
      setStep("confirm");
      setCooldown(RESEND_COOLDOWN_SECONDS);
    } catch (err) {
      setError(getErrorMessage(err, t));
    } finally {
      setBusy(false);
    }
  };

  const typedEmailMatches = confirmEmail.trim().toLowerCase() === email.trim().toLowerCase();
  const canSubmit =
    code.trim().length === 6 &&
    typedEmailMatches &&
    word === CONFIRM_WORD &&
    (!needsTwoFactor || twoFactorCode.trim().length > 0);

  const submit = (event) => {
    event.preventDefault();
    setError("");
    if (canSubmit) setAskFinal(true);
  };

  const deleteAccount = async () => {
    setAskFinal(false);
    setBusy(true);
    setError("");
    try {
      await api.post("/account-deletion/confirm", {
        email: email.trim(),
        code: code.trim(),
        confirm_email: confirmEmail.trim(),
        confirmation: word,
        ...(needsTwoFactor ? { two_factor_code: twoFactorCode.trim() } : {}),
      });
      // La sesión ya no existe en el servidor: se limpia también la copia local.
      logout();
      setStep("done");
    } catch (err) {
      const data = err.response?.data;
      if (err.response?.status === 403 && data?.two_factor_required) {
        setNeedsTwoFactor(true);
        setError(data.msg);
      } else {
        setError(getErrorMessage(err, t));
      }
    } finally {
      setBusy(false);
    }
  };

  if (step === "done") {
    return (
      <div className="max-w-xl mx-auto px-4 sm:px-6 py-16 sm:py-24">
        <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-ink dark:text-ink-dark">
          Tu cuenta fue eliminada
        </h1>
        <p className="mt-4 text-muted dark:text-muted-dark">
          Eliminamos tu perfil y los datos asociados. Te enviamos un correo de confirmación.
          Gracias por haber estado en THERS.
        </p>
        <Link
          to="/"
          className="mt-8 inline-flex text-sm font-semibold px-4 py-2 rounded-full bg-pulse-600 hover:bg-pulse-700 text-white transition"
        >
          Ir al inicio
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-xl mx-auto px-4 sm:px-6 py-16 sm:py-24">
      <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-ink dark:text-ink-dark">
        Eliminar tu cuenta de THERS
      </h1>
      <p className="mt-4 text-muted dark:text-muted-dark">
        Aquí puedes pedir la eliminación de tu cuenta y de sus datos, sin necesidad de tener la
        app instalada. <strong className="text-ink dark:text-ink-dark">Es definitiva: no se puede
        deshacer.</strong>
      </p>

      <div className="mt-6 rounded-lg border border-line dark:border-line-dark p-4 text-sm text-muted dark:text-muted-dark">
        <p className="font-semibold text-ink dark:text-ink-dark">Qué se elimina</p>
        <p className="mt-1">
          Tu perfil, tus publicaciones, comentarios, me gusta, seguidores y seguidos, tus
          notificaciones, tus mensajes (enviados y recibidos, en las dos bandejas), tus sesiones y
          tus imágenes de perfil y portada. Las personas con las que hablabas dejarán de
          encontrarte («Usuario no encontrado»).
        </p>
        <p className="mt-3 font-semibold text-ink dark:text-ink-dark">Qué puede quedar</p>
        <p className="mt-1">
          Las copias de seguridad de nuestro proveedor de base de datos y los registros del
          servidor pueden conservar datos durante un tiempo limitado hasta que caduquen. El plazo
          exacto se indicará en la Política de Privacidad{" "}
          <span className="font-semibold">[pendiente de publicar]</span>.
        </p>
      </div>

      {step === "email" && (
        <form onSubmit={requestCode} className="mt-8 space-y-5" noValidate>
          <Field
            id="del-email"
            label="Correo de tu cuenta"
            hint="Te enviaremos un código de confirmación a esta dirección."
          >
            <input
              id="del-email"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className={inputClass}
            />
          </Field>

          {error && (
            <p role="alert" className="text-sm text-ember-500">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={busy}
            className="inline-flex items-center gap-2 text-sm font-semibold px-5 py-2.5 rounded-full bg-pulse-600 hover:bg-pulse-700 text-white transition disabled:opacity-60"
          >
            {busy && <Spinner />}
            Enviar código
          </button>
        </form>
      )}

      {step === "confirm" && (
        <form onSubmit={submit} className="mt-8 space-y-5" noValidate>
          <p className="text-sm text-muted dark:text-muted-dark" role="status">
            Si existe una cuenta con <strong className="text-ink dark:text-ink-dark">{email}</strong>,
            te enviamos un código. Vence en 10 minutos.
          </p>

          <Field id="del-code" label="Código de 6 dígitos">
            <input
              id="del-code"
              inputMode="numeric"
              autoComplete="one-time-code"
              maxLength={6}
              value={code}
              onChange={(event) => setCode(event.target.value.replace(/\D/g, ""))}
              className={inputClass}
            />
          </Field>

          {needsTwoFactor && (
            <Field
              id="del-2fa"
              label="Código de verificación en dos pasos"
              hint="El de tu app autenticadora, o un código de recuperación."
            >
              <input
                id="del-2fa"
                autoComplete="one-time-code"
                value={twoFactorCode}
                onChange={(event) => setTwoFactorCode(event.target.value)}
                className={inputClass}
              />
            </Field>
          )}

          <Field
            id="del-confirm-email"
            label="Escribe tu correo para confirmar"
            hint="Debe coincidir con el correo de la cuenta."
          >
            <input
              id="del-confirm-email"
              type="email"
              autoComplete="off"
              value={confirmEmail}
              onChange={(event) => setConfirmEmail(event.target.value)}
              className={inputClass}
            />
          </Field>

          <Field
            id="del-word"
            label={`Escribe ${CONFIRM_WORD} para continuar`}
            hint="En mayúsculas, tal como se muestra."
          >
            <input
              id="del-word"
              autoComplete="off"
              autoCapitalize="characters"
              value={word}
              onChange={(event) => setWord(event.target.value)}
              className={inputClass}
            />
          </Field>

          {error && (
            <p role="alert" className="text-sm text-ember-500">
              {error}
            </p>
          )}

          <div className="flex flex-wrap items-center gap-3">
            <button
              type="submit"
              disabled={!canSubmit || busy}
              className={`inline-flex items-center gap-2 text-sm font-semibold px-5 py-2.5 rounded-full transition ${
                canSubmit && !busy
                  ? "bg-ember-500 hover:bg-ember-600 text-white"
                  : "bg-line dark:bg-line-dark text-muted dark:text-muted-dark cursor-not-allowed"
              }`}
            >
              {busy && <Spinner />}
              Eliminar cuenta
            </button>
            <button
              type="button"
              onClick={requestCode}
              disabled={busy || cooldown > 0}
              className="text-sm text-pulse-600 dark:text-pulse-300 hover:underline disabled:opacity-60 disabled:no-underline"
            >
              {cooldown > 0 ? `Reenviar código (${cooldown} s)` : "Reenviar código"}
            </button>
          </div>
        </form>
      )}

      <ConfirmDialog
        open={askFinal}
        destructive
        title="Última advertencia"
        description="Vas a eliminar tu cuenta de THERS y sus datos de forma definitiva. No podremos recuperarla. ¿Estás totalmente seguro?"
        confirmLabel="Sí, eliminar mi cuenta"
        cancelLabel="No, volver"
        onConfirm={deleteAccount}
        onCancel={() => setAskFinal(false)}
      />
    </div>
  );
}
