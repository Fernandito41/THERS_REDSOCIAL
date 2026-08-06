// Header (TopNav) — chrome persistente del App Shell (DS-001 §9.1).
//
// Módulo 3 (Navigation System):
// - sticky top-0 z-10 — permanece fijo sobre el contenido (DS-001 §9.1:
//   "Permanece fijo con z-index por encima del contenido pero por debajo
//   de modales"). Corrección respecto a Módulo 2: el Header era `shrink-0`
//   dentro de un flex column, lo que lo fijaba visualmente pero no era
//   verdaderamente sticky — ahora es sticky independiente del scroll.
// - Aplica tokens de color DS-001 §4 en lugar de clases Tailwind gray-*:
//   bg-gray-50 → var(--color-surface) | border-gray-200 → var(--color-border)
//   text-gray-900 → var(--color-text-primary) | text-gray-400 → var(--color-text-secondary)
//   (DS-001 §4 — regla vinculante: ningún color hardcodeado en componentes)
// - Logo como NavLink funcional a Home (PV-001 Parte 1 §1:
//   "un click, desde cualquier punto del Handbook, regresa a Home").
// - Buscador y acciones permanecen como placeholders (Módulo 4+).
//
// El componente es idéntico en las tres plantillas — Header no conoce
// ni le importa qué layout lo contiene (FAS-001 §5: bajo acoplamiento).

import { NavLink } from 'react-router-dom'

function Header() {
  return (
    <header
      className="sticky top-0 z-10 flex h-16 shrink-0 items-center justify-between px-6"
      style={{
        backgroundColor: 'var(--color-surface)',
        borderBottom: '1px solid var(--color-border)',
      }}
    >
      {/* Logo / wordmark — NavLink a Home (PV-001 Parte 1 §1).
          Inter Bold, altura ≥ 20px (DS-001 §3.2). */}
      <NavLink
        to="/"
        className="flex items-baseline gap-2"
        style={{ textDecoration: 'none' }}
      >
        <span
          className="text-lg font-bold"
          style={{ color: 'var(--color-text-primary)' }}
        >
          THERS
        </span>
        <span
          className="text-sm"
          style={{ color: 'var(--color-text-secondary)' }}
        >
          Engineering Handbook
        </span>
      </NavLink>

      {/* Buscador — placeholder visual (PV-001 Parte 1 §1).
          320px ancho, 40px alto, border 1px color-border, radio 6px.
          Módulo 4+: modal Ctrl+K, búsqueda client-side (ARC-001 §11). */}
      <div
        className="flex w-80 items-center justify-between rounded-md px-3 py-2 text-sm"
        style={{
          border: '1px solid var(--color-border)',
          backgroundColor: 'var(--color-surface-raised)',
          color: 'var(--color-text-secondary)',
        }}
        aria-hidden="true"
      >
        <span>Buscar en el Handbook...</span>
        <span
          className="text-xs font-mono"
          style={{ color: 'var(--color-text-disabled)' }}
        >
          Ctrl+K
        </span>
      </div>

      {/* Acciones — toggle de tema + enlace GitHub (DS-001 §9.1).
          Área de toque 40×40px (DS-001 §12 — mínimo 24×24px).
          Módulo 4+: ThemeToggle (DS-001 §9, DS-001 §10) + enlace real. */}
      <div className="flex items-center gap-3" aria-hidden="true">
        <span
          className="flex h-10 w-10 items-center justify-center rounded-md"
          style={{ border: '1px solid var(--color-border)' }}
        />
        <span
          className="flex h-10 w-10 items-center justify-center rounded-md"
          style={{ border: '1px solid var(--color-border)' }}
        />
      </div>
    </header>
  )
}

export default Header
