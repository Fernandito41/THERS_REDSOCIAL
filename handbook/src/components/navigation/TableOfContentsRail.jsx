// TableOfContentsRail — riel derecho de Tabla de Contenidos (DS-001 §9.13).
//
// Módulo 6 (Search + Scroll-spy): implementación completa del ítem activo.
//
// DS-001 §9.13 especificación:
//   - Ancho fijo 220px (token toc-rail, DS-001 §8.1)
//   - Solo H2 y H3 del documento actual
//   - H3 con indentación space-4 (16px) respecto a H2
//   - Ítem activo (scroll-spy): texto color-primary + barra izquierda 2px
//     mismo lenguaje visual que el ítem activo del Sidebar (DS-001 §9.2)
//   - hidden en mobile/tablet (lg:block — DS-001 §11)
//
// El border-l-2 es siempre 2px (solo cambia el color) para evitar layout shift
// al cambiar el ítem activo — mismo patrón que el Sidebar expandido.
//
// activeId proviene del TocContext, actualizado por el IntersectionObserver
// en DocumentPage.

import { useToc } from '../../providers/TocContext'

function TableOfContentsRail() {
  const { headings, activeId } = useToc()

  return (
    <aside
      className="hidden shrink-0 overflow-y-auto lg:block"
      style={{
        width: '220px',
        borderLeft: '1px solid var(--color-border)',
        backgroundColor: 'var(--color-bg)',
      }}
      aria-label="Tabla de contenidos"
    >
      <div className="p-4">
        <p
          className="mb-3 text-xs font-semibold uppercase tracking-wider"
          style={{ color: 'var(--color-text-secondary)' }}
        >
          En esta página
        </p>

        {headings.length === 0 ? (
          <p className="text-xs" style={{ color: 'var(--color-text-disabled)' }}>
            Sin secciones
          </p>
        ) : (
          // DS-001 §9.13: H2 sin indent, H3 con indent space-4
          // El border-l-2 siempre presente (solo cambia el color) para evitar
          // layout shift — mismo patrón que Sidebar expandido (DS-001 §9.2)
          <nav aria-label="Secciones del documento">
            <ul className="space-y-0.5">
              {headings.map((heading) => {
                const isActive = heading.id === activeId
                return (
                  <li
                    key={heading.id}
                    style={{ paddingLeft: heading.level === 3 ? '12px' : '0' }}
                  >
                    <a
                      href={`#${heading.id}`}
                      className="block truncate border-l-2 py-1 pl-2 text-xs leading-relaxed transition-colors"
                      style={{
                        borderColor: isActive
                          ? 'var(--color-primary)'
                          : 'transparent',
                        color: isActive
                          ? 'var(--color-primary)'
                          : 'var(--color-text-secondary)',
                        textDecoration: 'none',
                        fontWeight: isActive ? 500 : 400,
                      }}
                      onMouseEnter={(e) => {
                        if (!isActive) {
                          e.currentTarget.style.color = 'var(--color-text-primary)'
                        }
                      }}
                      onMouseLeave={(e) => {
                        if (!isActive) {
                          e.currentTarget.style.color =
                            'var(--color-text-secondary)'
                        }
                      }}
                      aria-current={isActive ? 'location' : undefined}
                    >
                      {heading.text}
                    </a>
                  </li>
                )
              })}
            </ul>
          </nav>
        )}
      </div>
    </aside>
  )
}

export default TableOfContentsRail
