import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "@features/auth";
import { getErrorMessage } from "@shared/lib/api";
import { useToast } from "@shared/components/Toast";
import { useLanguage } from "@shared/i18n";
import Spinner from "@shared/components/Spinner";
import AuthCard from "../components/AuthCard";
import GoogleSignInButton from "../components/GoogleSignInButton";
import TextField from "../components/TextField";
import PasswordField from "../components/PasswordField";
import { isValidEmail } from "../lib/validators";

export default function Login() {
  const navigate = useNavigate();
  const { login, loginWithGoogle } = useAuth();
  const toast = useToast();
  const { t } = useLanguage();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isGoogleSubmitting, setIsGoogleSubmitting] = useState(false);

  // "Continuar con Google" (ADR-012-google-sign-in.md, FASE 16) -- mismo
  // criterio de manejo de errores que handleSubmit: red/backend caído
  // (getErrorMessage genérico), credencial rechazada o email de Google sin
  // verificar (400, con `data.msg` propio de cada caso ya distinguido por
  // el backend). `profile_completed` decide a dónde navegar en éxito --
  // mismo patrón que el `email_verified` de handleSubmit.
  const handleGoogleCredential = async (credential) => {
    if (isGoogleSubmitting) return;
    setIsGoogleSubmitting(true);
    try {
      const result = await loginWithGoogle(credential);
      if (result.twoFactorRequired) {
        // La cuenta tiene 2FA: Google autenticó la identidad pero falta el
        // segundo factor (ADR-026 §Seguridad).
        navigate("/two-factor", { state: { twoFactorToken: result.twoFactorToken } });
        return;
      }
      navigate(result.user.profile_completed ? "/feed" : "/complete-profile");
    } catch (error) {
      console.error(error);
      toast.error(getErrorMessage(error, t), { title: t("auth.login.toastErrorTitle") });
    } finally {
      setIsGoogleSubmitting(false);
    }
  };

  const validate = () => {
    const next = {};
    if (!email.trim()) next.email = t("auth.login.errorEmailRequired");
    else if (!isValidEmail(email)) next.email = t("auth.login.errorEmailInvalid");
    if (!password) next.password = t("auth.login.errorPasswordRequired");
    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (isSubmitting || !validate()) return;

    setIsSubmitting(true);
    try {
      // .trim() solo en email (mismo motivo que en backend/auth_routes.py) --
      // la contraseña nunca se normaliza, se envía tal cual la escribió el usuario.
      const result = await login({ email: email.trim(), password });
      if (result.twoFactorRequired) {
        // 200 con `two_factor_required`: nada falló, falta el segundo paso
        // (ADR-026 §Contrato API). Todavía no hay sesión guardada.
        navigate("/two-factor", { state: { twoFactorToken: result.twoFactorToken } });
        return;
      }
      navigate("/feed");
    } catch (error) {
      // Credenciales correctas pero cuenta todavía sin verificar
      // (ADR-011-mandatory-email-verification.md §Decisión) -- nunca se
      // emitió un JWT para este caso (login_use_case.py nunca llega a
      // create_access_token()). En vez del toast de error genérico, se
      // avisa y se lleva a la pantalla que pide el código de verificación,
      // igual que si acabara de registrarse.
      if (error.response?.status === 403 && error.response?.data?.email_verified === false) {
        toast.info(t("auth.login.emailNotVerified"));
        navigate("/verify-registration-code", { state: { email: email.trim() } });
        return;
      }
      console.error(error);
      toast.error(getErrorMessage(error, t), { title: t("auth.login.toastErrorTitle") });
    } finally {
      setIsSubmitting(false);
    }
  };

  const isValid = email.trim() && password;

  return (
    <AuthCard
      title={
        <>
          {t("auth.login.titlePrefix")} <span className="font-bold">Thers</span>
        </>
      }
      subtitle={t("auth.login.subtitle")}
    >
      {/* GOOGLE LOGIN -- ADR-012-google-sign-in.md, botón real */}
      <GoogleSignInButton onCredential={handleGoogleCredential} disabled={isGoogleSubmitting} />

      {/* DIVISOR */}
      <div className="flex items-center my-6">
        <div className="flex-1 h-px bg-line-dark"></div>
        <span className="px-3 text-muted-dark text-sm">{t("auth.or")}</span>
        <div className="flex-1 h-px bg-line-dark"></div>
      </div>

      {/* FORM */}
      <form onSubmit={handleSubmit} className="space-y-4" noValidate>
        <TextField
          label={t("auth.login.emailLabel")}
          type="email"
          placeholder={t("auth.login.emailPlaceholder")}
          autoComplete="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          error={errors.email}
        />

        <PasswordField
          label={t("auth.login.passwordLabel")}
          placeholder={t("auth.login.passwordPlaceholder")}
          autoComplete="current-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          error={errors.password}
        />

        <button
          type="submit"
          disabled={!isValid || isSubmitting}
          className={`w-full py-3 rounded-full font-semibold transition flex items-center justify-center gap-2 ${
            isValid && !isSubmitting
              ? "bg-pulse-600 hover:bg-pulse-700 text-white"
              : "bg-line-dark text-muted-dark cursor-not-allowed"
          }`}
        >
          {isSubmitting && <Spinner />}
          {isSubmitting ? t("auth.login.submitting") : t("auth.login.submit")}
        </button>
      </form>

      {/* LINKS */}
      <div className="text-center mt-6 space-y-3">
        <Link to="/forgot-password" className="text-sm text-pulse-400 hover:underline">
          {t("auth.login.forgotPassword")}
        </Link>

        <div className="mt-6">
          <p className="text-sm text-muted-dark text-center mb-3">{t("auth.login.noAccount")}</p>

          <button
            onClick={() => navigate("/register")}
            className="w-full border border-line-dark text-ink-dark py-3 rounded-full font-semibold hover:bg-line-dark transition"
          >
            {t("auth.login.createAccount")}
          </button>
        </div>
      </div>
    </AuthCard>
  );
}
