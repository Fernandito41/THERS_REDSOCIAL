// DocumentLayout — layout de las páginas de documento individual.
//
// Módulo 3 (Navigation System).
//
// Plantilla "Document Page" (WF-001 §3.2):
//   La plantilla dominante — más del 90% del contenido del Handbook vive aquí.
//
// Tres columnas en desktop (DS-001 §8.1 y PV-001 Parte 2):
//   ├── Sidebar      260px fijo  — árbol de navegación expandido
//   ├── Contenido    flex-1      — columna de lectura (max-width 760px interno)
//   └── TOC rail     220px fijo  — tabla de contenidos (placeholder en Módulo 3)
//
// El TOC rail es un placeholder estructural en esta etapa — el scroll-spy y
// la lógica de headings pertenecen al módulo de Content Layer (ARC-001 §1 capa 3).
//
// El <Outlet /> recibe la página hija resuelta por el router (DocumentPage).

import { Outlet } from 'react-router-dom'
import Header from '../components/navigation/Header'
import Sidebar from '../components/navigation/Sidebar'
import MainContent from '../components/layout/MainContent'
import TableOfContentsRail from '../components/navigation/TableOfContentsRail'

function DocumentLayout() {
  return (
    <div
      id="app-shell-document"
      className="flex h-screen flex-col"
      style={{ backgroundColor: 'var(--color-bg)' }}
    >
      <Header />
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar expandido — rama de la categoría activa resaltada */}
        <Sidebar variant="expanded" />
        <MainContent>
          <Outlet />
        </MainContent>
        {/* TOC rail — placeholder 220px. Scroll-spy y headings en Módulo 4+ */}
        <TableOfContentsRail />
      </div>
    </div>
  )
}

export default DocumentLayout
