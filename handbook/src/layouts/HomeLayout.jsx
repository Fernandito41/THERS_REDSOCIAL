// HomeLayout — layout exclusivo de la página de inicio.
//
// Módulo 3 (Navigation System).
//
// Plantilla "Home / Landing" (WF-001 §3.2):
//   - Header sticky (DS-001 §9.1)
//   - Sidebar colapsado a franja de iconos de 64px (PV-001 Parte 1 §2):
//     "el único estado que existe en Home — no hay expansión en línea
//      dentro de esta plantilla"
//   - Sin estado activo en los iconos del sidebar (PV-001 Parte 1 §2):
//     "en Home, ningún ícono se muestra en estado activo"
//   - Área de contenido principal (Outlet — HomePage)
//   - Sin TOC rail: Home no es una página de documento (WF-001 §5)
//
// El <Outlet /> recibe la página hija resuelta por el router (HomePage).

import { Outlet } from 'react-router-dom'
import Header from '../components/navigation/Header'
import Sidebar from '../components/navigation/Sidebar'
import MainContent from '../components/layout/MainContent'
import Footer from '../components/layout/Footer'
import { DrawerProvider } from '../providers/DrawerContext'

function HomeLayout() {
  return (
    <DrawerProvider>
    {/* container-app 1440px (DS-001 §8.1 / PV-001 Responsive §2 bp-wide):
        el espacio adicional en monitores ultrawide se vuelve padding lateral,
        no un App Shell sin límite (Módulo 10 — cierre de fidelidad visual). */}
    <div
      id="app-shell-home"
      className="mx-auto flex h-screen flex-col"
      style={{ backgroundColor: 'var(--color-bg)', maxWidth: '1440px' }}
    >
      {/* Skip to content — DS-001 §12, primer elemento Tab de la página */}
      <a href="#main-content" className="skip-to-content">
        Saltar al contenido principal
      </a>
      <Header />
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar colapsado — variante de Home (franja 64px, solo iconos) */}
        <Sidebar variant="collapsed" />
        <MainContent>
          {/* Footer empujado al fondo del área de scroll (PV-001 §7) */}
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

export default HomeLayout
