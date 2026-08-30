// DocumentPage — página de documento individual.
//
// Módulo 6 (Search + Scroll-spy): añade IntersectionObserver para el scroll-spy
// del TOC. El efecto que extrae headings y el que observa el scroll se unifican
// en un solo useEffect para garantizar que el observer solo corre después de que
// los headings están en el DOM (misma dependencia: [categorySlug, docSlug]).
//
// Flujo completo:
//   1. Obtiene el documento del registro (src/content/registry.js).
//   2. Renderiza el componente React del MDX.
//   3. useEffect post-render:
//      a. Extrae H2/H3[id] del DOM → setHeadings(TocContext) para el TOC display.
//      b. IntersectionObserver observa los mismos headings → setActiveId(TocContext)
//         para el scroll-spy activo (DS-001 §9.13).
//   4. Cleanup: desconecta el observer y resetea headings + activeId al salir.

import { useParams, Link } from 'react-router-dom'
import { useEffect, useRef } from 'react'

import { ROOT_CATEGORIES } from '../routes/routes'
import { getDocument } from '../content/registry'
import { useToc } from '../providers/TocContext'
import Breadcrumbs from '../components/ui/Breadcrumbs'
import Badge from '../components/ui/Badge'
import CodeBlock from '../components/ui/CodeBlock'
import PrevNext from '../components/ui/PrevNext'

