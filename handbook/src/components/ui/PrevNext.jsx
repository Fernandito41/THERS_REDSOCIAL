// PrevNext — navegación secuencial entre documentos (WF-001 §5 plano Secuencial).
//
// Módulo 7 (Responsive + Sequential Navigation).
//
// WF-001 §5 Plano Secuencial: Prev/Next entre documentos de la misma categoría.
// El orden de los documentos lo determina el registro (src/content/registry.js),
// que los ordena alfabéticamente por título al inicializar.
//
// Anatomía (DS-001 §9.5 — mismo lenguaje visual que las Cards):
//   ← Anterior   |   Siguiente →
//   Título prev   |   Título next
//
// Si no hay documento previo, la celda izquierda queda vacía (flex-1 spacer).
// Si no hay documento siguiente, la celda derecha queda vacía.
// Si el documento no tiene ni prev ni next (categoría de 1 doc), no renderiza.

import { Link } from 'react-router-dom'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { getCategoryDocs } from '../../content/registry'

function PrevNext({ categorySlug, docSlug }) {
  const docs = getCategoryDocs(categorySlug)
  const currentIndex = docs.findIndex((d) => d.slug === docSlug)

  // Documento no encontrado en el registro o categoría de 1 solo doc
  if (currentIndex === -1 || docs.length < 2) return null

  const prev = docs[currentIndex - 1] ?? null
  const next = docs[currentIndex + 1] ?? null

  if (!prev && !next) return null

  return (
    <nav
      className="mt-12 flex items-stretch gap-4 border-t pt-6"
      aria-label="Navegación entre documentos"
      style={{ borderColor: 'var(--color-border)' }}
    >
      {/* Celda izquierda — documento anterior */}
      {prev ? (
        <Link
          to={prev.path}
          className="flex flex-1 flex-col gap-1 rounded-lg p-4 transition-shadow"
          style={{
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
          <span
            className="flex items-center gap-1 text-xs"
            style={{ color: 'var(--color-text-secondary)' }}
          >
            <ChevronLeft size={14} strokeWidth={2} aria-hidden="true" />
            Anterior
          </span>
          <span
            className="text-sm font-medium leading-snug"
            style={{ color: 'var(--color-text-primary)' }}
          >
            {prev.frontmatter.title}
          </span>
        </Link>
      ) : (
        // Spacer para mantener el next alineado a la derecha
        <div className="flex-1" aria-hidden="true" />
      )}

      {/* Celda derecha — documento siguiente */}
      {next ? (
        <Link
          to={next.path}
          className="flex flex-1 flex-col items-end gap-1 rounded-lg p-4 transition-shadow"
          style={{
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
          <span
            className="flex items-center gap-1 text-xs"
            style={{ color: 'var(--color-text-secondary)' }}
          >
            Siguiente
            <ChevronRight size={14} strokeWidth={2} aria-hidden="true" />
          </span>
          <span
            className="text-right text-sm font-medium leading-snug"
            style={{ color: 'var(--color-text-primary)' }}
          >
            {next.frontmatter.title}
          </span>
        </Link>
      ) : (
        <div className="flex-1" aria-hidden="true" />
      )}
    </nav>
  )
}

export default PrevNext
