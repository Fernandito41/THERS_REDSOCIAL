import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { IoArrowBack } from "react-icons/io5";
import { useToast } from "@shared/components/Toast";
import { useLanguage } from "@shared/i18n";
import Spinner from "@shared/components/Spinner";
import { api, getErrorMessage } from "@shared/lib/api";
import AuthCard from "../components/AuthCard";
import TextField from "../components/TextField";
import { isValidEmail } from "../lib/validators";

// POST /api/forgot-password (ADR-010-password-reset-otp-flow.md,
// API_CONTRACT.md §4.8) -- endpoint público, sin JWT. Siempre responde 200
// con el mismo mensaje genérico exista o no el email (anti-enumeración) --
// por eso esta pantalla nunca puede mostrar "ese email no existe": si la
// request no lanza (sin error de red/servidor), se navega a
// /verify-reset-code sin importar si el backend realmente encontró una
// cuenta o no. El email viaja como router state (no como query param) --
// no debe quedar en el historial/URL.
export default function ForgotPassword() {
  const navigate = useNavigate();
  const toast = useToast();
  const { t } = useLanguage();

  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (e) => {
    setEmail(e.target.value);
    if (error) setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (isSubmitting) return;

    const trimmedEmail = email.trim();
    if (!trimmedEmail) {
      setError(t("auth.forgotPassword.errorEmailRequired"));
      return;
    }
    if (!isValidEmail(trimmedEmail)) {
      setError(t("auth.forgotPassword.errorEmailInvalid"));
      return;
    }

    setIsSubmitting(true);

    try {
      await api.post("/forgot-password", { email: trimmedEmail });
      navigate("/verify-reset-code", { state: { email: trimmedEmail } });
    } catch (err) {
      toast.error(getErrorMessage(err, t));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AuthCard title={t("auth.forgotPassword.title")} subtitle={t("auth.forgotPassword.subtitle")}>
      <form onSubmit={handleSubmit} className="space-y-4" noValidate>
        <p className="text-sm text-muted-dark">{t("auth.forgotPassword.intro")}</p>

        <TextField
          label={t("auth.forgotPassword.emailLabel")}
          type="email"
          placeholder={t("auth.forgotPassword.emailLabel")}
          autoComplete="email"
          value={email}
          onChange={handleChange}
          error={error}
        />

        <button
          type="submit"
          disabled={!email.trim() || isSubmitting}
          className={`w-full py-3 rounded-full font-semibold transition flex items-center justify-center gap-2 ${
            email.trim() && !isSubmitting
              ? "bg-pulse-600 hover:bg-pulse-700 text-white"
              : "bg-line-dark text-muted-dark cursor-not-allowed"
          }`}
        >
          {isSubmitting && <Spinner />}
          {isSubmitting ? t("auth.forgotPassword.submitting") : t("auth.forgotPassword.submit")}
        </button>
      </form>

      <div className="text-center mt-6">
        <Link
          to="/login"
          className="inline-flex items-center gap-1.5 text-sm text-pulse-400 hover:underline"
        >
          <IoArrowBack size={14} />
          {t("auth.forgotPassword.backToLogin")}
        </Link>
      </div>
    </AuthCard>
  );
}
