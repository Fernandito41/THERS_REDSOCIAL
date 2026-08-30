// Footer — DS-001 §9.3.
//
// Presente solo en Home y páginas índice de categoría.
// No se incluye en DocumentPage (el scroll largo haría que el Footer
// no agregara valor y añadiría scroll innecesario — DS-001 §9.3).
//
// Contenido: versión del Handbook · link a "Cómo contribuir" · copyright.
// Tipografía text-caption (12px), color text-secondary / text-disabled.
// Padding vertical space-8 (32px), fondo color-surface con borde superior.
//
// La versión se actualiza manualmente al cierre de cada módulo hasta que
// el Content Layer aporte datos dinámicos de versioning (ARC-001 §1 capa 1).

import { Link } from 'react-router-dom'

const HANDBOOK_VERSION = '0.4.0'

function Footer() {
  return (
    <footer
      className="mt-auto border-t px-8 py-8"
      style={{
        borderColor: 'var(--color-border)',
        backgroundColor: 'var(--color-surface)',
      }}
    >
      <div className="mx-auto flex max-w-5xl flex-col items-center gap-2 text-center sm:flex-row sm:justify-between sm:text-left">
        <p className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>
          THERS Engineering Handbook{' '}
          <span style={{ color: 'var(--color-text-disabled)' }}>
            v{HANDBOOK_VERSION}
          </span>
        </p>

        <Link
          to="/meta/como-contribuir"
          className="text-xs"
          style={{ color: 'var(--color-text-secondary)', textDecoration: 'none' }}
          onMouseEnter={(e) => {
            e.currentTarget.style.color = 'var(--color-primary)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.color = 'var(--color-text-secondary)'
          }}
        >
          Cómo contribuir
        </Link>

        <p className="text-xs" style={{ color: 'var(--color-text-disabled)' }}>
          © {new Date().getFullYear()} Equipo THERS
        </p>
      </div>
    </footer>
  )
}

export default Footer
