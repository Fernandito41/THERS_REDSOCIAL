import { useNavigate } from "react-router-dom";
import { IoClose } from "react-icons/io5";
import Logo from "@shared/components/Logo";

// Shell visual compartido por Login/Register/ForgotPassword/ResetPassword --
// centraliza el fondo oscuro fijo, la tarjeta, el botón de cerrar y el logo
// para que las 4 pantallas de auth se mantengan consistentes (Fase 10) sin
// duplicar el mismo markup en cada página.
export default function AuthCard({ title, subtitle, children, onClose, closeLabel = "Cerrar" }) {
  const navigate = useNavigate();
  const handleClose = onClose || (() => navigate(-1));

  return (
    <div className="min-h-screen flex items-center justify-center bg-canvas-dark px-4 py-10">
      <div className="w-full max-w-md bg-surface-dark p-8 rounded-2xl shadow-xl border border-line-dark relative">
        <div className="absolute top-3 left-3">
          <button
            type="button"
            onClick={handleClose}
            aria-label={closeLabel}
            className="text-ink-dark hover:bg-line-dark p-2 rounded-full focus:outline-none focus:ring-2 focus:ring-pulse-500"
          >
            <IoClose size={24} />
          </button>
        </div>

        <div className="flex justify-center mb-4">
          <Logo />
        </div>

        <h1 className="text-2xl font-semibold text-ink-dark text-center">{title}</h1>
        {subtitle && <p className="text-muted-dark text-sm text-center mt-2 mb-6">{subtitle}</p>}

        {children}
      </div>
    </div>
  );
}
