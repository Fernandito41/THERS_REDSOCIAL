// DrawerContext — estado del drawer mobile del Sidebar (DS-001 §11).
//
// Módulo 7 (Responsive + Sequential Navigation).
//
// DS-001 §11: en mobile, el Sidebar es oculto por defecto y se convierte en
// un Drawer deslizable desde la izquierda activado por el icono de menú del Header.
//
// Arquitectura:
//   Layout (DrawerProvider)
//   ├── Header  → lee useDrawer() para mostrar el botón hamburger y abrir el drawer
//   ├── Sidebar → lee useDrawer() para renderizar el panel móvil cuando isOpen=true
//   └── Outlet  → página hija (no necesita el contexto)
//
// El DrawerProvider cierra el drawer automáticamente al cambiar de ruta
// (pathname effect) — garantía de que el drawer no queda abierto al navegar.
// Los NavLinks del Sidebar también llaman a close() onClick como mecanismo primario.

import { createContext, useContext, useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'

const DrawerContext = createContext({
  isOpen: false,
  open: () => {},
  close: () => {},
  toggle: () => {},
})

export function DrawerProvider({ children }) {
  const [isOpen, setIsOpen] = useState(false)
  const { pathname } = useLocation()

  // Cierra el drawer en cada cambio de ruta (safety net: los NavLinks también
  // llaman a close() onClick, pero este efecto cubre navegación programática)
  useEffect(() => {
    setIsOpen(false)
  }, [pathname])

  const ctx = {
    isOpen,
    open: () => setIsOpen(true),
    close: () => setIsOpen(false),
    toggle: () => setIsOpen((prev) => !prev),
  }

  return (
    <DrawerContext.Provider value={ctx}>{children}</DrawerContext.Provider>
  )
}

export function useDrawer() {
  return useContext(DrawerContext)
}
