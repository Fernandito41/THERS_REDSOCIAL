// Breadcrumbs — DS-001 §9.4.
//
// Tipografía text-body-sm (14px), separador "/" en color-text-secondary.
// Niveles intermedios: links en color-text-secondary → color-primary en hover.
// Nivel actual (último): color-text-primary, sin subrayado, no interactivo.
//
// DS-001 §11 responsive: en mobile se trunca a 2 niveles, en tablet a 3,
// en desktop se muestra completo. Esta implementación muestra el array completo;
// el truncado móvil con elemento "…" expandible se reserva para Módulo 5.
//
// Props:
//   items — array de { label: string, href?: string }
//     - href ausente o undefined → el ítem se renderiza como texto no interactivo.
//     - El último ítem siempre se renderiza como texto (aria-current="page"),
//       independientemente de si tiene href.

import { Link } from 'react-router-dom'

function Breadcrumbs({ items = [] }) {
  if (!items.length) return null

  return (
    <nav aria-label="Breadcrumb">
      <ol className="flex flex-wrap items-center gap-1.5 text-sm">
        {items.map((item, index) => {
          const isLast = index === items.length - 1

          return (
            <li key={index} className="flex items-center gap-1.5">
              {index > 0 && (
                <span
                  aria-hidden="true"
                  style={{ color: 'var(--color-text-secondary)' }}
                >
                  /
                </span>
              )}

              {isLast || !item.href ? (
                <span
                  aria-current={isLast ? 'page' : undefined}
                  style={{ color: 'var(--color-text-primary)' }}
                >
                  {item.label}
                </span>
              ) : (
                <Link
                  to={item.href}
                  style={{
                    color: 'var(--color-text-secondary)',
                    textDecoration: 'none',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.color = 'var(--color-primary)'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.color = 'var(--color-text-secondary)'
                  }}
                >
                  {item.label}
                </Link>
              )}
            </li>
          )
        })}
      </ol>
    </nav>
  )
}

export default Breadcrumbs
