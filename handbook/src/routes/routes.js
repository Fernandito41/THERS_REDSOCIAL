// Datos de navegación del Handbook — fuente de verdad para el Sidebar y el router.
//
// Módulo 3 (Navigation System): se puebla ROOT_CATEGORIES con las 8 categorías
// raíz del sitemap (ARC-001 §2). El router real vive en routes/index.jsx y
// consume este archivo para construir las rutas de React Router.
//
// Iconos: strings de nombre Lucide (DS-001 §6.1 — única biblioteca aprobada).
// El mapeo string → componente Lucide vive en Sidebar.jsx para mantener
// este archivo libre de dependencias React (FAS-001 §4 — Utilidades no
// deben depender de la capa de Presentación).
//
// Mapeo categoría → icono: DS-001 §8 / ARC-001 §8.

// ── 8 categorías raíz del sitemap (ARC-001 §2) ─────────────────────────────
// Orden oficial del sitemap — nunca se reordena por frecuencia de uso ni
// personalización, para que la posición sea memorizable (PV-001 Parte 1 §2).
export const ROOT_CATEGORIES = [
  {
    path: '/organizacion',
    name: 'Organización',
    icon: 'building-2',
    description: 'Manual de Organización, Manual Operativo y reglas del equipo.',
  },
  {
    path: '/estrategia',
    name: 'Estrategia',
    icon: 'brain-circuit',
    description: 'Plan Estratégico IA, visión y objetivos del proyecto.',
  },
  {
    path: '/arquitectura',
    name: 'Arquitectura',
    icon: 'layout-template',
    description: 'Decisiones técnicas (ADR), diagramas y visión de sistema.',
  },
  {
    path: '/ingenieria',
    name: 'Ingeniería',
    icon: 'layout-panel-left',
    description: 'Frontend, Backend, PostgreSQL, Docker y Git.',
  },
  {
    path: '/academy',
    name: 'Academy',
    icon: 'graduation-cap',
    description: 'Onboarding, glosario THERS y tutoriales paso a paso.',
  },
  {
    path: '/playbooks',
    name: 'Playbooks',
    icon: 'list-checks',
    description: 'Procesos de release, respuesta a incidentes y code review.',
  },
  {
    path: '/roadmap',
    name: 'Roadmap',
    icon: 'map',
    description: 'Roadmap actual del proyecto THERS.',
  },
  {
    path: '/meta',
    name: 'Meta',
    icon: 'settings',
    description: 'Cómo contribuir, convenciones de documentación y changelog.',
  },
]

// ── Rutas completas del Handbook ────────────────────────────────────────────
// Array vacío preservado de Módulo 2: la forma del dato (path / layout / page)
// ya estaba definida. En Módulo 3 el router se construye programáticamente en
// routes/index.jsx usando ROOT_CATEGORIES, por lo que este array no es necesario
// en esta iteración. Queda disponible para rutas especiales futuras (404,
// /search, /meta/changelog) que no corresponden a ninguna categoría raíz.
export const routes = []
