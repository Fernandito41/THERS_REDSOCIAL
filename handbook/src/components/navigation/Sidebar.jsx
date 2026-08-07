// Sidebar — plano Global y Local de navegación (WF-001 §5).
//
// Módulo 7 (Responsive + Sequential Navigation): soporte de drawer mobile.
//
// DS-001 §11 responsive:
//   Desktop (≥ lg):  Sidebar estático fijo, siempre visible.
//   Mobile/Tablet:   Sidebar oculto; se activa como Drawer superpuesto
//                    cuando DrawerContext.isOpen = true (botón hamburger del Header).
//                    El Drawer siempre muestra la variante expandida (icon + nombre).
//
// Los NavLinks en el drawer llaman a close() en onClick para cerrar
// el drawer al navegar — el DrawerProvider también cierra en cambio de pathname.
//
// Variante `variant` solo aplica al sidebar de desktop (comportamiento heredado
// de Módulo 3). El drawer mobile siempre es expanded independientemente del variant.

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
  X,
} from 'lucide-react'

import { ROOT_CATEGORIES } from '../../routes/routes'
import { useDrawer } from '../../providers/DrawerContext'

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

// ── Nav items expandidos ──────────────────────────────────────────────────
// Extraído como función para reutilizarlo en desktop y mobile drawer
// sin duplicar el JSX de cada NavLink (DRY — FAS-001 §5 cohesión).
// onNavigate: llamado onClick en cada ítem — cierra el drawer en mobile.
function ExpandedNavItems({ onNavigate }) {
  return (
    <ul className="space-y-1 p-4">
      {ROOT_CATEGORIES.map((category) => {
        const Icon = ICON_MAP[category.icon]
        return (
          <li key={category.path}>
            <NavLink
              to={category.path}
              onClick={onNavigate}
              className={({ isActive }) =>
                [
                  'flex items-center gap-3 rounded-md border-l-2 px-3 py-2 text-sm transition-colors',
                  isActive
                    ? 'border-[var(--color-primary)] text-[var(--color-primary)]'
                    : 'border-transparent text-[var(--color-text-primary)]',
                ].join(' ')
              }
              style={({ isActive }) =>
                isActive ? { backgroundColor: 'var(--color-primary-8)' } : {}
              }
              onMouseEnter={(e) => {
                if (!e.currentTarget.dataset.active)
                  e.currentTarget.style.backgroundColor =
                    'var(--color-sidebar-item-hover)'
              }}
              onMouseLeave={(e) => {
                if (!e.currentTarget.dataset.active)
                  e.currentTarget.style.backgroundColor = ''
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
  )
}

// ── Componente ───────────────────────────────────────────────────────────
function Sidebar({ variant = 'expanded' }) {
  const { isOpen, close } = useDrawer()
  const isCollapsed = variant === 'collapsed'

  return (
    <>
      {/* ── Desktop sidebar — hidden en mobile/tablet (< lg) ─────────────
          Mismo comportamiento que en Módulos 3–6: estático, siempre visible
          en pantallas lg+. El variant controla collapsed vs expanded.     */}
      <aside
        className="hidden shrink-0 overflow-y-auto lg:block"
        style={{
          width: isCollapsed ? '64px' : '260px',
          backgroundColor: 'var(--color-surface)',
          borderRight: '1px solid var(--color-border)',
        }}
        aria-label="Navegación del Handbook"
      >
        <nav>
          {isCollapsed ? (
            // Variante colapsada — franja de iconos (HomeLayout)
            <ul className="flex flex-col items-center gap-1 py-6">
              {ROOT_CATEGORIES.map((category) => {
                const Icon = ICON_MAP[category.icon]
                return (
                  <li key={category.path}>
                    <NavLink
                      to={category.path}
                      title={category.name}
                      className="flex h-10 w-10 items-center justify-center rounded-md transition-colors"
                      style={{ color: 'var(--color-text-secondary)' }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.backgroundColor =
                          'var(--color-sidebar-item-hover)'
                        e.currentTarget.style.color =
                          'var(--color-text-primary)'
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
                      <span className="sr-only">{category.name}</span>
                    </NavLink>
                  </li>
                )
              })}
            </ul>
          ) : (
            // Variante expandida — icon + nombre
            <ExpandedNavItems onNavigate={close} />
          )}
        </nav>
      </aside>

      {/* ── Mobile drawer — solo visible en < lg cuando isOpen = true ────
          DS-001 §11: Sidebar en mobile es binario (oculto | drawer completo).
          El drawer siempre muestra la variante expandida independientemente
          del prop variant del desktop (DS-001 §10 / §11).                */}
      {isOpen && (
        <>
          {/* Overlay — color-overlay cubre el contenido detrás del drawer */}
          <div
            className="fixed inset-0 z-20 lg:hidden"
            style={{ backgroundColor: 'var(--color-overlay)' }}
            onClick={close}
            aria-hidden="true"
          />

          {/* Panel del drawer */}
          <aside
            className="fixed inset-y-0 left-0 z-30 flex w-64 flex-col overflow-y-auto lg:hidden"
            style={{
              backgroundColor: 'var(--color-surface)',
              borderRight: '1px solid var(--color-border)',
            }}
            aria-label="Menú de navegación"
          >
            {/* Header del drawer — wordmark + botón de cierre */}
            <div
              className="flex h-16 shrink-0 items-center justify-between px-4"
              style={{ borderBottom: '1px solid var(--color-border)' }}
            >
              <span
                className="text-base font-bold"
                style={{ color: 'var(--color-text-primary)' }}
              >
                THERS
              </span>
              <button
                type="button"
                onClick={close}
                className="flex h-8 w-8 items-center justify-center rounded-md transition-colors"
                style={{ color: 'var(--color-text-secondary)' }}
                aria-label="Cerrar menú"
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor =
                    'var(--color-sidebar-item-hover)'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'transparent'
                }}
              >
                <X size={18} strokeWidth={2} aria-hidden="true" />
              </button>
            </div>

            {/* Nav items — siempre expanded en el drawer */}
            <nav className="flex-1 overflow-y-auto">
              <ExpandedNavItems onNavigate={close} />
            </nav>
          </aside>
        </>
      )}
    </>
  )
}

export default Sidebar
