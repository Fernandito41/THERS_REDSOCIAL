import { NavLink, Outlet, useOutletContext, useParams } from "react-router-dom";
import Icon from "@shared/components/Icon";
import { useLanguage } from "@shared/i18n";
import { SETTINGS_SECTIONS } from "@/app/layout/thers/navigation";
import { SETTINGS_CONTENT } from "../data/settingsSections";

/**
 * Shell de Configuración — REF-SET-01..12.
 *
 * Composición de la referencia: migas de pan arriba, y debajo una rejilla de
 * 12 columnas con el menú local de ajustes a la izquierda (4 columnas) y el
 * panel de la sección a la derecha (8 columnas).
 *
 * VARIANTE DE SHELL: `settings` — sidebar de 256px y neutrales Luminous, que
 * es lo que muestran 9 de las 12 referencias. Las otras tres (REF-SET-09/10/11)
 * usan 288px y slate; se unifican aquí a propósito, porque si no la sidebar
 * cambiaría de ancho y de color al navegar dentro del mismo menú. Desviación
 * registrada en docs/THERS_REFERENCE_MANIFEST.md §5.1 y en THERS_VISUAL_QA.md.
 *
 * NO se reproducen dos elementos de la referencia:
 *  · «Sincronización segura activa» en la barra de estado — el archivo maestro
 *    §10.2 la nombra expresamente como estado que no puede ser fijo del cliente.
 *  · «Nivel de blindaje 85%» en el menú lateral — es una puntuación de
 *    seguridad inventada; no hay nada que la calcule.
 */
export default function SettingsLayout() {
  const { t } = useLanguage();
  const context = useOutletContext();
  const { section } = useParams();
  const current = SETTINGS_CONTENT[section];

  return (
    <div className="mx-auto flex w-full max-w-7xl flex-col gap-6 py-4">
      <nav aria-label="Ruta de navegación" className="flex items-center gap-2 px-1">
        <ol className="flex flex-wrap items-center gap-2 text-label-md text-th-fg-muted">
          <li>
            <NavLink to="/settings" className="th-focus-ring hover:text-th-fg-strong">
              Configuración
            </NavLink>
          </li>
          {current && (
            <>
              <li aria-hidden="true">
                <Icon name="chevron_right" size={16} />
              </li>
              <li className="font-bold text-th-fg-strong" aria-current="page">
                {current.title}
              </li>
            </>
          )}
        </ol>
      </nav>

      <div className="grid grid-cols-12 items-start gap-6">
        <nav
          aria-label="Secciones de configuración"
          className="col-span-12 flex flex-col gap-1 rounded-th-card border border-th-border bg-th-surface p-4 shadow-th-card lg:col-span-4"
        >
          <p className="px-2 pb-2 text-label-md font-bold uppercase tracking-wider text-th-fg-subtle">
            Ajustes del perfil
          </p>

          {SETTINGS_SECTIONS.map((item) => (
            <NavLink
              key={item.id}
              to={`/settings/${item.id}`}
              className={({ isActive }) =>
                `flex min-h-[44px] items-center gap-3 rounded-th-input px-3 py-2.5 text-label-lg transition-colors th-focus-ring ${
                  isActive
                    ? "bg-th-brand-soft font-bold text-th-brand-fg"
                    : "font-medium text-th-fg-muted hover:bg-th-surface-subtle hover:text-th-fg-strong"
                }`
              }
            >
              {({ isActive }) => (
                <>
                  <Icon
                    name={item.icon}
                    size={20}
                    fill={isActive ? 1 : 0}
                    className={isActive ? "text-th-brand" : "text-th-fg-subtle"}
                  />
                  <span className="truncate">{t(item.labelKey)}</span>
                </>
              )}
            </NavLink>
          ))}
        </nav>

        <div className="col-span-12 flex flex-col gap-6 lg:col-span-8">
          <Outlet context={context} />
        </div>
      </div>
    </div>
  );
}
