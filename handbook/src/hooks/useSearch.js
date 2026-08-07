// useSearch — hook del motor de búsqueda client-side (DS-001 §9.12).
//
// Módulo 6 (Search + Scroll-spy).
//
// Filtra el índice completo de documentos (getAllDocs) contra la query del usuario.
// Los campos buscados son: title, description, code (frontmatter de cada MDX).
//
// El índice se construye una sola vez al inicializar el módulo (fuera del hook)
// porque getAllDocs() es determinista y no cambia en runtime — el contenido
// es estático (construido en build time via import.meta.glob eager).
//
// Rendimiento: la búsqueda es lineal O(n) sobre el número de documentos.
// Para el volumen esperado de un handbook interno (< 200 docs), es suficiente.
// Si en el futuro el corpus crece, se puede migrar a FlexSearch o fuse.js
// sin cambiar la API de este hook.

import { useMemo } from 'react'
import { getAllDocs } from '../content/registry'

// Índice precalculado una sola vez
const ALL_DOCS = getAllDocs()

/**
 * Filtra documentos del Handbook que coinciden con la query.
 * @param {string} query — texto libre del usuario
 * @returns {Array<{slug, path, frontmatter, Component}>} docs que coinciden
 */
export function useSearch(query) {
  return useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return []

    return ALL_DOCS.filter((doc) => {
      const { title = '', description = '', code = '' } = doc.frontmatter
      return (
        title.toLowerCase().includes(q) ||
        description.toLowerCase().includes(q) ||
        code.toLowerCase().includes(q)
      )
    })
  }, [query])
}
