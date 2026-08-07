// Header (TopNav) — chrome persistente del App Shell (DS-001 §9.1).
//
// Módulo 7 (Responsive + Sequential Navigation): ajuste responsive mobile.
//
// DS-001 §11 breakpoints para el Header:
//   Mobile (< sm):   Wordmark + icono buscador + icono menú
//   Tablet (sm–lg):  Wordmark + barra buscador completa + icono menú + acciones
//   Desktop (≥ lg):  Wordmark + barra buscador completa + acciones (sin icono menú)
//
// El icono de menú (Menu) abre el drawer de Sidebar via DrawerContext.
// Solo es visible en < lg (donde el Sidebar desktop está oculto).
//
// Ctrl/Cmd+K registrado en document — abre el SearchModal desde cualquier ruta.

import { useState, useEffect, useCallback } from 'react'
import { NavLink } from 'react-router-dom'
import { ExternalLink, Search, Menu } from 'lucide-react'

import ThemeToggle from '../ui/ThemeToggle'
import SearchModal from '../ui/SearchModal'
import { useDrawer } from '../../providers/DrawerContext'

function Header() {
  const [searchOpen, setSearchOpen] = useState(false)
  const { toggle: toggleDrawer } = useDrawer()

  const openSearch = useCallback(() => setSearchOpen(true), [])
  const closeSearch = useCallback(() => setSearchOpen(false), [])

  // Ctrl+K / Cmd+K — acceso global al buscador (DS-001 §9.12)
  useEffect(() => {
    const handler = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        setSearchOpen(true)
      }
    }
    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [])

  return (
    <>
      <header
        className="sticky top-0 z-10 flex h-16 shrink-0 items-center gap-3 px-4 sm:px-6"
        style={{
          backgroundColor: 'var(--color-surface)',
          borderBottom: '1px solid var(--color-border)',
        }}
      >
        {/* ── Logo / wordmark — NavLink a Home (PV-001 Parte 1 §1) ─────── */}
        <NavLink
          to="/"
          className="flex shrink-0 items-baseline gap-2"
          style={{ textDecoration: 'none' }}
        >
          <span
            className="text-lg font-bold"
            style={{ color: 'var(--color-text-primary)' }}
          >
            THERS
          </span>
          <span
            className="hidden text-sm sm:inline"
            style={{ color: 'var(--color-text-secondary)' }}
          >
            Engineering Handbook
          </span>
        </NavLink>

        {/* ── Barra de búsqueda — oculta en mobile, visible en sm+ ─────── */}
        <button
          type="button"
          onClick={openSearch}
          className="hidden w-72 flex-1 items-center justify-between rounded-md px-3 py-2 text-sm transition-colors sm:flex sm:max-w-xs"
          style={{
            border: '1px solid var(--color-border)',
            backgroundColor: 'var(--color-surface-raised)',
            color: 'var(--color-text-secondary)',
          }}
          aria-label="Buscar en el Handbook (Ctrl+K)"
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = 'var(--color-border-strong)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = 'var(--color-border)'
          }}
        >
          <span>Buscar...</span>
          <span
            className="font-mono text-xs"
            style={{ color: 'var(--color-text-disabled)' }}
          >
            Ctrl+K
          </span>
        </button>

        {/* Spacer — empuja las acciones a la derecha en mobile */}
        <div className="flex-1 sm:hidden" aria-hidden="true" />

        {/* ── Acciones ──────────────────────────────────────────────────── */}
        <div className="flex shrink-0 items-center gap-2">
          {/* Icono de búsqueda — solo mobile (< sm), abre el mismo SearchModal */}
          <button
            type="button"
            onClick={openSearch}
            className="flex h-10 w-10 items-center justify-center rounded-md transition-colors sm:hidden"
            style={{
              border: '1px solid var(--color-border)',
              color: 'var(--color-text-secondary)',
            }}
            aria-label="Buscar en el Handbook"
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor =
                'var(--color-sidebar-item-hover)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'transparent'
            }}
          >
            <Search size={18} strokeWidth={2} aria-hidden="true" />
          </button>

          {/* ThemeToggle — siempre visible */}
          <ThemeToggle />

          {/* GitHub link — oculto en mobile para no saturar el header */}
          <a
            href="https://github.com/Fernandito41/THERS_REDSOCIAL"
            target="_blank"
            rel="noopener noreferrer"
            className="hidden h-10 w-10 items-center justify-center rounded-md transition-colors sm:flex"
            style={{
              border: '1px solid var(--color-border)',
              color: 'var(--color-text-secondary)',
            }}
            aria-label="Ver repositorio en GitHub"
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor =
                'var(--color-sidebar-item-hover)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'transparent'
            }}
          >
            <ExternalLink size={18} strokeWidth={2} aria-hidden="true" />
          </a>

          {/* Icono de menú (hamburger) — solo visible en < lg donde el
              Sidebar desktop está oculto (DS-001 §11).
              Abre el drawer del Sidebar via DrawerContext.              */}
          <button
            type="button"
            onClick={toggleDrawer}
            className="flex h-10 w-10 items-center justify-center rounded-md transition-colors lg:hidden"
            style={{
              border: '1px solid var(--color-border)',
              color: 'var(--color-text-secondary)',
            }}
            aria-label="Abrir menú de navegación"
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor =
                'var(--color-sidebar-item-hover)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'transparent'
            }}
          >
            <Menu size={18} strokeWidth={2} aria-hidden="true" />
          </button>
        </div>
      </header>

      {/* SearchModal — portal a document.body, z-50 (DS-001 §9.18) */}
      <SearchModal isOpen={searchOpen} onClose={closeSearch} />
    </>
  )
}

export default Header
