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
import { isValidEmail } from "../lib/validators";

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const { notice, notify } = useOAuthNotice();
  const toast = useToast();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validate = () => {
    const next = {};
    if (!email.trim()) next.email = "Ingresá tu correo electrónico.";
    else if (!isValidEmail(email)) next.email = "Ingresá un correo electrónico válido.";
    if (!password) next.password = "Ingresá tu contraseña.";
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
      await login({ email: email.trim(), password });
      navigate("/feed");
    } catch (error) {
      console.error(error);
      toast.error(getErrorMessage(error), { title: "No pudimos iniciar sesión" });
    } finally {
      setIsSubmitting(false);
    }
  };

  const isValid = email.trim() && password;

  return (
    <AuthCard
      title={
        <>
          Inicia sesión en <span className="font-bold">Thers</span>
        </>
      }
      subtitle="Bienvenido de nuevo"
    >
      {/* GOOGLE LOGIN */}
      <button
        type="button"
        onClick={() => notify("google")}
        className="w-full flex items-center justify-center gap-3 bg-white text-black py-3 rounded-full font-semibold hover:bg-gray-200 transition"
      >
        <FcGoogle size={20} />
        Iniciar sesión con Google
      </button>

      {/* APPLE LOGIN */}
      <button
        type="button"
        onClick={() => notify("apple")}
        className="w-full flex items-center justify-center gap-3 bg-black text-white border border-line-dark py-3 rounded-full font-semibold hover:bg-gray-900 transition mt-3"
      >
        <FaApple size={18} />
        Iniciar sesión con Apple
      </button>

      {notice && (
        <p
          role="status"
          className="flex items-start gap-1.5 text-xs text-muted-dark bg-black/30 rounded-lg px-3 py-2 mt-3"
        >
          <IoInformationCircleOutline size={15} className="shrink-0 mt-0.5" />
          {notice === "google" ? "Google" : "Apple"} todavía no está configurado en el backend de THERS
          — esta cuenta no puede iniciar sesión así por ahora.
        </p>
      )}

      {/* DIVISOR */}
      <div className="flex items-center my-6">
        <div className="flex-1 h-px bg-line-dark"></div>
        <span className="px-3 text-muted-dark text-sm">o</span>
        <div className="flex-1 h-px bg-line-dark"></div>
      </div>

      {/* FORM */}
      <form onSubmit={handleSubmit} className="space-y-4" noValidate>
        <TextField
          label="Correo electrónico"
          type="email"
          placeholder="Correo electrónico"
          autoComplete="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          error={errors.email}
        />

        <PasswordField
          label="Contraseña"
          placeholder="Contraseña"
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
          {isSubmitting ? "Iniciando sesión..." : "Iniciar sesión"}
        </button>
      </form>

      {/* LINKS */}
      <div className="text-center mt-6 space-y-3">
        <Link to="/forgot-password" className="text-sm text-pulse-400 hover:underline">
          ¿Olvidaste tu contraseña?
        </Link>

        <div className="mt-6">
          <p className="text-sm text-muted-dark text-center mb-3">¿No tienes una cuenta?</p>

          <button
            onClick={() => navigate("/register")}
            className="w-full border border-line-dark text-ink-dark py-3 rounded-full font-semibold hover:bg-line-dark transition"
          >
            Crear cuenta
          </button>
        </div>
      </div>
    </AuthCard>
  );
}
