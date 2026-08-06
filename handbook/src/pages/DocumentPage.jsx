// DocumentPage — página de documento individual.
//
// Módulo 3 (Navigation System): placeholder estructural.
//
// La plantilla dominante del Handbook (WF-001 §3.2):
// "más del 90% del contenido del Handbook vive aquí".
//
// En Módulo 3 establece:
//   - La ruta dinámica /:category/:doc funciona y resuelve parámetros
//   - La página se renderiza dentro de DocumentLayout (Header + Sidebar + TOC)
//   - El encabezado muestra la ruta actual para confirmar que la navegación funciona
//
// Qué falta para la especificación completa (PV-001 Parte 2 / Módulo 4+):
//   - Breadcrumbs (DS-001 §9.4) — requieren router + frontmatter
//   - Encabezado del Documento: código, badge de estado, versión, autor (PV-001 Parte 2 §4)
//   - Contenido MDX renderizado (ARC-001 §1 capa 2 — Build Layer)
//   - Prev/Next (WF-001 §5 plano Secuencial — requiere orden del frontmatter)
//   - Documentos relacionados (PV-001 Parte 2 §9)
//   - Footer condensado (PV-001 Parte 2 §10 / DS-001 §9.3 variante)
//
// FAS-001 §7 — independencia entre páginas: DocumentPage no depende del
// estado de ninguna otra página, solo de los params de la URL.

import { useParams, Link } from 'react-router-dom'
import { ROOT_CATEGORIES } from '../routes/routes'

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
      {/* ── Breadcrumb placeholder ────────────────────────────────────────
          DS-001 §9.4 — implementación real en Módulo 4+ (requiere frontmatter).
          En Módulo 3 solo confirma la ruta actual.                          */}
      <nav
        className="mb-6 flex items-center gap-2 text-sm"
        aria-label="Breadcrumb"
      >
        <Link to="/" style={{ color: 'var(--color-text-secondary)' }}>
          Inicio
        </Link>
        <span style={{ color: 'var(--color-text-secondary)' }}>›</span>
        {parentCategory && (
          <>
            <Link
              to={parentCategory.path}
              style={{ color: 'var(--color-text-secondary)' }}
            >
              {parentCategory.name}
            </Link>
            <span style={{ color: 'var(--color-text-secondary)' }}>›</span>
          </>
        )}
        <span style={{ color: 'var(--color-text-primary)' }}>{docSlug}</span>
      </nav>

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

        {/* Badge de estado placeholder — DS-001 §9.11 en Módulo 4+ */}
        <div className="mt-3 flex items-center gap-3">
          <span
            className="inline-flex items-center rounded px-2 py-0.5 text-xs font-medium"
            style={{
              backgroundColor: 'var(--color-warning)',
              color: '#fff',
            }}
          >
            Draft
          </span>
          <span
            className="text-xs"
            style={{ color: 'var(--color-text-secondary)' }}
          >
            Contenido provisional — Módulo 3
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
