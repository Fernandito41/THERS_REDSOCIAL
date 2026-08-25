import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { IoArrowBack, IoInformationCircleOutline } from "react-icons/io5";
import { useToast } from "@shared/components/Toast";
import Spinner from "@shared/components/Spinner";
import AuthCard from "../components/AuthCard";
import TextField from "../components/TextField";
import { isValidEmail } from "../lib/validators";

// INTEGRACIÓN PENDIENTE DEL BACKEND
// ----------------------------------
// API_CONTRACT.md (§4, §9) todavía no documenta ningún endpoint de
// recuperación de contraseña por email -- el equipo de Backend lo está
// implementando en paralelo (ver contexto de la tarea). Esta página NO
// inventa la ruta ni el formato del endpoint, y NO simula una respuesta
// exitosa del servidor: valida el email en el Frontend (UX) y deja este
// punto exacto marcado para reemplazar por la llamada real a través de
// `api` (shared/lib/api.js) en cuanto el contrato se documente y ratifique.
// Cuando eso ocurra, la integración es mínima: reemplazar el bloque
// comentado más abajo por `await api.post(<endpoint de API_CONTRACT.md>, { email })`
// y manejar sus respuestas de éxito/error con el mismo `toast` ya cableado.
export default function ForgotPassword() {
  const navigate = useNavigate();
  const toast = useToast();

  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleChange = (e) => {
    setEmail(e.target.value);
    if (error) setError("");
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (isSubmitting) return;

    if (!email.trim()) {
      setError("Ingresá tu correo electrónico.");
      return;
    }
    if (!isValidEmail(email)) {
      setError("Ingresá un correo electrónico válido.");
      return;
    }

    setIsSubmitting(true);

    // --- INTEGRACIÓN PENDIENTE: reemplazar este bloque por la llamada real
    // al Backend cuando el endpoint exista y esté documentado en
    // API_CONTRACT.md. No se llama a ningún endpoint inventado.
    setSubmitted(true);
    setIsSubmitting(false);
    toast.info(
      "El equipo de Backend está terminando de implementar el envío del correo de recuperación. Todavía no podemos enviarte el enlace, pero esta pantalla ya está lista para conectarse en cuanto esté disponible.",
      { title: "Función en construcción", duration: 8000 }
    );
    // --- fin del punto de integración pendiente
  };

  return (
    <AuthCard title="Recuperar contraseña" subtitle="Te ayudamos a volver a tu cuenta.">
      {submitted ? (
        <div className="space-y-4">
          <p
            role="status"
            className="flex items-start gap-1.5 text-sm text-muted-dark bg-black/30 rounded-lg px-3 py-3"
          >
            <IoInformationCircleOutline size={18} className="shrink-0 mt-0.5 text-pulse-400" />
            La recuperación de contraseña por correo está en desarrollo en el Backend de THERS.
            Todavía no podemos enviarte el enlace, pero muy pronto vas a poder recuperar tu cuenta
            desde acá.
          </p>

          <button
            type="button"
            onClick={() => navigate("/login")}
            className="w-full border border-line-dark text-ink-dark py-3 rounded-full font-semibold hover:bg-line-dark transition"
          >
            Volver a iniciar sesión
          </button>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4" noValidate>
          <p className="text-sm text-muted-dark">
            Ingresá el correo electrónico asociado a tu cuenta y te ayudaremos a recuperar el
            acceso.
          </p>

          <TextField
            label="Correo electrónico"
            type="email"
            placeholder="Correo electrónico"
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
            {isSubmitting ? "Enviando..." : "Enviar enlace de recuperación"}
          </button>
        </form>
      )}

      <div className="text-center mt-6">
        <Link
          to="/login"
          className="inline-flex items-center gap-1.5 text-sm text-pulse-400 hover:underline"
        >
          <IoArrowBack size={14} />
          Volver a iniciar sesión
        </Link>
      </div>
    </AuthCard>
  );
}
