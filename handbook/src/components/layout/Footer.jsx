// Footer — chrome de cierre del App Shell (DS-001 §9.3).
//
// Módulo 8 (Footer + Accesibilidad).
//
// DS-001 §9.3: "Solo en Home y páginas índice de categoría."
// PV-001 §7 (Home) y §8 (Category): cuatro bloques horizontales.
//
// Estructura:
//   Versión        | Contribuir | Documentos de referencia | Equipo
//
// Responsive (PV-001 Parte 4 §3):
//   Mobile (< sm): bloques apilados verticalmente, centrados.
//   Tablet (sm):   2 columnas de 2 bloques si caben, si no continúan apilados.
//   Desktop (lg+): fila horizontal de 4 bloques.

import { Link } from 'react-router-dom'

const DOCS_REF = [
  { label: 'ARC-001', to: '/arquitectura/vision-sistema' },
  { label: 'DS-001', to: '/arquitectura/adr-001-monorepo' },
  { label: 'META', to: '/meta/como-contribuir' },
]

function Footer() {
  return (
    <footer
      className="mt-auto shrink-0 px-6 py-8"
      style={{
        borderTop: '1px solid var(--color-border)',
        backgroundColor: 'var(--color-surface)',
      }}
    >
      {/* Cuatro bloques — fila en desktop, columna en mobile (PV-001 §7) */}
      <div
        className="flex flex-col gap-6 text-xs sm:flex-row sm:flex-wrap sm:gap-8"
        style={{ color: 'var(--color-text-secondary)' }}
      >
        {/* ── Versión ──────────────────────────────────────────────────── */}
        <div className="flex flex-col gap-1">
          <span
            className="font-medium"
            style={{ color: 'var(--color-text-primary)' }}
          >
            Versión
          </span>
          <span>THERS Handbook v0.1</span>
          <Link
            to="/roadmap/roadmap-actual"
            className="transition-colors"
            style={{ color: 'var(--color-primary)', textDecoration: 'none' }}
            onMouseEnter={(e) => {
              e.currentTarget.style.textDecoration = 'underline'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.textDecoration = 'none'
            }}
          >
            Ver historial →
          </Link>
        </div>

        {/* ── Contribuir ───────────────────────────────────────────────── */}
        <div className="flex flex-col gap-1">
          <span
            className="font-medium"
            style={{ color: 'var(--color-text-primary)' }}
          >
            Contribuir
          </span>
          <Link
            to="/meta/como-contribuir"
            style={{ color: 'var(--color-primary)', textDecoration: 'none' }}
            onMouseEnter={(e) => {
              e.currentTarget.style.textDecoration = 'underline'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.textDecoration = 'none'
            }}
          >
            Cómo contribuir
          </Link>
        </div>

        {/* ── Documentos de referencia ─────────────────────────────────── */}
        <div className="flex flex-col gap-1">
          <span
            className="font-medium"
            style={{ color: 'var(--color-text-primary)' }}
          >
            Documentos de referencia
          </span>
          <div className="flex flex-wrap gap-3">
            {DOCS_REF.map(({ label, to }) => (
              <Link
                key={label}
                to={to}
                style={{
                  color: 'var(--color-primary)',
                  textDecoration: 'none',
                  fontFamily: 'JetBrains Mono, ui-monospace, monospace',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.textDecoration = 'underline'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.textDecoration = 'none'
                }}
              >
                {label}
              </Link>
            ))}
          </div>
        </div>

        {/* ── Equipo — empujado a la derecha en desktop (PV-001 §7) ────── */}
        <div className="flex flex-col gap-1 sm:ml-auto">
          <span
            className="font-medium"
            style={{ color: 'var(--color-text-primary)' }}
          >
            THERS Team
          </span>
          <span>© 2026 Todos los derechos reservados</span>
        </div>
      </div>
    </footer>
  )
}

export default Footer
