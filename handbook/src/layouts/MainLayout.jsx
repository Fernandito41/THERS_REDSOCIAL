// MainLayout — App Shell base del Handbook (ARC-001 §1).
//
// Módulo 3 (Navigation System):
// - Mantiene la composición del Módulo 2: Header + Sidebar + MainContent.
// - Aplica tokens de color DS-001 §4 (corrige bg-gray-50 y border-gray-200
//   que usaba el código anterior, contradiciendo DS-001 §4 — regla vinculante).
// - Pasa variant="expanded" al Sidebar (comportamiento por defecto: panel
//   completo de 260px con categorías y nombres visibles).
//
// Uso actual: no es invocado directamente por el router. Las plantillas
// específicas (HomeLayout, CategoryLayout, DocumentLayout) componen los mismos
// bloques de forma independiente para controlar el variant del Sidebar y la
// presencia o ausencia del TOC rail (PV-001 Partes 1–3 / WF-001 §3.2).
//
// MainLayout se conserva como referencia de la composición base del App Shell
// y puede servir como plantilla para nuevos layouts futuros.

import Header from '../components/navigation/Header'
import Sidebar from '../components/navigation/Sidebar'
import MainContent from '../components/layout/MainContent'

function MainLayout({ children }) {
  return (
    <div
      id="app-shell"
      className="mx-auto flex h-screen flex-col"
      style={{ backgroundColor: 'var(--color-bg)', maxWidth: '1440px' }}
    >
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar variant="expanded" />
        <MainContent>{children}</MainContent>
      </div>
    </div>
  )
}

export default MainLayout
