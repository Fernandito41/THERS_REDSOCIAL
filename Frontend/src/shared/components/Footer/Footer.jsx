import { Link } from "react-router-dom";
import BrandMark from "@shared/components/BrandMark";
import { FOOTER_GROUPS } from "./footerLinks";
import FooterSection from "./FooterSection";

export default function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="border-t border-line dark:border-line-dark bg-surface dark:bg-surface-dark">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-10 sm:py-12">
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-8 sm:gap-6">
          <div className="sm:col-span-1">
            <Link to="/">
              <BrandMark />
            </Link>
            {/* Placeholder: descripción provisional, pendiente de copy definitivo */}
            <p className="mt-3 text-sm text-muted dark:text-muted-dark max-w-xs">
              Un espacio para compartir momentos, ideas y lo que resuena contigo. (Texto provisional)
            </p>
          </div>

          <div className="sm:col-span-3 grid grid-cols-1 sm:grid-cols-3 gap-x-6">
            {FOOTER_GROUPS.map((group) => (
              <FooterSection key={group.id} title={group.title} links={group.links} />
            ))}
          </div>
        </div>

        <div className="mt-10 pt-6 border-t border-line dark:border-line-dark">
          <p className="text-xs text-muted dark:text-muted-dark">© {year} THERS. Todos los derechos reservados.</p>
        </div>
      </div>
    </footer>
  );
}
