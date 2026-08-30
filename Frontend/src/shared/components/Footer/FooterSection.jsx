import FooterLink from "./FooterLink";

// Una columna de grupo del footer: label en versalita + lista de enlaces
// planos. Siempre visible en todos los anchos (sin <details>): son listas
// cortas y verlas completas es mas claro que un acordeon. La jerarquia
// label vs enlace la da el tamano/versalita/tracking, no el color.
export default function FooterSection({ title, links, tone = "dark" }) {
  const labelColor =
    tone === "light" ? "text-footer-link-soft dark:text-footer-link" : "text-footer-link";

  return (
    <div>
      <h3 className={`text-xs font-medium uppercase tracking-[0.08em] ${labelColor}`}>
        {title}
      </h3>
      <ul className="mt-4 space-y-3">
        {links.map((link) => (
          <li key={link.to}>
            <FooterLink to={link.to} tone={tone}>
              {link.label}
            </FooterLink>
          </li>
        ))}
      </ul>
    </div>
  );
}
