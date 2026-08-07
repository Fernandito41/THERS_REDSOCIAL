// DocumentLayout — layout de las páginas de documento individual.
//
// Módulo 5 (Content Layer): envuelve con TocProvider para que DocumentPage
// pueda publicar los headings del MDX y TableOfContentsRail los consuma.
// La arquitectura del provider evita prop drilling a través del router.
//
// Tres columnas en desktop (DS-001 §8.1 y PV-001 Parte 2):
//   ├── Sidebar      260px fijo  — árbol de navegación expandido
//   ├── Contenido    flex-1      — columna de lectura (max-width 760px interno)
//   └── TOC rail     220px fijo  — headings del documento (real en Módulo 5)

import { Outlet } from 'react-router-dom'
import Header from '../components/navigation/Header'
import Sidebar from '../components/navigation/Sidebar'
import MainContent from '../components/layout/MainContent'
import TableOfContentsRail from '../components/navigation/TableOfContentsRail'
import { TocProvider } from '../providers/TocContext'
import { DrawerProvider } from '../providers/DrawerContext'

function DocumentLayout() {
  return (
    <DrawerProvider>
    <TocProvider>
      {/* container-app 1440px (DS-001 §8.1 / PV-001 Responsive §2 bp-wide) —
          Módulo 10, mismo criterio que HomeLayout y CategoryLayout. */}
      <div
        id="app-shell-document"
        className="mx-auto flex h-screen flex-col"
        style={{ backgroundColor: 'var(--color-bg)', maxWidth: '1440px' }}
      >
        {/* Skip to content — DS-001 §12 */}
        <a href="#main-content" className="skip-to-content">
          Saltar al contenido principal
        </a>
        <Header />
        <div className="flex flex-1 overflow-hidden">
          <Sidebar variant="expanded" />
          <MainContent>
            <Outlet />
          </MainContent>
          <TableOfContentsRail />
        </div>
      </div>
    </TocProvider>
    </DrawerProvider>
  )
}

export default DocumentLayout
