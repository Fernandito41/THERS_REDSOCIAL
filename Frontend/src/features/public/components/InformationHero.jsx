import { Link } from "react-router-dom";
import PhoneMockup from "./PhoneMockup";
import RevealOnScroll from "./RevealOnScroll";

export default function InformationHero() {
  return (
    <section className="max-w-6xl mx-auto px-4 sm:px-6 pt-16 sm:pt-24 pb-12 grid gap-12 md:grid-cols-2 items-center">
      <RevealOnScroll>
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-ink dark:text-ink-dark leading-[1.05]">
          THERS conecta personas, ideas y momentos reales.
        </h1>
        <p className="mt-5 text-base sm:text-lg text-muted dark:text-muted-dark max-w-md">
          Compartí historias, descubrí comunidades y conversá de forma auténtica desde un solo lugar.
        </p>
        <Link
          to="/"
          className="mt-8 inline-flex items-center justify-center bg-pulse-600 hover:bg-pulse-700 text-white font-semibold px-6 py-3 rounded-full shadow-glow transition-colors"
        >
          Explorar THERS
        </Link>
      </RevealOnScroll>

      <RevealOnScroll className="flex justify-center">
        <PhoneMockup />
      </RevealOnScroll>
    </section>
  );
}
