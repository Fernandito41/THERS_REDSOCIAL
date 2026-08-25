import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { IoInformationCircleOutline } from "react-icons/io5";
import { useToast } from "@shared/components/Toast";
import Spinner from "@shared/components/Spinner";
import AuthCard from "../components/AuthCard";
import PasswordField from "../components/PasswordField";
import PasswordStrength from "../components/PasswordStrength";

// INTEGRACIÓN PENDIENTE DEL BACKEND
// ----------------------------------
// Igual que ForgotPassword.jsx: API_CONTRACT.md no documenta todavía ningún
// endpoint de reseteo de contraseña. El token se lee de la URL (?token=...)
// porque es el mecanismo estándar de los flujos de "reset por email", pero
// su formato/validez real (expiración, un solo uso, etc.) depende
// exclusivamente de lo que Backend defina y documente -- no se inventa aquí.
// Cuando el endpoint exista: reemplazar el bloque comentado en handleSubmit
// por la llamada real (`token` + nueva contraseña) y, en su éxito, activar
// `setSuccess(true)` -- esa rama de UI ("Tu contraseña fue actualizada
// correctamente.") ya está implementada y lista, solo queda conectarla.
export default function ResetPassword() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");
  const toast = useToast();

  const [form, setForm] = useState({ password: "", confirmPassword: "" });
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  // setSuccess(true) es el punto de integración real: se invoca dentro de
  // handleSubmit una vez que exista la llamada al Backend (ver comentario
  // en handleSubmit más abajo).
  // eslint-disable-next-line no-unused-vars
  const [success, setSuccess] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const validate = () => {
    const next = {};
    if (!form.password) next.password = "Ingresá una nueva contraseña.";
    else if (form.password.length < 8) next.password = "Usá al menos 8 caracteres.";
    if (form.confirmPassword !== form.password) next.confirmPassword = "Las contraseñas no coinciden.";
    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (isSubmitting || !token || !validate()) return;

    setIsSubmitting(true);

    // --- INTEGRACIÓN PENDIENTE: reemplazar este bloque por la llamada real
    // al Backend (token + nueva contraseña) cuando el endpoint exista y esté
    // documentado en API_CONTRACT.md. En éxito real: setSuccess(true).
    setIsSubmitting(false);
    toast.info(
      "El equipo de Backend está terminando de implementar el reseteo de contraseña. Este formulario ya valida los datos y está listo para conectarse en cuanto el endpoint esté disponible.",
      { title: "Función en construcción", duration: 8000 }
    );
    // --- fin del punto de integración pendiente
  };

  if (!token) {
    return (
      <AuthCard title="Enlace inválido" subtitle="Este enlace de recuperación no es válido o expiró.">
        <p
          role="alert"
          className="flex items-start gap-1.5 text-sm text-muted-dark bg-black/30 rounded-lg px-3 py-3"
        >
          <IoInformationCircleOutline size={18} className="shrink-0 mt-0.5 text-pulse-400" />
          Pedí un nuevo enlace desde la pantalla de recuperación de contraseña.
        </p>

        <Link
          to="/forgot-password"
          className="w-full mt-4 block text-center bg-pulse-600 hover:bg-pulse-700 text-white py-3 rounded-full font-semibold transition"
        >
          Solicitar nuevo enlace
        </Link>
      </AuthCard>
    );
  }

  if (success) {
    return (
      <AuthCard title="Contraseña actualizada" subtitle="Ya podés iniciar sesión con tu nueva contraseña.">
        <p role="status" className="text-sm text-muted-dark text-center">
          Tu contraseña fue actualizada correctamente.
        </p>

        <button
          type="button"
          onClick={() => navigate("/login")}
          className="w-full mt-4 bg-pulse-600 hover:bg-pulse-700 text-white py-3 rounded-full font-semibold transition"
        >
          Ir a iniciar sesión
        </button>
      </AuthCard>
    );
  }

  const isValid = form.password && form.confirmPassword;

  return (
    <AuthCard title="Crear nueva contraseña" subtitle="Elegí una contraseña segura para tu cuenta.">
      <form onSubmit={handleSubmit} className="space-y-4" noValidate>
        <div>
          <PasswordField
            label="Nueva contraseña"
            name="password"
            placeholder="Nueva contraseña"
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
          {isSubmitting ? "Actualizando..." : "Actualizar contraseña"}
        </button>
      </form>

      <div className="text-center mt-6">
        <Link to="/login" className="text-sm text-pulse-400 hover:underline">
          Volver a iniciar sesión
        </Link>
      </div>
    </AuthCard>
  );
}
