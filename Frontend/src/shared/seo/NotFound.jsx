import { Link } from "react-router-dom";

// Ruta comodín. Es una página real con `noindex` (RouteSeo no la tiene en la
// tabla). Sin HTTP 404 real —es una SPA estática— Google la ve como "soft 404";
// el noindex evita que entre al índice. El 404 de servidor lo resuelve el
// hosting (ADR-033 §4).
export default function NotFound() {
  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-24 text-center">
      <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-ink dark:text-ink-dark">
        No encontramos esta página
      </h1>
      <p className="mt-4 text-muted dark:text-muted-dark">
        Puede que el enlace esté roto o que la página haya cambiado de dirección.
      </p>
      <Link
        to="/"
        className="mt-8 inline-flex text-sm font-semibold px-4 py-2 rounded-full bg-pulse-600 hover:bg-pulse-700 text-white transition"
      >
        Ir al inicio
      </Link>
    </div>
  );
}
