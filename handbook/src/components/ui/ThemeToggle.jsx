// ThemeToggle — DS-001 §9 / §10.
//
// Escribe data-theme="dark" | "light" en <html>, persistido en localStorage.
// El atributo data-theme en <html> es la única fuente de verdad del tema
// (DS-001 §10 — sin FOUC, sin duplicar componentes).
// El script anti-FOUC en index.html inicializa data-theme antes de React,
// por lo que getInitialTheme() solo necesita leer el atributo ya aplicado.
//
// Icono Moon (modo claro activo → click cambia a oscuro) /
//        Sun  (modo oscuro activo → click cambia a claro).
// Área de toque 40×40px (DS-001 §12 — mínimo 24×24px).
// FAS-001 §5 — bajo acoplamiento: sin contexto global ni prop drilling.

import { useState, useEffect } from 'react'
import { Sun, Moon } from 'lucide-react'

function getInitialTheme() {
  // Lee el atributo ya resuelto por el script anti-FOUC — nunca lee
  // localStorage directamente para evitar inconsistencias en SSR/hydration.
  return document.documentElement.getAttribute('data-theme') === 'dark'
    ? 'dark'
    : 'light'
}

function ThemeToggle() {
  const [theme, setTheme] = useState(getInitialTheme)

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('theme', theme)
  }, [theme])

  const toggle = () => setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'))

  return (
    <button
      type="button"
      onClick={toggle}
      className="flex h-10 w-10 items-center justify-center rounded-md transition-colors"
      style={{
        border: '1px solid var(--color-border)',
        color: 'var(--color-text-secondary)',
      }}
      aria-label={
        theme === 'dark' ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'
      }
      onMouseEnter={(e) => {
        e.currentTarget.style.backgroundColor =
          'var(--color-sidebar-item-hover)'
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.backgroundColor = 'transparent'
      }}
    >
      {theme === 'dark' ? (
        <Sun size={18} strokeWidth={2} aria-hidden="true" />
      ) : (
        <Moon size={18} strokeWidth={2} aria-hidden="true" />
      )}
    </button>
  )
}

export default ThemeToggle
