// HomePage — página de inicio del Handbook.
//
// Módulo 3 (Navigation System).
//
// Implementa las secciones definidas en WF-001 §8 (wireframe Home) y
// PV-001 Parte 1 (especificación visual):
//
//   [1] Hero  — título "THERS Engineering Handbook" en text-display (36px/700),
//               subtítulo en text-body / text-secondary. Solo en Home (DS-001 §5.2).
//   [2] Grid de categorías — 8 Cards (DS-001 §9.5) en grid 4×2, una por cada
//               categoría raíz del sitemap (ARC-001 §2).
//               Cada card: icono icon-lg (24px) + título text-h4 + descripción.
//               Hover: border-color-border-strong + sombra sutil (DS-001 §9.5).
//               Click navega a la Category Index correspondiente.
//
// Secciones "Últimas actualizaciones" y "Accesos rápidos" (WF-001 §8 zonas 7–9)
// requieren datos dinámicos y se implementan en módulos posteriores.
//
// Convención: este componente no define ningún valor visual propio —
// todo viene de los tokens de DS-001 y de los componentes del Design System
// (FAS-001 §5 — coherencia con DS-001 como fuente de verdad visual).

import { Link } from 'react-router-dom'
import {
  Building2,
  BrainCircuit,
  LayoutTemplate,
  LayoutPanelLeft,
  GraduationCap,
  ListChecks,
  Map,
  Settings,
} from 'lucide-react'

import { ROOT_CATEGORIES } from '../routes/routes'
import Footer from '../components/ui/Footer'

// Mapeo nombre → componente Lucide (DS-001 §6.1 / ARC-001 §8)
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

// ── CategoryCard ──────────────────────────────────────────────────────────
// DS-001 §9.5 — Card: fondo color-surface, borde 1px color-border, radio 8px,
// padding space-4 (16px). Hover: borde pasa a color-border-strong + sombra sutil.
// Anatomía: icono → título text-h4 → descripción text-body-sm / text-secondary.
function CategoryCard({ category }) {
  const Icon = ICON_MAP[category.icon]

  return (
    <Link
      to={category.path}
      className="group flex flex-col gap-2 rounded-lg p-4 transition-shadow"
      style={{
        backgroundColor: 'var(--color-surface)',
        border: '1px solid var(--color-border)',
        textDecoration: 'none',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.borderColor = 'var(--color-border-strong)'
        e.currentTarget.style.boxShadow =
          '0 1px 4px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04)'
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.borderColor = 'var(--color-border)'
        e.currentTarget.style.boxShadow = 'none'
      }}
    >
      {/* Icono icon-lg (24px, stroke 2px — DS-001 §6.2) */}
      {Icon && (
        <Icon
          size={24}
          strokeWidth={2}
          aria-hidden="true"
          style={{ color: 'var(--color-text-secondary)' }}
        />
      )}

      {/* Título — text-h4 (DS-001 §5.2: 16px/600) */}
      <span
        className="text-base font-semibold"
        style={{ color: 'var(--color-text-primary)' }}
      >
        {category.name}
      </span>

      {/* Descripción — text-body-sm / text-secondary (DS-001 §5.2: 14px/400) */}
      <span
        className="text-sm leading-snug"
        style={{ color: 'var(--color-text-secondary)' }}
      >
        {category.description}
      </span>
    </Link>
  )
}

// ── HomePage ──────────────────────────────────────────────────────────────
function HomePage() {
  return (
    <div className="flex min-h-full flex-col">
    <div className="mx-auto w-full max-w-5xl flex-1 px-8 py-16">
      {/* ── [1] Hero ──────────────────────────────────────────────────────
          Centrado horizontalmente — única excepción al patrón left-aligned
          del resto del sistema (PV-001 Parte 1 §3).
          text-display: 36px/700 — único uso permitido en todo el Handbook
          (DS-001 §5.2). Padding vertical 3XL (64px) arriba y abajo.       */}
      <section className="mb-16 text-center">
        <h1
          className="text-4xl font-bold leading-tight tracking-tight"
          style={{ color: 'var(--color-text-primary)' }}
        >
          THERS Engineering Handbook
        </h1>
        <p
          className="mt-2 text-base"
          style={{ color: 'var(--color-text-secondary)' }}
        >
          La fuente de verdad técnica del equipo THERS — documentación,
          decisiones y procesos en un solo lugar.
        </p>
      </section>

      {/* Divisor horizontal entre secciones (PV-001 Parte 1 §8 — regla:
          cada divisor va siempre con space-XL en ambos lados)             */}
      <hr style={{ borderColor: 'var(--color-border)' }} />

      {/* ── [2] Grid de categorías ────────────────────────────────────────
          4 columnas en desktop, 2 en tablet, 1 en mobile.
          8 Cards — una por categoría raíz (ARC-001 §2 / WF-001 §8).
          DS-001 §9.5 — todas con la misma altura (uniform card height).   */}
      <section className="mt-8">
        <h2
          className="mb-6 text-sm font-semibold uppercase tracking-wider"
          style={{ color: 'var(--color-text-secondary)' }}
        >
          Categorías
        </h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {ROOT_CATEGORIES.map((category) => (
            <CategoryCard key={category.path} category={category} />
          ))}
        </div>
      </section>
    </div>
    {/* Footer — DS-001 §9.3: presente en Home y Category Index */}
    <Footer />
    </div>
  )
}

export default HomePage
