import { useRef } from "react";
import { Link } from "react-router-dom";
import { motion, useInView, useReducedMotion } from "motion/react";
import BrandMark from "@shared/components/BrandMark";
import { FOOTER_GROUPS, LEGAL_LINKS } from "./footerLinks";
import FooterSection from "./FooterSection";
import FooterLink from "./FooterLink";

// Misma curva "ease-out fuerte" que `capsule-in` / la utilidad `ease-strong`
// de tailwind.config.js -- Motion la consume como array.
const EASE_STRONG = [0.16, 1, 0.3, 1];

const DESCRIPTOR = "Publicás en Cápsulas, marcás tu mood y seguís el Pulse de la comunidad.";

// Variante `compact` -- una sola barra fina. Se usa bajo el formulario de
// AuthPage, donde el zocalo completo de 4 columnas sobra. Se queda siempre en
// superficie clara (un slab oscuro debajo de un login seria agresivo).
function CompactFooter() {
  const year = new Date().getFullYear();

  return (
    <footer
      aria-label="Pie de página"
      className="border-t border-footer-line-soft bg-surface dark:border-footer-line dark:bg-surface-dark"
    >
      <div className="mx-auto flex max-w-6xl flex-col items-center gap-4 px-4 py-8 text-center sm:flex-row sm:justify-between sm:px-6 sm:text-left">
        <Link to="/" className="inline-flex transition-transform duration-100 active:scale-[0.98]">
          <BrandMark size="text-base" />
        </Link>

        <nav aria-label="Enlaces legales" className="flex flex-wrap items-center justify-center gap-x-4 gap-y-1">
          {LEGAL_LINKS.map((link) => (
            <FooterLink key={link.to} to={link.to} tone="light">
              {link.label}
            </FooterLink>
          ))}
        </nav>

        <p className="text-xs text-footer-link-soft dark:text-footer-link">
          © <span className="tabular-nums">{year}</span> THERS
        </p>
      </div>
    </footer>
  );
}

// Variante `default` -- el zocalo de producto. Tres franjas: marca + descriptor,
// navegacion en 4 columnas, barra legal. Superficie oscura con profundidad
// (bruma de marca + grano + realce interior; ver `.footer-surface` en
// index.css). Entrada unica y sutil al entrar en viewport.
function DefaultFooter() {
  const year = new Date().getFullYear();
  const ref = useRef(null);
  const reduce = useReducedMotion();
  const inView = useInView(ref, { once: true, margin: "-80px" });

  return (
    <motion.footer
      ref={ref}
      aria-label="Pie de página"
      initial={reduce ? false : { opacity: 0, y: 8 }}
      animate={inView || reduce ? { opacity: 1, y: 0 } : undefined}
      transition={{ duration: reduce ? 0 : 0.4, ease: EASE_STRONG }}
      className="footer-surface border-t border-footer-line text-footer-link"
    >
      <div className="mx-auto max-w-6xl px-4 pb-8 pt-14 sm:px-6 sm:pb-12 sm:pt-20">
        {/* Franja 1 -- marca + descriptor */}
        <div>
          <Link
            to="/"
            className="inline-flex transition-transform duration-100 active:scale-[0.98]"
          >
            <BrandMark size="text-lg" tone="invert" />
          </Link>
          <p className="mt-3 max-w-xs text-sm leading-relaxed text-footer-link">{DESCRIPTOR}</p>
        </div>

        {/* Franja 2 -- navegacion */}
        <nav
          aria-label="Enlaces del pie de página"
          className="mt-12 grid grid-cols-1 gap-x-8 gap-y-10 sm:mt-14 sm:grid-cols-2 lg:grid-cols-4"
        >
          {FOOTER_GROUPS.map((group) => (
            <FooterSection key={group.id} title={group.title} links={group.links} />
          ))}
        </nav>

        {/* Franja 3 -- barra legal */}
        <div className="mt-14">
          <div className="footer-rule" aria-hidden="true" />
          <p className="mt-8 text-xs text-footer-link">
            © <span className="tabular-nums">{year}</span> THERS. Todos los derechos reservados.
          </p>
        </div>
      </div>
    </motion.footer>
  );
}

export default function Footer({ variant = "default" }) {
  return variant === "compact" ? <CompactFooter /> : <DefaultFooter />;
}