function DocumentPage() {
  const { category: categorySlug, doc: docSlug } = useParams()
  const { setHeadings, setActiveId } = useToc()
  const contentRef = useRef(null)

  const doc = getDocument(categorySlug, docSlug)

  // ── Headings + Scroll-spy (DS-001 §9.13) ──────────────────────────────────
  // Un solo efecto que:
  //  1. Extrae headings del DOM y los publica al TOC via TocContext.
  //  2. Configura un IntersectionObserver para rastrear el heading activo
  //     mientras el usuario hace scroll.
  //
  // rootMargin: '-64px 0px -70% 0px'
  //   - top: -64px excluye la zona del sticky Header (DS-001 §9.1: 64px alto)
  //   - bottom: -70% limita la zona activa al 30% superior del viewport,
  //     de modo que solo el heading "próximo a ser leído" queda activo.
  useEffect(() => {
    const container = contentRef.current
    if (!container) {
      setHeadings([])
      setActiveId(null)
      return
    }

    // 1. Extracción de headings
    const headingEls = Array.from(container.querySelectorAll('h2[id], h3[id]'))
    setHeadings(
      headingEls.map((el) => ({
        id: el.id,
        text: el.textContent,
        level: Number(el.tagName[1]),
      })),
    )

    if (headingEls.length === 0) {
      setActiveId(null)
      return
    }

    // 2. Scroll-spy via IntersectionObserver
    // Conjunto de IDs de headings actualmente en la zona de intersección.
    // Se usa un Set mutable (no estado) para evitar re-renders innecesarios
    // en cada tick del observer.
    const activeSet = new Set()

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            activeSet.add(entry.target.id)
          } else {
            activeSet.delete(entry.target.id)
          }
        })
        // Publica el primer heading (en orden de documento) que está activo
        const firstActive = headingEls.find((el) => activeSet.has(el.id))
        setActiveId(firstActive?.id ?? null)
      },
      { rootMargin: '-64px 0px -70% 0px', threshold: 0 },
    )

    headingEls.forEach((el) => observer.observe(el))

    return () => {
      observer.disconnect()
      setHeadings([])
      setActiveId(null)
    }
  }, [categorySlug, docSlug, setHeadings, setActiveId])

  // ── Documento no encontrado ───────────────────────────────────────────────
  if (!doc) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <p
            className="text-base font-medium"
            style={{ color: 'var(--color-text-primary)' }}
          >
            Documento no encontrado
          </p>
          <p
            className="mt-1 font-mono text-sm"
            style={{ color: 'var(--color-text-secondary)' }}
          >
            {categorySlug}/{docSlug}
          </p>
          <Link
            to="/"
            className="mt-3 block text-sm"
            style={{ color: 'var(--color-primary)' }}
          >
            Volver al inicio
          </Link>
        </div>
      </div>
    )
  }

  const { Component, frontmatter } = doc
  const parentCategory = ROOT_CATEGORIES.find(
    (c) => c.path === `/${categorySlug}`,
  )
  const title = frontmatter?.title ?? docSlug

  return (
    // Columna de lectura — max-width 760px (DS-001 §8.1 container-content)
    <div className="mx-auto w-full px-8 py-8" style={{ maxWidth: '760px' }}>
      {/* ── Breadcrumbs (DS-001 §9.4) ───────────────────────────────────── */}
      <div className="mb-6">
        <Breadcrumbs
          items={[
            { label: 'Inicio', href: '/' },
            ...(parentCategory
              ? [{ label: parentCategory.name, href: parentCategory.path }]
              : []),
            { label: title },
          ]}
        />
      </div>

      {/* ── Encabezado del documento (PV-001 Parte 2 §4) ─────────────────── */}
      <header className="mb-8">
        {frontmatter?.code && (
          <p
            className="mb-1 font-mono text-xs"
            style={{ color: 'var(--color-text-secondary)' }}
          >
            {frontmatter.code}
          </p>
        )}

        <h1
          className="text-3xl font-bold leading-tight"
          style={{ color: 'var(--color-text-primary)' }}
        >
          {title}
        </h1>

        <div className="mt-3 flex flex-wrap items-center gap-3">
          <Badge variant={frontmatter?.status ?? 'draft'} />
          {frontmatter?.version && (
            <span
              className="font-mono text-xs"
              style={{ color: 'var(--color-text-disabled)' }}
            >
              v{frontmatter.version}
            </span>
          )}
          {frontmatter?.author && (
            <span
              className="text-xs"
              style={{ color: 'var(--color-text-secondary)' }}
            >
              {frontmatter.author}
            </span>
          )}
        </div>

        <hr className="mt-6" style={{ borderColor: 'var(--color-border)' }} />
      </header>

      {/* ── Contenido MDX (DS-001 §5.2 / §7) ────────────────────────────── */}
      <main ref={contentRef} className="handbook-prose">
        <Component components={{ pre: CodeBlock }} />
      </main>

      {/* ── Navegación secuencial (WF-001 §5 Plano Secuencial) ───────────── */}
      <PrevNext categorySlug={categorySlug} docSlug={docSlug} />

      {/* ── Footer condensado del documento (PV-001 §10) ─────────────────
          Una sola línea: Editar en GitHub · Reportar problema · versión.
          DS-001 §9.3 excluye el Footer completo de las páginas de documento;
          PV-001 §10 define esta variante condensada como utilidad específica
          del contexto de lectura técnica.                                   */}
      <div
        className="mt-10 flex flex-wrap items-center justify-between gap-4 border-t pt-4 text-xs"
        style={{
          borderColor: 'var(--color-border)',
          color: 'var(--color-text-secondary)',
        }}
      >
        <a
          href={`https://github.com/Fernandito41/THERS_REDSOCIAL/edit/develop/handbook/content/${categorySlug}/${docSlug}.mdx`}
          target="_blank"
          rel="noopener noreferrer"
          style={{ color: 'var(--color-primary)', textDecoration: 'none' }}
          onMouseEnter={(e) => {
            e.currentTarget.style.textDecoration = 'underline'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.textDecoration = 'none'
          }}
        >
          Editar esta página en GitHub
        </a>
        <a
          href={`https://github.com/Fernandito41/THERS_REDSOCIAL/issues/new?title=${encodeURIComponent(`[${frontmatter?.code ?? docSlug}] Reportar un problema`)}&body=${encodeURIComponent(`**Documento:** ${frontmatter?.title ?? docSlug}\n**Ruta:** /${categorySlug}/${docSlug}\n\n**Descripción del problema:**\n`)}`}
          target="_blank"
          rel="noopener noreferrer"
          style={{ color: 'var(--color-text-secondary)', textDecoration: 'none' }}
          onMouseEnter={(e) => {
            e.currentTarget.style.color = 'var(--color-text-primary)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.color = 'var(--color-text-secondary)'
          }}
        >
          Reportar un problema
        </a>
        <span>v0.1</span>
      </div>
    </div>
  )
}

export default DocumentPage
