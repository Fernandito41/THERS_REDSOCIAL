import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@features/auth";
import { getErrorMessage } from "@shared/lib/api";
import { useToast } from "@shared/components/Toast";
import { useLanguage } from "@shared/i18n";
import Spinner from "@shared/components/Spinner";
import AuthCard from "../components/AuthCard";
import TextField from "../components/TextField";
import PhoneField, { DEFAULT_COUNTRY_CODE } from "../components/PhoneField";
import BirthDateField from "../components/BirthDateField";
import { isValidUsername, isValidPhone } from "../lib/validators";
import { calculateAge, isValidISODate, MIN_AGE_YEARS } from "../lib/dateUtils";

// "Complete your profile" -- ADR-012-google-sign-in.md §Decisión, FASE 18.
// Una cuenta creada vía "Continuar con Google" llega acá con
// `profile_completed=false` (ProtectedRoute.jsx la redirige apenas detecta
// ese estado, sin que el Frontend pueda saltárselo manipulando rutas -- el
// backend es quien decide el estado real, PATCH /api/users/me lo confirma).
// Reutiliza PATCH /api/users/me (ADR-003) tal cual -- no existe un endpoint
// nuevo para esto.
//
// El campo de username arranca VACÍO a propósito, nunca prellenado con el
// placeholder que el backend generó (`user_xxxxxxxxxxxx`) -- mostrar ese
// valor como si fuera una sugerencia real invitaría a dejarlo tal cual,
// exactamente lo que la tarea de origen pide evitar ("no generes
// silenciosamente un username permanente extraño"). Se exige elegir uno
// nuevo para completar el onboarding.
export default function CompleteProfile() {
  const navigate = useNavigate();
  const { updateProfile, logout } = useAuth();
  const toast = useToast();
  const { t } = useLanguage();

  const [form, setForm] = useState({
    username: "",
    countryCode: DEFAULT_COUNTRY_CODE,
    phone: "",
    birthDate: "",
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

    if (!form.username.trim()) next.username = t("auth.register.errorUsernameRequired");
    else if (!isValidUsername(form.username))
      next.username = t("auth.register.errorUsernameInvalid");

    if (!form.phone.trim()) next.phone = t("auth.register.errorPhoneRequired");
    else if (!isValidPhone(form.phone)) next.phone = t("auth.register.errorPhoneInvalid");

    if (!form.birthDate) next.birthDate = t("auth.register.errorBirthDateRequired");
    else if (!isValidISODate(form.birthDate)) next.birthDate = t("auth.register.errorBirthDateInvalid");
    else if (calculateAge(form.birthDate) < MIN_AGE_YEARS)
      next.birthDate = t("auth.register.errorBirthDateMinAge", { minAge: MIN_AGE_YEARS });

    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (isSubmitting || !validate()) return;

    setIsSubmitting(true);
    try {
      const updatedUser = await updateProfile({
        username: form.username.trim(),
        phone: form.phone.trim(),
        country_code: form.countryCode,
        birth_date: form.birthDate,
      });
      toast.success(t("auth.completeProfile.toastSuccess"));
      // `updateProfile` ya persiste `profile_completed: true` (el backend lo
      // recalcula, update_profile_use_case.py) -- ProtectedRoute.jsx no
      // volverá a redirigir acá.
      if (updatedUser.profile_completed) {
        navigate("/feed");
      }
    } catch (error) {
      console.error(error);
      toast.error(getErrorMessage(error, t), { title: t("auth.completeProfile.toastErrorTitle") });
    } finally {
      setIsSubmitting(false);
    }
  };

  const isValid = form.username.trim() && form.phone.trim() && form.birthDate;

  return (
    <AuthCard
      title={t("auth.completeProfile.title")}
      subtitle={t("auth.completeProfile.subtitle")}
      // Sin botón de cerrar hacia atrás con `navigate(-1)`: no hay una
      // pantalla anterior a la que volver dentro de este flujo sin salir de
      // la sesión -- cerrar significa cerrar sesión, no descartar el paso.
      onClose={logout}
      closeLabel={t("auth.completeProfile.logoutAria")}
    >
      <form onSubmit={handleSubmit} className="space-y-4" noValidate>
        <TextField
          label={t("auth.register.usernameLabel")}
          name="username"
          placeholder={t("auth.completeProfile.usernamePlaceholder")}
          autoComplete="username"
          value={form.username}
          onChange={handleChange}
          error={errors.username}
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

        <BirthDateField value={form.birthDate} onChange={handleBirthDateChange} error={errors.birthDate} />

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
          {isSubmitting ? t("auth.completeProfile.submitting") : t("auth.completeProfile.submit")}
        </button>
      </form>
    </AuthCard>
  );
}
