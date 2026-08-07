// SearchModal — buscador del Handbook (DS-001 §9.12).
//
// Módulo 6 (Search + Scroll-spy).
//
// Activación: click en el buscador del Header o Ctrl/Cmd+K global.
// Cierre: Esc, click en el overlay, o navegar a un resultado.
//
// DS-001 §9.12 especificación:
//   - Modal centrado max-width 640px (DS-001 §9.18 variante md)
//   - Resultados agrupados por categoría con encabezado text-caption uppercase
//   - Título coincidente resaltado en color-primary SIN fondo de color
//     (DS-001 §9.12: "nunca resaltado con fondo de color")
//   - Navegación por teclado: ↑↓ entre resultados, ↵ para abrir, Esc para cerrar
//   - Overlay color-overlay, foco atrapado dentro del modal (DS-001 §12)
//
// Usa createPortal para renderizar en document.body — garantiza que el z-index
// sea correcto independientemente del stacking context del componente padre.

import { useState, useEffect, useRef, useCallback } from 'react'
import { createPortal } from 'react-dom'
import { useNavigate } from 'react-router-dom'
import { Search, X } from 'lucide-react'

import { useSearch } from '../../hooks/useSearch'
import { ROOT_CATEGORIES } from '../../routes/routes'

// ── Highlight ────────────────────────────────────────────────────────────────
// DS-001 §9.12: resaltado en color-primary, sin fondo de color.
// Solo resalta la primera ocurrencia de la query en el texto.
function Highlight({ text, query }) {
  if (!query.trim()) return <>{text}</>
  const q = query.trim()
  const idx = text.toLowerCase().indexOf(q.toLowerCase())
  if (idx === -1) return <>{text}</>
  return (
    <>
      {text.slice(0, idx)}
      <span style={{ color: 'var(--color-primary)', fontWeight: 600 }}>
        {text.slice(idx, idx + q.length)}
      </span>
      {text.slice(idx + q.length)}
    </>
  )
}

