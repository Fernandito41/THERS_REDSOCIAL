import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { IoInformationCircleOutline } from "react-icons/io5";
import { useToast } from "@shared/components/Toast";
import { useLanguage } from "@shared/i18n";
import Spinner from "@shared/components/Spinner";
import { api, getErrorMessage } from "@shared/lib/api";
import AuthCard from "../components/AuthCard";
import PasswordField from "../components/PasswordField";
import PasswordStrength from "../components/PasswordStrength";

// POST /api/reset-password (ADR-010-password-reset-otp-flow.md,
// API_CONTRACT.md §4.8, reemplaza el flujo de enlace de
// ADR-009-password-reset-and-email-verification.md) -- endpoint público,
// sin JWT: la identidad la aporta la autorización temporal, no una sesión
// iniciada en este navegador. Esa autorización llega por router state desde
// VerifyResetCode.jsx (nunca por la URL, a diferencia del ?token= anterior)
// -- si falta (navegación directa a esta URL, o F5, que descarta el state
// de React Router), no hay forma de continuar: se ofrece volver a pedir un
// código nuevo. Los errores (autorización inválida/expirada/ya usada,
// contraseñas que no coinciden, contraseña demasiado corta) llegan todos
// como 400 con el mismo formato {"msg": "..."} que el resto de la API --
// getErrorMessage() ya sabe mostrar ese mensaje tal cual (shared/lib/api.js).
export default function ResetPassword() {
  const navigate = useNavigate();
  const location = useLocation();
  const resetAuthorization = location.state?.resetAuthorization;
  const toast = useToast();
  const { t } = useLanguage();

  const [form, setForm] = useState({ password: "", confirmPassword: "" });
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const validate = () => {
    const next = {};
    if (!form.password) next.password = t("auth.resetPassword.errorPasswordRequired");
    else if (form.password.length < 8) next.password = t("auth.resetPassword.errorPasswordTooShort");
    if (form.confirmPassword !== form.password)
      next.confirmPassword = t("auth.resetPassword.errorConfirmPasswordMismatch");
    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (isSubmitting || !resetAuthorization || !validate()) return;

    setIsSubmitting(true);

    try {
      // Whitelist explícita de lo que se envía -- mismo criterio que el
      // resto de llamadas a `api` en este proyecto (nunca se manda el
      // objeto `form` completo tal cual, aunque hoy coincida 1:1).
      await api.post("/reset-password", {
        reset_authorization: resetAuthorization,
        password: form.password,
        confirm_password: form.confirmPassword,
      });
      setSuccess(true);
    } catch (error) {
      toast.error(getErrorMessage(error, t));
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!resetAuthorization) {
    return (
      <AuthCard title={t("auth.resetPassword.invalidLinkTitle")} subtitle={t("auth.resetPassword.invalidLinkSubtitle")}>
        <p
          role="alert"
          className="flex items-start gap-1.5 text-sm text-muted-dark bg-black/30 rounded-lg px-3 py-3"
        >
          <IoInformationCircleOutline size={18} className="shrink-0 mt-0.5 text-pulse-400" />
          {t("auth.resetPassword.invalidLinkNotice")}
        </p>

        <Link
          to="/forgot-password"
          className="w-full mt-4 block text-center bg-pulse-600 hover:bg-pulse-700 text-white py-3 rounded-full font-semibold transition"
        >
          {t("auth.resetPassword.requestNewLink")}
        </Link>
      </AuthCard>
    );
  }

  if (success) {
    return (
      <AuthCard title={t("auth.resetPassword.successTitle")} subtitle={t("auth.resetPassword.successSubtitle")}>
        <p role="status" className="text-sm text-muted-dark text-center">
          {t("auth.resetPassword.successMessage")}
        </p>

        <button
          type="button"
          onClick={() => navigate("/login")}
          className="w-full mt-4 bg-pulse-600 hover:bg-pulse-700 text-white py-3 rounded-full font-semibold transition"
        >
          {t("auth.resetPassword.goToLogin")}
        </button>
      </AuthCard>
    );
  }

  const isValid = form.password && form.confirmPassword;

  return (
    <AuthCard title={t("auth.resetPassword.title")} subtitle={t("auth.resetPassword.subtitle")}>
      <form onSubmit={handleSubmit} className="space-y-4" noValidate>
        <div>
          <PasswordField
            label={t("auth.resetPassword.newPasswordLabel")}
            name="password"
            placeholder={t("auth.resetPassword.newPasswordLabel")}
            autoComplete="new-password"
            value={form.password}
            onChange={handleChange}
            error={errors.password}
          />
          <PasswordStrength password={form.password} />
        </div>

        <PasswordField
          label={t("auth.resetPassword.confirmPasswordLabel")}
          name="confirmPassword"
          placeholder={t("auth.resetPassword.confirmPasswordLabel")}
          autoComplete="new-password"
          value={form.confirmPassword}
          onChange={handleChange}
          error={errors.confirmPassword}
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
          {isSubmitting ? t("auth.resetPassword.submitting") : t("auth.resetPassword.submit")}
        </button>
      </form>

      <div className="text-center mt-6">
        <Link to="/login" className="text-sm text-pulse-400 hover:underline">
          {t("auth.resetPassword.backToLogin")}
        </Link>
      </div>
    </AuthCard>
  );
}
