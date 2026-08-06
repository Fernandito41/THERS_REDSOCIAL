// TableOfContentsRail — riel derecho de Tabla de Contenidos (DS-001 §9.13).
//
// Módulo 3 (Navigation System): placeholder estructural.
// Establece el ancho fijo y la posición correcta en el layout de 3 columnas
// de DocumentLayout, sin implementar la lógica real aún.
//
// Especificación DS-001 §9.13 / PV-001 Parte 2 §5 — qué debe ser en Módulo 4+:
//   - Ancho fijo 220px (token toc-rail, DS-001 §8.1)
//   - position sticky respecto al scroll vertical de la página
//   - Ítem activo (scroll-spy): text-color-primary + barra izquierda 2px
//     Mismo lenguaje visual que el ítem activo del Sidebar (DS-001 §9.2)
//   - Solo H2 y H3 del documento actual (máx. 2 niveles de profundidad)
//   - H3 de sección no activa: colapsados (PV-001 Parte 2 §5 — Divulgación
//     progresiva aplicada al TOC)
//   - En mobile/tablet: se convierte en acordeón "En esta página" al inicio
//     del contenido (DS-001 §11 / WF-001 §5 plano Contextual)
//
// Plano de navegación: Contextual (WF-001 §5) — responde "¿dónde estoy dentro
// de este documento?". Solo existe en DocumentLayout, nunca en Home ni Category.

function TableOfContentsRail() {
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
      {/* Placeholder — scroll-spy y lógica de headings en Módulo 4+
          (requiere parsing de headings del contenido MDX renderizado) */}
      <div className="p-4">
        <p
          className="mb-3 text-xs font-semibold uppercase tracking-wider"
          style={{ color: 'var(--color-text-secondary)' }}
        >
          En esta página
        </p>
        <div
          className="flex items-center justify-center rounded-md border border-dashed py-8 text-xs"
          style={{
            borderColor: 'var(--color-border)',
            color: 'var(--color-text-disabled)',
          }}
        >
          TOC — Módulo 4+
        </div>
      </div>
    </aside>
  )
}

export default TableOfContentsRail
