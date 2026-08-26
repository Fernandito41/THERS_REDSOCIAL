import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { FcGoogle } from "react-icons/fc";
import { FaApple } from "react-icons/fa";
import { IoInformationCircleOutline } from "react-icons/io5";
import { useAuth, useOAuthNotice } from "@features/auth";
import { getErrorMessage } from "@shared/lib/api";
import { useToast } from "@shared/components/Toast";
import Spinner from "@shared/components/Spinner";
import AuthCard from "../components/AuthCard";
import TextField from "../components/TextField";
import PasswordField from "../components/PasswordField";
import PasswordStrength from "../components/PasswordStrength";
import { isValidEmail } from "../lib/validators";

export default function Register() {
  const navigate = useNavigate();
  const { register } = useAuth();
  const { notice, notify } = useOAuthNotice();
  const toast = useToast();

  const [form, setForm] = useState({ name: "", email: "", password: "", confirmPassword: "" });
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const validate = () => {
    const next = {};
    if (!form.name.trim()) next.name = "Ingresá tu nombre.";
    if (!form.email.trim()) next.email = "Ingresá tu correo electrónico.";
    else if (!isValidEmail(form.email)) next.email = "Ingresá un correo electrónico válido.";
    if (!form.password) next.password = "Ingresá una contraseña.";
    // Longitud mínima: solo UX -- la regla de seguridad definitiva de
    // contraseña sigue PENDIENTE DE APROBACIÓN en API_CONTRACT.md §9 (ítem 2)
    // y la impone el Backend, no este formulario.
    else if (form.password.length < 8) next.password = "Usá al menos 8 caracteres.";
    if (form.confirmPassword !== form.password) next.confirmPassword = "Las contraseñas no coinciden.";
    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    if (isSubmitting || !validate()) return;

    setIsSubmitting(true);
    try {
      // .trim() solo en email (mismo motivo que en backend/auth_routes.py) --
      // si el email queda con espacios al registrarse, un login posterior con
      // el mismo email "limpio" nunca hace match. La contraseña no se toca.
      await register({ name: form.name, email: form.email.trim(), password: form.password });
      toast.success("Cuenta creada correctamente.");
      navigate("/login");
    } catch (error) {
      console.error(error);
      toast.error(getErrorMessage(error), { title: "No pudimos crear tu cuenta" });
    } finally {
      setIsSubmitting(false);
    }
  };

  const isValid = form.name.trim() && form.email.trim() && form.password && form.confirmPassword;

  return (
    <AuthCard
      title={
        <>
          Crea tu cuenta en <span className="font-bold">Thers</span>
        </>
      }
      subtitle="Únete y comienza a compartir."
    >
      {/* GOOGLE */}
      <button
        type="button"
        onClick={() => notify("google")}
        className="w-full flex items-center justify-center gap-3 bg-white text-black py-3 rounded-full font-semibold hover:bg-gray-200 transition"
      >
        <FcGoogle size={20} />
        Crear cuenta con Google
      </button>

      {/* APPLE */}
      <button
        type="button"
        onClick={() => notify("apple")}
        className="w-full flex items-center justify-center gap-3 bg-black text-white border border-line-dark py-3 rounded-full font-semibold hover:bg-gray-900 transition mt-3"
      >
        <FaApple size={18} />
        Crear cuenta con Apple
      </button>

      {notice && (
        <p
          role="status"
          className="flex items-start gap-1.5 text-xs text-muted-dark bg-black/30 rounded-lg px-3 py-2 mt-3"
        >
          <IoInformationCircleOutline size={15} className="shrink-0 mt-0.5" />
          {notice === "google" ? "Google" : "Apple"} todavía no está configurado en el backend de THERS
          — esta cuenta no puede registrarse así por ahora.
        </p>
      )}

      {/* DIVISOR */}
      <div className="flex items-center my-6">
        <div className="flex-1 h-px bg-line-dark"></div>
        <span className="px-3 text-muted-dark text-sm">o</span>
        <div className="flex-1 h-px bg-line-dark"></div>
      </div>

      {/* FORMULARIO */}
      <form onSubmit={handleRegister} className="space-y-4" noValidate>
        <TextField
          label="Nombre"
          name="name"
          placeholder="Nombre"
          autoComplete="name"
          value={form.name}
          onChange={handleChange}
          error={errors.name}
        />

        <TextField
          label="Correo electrónico"
          name="email"
          type="email"
          placeholder="Correo electrónico"
          autoComplete="email"
          value={form.email}
          onChange={handleChange}
          error={errors.email}
        />

        <div>
          <PasswordField
            label="Contraseña"
            name="password"
            placeholder="Contraseña"
            autoComplete="new-password"
            value={form.password}
            onChange={handleChange}
            error={errors.password}
          />
          <PasswordStrength password={form.password} />
        </div>

        <PasswordField
          label="Confirmar contraseña"
          name="confirmPassword"
          placeholder="Confirmar contraseña"
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
          {isSubmitting ? "Creando cuenta..." : "Crear cuenta"}
        </button>

        <p className="text-xs text-muted-dark mt-4">
          Al registrarte, aceptas los{" "}
          <Link to="/terms" className="text-pulse-400 hover:underline">
            Términos de servicio
          </Link>{" "}
          y la{" "}
          <Link to="/privacy" className="text-pulse-400 hover:underline">
            Política de privacidad
          </Link>
          , incluido el{" "}
          <Link to="/cookies" className="text-pulse-400 hover:underline">
            uso de cookies
          </Link>
          .
        </p>
      </form>

      {/* LOGIN CTA */}
      <div className="mt-6">
        <p className="text-sm text-muted-dark text-center mb-3">¿Ya tienes una cuenta?</p>

        <button
          onClick={() => navigate("/login")}
          className="w-full border border-line-dark text-ink-dark py-3 rounded-full font-semibold hover:bg-line-dark transition"
        >
          Iniciar sesión
        </button>
      </div>
    </AuthCard>
  );
}
