import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { IoClose } from "react-icons/io5";
import { FcGoogle } from "react-icons/fc";
import Logo from "@shared/components/Logo";
import { Link } from "react-router-dom";


export default function Register() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
  });

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleRegister = (e) => {
    e.preventDefault();
    console.log(form);
    navigate("/login"); // temporal
  };

  const isValid =
    form.name.trim() &&
    form.email.trim() &&
    form.password.trim();

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
          Crea tu cuenta en <span className="font-bold">Thers</span>
        </h2>

        <p className="text-gray-400 text-sm text-center mt-2 mb-6">
          Únete y comienza a compartir.
        </p>

        {/* GOOGLE */}
        <button className="w-full flex items-center justify-center gap-3 bg-white text-black py-3 rounded-full font-semibold hover:bg-gray-200 transition">
          <FcGoogle size={20} />
          Crear cuenta con Google
        </button>

        {/* DIVISOR */}
        <div className="flex items-center my-6">
          <div className="flex-1 h-px bg-gray-700"></div>
          <span className="px-3 text-gray-400 text-sm">o</span>
          <div className="flex-1 h-px bg-gray-700"></div>
        </div>

        {/* FORMULARIO */}
        <form onSubmit={handleRegister} className="space-y-4">

          <input
            type="text"
            name="name"
            placeholder="Nombre"
            value={form.name}
            onChange={handleChange}
            className="w-full bg-transparent border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
          />

          <input
            type="email"
            name="email"
            placeholder="Correo electrónico"
            value={form.email}
            onChange={handleChange}
            className="w-full bg-transparent border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
          />

          <input
            type="password"
            name="password"
            placeholder="Contraseña"
            value={form.password}
            onChange={handleChange}
            className="w-full bg-transparent border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
          />

          <button
            disabled={!isValid}
            className={`w-full py-3 rounded-full font-semibold transition ${
              isValid
                ? "bg-purple-600 hover:bg-purple-700 text-white"
                : "bg-gray-700 text-gray-400 cursor-not-allowed"
            }`}
          >
            Crear cuenta
          </button>
        <p className="text-xs text-gray-500 mt-4">
  Al registrarte, aceptas los{" "}
  <Link to="/terms" className="text-blue-500 hover:underline">
    Términos de servicio
  </Link>{" "}
  y la{" "}
  <Link to="/privacy" className="text-blue-500 hover:underline">
    Política de privacidad
  </Link>
  , incluido el{" "}
  <Link to="/cookies" className="text-blue-500 hover:underline">
    uso de cookies
  </Link>.
</p>

        </form>

        {/* LOGIN CTA */}
        <div className="mt-6">
          <p className="text-sm text-gray-400 text-center mb-3">
            ¿Ya tienes una cuenta?
          </p>

          <button
            onClick={() => navigate("/login")}
            className="w-full border border-gray-700 text-white py-3 rounded-full font-semibold hover:bg-gray-800 transition"
          >
            Iniciar sesión
          </button>
        </div>

      </div>
    </div>
  );
}