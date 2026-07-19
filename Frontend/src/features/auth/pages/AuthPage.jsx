import { useNavigate } from "react-router-dom";
import { FcGoogle } from "react-icons/fc";
import { FaApple } from "react-icons/fa";
import { Link } from "react-router-dom";
import collage from "@/assets/collage.png";
import logo from "@/assets/logo_oficial.jpeg"; 

export default function AuthPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex bg-white relative"> 

      
      <div className="absolute top-5 left-5 z-10 bg-white/10 backdrop-blur-md p-2 rounded-full shadow-lg">
        <img
          src={logo}
          alt="THERS"
          className="w-12 h-12 rounded-full object-cover"
        />
      </div>

      {/* IZQUIERDA */}
      <div className="hidden md:flex w-1/2 relative items-center justify-center bg-black overflow-hidden">
        
        <img
          src={collage}
          alt="Collage redes sociales"
          className="w-full h-full object-cover opacity-80"
        />

        <div className="absolute inset-0 bg-black/40"></div>

        <div className="absolute inset-0 flex items-center justify-center text-center px-6">
          <h1 className="text-white text-4xl md:text-5xl font-extrabold">
            Conecta con el mundo
          </h1>
        </div>

      </div>

      {/* DERECHA */}
      <div className="w-full md:w-1/2 flex flex-col justify-center px-10 max-w-md mx-auto">

        <h1 className="text-5xl font-extrabold mb-6 leading-tight">
          Lo que está pasando ahora
        </h1>

        <h2 className="text-2xl font-bold mb-6">
          Únete hoy
        </h2>

        <button className="w-full flex items-center justify-center gap-3 border py-3 rounded-full font-semibold">
          <FcGoogle size={20} />
          Registrarse con Google
        </button>

        <button className="w-full flex items-center justify-center gap-3 bg-black text-white py-3 rounded-full font-semibold mt-3">
          <FaApple size={18} />
          Registrarse con Apple
        </button>

        <div className="flex items-center my-4">
          <div className="flex-1 h-px bg-gray-300"></div>
          <span className="px-3 text-gray-500">o</span>
          <div className="flex-1 h-px bg-gray-300"></div>
        </div>

        <button
          onClick={() => navigate("/register")}
          className="w-full bg-black text-white py-3 rounded-full font-bold"
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

        <div className="mt-10 text-sm font-semibold flex justify-center gap-2 items-center">
          <span className="font-bold">¿Ya tienes una cuenta?</span>

          <button
            onClick={() => navigate("/login")}
            className="bg-blue-500 text-white px-4 py-2 rounded-full font-bold hover:bg-blue-600 transition"
          >
            Iniciar sesión
          </button>
        </div>

      </div>
    </div>
  );
}