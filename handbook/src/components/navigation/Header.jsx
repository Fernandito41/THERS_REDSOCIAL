// Header (TopNav) — chrome persistente del App Shell (DS-001 §9.1).
//
// Módulo 4 (Design System Components):
// - ThemeToggle: toggle de tema claro/oscuro (DS-001 §9 / §10).
// - GitHub: enlace externo al repositorio con icono Lucide Github (DS-001 §9.1).
// - Buscador permanece como placeholder visual (Módulo 5+: modal Ctrl+K).
//
// El componente es idéntico en las tres plantillas — Header no conoce
// ni le importa qué layout lo contiene (FAS-001 §5: bajo acoplamiento).

import { NavLink } from 'react-router-dom'
import { ExternalLink } from 'lucide-react'
import ThemeToggle from '../ui/ThemeToggle'

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
          Área de toque 40×40px mínimo (DS-001 §12).                     */}
      <div className="flex items-center gap-3">
        <ThemeToggle />
        <a
          href="https://github.com/Fernandito41/THERS_REDSOCIAL_2026"
          target="_blank"
          rel="noopener noreferrer"
          className="flex h-10 w-10 items-center justify-center rounded-md transition-colors"
          style={{
            border: '1px solid var(--color-border)',
            color: 'var(--color-text-secondary)',
          }}
          aria-label="Ver repositorio en GitHub"
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor =
              'var(--color-sidebar-item-hover)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = 'transparent'
          }}
        >
          <ExternalLink size={18} strokeWidth={2} aria-hidden="true" />
        </a>
      </div>
    </header>
  )
}

export default Header
