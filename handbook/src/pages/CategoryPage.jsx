// CategoryPage — página índice de una categoría (Category Index).
//
// Módulo 5 (Content Layer): muestra la lista real de documentos de la categoría
// obtenida desde el registro de contenido (src/content/registry.js).
//
// Si la categoría no tiene documentos en el registro, muestra el estado vacío
// del Módulo 3 (indicando que no hay contenido aún).
//
// FAS-001 §7 — independencia entre páginas: solo depende de la URL actual.

import { useLocation, Link } from 'react-router-dom'
import {
  Building2,
  BrainCircuit,
  LayoutTemplate,
  LayoutPanelLeft,
  GraduationCap,
  ListChecks,
  Map,
  Settings,
  FileText,
} from 'lucide-react'

import { ROOT_CATEGORIES } from '../routes/routes'
import { getCategoryDocs } from '../content/registry'
import Badge from '../components/ui/Badge'
import Footer from '../components/ui/Footer'
import Card from '../components/ui/Card'

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

// ── CategoryPage ─────────────────────────────────────────────────────────────
// DocumentCard fue reemplazada por el componente Card compartido
// (Módulo 9, variant="document") — DS-001 §9.5 exige una sola estructura
// base para todas las variantes de tarjeta, antes duplicada con CategoryCard.
function CategoryPage() {
  const { pathname } = useLocation()
  const category = ROOT_CATEGORIES.find((c) => c.path === pathname)
  const Icon = category ? ICON_MAP[category.icon] : null

  // Slug de la categoría sin la barra inicial ("/ingenieria" → "ingenieria")
  const categorySlug = pathname.slice(1)
  const docs = getCategoryDocs(categorySlug)

  // Categoría no encontrada — ruta inválida (404 real en Módulo 6)
  if (!category) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <p
            className="text-base font-medium"
            style={{ color: 'var(--color-text-primary)' }}
          >
            Categoría no encontrada
          </p>
          <Link
            to="/"
            className="mt-2 block text-sm"
            style={{ color: 'var(--color-primary)' }}
          >
            Volver al inicio
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="flex min-h-full flex-col">
      <div className="mx-auto w-full max-w-4xl flex-1 px-8 py-8">
        {/* ── Encabezado de categoría (PV-001 Parte 3 §1) ───────────────── */}
        <header className="mb-8">
          <div className="flex items-center gap-4">
            <div
              className="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg"
              style={{
                backgroundColor: 'var(--color-surface)',
                border: '1px solid var(--color-border)',
              }}
            >
              {Icon && (
                <Icon
                  size={24}
                  strokeWidth={2}
                  aria-hidden="true"
                  style={{ color: 'var(--color-text-secondary)' }}
                />
              )}
            </div>
            <h1
              className="text-3xl font-bold leading-tight"
              style={{ color: 'var(--color-text-primary)' }}
            >
              {category.name}
            </h1>
          </div>
          <p
            className="mt-3 text-base leading-relaxed"
            style={{ color: 'var(--color-text-secondary)' }}
          >
            {category.description}
          </p>
          <hr className="mt-6" style={{ borderColor: 'var(--color-border)' }} />
        </header>

        {/* ── Lista de documentos ────────────────────────────────────────── */}
        <section>
          <h2
            className="mb-4 text-sm font-semibold uppercase tracking-wider"
            style={{ color: 'var(--color-text-secondary)' }}
          >
            Documentos
            {docs.length > 0 && (
              <span
                className="ml-2 font-mono font-normal normal-case"
                style={{ color: 'var(--color-text-disabled)' }}
              >
                {docs.length}
              </span>
            )}
          </h2>

          {docs.length > 0 ? (
            <div className="flex flex-col gap-2">
              {docs.map((doc) => (
                <Card
                  key={doc.slug}
                  to={doc.path}
                  icon={FileText}
                  title={doc.frontmatter.title}
                  description={doc.frontmatter.description}
                  badge={<Badge variant={doc.frontmatter.status} />}
                  meta={doc.frontmatter.code}
                  variant="document"
                />
              ))}
            </div>
          ) : (
            // Estado vacío — categoría sin contenido MDX en el registro
            <div
              className="flex items-center justify-center rounded-lg border border-dashed py-16 text-center"
              style={{ borderColor: 'var(--color-border)' }}
            >
              <div>
                <p
                  className="text-sm font-medium"
                  style={{ color: 'var(--color-text-secondary)' }}
                >
                  Sin documentos aún
                </p>
                <p
                  className="mt-1 text-xs"
                  style={{ color: 'var(--color-text-disabled)' }}
                >
                  Los documentos de esta categoría se añaden en{' '}
                  <code>content/{categorySlug}/</code>
                </p>
              </div>
            </div>
          )}
        </section>
      </div>
      <Footer />
    </div>
  )
}

export default CategoryPage
