import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { FcGoogle } from "react-icons/fc";
import { FaApple } from "react-icons/fa";
import {
  IoArrowBack,
  IoCheckmarkCircleOutline,
  IoCloseCircleOutline,
  IoInformationCircleOutline,
  IoSparklesOutline,
} from "react-icons/io5";
import { useAuth, useOAuthNotice } from "@features/auth";
import { getErrorMessage } from "@shared/lib/api";
import { useToast } from "@shared/components/Toast";
import { useLanguage } from "@shared/i18n";
import Spinner from "@shared/components/Spinner";
import AmbientGlow from "@shared/components/AmbientGlow";
import Logo from "@shared/components/Logo";
import LanguageSwitcher from "@shared/components/LanguageSwitcher";
import TextField from "../components/TextField";
import PasswordField from "../components/PasswordField";
import PasswordStrength from "../components/PasswordStrength";
import PhoneField, { DEFAULT_COUNTRY_CODE } from "../components/PhoneField";
import BirthDateField from "../components/BirthDateField";
import TrustNote from "../components/TrustNote";
import { isValidEmail, isValidUsername, isValidPhone } from "../lib/validators";
import { calculateAge, isValidISODate, MIN_AGE_YEARS } from "../lib/dateUtils";

export default function Register() {
  const navigate = useNavigate();
  const { register } = useAuth();
  const { notice, notify } = useOAuthNotice();
  const toast = useToast();
  const { t } = useLanguage();

  const FEATURE_HIGHLIGHTS = [
    { title: t("auth.register.featureShareTitle"), detail: t("auth.register.featureShareDetail") },
    { title: t("auth.register.featureDiscoverTitle"), detail: t("auth.register.featureDiscoverDetail") },
    { title: t("auth.register.featureConnectTitle"), detail: t("auth.register.featureConnectDetail") },
  ];

  const [form, setForm] = useState({
    name: "",
    username: "",
    email: "",
    countryCode: DEFAULT_COUNTRY_CODE,
    phone: "",
    birthDate: "",
    password: "",
    confirmPassword: "",
  });
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    if (errors[e.target.name]) setErrors({ ...errors, [e.target.name]: undefined });
  };

  const handleCountryCodeChange = (countryCode) => setForm((f) => ({ ...f, countryCode }));

  const handleBirthDateChange = (birthDate) => {
    setForm((f) => ({ ...f, birthDate }));
    if (errors.birthDate) setErrors((prev) => ({ ...prev, birthDate: undefined }));
  };

  const validate = () => {
    const next = {};

    if (!form.name.trim()) next.name = t("auth.register.errorNameRequired");

    if (!form.username.trim()) next.username = t("auth.register.errorUsernameRequired");
    else if (!isValidUsername(form.username))
      next.username = t("auth.register.errorUsernameInvalid");

    if (!form.email.trim()) next.email = t("auth.register.errorEmailRequired");
    else if (!isValidEmail(form.email)) next.email = t("auth.register.errorEmailInvalid");

    if (!form.phone.trim()) next.phone = t("auth.register.errorPhoneRequired");
    else if (!isValidPhone(form.phone)) next.phone = t("auth.register.errorPhoneInvalid");

    if (!form.birthDate) next.birthDate = t("auth.register.errorBirthDateRequired");
    else if (!isValidISODate(form.birthDate)) next.birthDate = t("auth.register.errorBirthDateInvalid");
    else if (calculateAge(form.birthDate) < MIN_AGE_YEARS)
      next.birthDate = t("auth.register.errorBirthDateMinAge", { minAge: MIN_AGE_YEARS });

    if (!form.password) next.password = t("auth.register.errorPasswordRequired");
    // Longitud mínima: solo UX -- la regla de seguridad definitiva de
    // contraseña sigue PENDIENTE DE APROBACIÓN en API_CONTRACT.md §9 (ítem 2)
    // y la impone el Backend, no este formulario.
    else if (form.password.length < 8) next.password = t("auth.register.errorPasswordTooShort");

    if (form.confirmPassword !== form.password)
      next.confirmPassword = t("auth.register.errorConfirmPasswordMismatch");

    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    if (isSubmitting || !validate()) return;

    setIsSubmitting(true);
    try {
      // TODO BACKEND: el formulario ya recolecta username, teléfono
      // (countryCode + phone) y fecha de nacimiento (birthDate, ISO
      // yyyy-mm-dd), pero el contrato actual de POST /api/register
      // (API_CONTRACT.md §4.1) solo acepta { name, email, password } -- esa
      // es la única entidad ratificada de `users` hoy (DATABASE_ARCHITECTURE.md
      // §4.A). Enviar campos que el backend no espera no los persistiría, así
      // que se mantiene el contrato actual sin romperlo. Cuando Backend
      // documente el contrato ampliado en API_CONTRACT.md, agregar acá:
      //   phone: `${form.countryCode}${form.phone.trim()}`, birthDate: form.birthDate, username: form.username.trim()
      await register({ name: form.name.trim(), email: form.email.trim(), password: form.password });
      toast.success(t("auth.register.toastSuccess"));
      navigate("/login");
    } catch (error) {
      console.error(error);
      toast.error(getErrorMessage(error, t), { title: t("auth.register.toastErrorTitle") });
    } finally {
      setIsSubmitting(false);
    }
  };

  const isValid =
    form.name.trim() &&
    form.username.trim() &&
    form.email.trim() &&
    form.phone.trim() &&
    form.birthDate &&
    form.password &&
    form.confirmPassword;

  const passwordsTyped = form.confirmPassword.length > 0;
  const passwordsMatch = form.password === form.confirmPassword;

  return (
    <div className="min-h-screen bg-canvas-dark flex flex-col lg:flex-row">
      {/* PANEL IZQUIERDO -- identidad THERS, solo desktop/tablet ancho (lg+) */}
      <aside className="hidden lg:flex lg:w-1/2 relative overflow-hidden bg-gradient-to-br from-pulse-900 via-canvas-dark to-canvas-dark border-r border-line-dark">
        <AmbientGlow />

        <button
          type="button"
          onClick={() => navigate("/")}
          className="absolute top-6 left-6 z-20 flex items-center gap-1.5 text-sm font-medium text-muted-dark hover:text-ink-dark focus:outline-none focus:ring-2 focus:ring-pulse-500 rounded-full px-3 py-1.5 hover:bg-white/5 transition"
        >
          <IoArrowBack size={16} aria-hidden="true" />
          {t("auth.register.back")}
        </button>

        <div className="absolute top-6 right-6 z-20">
          <LanguageSwitcher />
        </div>

        <div className="relative z-10 flex flex-col justify-center px-12 xl:px-20 py-16 max-w-xl">
          <Logo size="text-4xl" />

          <h1 className="mt-8 text-4xl xl:text-5xl font-extrabold tracking-tight text-ink-dark leading-tight">
            {t("auth.register.heroTitle")}
          </h1>

          <p className="mt-4 text-muted-dark text-base">{t("auth.register.heroSubtitle")}</p>

          <ul className="mt-10 space-y-5">
            {FEATURE_HIGHLIGHTS.map((item) => (
              <li key={item.title} className="flex items-start gap-3">
                <span className="mt-1 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-pulse-500/20 text-pulse-300">
                  <IoSparklesOutline size={14} aria-hidden="true" />
                </span>
                <div>
                  <p className="text-sm font-semibold text-ink-dark">{item.title}</p>
                  <p className="text-sm text-muted-dark">{item.detail}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </aside>

      {/* PANEL DERECHO -- formulario */}
      <main className="flex-1 flex flex-col">
        <div className="w-full max-w-xl mx-auto px-5 sm:px-8 py-8 sm:py-12">
          {/* Header compacto solo en mobile/tablet angosto (sin panel izquierdo visible) */}
          <div className="flex items-center justify-between lg:hidden mb-8">
            <button
              type="button"
              onClick={() => navigate("/")}
              aria-label={t("auth.register.backAria")}
              className="text-ink-dark hover:bg-line-dark p-2 -ml-2 rounded-full focus:outline-none focus:ring-2 focus:ring-pulse-500"
            >
              <IoArrowBack size={22} />
            </button>
            <Logo size="text-2xl" />
            <LanguageSwitcher />
          </div>

          <div className="hidden lg:flex justify-end mb-6">
            <LanguageSwitcher />
          </div>

          <header className="mb-8 animate-float-in">
            <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-ink-dark">
              {t("auth.register.title")}
            </h1>
            <p className="mt-3 text-muted-dark text-sm sm:text-base max-w-md">
              {t("auth.register.subtitle")}
            </p>
          </header>

          {/* GOOGLE / APPLE -- sin backend real todavía, ver useOAuthNotice */}
          <div className="space-y-3">
            <button
              type="button"
              onClick={() => notify("google")}
              className="w-full flex items-center justify-center gap-3 bg-white text-black py-3 rounded-full font-semibold hover:bg-gray-200 active:scale-[0.99] transition"
            >
              <FcGoogle size={20} />
              {t("auth.oauthGoogleRegister")}
            </button>

            <button
              type="button"
              onClick={() => notify("apple")}
              className="w-full flex items-center justify-center gap-3 bg-black text-white border border-line-dark py-3 rounded-full font-semibold hover:bg-gray-900 active:scale-[0.99] transition"
            >
              <FaApple size={18} />
              {t("auth.oauthAppleRegister")}
            </button>
          </div>

          {notice && (
            <p
              role="status"
              className="flex items-start gap-1.5 text-xs text-muted-dark bg-black/30 rounded-lg px-3 py-2 mt-3 animate-float-in"
            >
              <IoInformationCircleOutline size={15} className="shrink-0 mt-0.5" />
              {t("auth.oauthNoticeRegister", {
                provider: notice === "google" ? t("auth.providerGoogle") : t("auth.providerApple"),
              })}
            </p>
          )}

          <div className="flex items-center my-6">
            <div className="flex-1 h-px bg-line-dark" />
            <span className="px-3 text-muted-dark text-sm">{t("auth.or")}</span>
            <div className="flex-1 h-px bg-line-dark" />
          </div>

          {/* FORMULARIO */}
          <form onSubmit={handleRegister} className="space-y-4" noValidate>
            <TextField
              label={t("auth.register.nameLabel")}
              name="name"
              placeholder={t("auth.register.nameLabel")}
              autoComplete="name"
              value={form.name}
              onChange={handleChange}
              error={errors.name}
            />

            <TextField
              label={t("auth.register.usernameLabel")}
              name="username"
              placeholder={t("auth.register.usernameLabel")}
              autoComplete="username"
              value={form.username}
              onChange={handleChange}
              error={errors.username}
            />

            {/* Correo + teléfono agrupados visualmente, en fila desde sm (>=640px) */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <TextField
                label={t("auth.register.emailLabel")}
                name="email"
                type="email"
                placeholder={t("auth.register.emailLabel")}
                autoComplete="email"
                value={form.email}
                onChange={handleChange}
                error={errors.email}
              />

              <PhoneField
                label={t("auth.register.phoneLabel")}
                name="phone"
                placeholder="0000-0000"
                autoComplete="tel-national"
                countryCode={form.countryCode}
                onCountryCodeChange={handleCountryCodeChange}
                value={form.phone}
                onChange={handleChange}
                error={errors.phone}
              />
            </div>

            <BirthDateField value={form.birthDate} onChange={handleBirthDateChange} error={errors.birthDate} />

            <div>
              <PasswordField
                label={t("auth.register.passwordLabel")}
                name="password"
                placeholder={t("auth.register.passwordLabel")}
                autoComplete="new-password"
                value={form.password}
                onChange={handleChange}
                error={errors.password}
              />
              <PasswordStrength password={form.password} />
            </div>

            <div>
              <PasswordField
                label={t("auth.register.confirmPasswordLabel")}
                name="confirmPassword"
                placeholder={t("auth.register.confirmPasswordLabel")}
                autoComplete="new-password"
                value={form.confirmPassword}
                onChange={handleChange}
                error={errors.confirmPassword}
              />
              {passwordsTyped && (
                <p
                  role="status"
                  className={`mt-1.5 flex items-center gap-1.5 text-xs ${
                    passwordsMatch ? "text-success-500" : "text-ember-400"
                  }`}
                >
                  {passwordsMatch ? (
                    <>
                      <IoCheckmarkCircleOutline size={14} aria-hidden="true" /> {t("auth.register.passwordsMatch")}
                    </>
                  ) : (
                    <>
                      <IoCloseCircleOutline size={14} aria-hidden="true" /> {t("auth.register.passwordsMismatch")}
                    </>
                  )}
                </p>
              )}
            </div>

            <TrustNote />

            <p className="text-xs text-muted-dark">
              {t("auth.register.acceptPrefix")}{" "}
              <Link to="/terms" className="text-pulse-400 hover:underline">
                {t("auth.register.termsLink")}
              </Link>{" "}
              {t("auth.register.acceptMiddle")}{" "}
              <Link to="/privacy" className="text-pulse-400 hover:underline">
                {t("auth.register.privacyLink")}
              </Link>
              .
            </p>

            <button
              type="submit"
              disabled={!isValid || isSubmitting}
              className={`w-full py-3 rounded-full font-semibold transition flex items-center justify-center gap-2 ${
                isValid && !isSubmitting
                  ? "bg-pulse-600 hover:bg-pulse-700 active:bg-pulse-800 text-white"
                  : "bg-line-dark text-muted-dark cursor-not-allowed"
              }`}
            >
              {isSubmitting && <Spinner />}
              {isSubmitting ? t("auth.register.submitting") : t("auth.register.submit")}
            </button>
          </form>

          {/* LOGIN CTA */}
          <div className="mt-6">
            <p className="text-sm text-muted-dark text-center mb-3">{t("auth.register.alreadyHaveAccount")}</p>

            <button
              onClick={() => navigate("/login")}
              className="w-full border border-line-dark text-ink-dark py-3 rounded-full font-semibold hover:bg-line-dark active:bg-line-dark/70 transition"
            >
              {t("auth.register.login")}
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
