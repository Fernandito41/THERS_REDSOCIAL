// CategoryPage — página índice de una categoría (Category Index).
//
// Módulo 3 (Navigation System).
//
// Implementa el encabezado de categoría definido en WF-001 §10 y
// PV-001 Parte 3 §1 (Encabezado de Categoría):
//   - Icono 48×48px (contenedor cuadrado) + nombre H1 (PV-001 Parte 3 §1)
//   - Descripción en text-body / text-secondary, máximo 2 líneas
//   - Grid de tarjetas de documentos (placeholder — contenido real en Módulo 4+)
//
// La categoría actual se resuelve desde la URL usando useLocation y
// buscando en ROOT_CATEGORIES (FAS-001 §7 — independencia entre páginas:
// ninguna página depende del estado de otra, solo de la URL actual).
//
// Secciones de Módulo 4+:
//   - Buscador local (WF-001 §10 zona 5)
//   - Filtros y etiquetas (WF-001 §10 zonas 4–6)
//   - Estadísticas de categoría (WF-001 §10 zona 7)
//   - Grid real de documentos (requiere Content Layer — ARC-001 §1 capa 1)

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

// ── Placeholder de tarjeta de documento ──────────────────────────────────
// DS-001 §9.5 — anatomía: icono → título text-h4 → badge de estado.
// En Módulo 4+ se alimenta desde el frontmatter de cada archivo MDX.
function DocumentCardPlaceholder({ index }) {
  return (
    <div
      className="flex items-start gap-3 rounded-lg p-4"
      style={{
        backgroundColor: 'var(--color-surface)',
        border: '1px solid var(--color-border)',
      }}
    >
      <FileText
        size={20}
        strokeWidth={1.5}
        aria-hidden="true"
        style={{ color: 'var(--color-text-disabled)', flexShrink: 0, marginTop: 2 }}
      />
      <div className="flex flex-col gap-1">
        <span
          className="text-sm font-semibold"
          style={{ color: 'var(--color-text-disabled)' }}
        >
          Documento {index + 1}
        </span>
        <span
          className="text-xs"
          style={{ color: 'var(--color-text-disabled)' }}
        >
          Contenido disponible en Módulo 4+
        </span>
      </div>
    </div>
  )
}

// ── CategoryPage ──────────────────────────────────────────────────────────
function CategoryPage() {
  const { pathname } = useLocation()
  const category = ROOT_CATEGORIES.find((c) => c.path === pathname)
  const Icon = category ? ICON_MAP[category.icon] : null

  // Categoría no encontrada — ruta inválida (404 real en Módulo 4+)
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
    <div className="mx-auto w-full max-w-4xl px-8 py-8">
      {/* ── Encabezado de categoría (PV-001 Parte 3 §1) ──────────────────
          Icono en contenedor 48×48px (radio 8px, border 1px color-border)
          + nombre H1 (text-h1: 30px/700).                                  */}
      <header className="mb-8">
        <div className="flex items-center gap-4">
          {/* Contenedor de icono 48×48px (PV-001 Parte 3 §1) */}
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

          {/* Nombre — text-h1 (DS-001 §5.2: 30px/700) */}
          <h1
            className="text-3xl font-bold leading-tight"
            style={{ color: 'var(--color-text-primary)' }}
          >
            {category.name}
          </h1>
        </div>

        {/* Descripción — text-body / text-secondary, máx. 2 líneas (PV-001 Parte 3 §1) */}
        <p
          className="mt-3 text-base leading-relaxed"
          style={{ color: 'var(--color-text-secondary)' }}
        >
          {category.description}
        </p>

        {/* Divisor (DS-001 §7 / PV-001 Parte 1 §8) */}
        <hr className="mt-6" style={{ borderColor: 'var(--color-border)' }} />
      </header>

      {/* ── Grid de documentos ────────────────────────────────────────────
          Placeholder — contenido real depende del Content Layer (ARC-001 §1
          capa 1: Markdown/MDX + frontmatter). Se implementa en Módulo 4+.
          Estructura: 2 columnas en desktop, 1 en mobile (WF-001 §10 zona 3). */}
      <section>
        <h2
          className="mb-4 text-sm font-semibold uppercase tracking-wider"
          style={{ color: 'var(--color-text-secondary)' }}
        >
          Documentos
        </h2>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {[...Array(4)].map((_, i) => (
            <DocumentCardPlaceholder key={i} index={i} />
          ))}
        </div>

        {/* Aviso de Módulo 4+ */}
        <p
          className="mt-6 text-center text-xs"
          style={{ color: 'var(--color-text-disabled)' }}
        >
          Los documentos reales de esta categoría se cargarán desde el Content
          Layer en el Módulo 4+.
        </p>
      </section>
    </div>
  )
}

export default CategoryPage
