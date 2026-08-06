// CategoryLayout — layout de las páginas Category Index.
//
// Módulo 3 (Navigation System).
//
// Plantilla "Category Index" (WF-001 §3.2):
//   - Header sticky (DS-001 §9.1)
//   - Sidebar expandido 260px con árbol de navegación (DS-001 §8.1)
//   - Área de contenido principal (Outlet — CategoryPage)
//   - Sin TOC rail: las páginas índice listan documentos, no tienen headings
//     propios que justifiquen una tabla de contenidos.
//     (WF-001 §5: plano Contextual — "exclusivo de Document Page y variantes")
//
// El <Outlet /> recibe la página hija resuelta por el router (CategoryPage).

import { Outlet } from 'react-router-dom'
import Header from '../components/navigation/Header'
import Sidebar from '../components/navigation/Sidebar'
import MainContent from '../components/layout/MainContent'

function CategoryLayout() {
  return (
    <div
      id="app-shell-category"
      className="flex h-screen flex-col"
      style={{ backgroundColor: 'var(--color-bg)' }}
    >
      <Header />
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar expandido — árbol completo con rama activa resaltada */}
        <Sidebar variant="expanded" />
        <MainContent>
          <Outlet />
        </MainContent>
      </div>
    </div>
  )
}

export default CategoryLayout
