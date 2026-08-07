// TocContext — contexto del plano de navegación Contextual (WF-001 §5).
//
// Módulo 6 (Search + Scroll-spy): añade activeId al estado del contexto.
// DocumentPage publica tanto los headings (para TOC display) como el activeId
// (para el scroll-spy activo) mediante este contexto.
// TableOfContentsRail lee ambos para renderizar la navegación "En esta página".
//
// Árbol de componentes:
//   DocumentLayout (TocProvider)
//   ├── MainContent → Outlet → DocumentPage  (escribe headings + activeId)
//   └── TableOfContentsRail                  (lee headings + activeId)
//
// activeId: id del heading actualmente visible en la zona superior del viewport,
// actualizado por un IntersectionObserver en DocumentPage (DS-001 §9.13).

import { createContext, useContext, useState } from 'react'

const TocContext = createContext({
  headings: [],
  setHeadings: () => {},
  activeId: null,
  setActiveId: () => {},
})

export function TocProvider({ children }) {
  const [headings, setHeadings] = useState([])
  const [activeId, setActiveId] = useState(null)
  return (
    <TocContext.Provider value={{ headings, setHeadings, activeId, setActiveId }}>
      {children}
    </TocContext.Provider>
  )
}

export function useToc() {
  return useContext(TocContext)
}
