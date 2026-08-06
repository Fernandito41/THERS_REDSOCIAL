// Router real del Handbook — Módulo 3 (Navigation System).
//
// Usa createBrowserRouter de React Router v7 con rutas anidadas para que los
// layouts (Header + Sidebar) sean persistentes y no se remonten al navegar
// entre páginas del mismo layout (FAS-001 §6 — bajo acoplamiento, rendimiento).
//
// Arquitectura de layouts (WF-001 §3.2, PV-001 Partes 0–3):
//   HomeLayout     → '/'              — Sidebar colapsado a iconos (64px)
//   CategoryLayout → '/[categoria]'   — Sidebar expandido (260px), sin TOC
//   DocumentLayout → '/[cat]/[doc]'   — Sidebar expandido + TOC rail (220px)
//
// Cada layout usa <Outlet /> para renderizar la página hija correspondiente,
// manteniendo Header y Sidebar activos sin re-render entre rutas del mismo grupo.

import { createBrowserRouter, RouterProvider } from 'react-router-dom'

import HomeLayout from '../layouts/HomeLayout'
import CategoryLayout from '../layouts/CategoryLayout'
import DocumentLayout from '../layouts/DocumentLayout'

import HomePage from '../pages/HomePage'
import CategoryPage from '../pages/CategoryPage'
import DocumentPage from '../pages/DocumentPage'

import { ROOT_CATEGORIES } from './routes'

// ── Paths de las 8 categorías raíz (ARC-001 §2) ──────────────────────────
const CATEGORY_PATHS = ROOT_CATEGORIES.map((c) => c.path)

const router = createBrowserRouter([
  // ── Home ('/')  ──────────────────────────────────────────────────────────
  // Layout con Sidebar colapsado a franja de iconos (PV-001 Parte 1 §2).
  {
    path: '/',
    element: <HomeLayout />,
    children: [{ index: true, element: <HomePage /> }],
  },

  // ── Category Index — 8 rutas raíz (/organizacion, /estrategia …) ────────
  // Layout con Sidebar expandido. Sin TOC rail (WF-001 §5: plano Contextual
  // es exclusivo de Document Page y sus variantes).
  {
    element: <CategoryLayout />,
    children: CATEGORY_PATHS.map((path) => ({
      path,
      element: <CategoryPage />,
    })),
  },

  // ── Document Page — /:category/:doc ─────────────────────────────────────
  // Layout con Sidebar expandido + TOC rail 220px (DS-001 §8.1).
  // El parámetro :doc identifica el documento dentro de la categoría.
  // En esta etapa (Módulo 3) el contenido es un placeholder —
  // el rendering MDX real corresponde a módulos posteriores (ARC-001 §1 capa 2).
  {
    element: <DocumentLayout />,
    children: [
      {
        path: '/:category/:doc',
        element: <DocumentPage />,
      },
    ],
  },
])

// ── RouterProvider ────────────────────────────────────────────────────────
// Componente exportado que App.jsx renderiza directamente.
// Se extrae como componente para que App.jsx solo haga `return <Router />`,
// dejando la configuración de rutas encapsulada aquí (FAS-001 §4 — cohesión).
function Router() {
  return <RouterProvider router={router} />
}

export default Router
