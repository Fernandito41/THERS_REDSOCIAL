import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { FcGoogle } from "react-icons/fc";
import { IoClose } from "react-icons/io5";
import Logo from "@shared/components/Logo";
import { useAuth } from "@features/auth";

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [input, setInput] = useState("");

  const handleNext = async (e) => {
    e.preventDefault();

    try {
      await login({
        email: input,
        password: "123456" // temporal
      });

      navigate("/feed");
    } catch (error) {
      console.error(error);
      alert("Error al iniciar sesión");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0f0f11] px-4">

      <div className="w-full max-w-md bg-[#18181b] p-8 rounded-2xl shadow-xl border border-gray-800 relative">

        {/* CERRAR */}
        <div className="absolute top-3 left-3">
          <button
            onClick={() => navigate(-1)}
            className="text-white hover:bg-gray-800 p-2 rounded-full"
          >
            <IoClose size={24} />
          </button>
        </div>

        {/* LOGO */}
        <div className="flex justify-center mb-4">
          <Logo />
        </div>

        {/* TITULO */}
        <h2 className="text-2xl font-semibold text-white text-center">
          Inicia sesión en <span className="font-bold">Thers</span>
        </h2>

        <p className="text-gray-400 text-sm text-center mt-2 mb-6">
          Bienvenido de nuevo
        </p>

        {/* GOOGLE LOGIN */}
        <button className="w-full flex items-center justify-center gap-3 bg-white text-black py-3 rounded-full font-semibold hover:bg-gray-200 transition">
          <FcGoogle size={20} />
          Iniciar sesión con Google
        </button>

        {/* DIVISOR */}
        <div className="flex items-center my-6">
          <div className="flex-1 h-px bg-gray-700"></div>
          <span className="px-3 text-gray-400 text-sm">o</span>
          <div className="flex-1 h-px bg-gray-700"></div>
        </div>

        {/* FORM */}
        <form onSubmit={handleNext} className="space-y-4">

          <input
            type="text"
            placeholder="Correo, teléfono o @usuario"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="w-full bg-transparent border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
          />

          <button
            disabled={!input}
            className={`w-full py-3 rounded-full font-semibold transition ${
              input
                ? "bg-purple-600 hover:bg-purple-700 text-white"
                : "bg-gray-700 text-gray-400 cursor-not-allowed"
            }`}
          >
            Iniciar sesión
          </button>

        </form>

        {/* LINKS */}
        <div className="text-center mt-6 space-y-3">

          <button className="text-sm text-purple-400 hover:underline">
            ¿Olvidaste tu contraseña?
          </button>

          <div className="mt-6">
  <p className="text-sm text-gray-400 text-center mb-3">
    ¿No tienes una cuenta?
  </p>

  <button
    onClick={() => navigate("/register")}
    className="w-full border border-gray-700 text-white py-3 rounded-full font-semibold hover:bg-gray-800 transition"
  >
    Crear cuenta
  </button>
</div>
        </div>

      </div>
    </div>
  );
}