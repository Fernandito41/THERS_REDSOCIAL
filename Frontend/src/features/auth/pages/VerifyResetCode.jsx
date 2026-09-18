import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { IoInformationCircleOutline } from "react-icons/io5";
import { useToast } from "@shared/components/Toast";
import { useLanguage } from "@shared/i18n";
import Spinner from "@shared/components/Spinner";
import { api, getErrorMessage } from "@shared/lib/api";
import AuthCard from "../components/AuthCard";
import OtpCodeInput from "../components/OtpCodeInput";
import { maskEmail } from "../lib/maskEmail";

// Cooldown de "Reenviar código" -- mismo valor que
// PASSWORD_RESET_REQUEST_COOLDOWN_SECONDS (backend/app/domain/auth/token_policy.py,
// ADR-010-password-reset-otp-flow.md §Fase 11 de la tarea). El backend ya lo
// impone igual sin importar lo que haga este contador -- esto es solo UX,
// no la protección real (una request directa por Postman antes de que
// termine esta cuenta regresiva recibe el mismo mensaje genérico de
// siempre, sin generar un código nuevo).
const RESEND_COOLDOWN_SECONDS = 60;

function formatCooldown(totalSeconds) {
  const minutes = String(Math.floor(totalSeconds / 60)).padStart(2, "0");
  const seconds = String(totalSeconds % 60).padStart(2, "0");
  return `${minutes}:${seconds}`;
}

// POST /api/verify-reset-code (público) y, para "Reenviar código",
// POST /api/forgot-password de nuevo -- no hay un endpoint de resend
// separado (ADR-010 §Decisión: forgot-password ya invalida el código
// anterior y crea uno nuevo). `email` llega por router state desde
// ForgotPassword.jsx -- si falta (navegación directa a esta URL, o F5),
// no hay forma de continuar el flujo: se ofrece volver a pedir un código.
export default function VerifyResetCode() {
  const navigate = useNavigate();
  const location = useLocation();
  const toast = useToast();
  const { t } = useLanguage();
  const email = location.state?.email;

  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [isVerifying, setIsVerifying] = useState(false);
  const [isResending, setIsResending] = useState(false);
  const [cooldown, setCooldown] = useState(RESEND_COOLDOWN_SECONDS);

  useEffect(() => {
    if (cooldown <= 0) return;
    const interval = setInterval(() => setCooldown((prev) => Math.max(prev - 1, 0)), 1000);
    return () => clearInterval(interval);
  }, [cooldown]);

  const handleVerify = async (fullCode) => {
    if (isVerifying) return;
    setIsVerifying(true);
    setError("");

    try {
      const response = await api.post("/verify-reset-code", { email, code: fullCode });
      navigate("/reset-password", {
        state: { resetAuthorization: response.data.reset_authorization },
      });
    } catch (err) {
      setCode("");
      setError(getErrorMessage(err, t));
    } finally {
      setIsVerifying(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (code.length === 6) handleVerify(code);
  };

  const handleResend = async () => {
    if (cooldown > 0 || isResending) return;
    setIsResending(true);

    try {
      await api.post("/forgot-password", { email });
      setCode("");
      setError("");
      setCooldown(RESEND_COOLDOWN_SECONDS);
      toast.success(t("auth.verifyResetCode.resendSuccess"));
    } catch (err) {
      toast.error(getErrorMessage(err, t));
    } finally {
      setIsResending(false);
    }
  };

  if (!email) {
    return (
      <AuthCard
        title={t("auth.verifyResetCode.missingEmailTitle")}
        subtitle={t("auth.verifyResetCode.missingEmailSubtitle")}
      >
        <p
          role="alert"
          className="flex items-start gap-1.5 text-sm text-muted-dark bg-black/30 rounded-lg px-3 py-3"
        >
          <IoInformationCircleOutline size={18} className="shrink-0 mt-0.5 text-pulse-400" />
          {t("auth.verifyResetCode.missingEmailNotice")}
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

  return (
    <AuthCard
      title={t("auth.verifyResetCode.title")}
      subtitle={t("auth.verifyResetCode.subtitle", { email: maskEmail(email) })}
    >
      <form onSubmit={handleSubmit} className="space-y-6" noValidate>
        <OtpCodeInput
          value={code}
          onChange={setCode}
          onComplete={handleVerify}
          error={error}
          disabled={isVerifying}
        />

        <button
          type="submit"
          disabled={code.length !== 6 || isVerifying}
          className={`w-full py-3 rounded-full font-semibold transition flex items-center justify-center gap-2 ${
            code.length === 6 && !isVerifying
              ? "bg-pulse-600 hover:bg-pulse-700 text-white"
              : "bg-line-dark text-muted-dark cursor-not-allowed"
          }`}
        >
          {isVerifying && <Spinner />}
          {isVerifying ? t("auth.verifyResetCode.verifying") : t("auth.verifyResetCode.verify")}
        </button>
      </form>

      <div className="text-center mt-6 space-y-1">
        <p className="text-sm text-muted-dark">{t("auth.verifyResetCode.noCodeReceived")}</p>
        <button
          type="button"
          onClick={handleResend}
          disabled={cooldown > 0 || isResending}
          className={`text-sm font-semibold ${
            cooldown > 0 || isResending
              ? "text-muted-dark cursor-not-allowed"
              : "text-pulse-400 hover:underline"
          }`}
        >
          {cooldown > 0
            ? t("auth.verifyResetCode.resendIn", { time: formatCooldown(cooldown) })
            : t("auth.verifyResetCode.resend")}
        </button>
      </div>

      <div className="text-center mt-4">
        <Link to="/login" className="text-sm text-pulse-400 hover:underline">
          {t("auth.resetPassword.backToLogin")}
        </Link>
      </div>
    </AuthCard>
  );
}
