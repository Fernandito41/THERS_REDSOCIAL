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
import Footer from '../components/layout/Footer'
import { DrawerProvider } from '../providers/DrawerContext'

function CategoryLayout() {
  return (
    <DrawerProvider>
    {/* container-app 1440px (DS-001 §8.1 / PV-001 Responsive §2 bp-wide) —
        Módulo 10, mismo criterio que HomeLayout y DocumentLayout. */}
    <div
      id="app-shell-category"
      className="mx-auto flex h-screen flex-col"
      style={{ backgroundColor: 'var(--color-bg)', maxWidth: '1440px' }}
    >
      {/* Skip to content — DS-001 §12 */}
      <a href="#main-content" className="skip-to-content">
        Saltar al contenido principal
      </a>
      <Header />
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar expandido — árbol completo con rama activa resaltada */}
        <Sidebar variant="expanded" />
        <MainContent>
          {/* Footer al fondo del área scrollable (PV-001 §8) */}
          <div className="flex min-h-full flex-col">
            <div className="flex-1">
              <Outlet />
            </div>
            <Footer />
          </div>
        </MainContent>
      </div>
    </div>
    </DrawerProvider>
  )
}

export default CategoryLayout
