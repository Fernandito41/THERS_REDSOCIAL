import { Link } from "react-router-dom";
import RevealOnScroll from "./RevealOnScroll";

export default function InformationCta() {
  return (
    <section className="bg-surface dark:bg-surface-dark border-t border-line dark:border-line-dark">
      <RevealOnScroll className="max-w-3xl mx-auto px-4 sm:px-6 py-20 text-center">
        <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-ink dark:text-ink-dark">
          Tu próxima historia comienza acá.
        </h2>
        <p className="mt-3 text-muted dark:text-muted-dark">
          Cada vez más personas ya están compartiendo lo que aman en THERS.
        </p>
        <Link
          to="/register"
          className="mt-8 inline-flex items-center justify-center bg-pulse-600 hover:bg-pulse-700 text-white font-semibold px-6 py-3 rounded-full shadow-glow transition-colors"
        >
          Crear cuenta
        </Link>
      </RevealOnScroll>
    </section>
  );
}
