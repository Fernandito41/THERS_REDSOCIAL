// DocumentPage — página de documento individual.
//
// Módulo 4 (Design System Components):
// - Usa el componente Breadcrumbs real (DS-001 §9.4) en lugar del inline de M3.
// - Usa el componente Badge real (DS-001 §9.11) en lugar del span inline de M3.
//
// La plantilla dominante del Handbook (WF-001 §3.2):
// "más del 90% del contenido del Handbook vive aquí".
//
// Qué falta para la especificación completa (PV-001 Parte 2 / Módulo 5+):
//   - Contenido MDX renderizado (ARC-001 §1 capa 2 — Build Layer)
//   - Prev/Next (WF-001 §5 plano Secuencial — requiere orden del frontmatter)
//   - Documentos relacionados (PV-001 Parte 2 §9)
//   - Scroll-spy en TOC (DS-001 §9.13)
//
// FAS-001 §7 — independencia entre páginas: DocumentPage no depende del
// estado de ninguna otra página, solo de los params de la URL.

import { useParams } from 'react-router-dom'
import { ROOT_CATEGORIES } from '../routes/routes'
import Breadcrumbs from '../components/ui/Breadcrumbs'
import Badge from '../components/ui/Badge'

function DocumentPage() {
  const { category: categorySlug, doc: docSlug } = useParams()

  // Categoría padre del documento (para el encabezado de contexto)
  const parentCategory = ROOT_CATEGORIES.find(
    (c) => c.path === `/${categorySlug}`,
  )

  return (
    // Columna de lectura — max-width 760px (DS-001 §8.1 container-content)
    <div
      className="mx-auto w-full px-8 py-8"
      style={{ maxWidth: '760px' }}
    >
      {/* ── Breadcrumbs (DS-001 §9.4) ────────────────────────────────────
          Componente real del Design System — Módulo 4.
          El título del documento sigue siendo el slug hasta que el Content
          Layer (Módulo 5+) provea el frontmatter con el título real.       */}
      <div className="mb-6">
        <Breadcrumbs
          items={[
            { label: 'Inicio', href: '/' },
            ...(parentCategory
              ? [{ label: parentCategory.name, href: parentCategory.path }]
              : []),
            {
              label: docSlug
                .split('-')
                .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
                .join(' '),
            },
          ]}
        />
      </div>

      {/* ── Encabezado del documento ──────────────────────────────────────
          PV-001 Parte 2 §4 — Fila 1: código + título (H1).
          En Módulo 3: muestra el slug de la URL como título provisional.
          En Módulo 4+: se alimenta desde el frontmatter del archivo MDX.   */}
      <header className="mb-8">
        {/* Código del documento — JetBrains Mono, text-caption (DS-001 §5.2) */}
        <p
          className="mb-1 font-mono text-xs"
          style={{ color: 'var(--color-text-secondary)' }}
        >
          {categorySlug}/{docSlug}
        </p>

        {/* Título H1 — text-h1 (DS-001 §5.2: 30px/700). Uno solo por página. */}
        <h1
          className="text-3xl font-bold leading-tight"
          style={{ color: 'var(--color-text-primary)' }}
        >
          {docSlug
            .split('-')
            .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
            .join(' ')}
        </h1>

        {/* Badge de estado (DS-001 §9.11) — Módulo 4 */}
        <div className="mt-3 flex items-center gap-3">
          <Badge variant="draft" />
          <span
            className="text-xs"
            style={{ color: 'var(--color-text-secondary)' }}
          >
            Contenido provisional — MDX en Módulo 5+
          </span>
        </div>

        <hr className="mt-6" style={{ borderColor: 'var(--color-border)' }} />
      </header>

      {/* ── Área de contenido principal ───────────────────────────────────
          PV-001 Parte 2 §6 — max-width 760px, interlineado 1.7.
          En Módulo 4+: renderizará el MDX procesado por el Build Layer
          (ARC-001 §1 capa 2: Vite + plugin MDX + remark/rehype).           */}
      <main>
        <div
          className="flex items-center justify-center rounded-lg border border-dashed py-16 text-center"
          style={{
            borderColor: 'var(--color-border)',
          }}
        >
          <div>
            <p
              className="text-sm font-medium"
              style={{ color: 'var(--color-text-secondary)' }}
            >
              Contenido MDX
            </p>
            <p
              className="mt-1 text-xs"
              style={{ color: 'var(--color-text-disabled)' }}
            >
              El rendering de Markdown/MDX se implementa en el Módulo 4+
              (ARC-001 §1 — Build Layer: Vite + plugin MDX).
            </p>
          </div>
        </div>
      </main>
    </div>
  )
}

export default DocumentPage
