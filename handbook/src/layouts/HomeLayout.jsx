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

function HomeLayout() {
  return (
    <div
      id="app-shell-home"
      className="flex h-screen flex-col"
      style={{ backgroundColor: 'var(--color-bg)' }}
    >
      <Header />
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar colapsado — variante de Home (franja 64px, solo iconos) */}
        <Sidebar variant="collapsed" />
        <MainContent>
          <Outlet />
        </MainContent>
      </div>
    </div>
  )
}

export default HomeLayout
