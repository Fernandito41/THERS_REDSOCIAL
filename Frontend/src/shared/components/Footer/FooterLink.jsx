import { Link } from "react-router-dom";

// Enlace de navegacion del footer.
// `tone`: "dark" -> sobre el zocalo (variante default).
//         "light" -> sobre superficie clara (variante compact).
// Hover: cambio de color (150ms) + subrayado de 1px en el violeta de acento
// que crece desde la izquierda (transform, 200ms). Bajo prefers-reduced-motion
// el subrayado aparece sin animar. El anillo de foco lo aporta la regla global
// `:focus-visible` de index.css -- no se redefine aqui.
export default function FooterLink({ to, children, tone = "dark" }) {
  const color =
    tone === "light"
      ? "text-footer-link-soft hover:text-footer-link-soft-hover dark:text-footer-link dark:hover:text-footer-link-hover"
      : "text-footer-link hover:text-footer-link-hover";

  return (
    <Link
      to={to}
      className={`group relative inline-block rounded-sm text-sm ${color} transition-colors duration-150`}
    >
      {children}
      <span
        aria-hidden="true"
        className="pointer-events-none absolute left-0 -bottom-0.5 h-px w-full origin-left scale-x-0 bg-footer-accent transition-transform duration-200 ease-strong group-hover:scale-x-100 motion-reduce:transition-none"
      />
    </Link>
  );
}