// ── SearchModal ──────────────────────────────────────────────────────────────
function SearchModal({ isOpen, onClose }) {
  const [query, setQuery] = useState('')
  const [activeIndex, setActiveIndex] = useState(0)
  const inputRef = useRef(null)
  const navigate = useNavigate()
  const results = useSearch(query)

  // Reset query + activeIndex al abrir; auto-focus al input
  useEffect(() => {
    if (!isOpen) return
    setQuery('')
    setActiveIndex(0)
    // Espera un tick para que el portal esté en el DOM antes de hacer focus
    const id = setTimeout(() => inputRef.current?.focus(), 0)
    return () => clearTimeout(id)
  }, [isOpen])

  // Esc → cerrar
  useEffect(() => {
    if (!isOpen) return
    const handler = (e) => {
      if (e.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [isOpen, onClose])

  // Bloquear scroll del body mientras el modal está abierto
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => {
      document.body.style.overflow = ''
    }
  }, [isOpen])

  // Reset activeIndex cuando cambia el número de resultados
  useEffect(() => {
    setActiveIndex(0)
  }, [results.length])

  // Navegación por teclado dentro del input
  const handleKeyDown = useCallback(
    (e) => {
      if (e.key === 'ArrowDown') {
        e.preventDefault()
        setActiveIndex((i) => Math.min(i + 1, results.length - 1))
      } else if (e.key === 'ArrowUp') {
        e.preventDefault()
        setActiveIndex((i) => Math.max(i - 1, 0))
      } else if (e.key === 'Enter' && results[activeIndex]) {
        navigate(results[activeIndex].path)
        onClose()
      }
    },
    [results, activeIndex, navigate, onClose],
  )

  const handleResultClick = useCallback(
    (path) => {
      navigate(path)
      onClose()
    },
    [navigate, onClose],
  )

  if (!isOpen) return null

  // Agrupa resultados por categoría para los encabezados de grupo
  const grouped = results.reduce((acc, doc) => {
    const categorySlug = doc.path.split('/')[1]
    if (!acc[categorySlug]) acc[categorySlug] = []
    acc[categorySlug].push(doc)
    return acc
  }, {})

  return createPortal(
    // Overlay — color-overlay cubre toda la pantalla (DS-001 §9.18)
    <div
      className="fixed inset-0 z-50 flex items-start justify-center px-4 pt-24"
      style={{ backgroundColor: 'var(--color-overlay)' }}
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label="Buscador del Handbook"
    >
      {/* Contenedor modal — max-width 640px (DS-001 §9.18 variante md) */}
      <div
        className="w-full overflow-hidden rounded-xl"
        style={{
          maxWidth: '640px',
          backgroundColor: 'var(--color-surface-raised)',
          border: '1px solid var(--color-border)',
          boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* ── Fila de input ─────────────────────────────────────────────── */}
        <div
          className="flex items-center gap-3 px-4"
          style={{ borderBottom: '1px solid var(--color-border)' }}
        >
          <Search
            size={18}
            strokeWidth={2}
            aria-hidden="true"
            style={{ color: 'var(--color-text-secondary)', flexShrink: 0 }}
          />
          <input
            ref={inputRef}
            type="search"
            placeholder="Buscar en el Handbook..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            className="flex-1 bg-transparent py-4 text-sm outline-none"
            style={{ color: 'var(--color-text-primary)' }}
            aria-label="Buscar documentos"
            autoComplete="off"
            spellCheck={false}
          />
          <button
            type="button"
            onClick={onClose}
            className="flex h-6 w-6 items-center justify-center rounded"
            style={{ color: 'var(--color-text-secondary)' }}
            aria-label="Cerrar buscador"
          >
            <X size={14} strokeWidth={2} aria-hidden="true" />
          </button>
        </div>

        {/* ── Área de resultados ────────────────────────────────────────── */}
        <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
          {!query.trim() ? (
            // Estado inicial — sin query
            <div className="px-4 py-8 text-center">
              <p
                className="text-sm"
                style={{ color: 'var(--color-text-secondary)' }}
              >
                Escribe para buscar documentos, guías y ADRs
              </p>
              <p
                className="mt-1 text-xs"
                style={{ color: 'var(--color-text-disabled)' }}
              >
                Busca por título, código (ENG-001) o descripción
              </p>
            </div>
          ) : results.length === 0 ? (
            // Sin resultados
            <div className="px-4 py-8 text-center">
              <p
                className="text-sm"
                style={{ color: 'var(--color-text-secondary)' }}
              >
                Sin resultados para{' '}
                <strong style={{ color: 'var(--color-text-primary)' }}>
                  &ldquo;{query}&rdquo;
                </strong>
              </p>
            </div>
          ) : (
            // Resultados agrupados por categoría
            <ul role="listbox" aria-label="Resultados de búsqueda">
              {Object.entries(grouped).map(([categorySlug, docs]) => {
                const categoryMeta = ROOT_CATEGORIES.find(
                  (c) => c.path === `/${categorySlug}`,
                )
                return (
                  <li key={categorySlug}>
                    {/* Encabezado de grupo — DS-001 §9.12: text-caption uppercase */}
                    <p
                      className="px-4 pb-1 pt-3 text-xs font-semibold uppercase tracking-wider"
                      style={{ color: 'var(--color-text-secondary)' }}
                    >
                      {categoryMeta?.name ?? categorySlug}
                    </p>
                    <ul>
                      {docs.map((doc) => {
                        const globalIndex = results.indexOf(doc)
                        const isActive = globalIndex === activeIndex
                        return (
                          <li key={doc.path} role="option" aria-selected={isActive}>
                            <button
                              type="button"
                              className="flex w-full items-start gap-3 px-4 py-2.5 text-left transition-colors"
                              style={{
                                backgroundColor: isActive
                                  ? 'var(--color-primary-8)'
                                  : 'transparent',
                              }}
                              onClick={() => handleResultClick(doc.path)}
                              onMouseEnter={() => setActiveIndex(globalIndex)}
                            >
                              <div className="min-w-0 flex-1">
                                <div className="flex items-center gap-2">
                                  <span
                                    className="truncate text-sm font-medium"
                                    style={{ color: 'var(--color-text-primary)' }}
                                  >
                                    <Highlight
                                      text={doc.frontmatter.title}
                                      query={query}
                                    />
                                  </span>
                                  {doc.frontmatter.code && (
                                    <span
                                      className="shrink-0 font-mono text-xs"
                                      style={{ color: 'var(--color-text-disabled)' }}
                                    >
                                      {doc.frontmatter.code}
                                    </span>
                                  )}
                                </div>
                                {doc.frontmatter.description && (
                                  <p
                                    className="mt-0.5 truncate text-xs"
                                    style={{ color: 'var(--color-text-secondary)' }}
                                  >
                                    <Highlight
                                      text={doc.frontmatter.description}
                                      query={query}
                                    />
                                  </p>
                                )}
                              </div>
                            </button>
                          </li>
                        )
                      })}
                    </ul>
                  </li>
                )
              })}
            </ul>
          )}

          {/* Footer del modal — atajos de teclado (solo si hay resultados) */}
          {query.trim() && results.length > 0 && (
            <div
              className="flex items-center gap-4 border-t px-4 py-2"
              style={{
                borderColor: 'var(--color-border)',
                backgroundColor: 'var(--color-surface)',
              }}
            >
              {[
                { key: '↑↓', label: 'navegar' },
                { key: '↵', label: 'abrir' },
                { key: 'Esc', label: 'cerrar' },
              ].map(({ key, label }) => (
                <span
                  key={key}
                  className="flex items-center gap-1 text-xs"
                  style={{ color: 'var(--color-text-disabled)' }}
                >
                  <kbd
                    className="rounded px-1 font-mono"
                    style={{
                      fontSize: '11px',
                      backgroundColor: 'var(--color-code-bg)',
                      border: '1px solid var(--color-border)',
                    }}
                  >
                    {key}
                  </kbd>
                  {label}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>,
    document.body,
  )
}

export default SearchModal
