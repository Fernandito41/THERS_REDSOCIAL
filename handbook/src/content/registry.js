// Content Registry — ARC-001 §1 capa 1 (Content Layer).
//
// Módulo 5: punto central de acceso al contenido MDX del Handbook.
//
// Usa import.meta.glob con eager:true para importar todos los archivos MDX
// en tiempo de build. Esto significa que todo el contenido se incluye en el
// bundle inicial — decisión válida para un handbook interno donde la velocidad
// de navegación prima sobre el tamaño del bundle.
//
// Cada módulo MDX exporta:
//   default     → componente React (el documento renderizable)
//   frontmatter → objeto con { code, title, status, version, author, description }
//                 (generado por remark-frontmatter + remark-mdx-frontmatter)
//
// Convención de paths: /content/{categoríaSlug}/{docSlug}.mdx
// El slug de la categoría debe coincidir con el path de ROOT_CATEGORIES
// sin la barra inicial: "/ingenieria" → "ingenieria".

const modules = import.meta.glob('/content/**/*.mdx', { eager: true })

// ── Construcción del registro en tiempo de inicialización del módulo ──────
// Shape: Record<categorySlug, DocEntry[]>
const registry = {}

for (const [modulePath, mod] of Object.entries(modules)) {
  // "/content/ingenieria/convenciones-react.mdx" → ["ingenieria", "convenciones-react"]
  const parts = modulePath
    .replace('/content/', '')
    .replace('.mdx', '')
    .split('/')
  if (parts.length !== 2) continue

  const [category, slug] = parts
  if (!registry[category]) registry[category] = []

  registry[category].push({
    slug,
    path: `/${category}/${slug}`,
    frontmatter: mod.frontmatter ?? {
      title: slug.replace(/-/g, ' '),
      status: 'draft',
      description: '',
    },
    Component: mod.default,
  })
}

// Ordena los docs de cada categoría por título (locale 'es')
for (const docs of Object.values(registry)) {
  docs.sort((a, b) =>
    a.frontmatter.title.localeCompare(b.frontmatter.title, 'es'),
  )
}

/**
 * Retorna todos los documentos de una categoría ordenados por título.
 * @param {string} categorySlug
 * @returns {Array<{slug, path, frontmatter, Component}>}
 */
export function getCategoryDocs(categorySlug) {
  return registry[categorySlug] ?? []
}

/**
 * Retorna un documento específico, o null si no existe.
 * @param {string} categorySlug
 * @param {string} docSlug
 * @returns {{ slug, path, frontmatter, Component } | null}
 */
export function getDocument(categorySlug, docSlug) {
  return (
    (registry[categorySlug] ?? []).find((d) => d.slug === docSlug) ?? null
  )
}

/**
 * Retorna todos los documentos del Handbook en una lista plana.
 * Usado por el motor de búsqueda (DS-001 §9.12) para indexar el contenido.
 * @returns {Array<{slug, path, frontmatter, Component}>}
 */
export function getAllDocs() {
  return Object.values(registry).flat()
}
