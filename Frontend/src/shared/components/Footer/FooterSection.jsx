import { IoChevronDown } from "react-icons/io5";
import FooterLink from "./FooterLink";
import FooterExpandableItem from "./FooterExpandableItem";

// Un link normal navega directo (FooterLink). Un link con `children` (hoy
// solo "Información") se expande in-place en vez de navegar
// (FooterExpandableItem) -- el resto de los ítems del footer no se ve
// afectado, no tienen `children`.
function FooterItem({ link }) {
  if (link.children) {
    return <FooterExpandableItem label={link.label} items={link.children} />;
  }
  return <FooterLink to={link.to}>{link.label}</FooterLink>;
}

// Desktop/tablet: columna estática siempre abierta.
// Mobile: <details>/<summary> nativo -- accordion accesible (teclado, lector
// de pantalla) sin necesidad de estado ni JS propio.
export default function FooterSection({ title, links }) {
  return (
    <div>
      <div className="hidden sm:block">
        <h3 className="text-sm font-semibold text-ink dark:text-ink-dark mb-3">{title}</h3>
        <ul className="space-y-2.5">
          {links.map((link) => (
            <li key={link.label}>
              <FooterItem link={link} />
            </li>
          ))}
        </ul>
      </div>

      <details className="group sm:hidden border-b border-line dark:border-line-dark">
        <summary className="flex items-center justify-between py-3.5 text-sm font-semibold text-ink dark:text-ink-dark cursor-pointer list-none [&::-webkit-details-marker]:hidden">
          {title}
          <IoChevronDown size={16} className="text-muted transition-transform group-open:rotate-180" aria-hidden="true" />
        </summary>
        <ul className="space-y-2.5 pb-4">
          {links.map((link) => (
            <li key={link.label}>
              <FooterItem link={link} />
            </li>
          ))}
        </ul>
      </details>
    </div>
  );
}
