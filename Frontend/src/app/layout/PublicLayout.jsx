import { Outlet, Link } from "react-router-dom";
import BrandMark from "@shared/components/BrandMark";
import { Footer } from "@shared/components/Footer";

// Layout de las páginas públicas/legales (Información, Blog, Ayuda, Popular,
// Ubicaciones, Importar contactos, Privacidad, Términos, Cookies). No requiere
// sesión y es independiente de AppShell -- no comparte nav rail ni mobile nav
// del producto autenticado.
export default function PublicLayout() {
  return (
    <div className="min-h-screen flex flex-col bg-canvas dark:bg-canvas-dark">
      <header className="border-b border-line dark:border-line-dark">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-4">
          <Link to="/">
            <BrandMark />
          </Link>
        </div>
      </header>

      <main className="flex-1">
        <Outlet />
      </main>

      <Footer />
    </div>
  );
}
