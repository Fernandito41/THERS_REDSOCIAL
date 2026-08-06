// Sidebar — plano Global y Local de navegación (WF-001 §5).
//
// Módulo 3 (Navigation System): implementación completa con NavLinks,
// iconos Lucide y active state oficial de DS-001.
//
// Acepta un prop `variant`:
//
//   'collapsed'  →  HomeLayout — franja de 64px con solo iconos.
//                   Sin estado activo en ningún ítem (PV-001 Parte 1 §2:
//                   "en Home, ningún ícono se muestra en estado activo").
//                   Un click navega a la Category Index de esa categoría.
//
//   'expanded'   →  CategoryLayout / DocumentLayout — panel de 260px con
//                   icono + nombre. Estado activo per DS-001 §9.2:
//                   fondo color-primary al 8% + barra izquierda 2px
//                   en color-primary + texto color-primary.
//                   NavLink hace isActive=true cuando la ruta coincide o
//                   empieza con el path de la categoría (comportamiento
//                   default de React Router — activa tanto /ingenieria como
//                   /ingenieria/frontend/convenciones-react).
//
// Iconos: Lucide — única biblioteca aprobada (DS-001 §6.1).
// El mapeo nombre → componente vive aquí para mantener routes.js libre
// de dependencias React (FAS-001 §4 — capas con dirección única).
// Mapeo oficial: DS-001 §8 / ARC-001 §8.
//
// Hover — ítems no activos:
//   Fondo color-sidebar-item-hover (token definido en index.css):
//   rgba(0,0,0,0.04) en light / rgba(255,255,255,0.04) en dark.
//   Aproxima "color-surface +4% de opacidad" de DS-001 §10.

import { NavLink } from 'react-router-dom'
import {
  Building2,
  BrainCircuit,
  LayoutTemplate,
  LayoutPanelLeft,
  GraduationCap,
  ListChecks,
  Map,
  Settings,
} from 'lucide-react'

import { ROOT_CATEGORIES } from '../../routes/routes'

// ── Mapeo icono-name → componente Lucide ────────────────────────────────
// Strings definidos en ROOT_CATEGORIES (routes.js) — se resuelven aquí
// para que routes.js no importe React ni Lucide (FAS-001 §4).
const ICON_MAP = {
  'building-2': Building2,
  'brain-circuit': BrainCircuit,
  'layout-template': LayoutTemplate,
  'layout-panel-left': LayoutPanelLeft,
  'graduation-cap': GraduationCap,
  'list-checks': ListChecks,
  map: Map,
  settings: Settings,
}

// ── Componente ───────────────────────────────────────────────────────────
function Sidebar({ variant = 'expanded' }) {
  const isCollapsed = variant === 'collapsed'

  return (
    <aside
      className="shrink-0 overflow-y-auto"
      style={{
        width: isCollapsed ? '64px' : '260px',
        backgroundColor: 'var(--color-surface)',
        borderRight: '1px solid var(--color-border)',
      }}
      aria-label="Navegación del Handbook"
    >
      <nav>
        {isCollapsed ? (
          // ── Variante colapsada (HomeLayout) ──────────────────────────
          // Franja de iconos icon-lg (24px, stroke 2px — DS-001 §6.2).
          // Sin estado activo; hover con fondo sutil (PV-001 Parte 1 §2).
          // El title del <a> provee el tooltip de accesibilidad (DS-001 §12).
          <ul className="flex flex-col items-center gap-1 py-6">
            {ROOT_CATEGORIES.map((category) => {
              const Icon = ICON_MAP[category.icon]
              return (
                <li key={category.path}>
                  <NavLink
                    to={category.path}
                    title={category.name}
                    className="flex h-10 w-10 items-center justify-center rounded-md transition-colors"
                    style={{
                      color: 'var(--color-text-secondary)',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor =
                        'var(--color-sidebar-item-hover)'
                      e.currentTarget.style.color = 'var(--color-text-primary)'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = 'transparent'
                      e.currentTarget.style.color =
                        'var(--color-text-secondary)'
                    }}
                  >
                    {Icon && (
                      <Icon size={24} strokeWidth={2} aria-hidden="true" />
                    )}
                    {/* Texto accesible para lectores de pantalla (DS-001 §12) */}
                    <span className="sr-only">{category.name}</span>
                  </NavLink>
                </li>
              )
            })}
          </ul>
        ) : (
          // ── Variante expandida (CategoryLayout / DocumentLayout) ──────
          // Icono icon-md (20px, stroke 1.5px — DS-001 §6.2) + nombre.
          // Estado activo DS-001 §9.2:
          //   background: color-primary-8 (via style — función de NavLink)
          //   border-left: 2px color-primary
          //   color: color-primary
          // El border-l-2 es siempre 2px (solo cambia el color) para que
          // el layout no salte al activar el ítem (estabilidad visual).
          <ul className="space-y-1 p-4">
            {ROOT_CATEGORIES.map((category) => {
              const Icon = ICON_MAP[category.icon]
              return (
                <li key={category.path}>
                  <NavLink
                    to={category.path}
                    className={({ isActive }) =>
                      [
                        'flex items-center gap-3 rounded-md border-l-2 px-3 py-2 text-sm transition-colors',
                        isActive
                          ? 'border-[var(--color-primary)] text-[var(--color-primary)]'
                          : 'border-transparent text-[var(--color-text-primary)]',
                      ].join(' ')
                    }
                    style={({ isActive }) =>
                      isActive
                        ? { backgroundColor: 'var(--color-primary-8)' }
                        : {}
                    }
                    onMouseEnter={(e) => {
                      // Hover solo en ítems no activos — el activo ya tiene fondo
                      if (!e.currentTarget.dataset.active) {
                        e.currentTarget.style.backgroundColor =
                          'var(--color-sidebar-item-hover)'
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (!e.currentTarget.dataset.active) {
                        e.currentTarget.style.backgroundColor = ''
                      }
                    }}
                  >
                    {Icon && (
                      <Icon
                        size={20}
                        strokeWidth={1.5}
                        aria-hidden="true"
                        style={{ flexShrink: 0 }}
                      />
                    )}
                    <span>{category.name}</span>
                  </NavLink>
                </li>
              )
            })}
          </ul>
        )}
      </nav>
    </aside>
  )
}

export default Sidebar
