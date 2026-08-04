# THERS Engineering Handbook

## Propuesta de Arquitectura UX, Information Architecture y Sistema de Frontend

**Documento de diseño — Fase Pre-desarrollo (sin código)**
**Rol del autor:** Principal UX Architect · Information Architect · Senior Frontend Engineer
**Versión:** 0.1 — Borrador para revisión del Comité Técnico
**Estado:** Propuesta (pendiente de aprobación según sección 11 del Manual de Organización — decisión de impacto medio/alto: nueva plataforma de documentación)

---

## Índice

1. [Arquitectura completa del portal](#1-arquitectura-completa-del-portal)
2. [Sitemap](#2-sitemap)
3. [Flujo de navegación](#3-flujo-de-navegación)
4. [Organización del menú lateral](#4-organización-del-menú-lateral)
5. [Componentes reutilizables](#5-componentes-reutilizables)
6. [Sistema de colores](#6-sistema-de-colores)
7. [Tipografía](#7-tipografía)
8. [Iconografía](#8-iconografía)
9. [Diseño responsive](#9-diseño-responsive)
10. [Modo oscuro](#10-modo-oscuro)
11. [Sistema de búsqueda](#11-sistema-de-búsqueda)
12. [Breadcrumbs](#12-breadcrumbs)
13. [Tabla de contenidos](#13-tabla-de-contenidos)
14. [Organización de futuras páginas](#14-organización-de-futuras-páginas)
15. [Recomendaciones UX](#15-recomendaciones-ux)
16. [Estructura de carpetas del proyecto](#16-estructura-de-carpetas-del-proyecto)
17. [Buenas prácticas para mantener el handbook durante varios años](#17-buenas-prácticas-para-mantener-el-handbook-durante-varios-años)

---

## 0. Principio rector

Antes de entrar en el detalle, una decisión de arquitectura marca todo lo demás:

> **El Handbook es "docs-as-code".** Vive en Git, se escribe en Markdown/MDX, se revisa por Pull Request (igual que el código, según el Manual de Organización sección 8-10) y se construye con el mismo stack que ya domina el equipo: **React + Vite + Tailwind**. No se introduce un framework de documentación ajeno (Docusaurus, GitBook, Confluence) que el equipo tendría que aprender aparte. Esto también implica que **Notion deja de ser la fuente de verdad de documentación técnica** (hoy referenciada en la sección 14 del Manual de Organización) y el Handbook la reemplaza como única fuente oficial. Notion queda solo para gestión operativa (backlog, sprints, minutas).

---

## 1. Arquitectura completa del portal

Se propone una arquitectura en 5 capas, desacopladas entre sí:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. CONTENT LAYER                                             │
│    Markdown/MDX + frontmatter, versionado en Git             │
│    (docs/ organizados por categoría — ver sección 16)        │
└───────────────────────────┬────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. BUILD LAYER                                                │
│    Vite + plugin MDX · remark/rehype (TOC, slugs, admoni-     │
│    tions, syntax highlight) · generación de índice de         │
│    búsqueda estático en build time                            │
└───────────────────────────┬────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. APP SHELL (React)                                          │
│    Router · Layout persistente (TopNav + Sidebar + TOC) ·     │
│    Content Renderer · Estado global (tema, búsqueda, sidebar) │
└───────────────────────────┬────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. DESIGN SYSTEM LAYER                                        │
│    Tailwind + tokens (color, tipografía, spacing) ·           │
│    Componentes reutilizables (sección 5)                      │
└───────────────────────────┬────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. DELIVERY LAYER                                             │
│    Build estático (SSG) → hosting interno / GitHub Pages /    │
│    Vercel privado · CI valida links rotos y frontmatter       │
└─────────────────────────────────────────────────────────────┘
```

**Por qué SSG (Static Site Generation) y no una SPA con datos en runtime:**
- El contenido cambia por PR, no por usuario final → no necesita backend propio.
- Carga instantánea, indexable, funciona sin depender de que Flask/PostgreSQL estén arriba.
- El Handbook no debe depender de la disponibilidad del backend de producto (Flask/PostgreSQL); es un sistema independiente.

**Justificación de no usar un CMS o Confluence:** el equipo ya trabaja 100% en GitHub Flow (branches, PRs, revisión — sección 8-10 del Manual). Un CMS externo rompería ese flujo y crearía una segunda fuente de verdad.

---

## 2. Sitemap

Estructura de primer y segundo nivel. Todo documento vive dentro de una de estas 8 categorías raíz; no se permiten páginas sueltas fuera de esta jerarquía (ver sección 14).

```
/ (Home)
│
├── /organizacion                     📘 Organización
│   ├── manual-de-organizacion        (ya existente — este repo)
│   ├── manual-operativo
│   ├── roles-y-responsabilidades
│   └── reglas-oficiales-del-equipo
│
├── /estrategia                       🧠 Estrategia
│   ├── plan-estrategico-ia
│   └── vision-y-objetivos
│
├── /arquitectura                     🏗️ Arquitectura
│   ├── vision-general
│   ├── diagramas-de-sistema
│   ├── decisiones-tecnicas (ADR)
│   └── integraciones
│
├── /ingenieria                       💻 Ingeniería
│   ├── /frontend
│   │   ├── convenciones-react
│   │   ├── componentes-y-estado
│   │   └── tailwind-y-estilos
│   ├── /backend
│   │   ├── api-flask
│   │   ├── autenticacion-jwt
│   │   └── endpoints
│   ├── /postgresql
│   │   ├── esquema-de-datos
│   │   ├── migraciones
│   │   └── convenciones-de-queries
│   ├── /docker
│   │   ├── entorno-local
│   │   └── despliegue
│   └── /git
│       ├── ramas-y-convenciones
│       ├── commits-y-prs
│       └── code-review
│
├── /academy                          🎓 Academy
│   ├── onboarding-nuevo-integrante
│   ├── glosario-thers
│   └── tutoriales-paso-a-paso
│
├── /playbooks                        📋 Playbooks
│   ├── proceso-de-release
│   ├── respuesta-a-incidentes
│   ├── checklist-de-code-review
│   └── checklist-de-onboarding
│
├── /roadmap                          🗺️ Roadmap
│   └── roadmap-actual
│
└── /meta                             ⚙️ Meta (sobre el propio handbook)
    ├── como-contribuir
    ├── convenciones-de-documentacion
    └── changelog-del-handbook
```

**Páginas de sistema** (no aparecen en el sidebar, pero forman parte del sitemap):
`/search` (resultados de búsqueda) · `/404` · `/changelog` (histórico global de todo el handbook, generado automáticamente por fecha de última edición).

---

## 3. Flujo de navegación

Se diseñan 4 flujos primarios, no mutuamente excluyentes:

**A. Flujo de exploración (Home → Categoría → Página)**
`Home` → tarjetas de categoría con descripción corta → `Sidebar` de la categoría → página específica. Es el flujo para alguien nuevo que no sabe qué busca.

**B. Flujo de búsqueda directa (Search-first)**
`Cmd/Ctrl+K` desde cualquier página → resultados agrupados por categoría → clic → aterriza directo en la página con el término resaltado y scroll automático al heading relevante. Es el flujo dominante una vez el equipo ya conoce el handbook.

**C. Flujo secuencial dentro de un manual**
Dentro de una categoría con orden lógico (ej. Academy/Onboarding, o Git: ramas → commits → PRs), navegación **Anterior / Siguiente** al final de cada página, para lectura guiada tipo curso.

**D. Flujo de referencia cruzada (cross-link)**
Enlaces contextuales "Ver también" dentro del contenido (ej. la página de PostgreSQL enlaza a la de Backend cuando se habla de migraciones). Evita que el usuario tenga que volver al sidebar para temas relacionados.

En todos los flujos, dos elementos permanecen **fijos y persistentes**: el Sidebar (izquierda) y el TopNav (arriba). El usuario nunca pierde la orientación de "dónde estoy dentro del árbol completo".

---

## 4. Organización del menú lateral

- **Estructura de árbol colapsable**, un nivel de profundidad visible por defecto (categoría → páginas); subcategorías con 3er nivel (ej. Ingeniería → Frontend) se colapsan por defecto salvo la sección donde el usuario está parado.
- **Auto-expansión contextual**: al entrar a una página, el sidebar expande automáticamente la rama que contiene esa página y la resalta (estado activo con color primario + barra lateral izquierda de acento).
- **Scroll independiente**: el sidebar tiene su propio scroll, separado del contenido, y mantiene la posición al navegar entre páginas de la misma sección.
- **Sticky/fijo** respecto al viewport, bajo el TopNav.
- **Contadores/badges opcionales** junto a categorías con contenido "nuevo" o "actualizado recientemente" (ej. punto de color o etiqueta "Actualizado").
- **Sección de favoritos/pins** (opcional, fase 2): el usuario marca páginas que usa frecuentemente (ej. "Convención de commits") y aparecen ancladas arriba del árbol.
- **Footer del sidebar**: enlace fijo a "Editar esta página en GitHub" y versión actual del handbook.

Jerarquía visual de 3 niveles:
```
📘 CATEGORÍA (mayúscula, bold, con icono)
   Página de nivel 1
   Página de nivel 1 (activa) ┃ ← barra de acento
      Subsección (heading h2 de esa página, si se ancla en sidebar extendido)
```

---

## 5. Componentes reutilizables

Sistema de componentes de la capa de Design System (sección 1, capa 4). Se agrupan por función:

**Navegación**
`TopNavBar` · `SidebarTree` · `Breadcrumbs` · `TableOfContentsRail` · `PrevNextNav` · `SearchModal (Cmd+K)` · `MobileDrawer`

**Contenido**
`CodeBlock` (con botón copiar y lenguaje etiquetado) · `Callout/Admonition` (variantes: Nota, Tip, Advertencia, Peligro — reutiliza el patrón `> **Nota:**` ya usado en el Manual de Organización) · `Tabs` (ej. para mostrar comandos en Windows/Mac/Linux) · `Table` (estilizada, responsive con scroll horizontal) · `Figure` (imagen + caption, como las del Manual) · `Accordion/Collapsible` · `ChecklistBlock` (renderiza las listas `- [ ]` con estilo, no interactivo por defecto) · `MermaidDiagram` (diagramas como código, ver sección 17) · `ADRCard` (tarjeta estructurada para decisiones técnicas, mapea la plantilla de la sección 12 del Manual)

**Metadatos y estado**
`PageMeta` (última actualización, autor/DRI, badge de estado: `Draft` / `Estable` / `Deprecado`) · `VersionBadge` · `FeedbackWidget` ("¿Esta página te resultó útil? Sí/No" + link a abrir Issue)

**Utilitarios**
`ThemeToggle` · `Button` · `Badge/Tag` · `EmptyState` · `404Page` · `SkeletonLoader` (mientras carga el índice de búsqueda)

Todos los componentes se construyen **headless-first** (lógica separada de estilos) para poder reutilizar tokens de Tailwind sin duplicar lógica de accesibilidad (foco, ARIA, teclado).

---

## 6. Sistema de colores

Paleta neutra de "developer tool" con un acento de marca, optimizada para lectura prolongada de texto técnico (no es una landing page de venta, es una herramienta de consulta diaria).

| Token | Uso | Light mode | Dark mode |
|---|---|---|---|
| `--color-primary` | Acento de marca, links, estado activo | `#4F46E5` (indigo-600) | `#818CF8` (indigo-400) |
| `--color-primary-hover` | Hover de elementos primarios | `#4338CA` | `#A5B4FC` |
| `--color-bg` | Fondo base | `#FFFFFF` | `#0F1115` |
| `--color-bg-secondary` | Sidebar, tarjetas | `#F7F8FA` | `#181B21` |
| `--color-border` | Bordes, separadores | `#E5E7EB` | `#2A2E37` |
| `--color-text` | Texto principal | `#1A1D23` | `#E6E8EB` |
| `--color-text-muted` | Texto secundario | `#6B7280` | `#9CA3AF` |
| `--color-success` | Confirmaciones, "Estable" | `#16A34A` | `#4ADE80` |
| `--color-warning` | Advertencias, "Draft" | `#D97706` | `#FBBF24` |
| `--color-danger` | Errores, "Deprecado" | `#DC2626` | `#F87171` |
| `--color-info` | Callouts informativos | `#0284C7` | `#38BDF8` |
| `--color-code-bg` | Fondo de bloques de código | `#F4F4F5` | `#14161B` |

Todos los pares light/dark cumplen **contraste WCAG AA (4.5:1)** mínimo para texto de cuerpo. Se define como tokens CSS (`--color-*`), no como colores hardcodeados en componentes, para que el cambio de tema sea un simple cambio de clase en `<html>` (ver sección 10).

---

## 7. Tipografía

| Uso | Familia | Fallback | Notas |
|---|---|---|---|
| UI y texto de cuerpo | **Inter** | system-ui, -apple-system, sans-serif | Excelente legibilidad en pantalla a tamaños pequeños |
| Código (inline y bloques) | **JetBrains Mono** | ui-monospace, Menlo, monospace | Distingue bien `0` de `O`, `1` de `l` — crítico en docs técnicas |
| Headings | Inter (misma familia, mayor peso) | — | Evita mezclar más de 2 familias |

**Escala tipográfica** (base 16px, ratio 1.25):

| Nivel | Tamaño | Peso | Uso |
|---|---|---|---|
| Display | 36px | 700 | Título de Home |
| H1 | 30px | 700 | Título de página |
| H2 | 24px | 600 | Secciones principales |
| H3 | 20px | 600 | Subsecciones |
| H4 | 16px | 600 | Sub-subsecciones |
| Body | 16px | 400 | Texto de cuerpo (line-height 1.7 para lectura larga) |
| Small | 14px | 400 | Metadatos, captions |
| Code | 14px | 400 | Bloques e inline code |

---

## 8. Iconografía

Se recomienda **Lucide** (set de iconos abierto, consistente en stroke-width, ya disponible en el ecosistema React del equipo).

- **Grosor de trazo único**: 1.5px–2px en todos los iconos, sin mezclar estilos "outline" y "filled".
- **Tamaños estándar**: 16px (inline en texto/badges) · 20px (sidebar, botones) · 24px (headers de sección).
- **Mapeo semántico por categoría** (usado en sidebar y tarjetas de Home):

| Categoría | Icono sugerido |
|---|---|
| Organización | `building-2` |
| Estrategia / Plan IA | `brain-circuit` |
| Arquitectura | `layout-template` / `boxes` |
| Frontend | `layout-panel-left` |
| Backend | `server` |
| PostgreSQL | `database` |
| Docker | `container` |
| Git | `git-branch` |
| Academy | `graduation-cap` |
| Playbooks | `list-checks` |
| Roadmap | `map` |
| Meta | `settings` |

- Callouts usan iconos semánticos fijos: Nota = `info`, Tip = `lightbulb`, Advertencia = `alert-triangle`, Peligro = `alert-octagon`.

---

## 9. Diseño responsive

| Breakpoint | Rango | Comportamiento |
|---|---|---|
| `mobile` | < 640px | Sidebar oculto tras drawer (hamburguesa). TOC oculta, se muestra como acordeón colapsable "En esta página" al inicio del contenido. Breadcrumbs truncados a 2 niveles (`Home › ... › Página actual`). |
| `tablet` | 640–1024px | Sidebar colapsable manualmente (icono toggle), overlay sobre el contenido al abrirse. TOC oculta u opcional en modal. |
| `desktop` | 1024–1440px | Layout de 3 columnas: Sidebar (fijo, ~260px) · Contenido (max-width ~760px para lectura óptima) · TOC (fijo, ~220px). |
| `wide` | > 1440px | Igual a desktop, con más padding lateral; el contenido **no** se estira a ancho completo (evita líneas de texto demasiado largas — mantener 65-75 caracteres por línea). |

Principio general: **mobile-first en el desarrollo, desktop-first en el uso real** (el equipo consulta el handbook mayormente desde laptop durante el trabajo), por lo que la experiencia desktop de 3 columnas es la prioridad de pulido, pero mobile debe ser completamente funcional para consultas rápidas.

---

## 10. Modo oscuro

- Implementación por **tokens CSS + atributo `data-theme` en `<html>`**, no por duplicar componentes.
- Detección inicial: `prefers-color-scheme` del sistema operativo, con **toggle manual** que sobreescribe y persiste la preferencia (guardado en almacenamiento local del navegador, no en sessionStorage).
- Sin parpadeo (FOUC): el tema se aplica antes del primer render mediante un script mínimo inline en el `<head>`, no después de que React hidrate.
- **Imágenes y diagramas**: los diagramas del Manual de Organización (organigrama, flujo de ramas) actualmente son PNG con fondo claro. Se recomienda migrarlos a **SVG o Mermaid** (texto-como-diagrama) para que hereden los tokens de color y no se vean con fondo blanco "flotando" en modo oscuro. Mientras tanto, los PNG existentes se envuelven en un contenedor con fondo blanco fijo, para no romper la legibilidad.
- Bloques de código: tema de sintaxis independiente para light/dark (ej. GitHub Light / GitHub Dark o equivalente), no solo invertir colores.

---

## 11. Sistema de búsqueda

- **Motor**: búsqueda 100% client-side sobre un índice estático generado en build time (ej. tipo Pagefind/FlexSearch) — evita depender de un servicio externo o de backend propio, coherente con la arquitectura SSG de la sección 1.
- **Entrada**: atajo `Ctrl/Cmd + K` global, además de un campo de búsqueda visible en el TopNav.
- **Modal de búsqueda**: overlay centrado, resultados agrupados por categoría (Organización, Ingeniería, etc.), con snippet de contexto y término resaltado.
- **Navegación por teclado**: flechas arriba/abajo + Enter, sin requerir mouse — clave para un equipo técnico.
- **Ranking**: prioriza coincidencias en título > headings > cuerpo; boost adicional a páginas marcadas `Estable` sobre `Draft`.
- **Casos vacíos**: si no hay resultados, sugerir categorías relacionadas y un link directo a "crear/pedir esta página" (Issue prellenado en GitHub) — esto también sirve como señal de qué documentación falta.
- **Analítica de búsqueda** (opcional, fase 2): registrar términos buscados sin resultados para priorizar qué escribir después — insumo directo para el Roadmap del propio handbook.
- **Escalabilidad**: si el handbook crece a cientos de páginas y la búsqueda estática se vuelve pesada, ruta de migración a un motor tipo Typesense/Meilisearch autohospedado, sin cambiar la experiencia de usuario.

---

## 12. Breadcrumbs

- Patrón fijo: `Home › Categoría › [Subcategoría] › Página actual`.
- **Autogenerado** a partir de la ruta de carpetas + el campo `title` del frontmatter de cada página (nunca se escribe a mano — ver gobernanza en sección 14).
- Cada nivel intermedio es clicable y navega a la página índice de esa categoría.
- El último nivel (página actual) no es clicable, se muestra en color muted.
- **Mobile**: colapsa niveles intermedios en un elemento `...` clicable que despliega el resto (evita romper el layout con breadcrumbs largos como `Ingeniería › Backend › Autenticación JWT`).

---

## 13. Tabla de contenidos

- **Ubicación**: riel fijo a la derecha en desktop/wide, generado automáticamente a partir de los headings `H2` y `H3` del MDX (no se mantiene a mano).
- **Scroll-spy**: resalta el heading correspondiente a la sección visible mientras el usuario hace scroll.
- **Título del riel**: "En esta página".
- **Mobile/Tablet**: se convierte en un acordeón colapsado por defecto, ubicado justo debajo del título H1 y antes del contenido.
- **Profundidad**: máximo 2 niveles (H2 y H3); H4 no aparece en el TOC para evitar ruido visual en páginas largas como el Manual de Organización.

---

## 14. Organización de futuras páginas

Gobernanza para que el handbook no se vuelva caótico a medida que crece:

**Frontmatter obligatorio en cada página** (metadatos, no visible como texto plano, controla breadcrumbs/TOC/badges automáticamente):

| Campo | Ejemplo | Propósito |
|---|---|---|
| `title` | "Autenticación JWT" | Usado en breadcrumbs, sidebar, `<title>` |
| `category` | `ingenieria/backend` | Determina posición en el sitemap |
| `order` | `3` | Orden dentro de su categoría |
| `status` | `draft` / `stable` / `deprecated` | Badge visual |
| `owner` | Nombre del integrante responsable | Aparece en `PageMeta` |
| `last_updated` | Fecha (autogenerada por Git) | Aparece en `PageMeta` |
| `tags` | `[jwt, seguridad, api]` | Insumo para búsqueda y "Ver también" |

**Regla para nuevas categorías raíz** (no subpáginas): agregar una categoría de primer nivel (ej. algo distinto a las 8 actuales) se trata como **decisión de alto impacto** (sección 11 del Manual de Organización): requiere propuesta breve + consenso del Comité Técnico, porque afecta el sidebar y el sitemap global.

**Regla para subpáginas dentro de una categoría existente**: cualquier integrante puede añadirlas directamente vía PR, sin proceso especial — mismo flujo que cualquier otro cambio de código.

**Plantillas**: cada categoría tiene un archivo `_template.mdx` con el frontmatter y esqueleto de secciones esperado (ej. la plantilla de Playbook siempre incluye "Cuándo usar este playbook", "Pasos", "Rollback").

---

## 15. Recomendaciones UX

- **Una sola fuente de verdad por tema.** Si algo ya está en el código (ej. un README de instalación), el handbook enlaza, no duplica. Duplicar contenido es la causa #1 de que la documentación quede desactualizada.
- **"Editar esta página" visible siempre**, con link directo al archivo en GitHub — reduce la fricción de reportar/corregir errores a casi cero.
- **Nunca una página huérfana**: toda página nueva debe aparecer en el sidebar y en el sitemap; si no amerita estar en el árbol de navegación, probablemente no debería existir como página independiente.
- **Terminología consistente**: un glosario único (`Academy/glosario-thers`) define términos como "Sprint", "ADR", "Hotfix" una sola vez; el resto del handbook enlaza a esa definición en vez de redefinir.
- **Progressive disclosure**: páginas largas (como este mismo Manual de Organización) se benefician de TOC + Accordion para secciones opcionales, en vez de forzar scroll infinito.
- **Feedback continuo**: el widget "¿Te sirvió esta página?" (sección 5) alimenta directamente la retrospectiva mensual del equipo (sección 6 del Manual de Organización) como insumo para "Revisión de documentación".
- **Accesibilidad no negociable**: navegación completa por teclado, roles ARIA en sidebar/TOC/breadcrumbs, contraste AA mínimo, `alt` obligatorio en frontmatter para toda imagen (no opcional).
- **Rendimiento como feature**: presupuesto de carga inicial objetivo (< 2s en conexión promedio); el índice de búsqueda se carga de forma diferida (lazy), no bloquea el render inicial.

---

## 16. Estructura de carpetas del proyecto

```
thers-handbook/
├── docs/                                # Content Layer — única fuente de verdad
│   ├── organizacion/
│   │   ├── manual-de-organizacion.mdx
│   │   ├── manual-operativo.mdx
│   │   ├── roles-y-responsabilidades.mdx
│   │   └── reglas-oficiales-del-equipo.mdx
│   ├── estrategia/
│   │   └── plan-estrategico-ia.mdx
│   ├── arquitectura/
│   │   ├── vision-general.mdx
│   │   └── decisiones/              # ADRs individuales
│   │       └── adr-001-*.mdx
│   ├── ingenieria/
│   │   ├── frontend/
│   │   ├── backend/
│   │   ├── postgresql/
│   │   ├── docker/
│   │   └── git/
│   ├── academy/
│   ├── playbooks/
│   ├── roadmap/
│   └── meta/
│
├── src/                                  # App Shell + Design System
│   ├── components/
│   │   ├── navigation/        (Sidebar, Breadcrumbs, TOC, TopNav)
│   │   ├── content/            (CodeBlock, Callout, Tabs, ADRCard...)
│   │   └── ui/                 (Button, Badge, ThemeToggle...)
│   ├── layouts/
│   │   └── DocLayout.tsx
│   ├── styles/
│   │   └── tokens.css          (colores, tipografía, spacing)
│   ├── lib/
│   │   ├── search-index.ts
│   │   └── mdx-plugins/        (remark/rehype: TOC, slugs, admonitions)
│   └── App.tsx
│
├── public/
│   └── media/                            (imágenes referenciadas por docs/)
│
├── scripts/
│   ├── check-links.ts                    (CI: detecta links rotos)
│   ├── validate-frontmatter.ts           (CI: valida campos obligatorios)
│   └── build-search-index.ts
│
├── .github/
│   └── workflows/
│       └── docs-ci.yml                   (lint + link check + build en cada PR)
│
├── vite.config.ts
├── tailwind.config.ts
└── README.md                             (cómo correr el handbook en local)
```

---

## 17. Buenas prácticas para mantener el handbook durante varios años

- **Ownership explícito**: cada página tiene un `owner` en el frontmatter (sección 14). Sin dueño, una página no se aprueba en PR.
- **Cadencia de revisión ligada al ritual existente**: la "Revisión de documentación" mensual (sección 6 del Manual de Organización) incluye ahora explícitamente auditar el handbook, no solo el README.
- **CI que falla el build ante contenido roto**: link checker automático (páginas/imágenes rotas) y validador de frontmatter en cada Pull Request — la documentación se trata con el mismo rigor que el código (mismo checklist de revisión, sección 9-10 del Manual).
- **Proceso de deprecación, no borrado silencioso**: una página obsoleta cambia `status: deprecated`, muestra un banner "Esta página está desactualizada, ver [X]" durante un período de transición, y solo se elimina después.
- **Changelog del propio handbook** (`meta/changelog-del-handbook`): cada cambio estructural (nueva categoría, reorganización del sidebar) queda registrado — igual filosofía que un ADR.
- **Diagramas como código, no como imágenes estáticas**: preferir Mermaid/texto sobre PNG exportados de herramientas externas (como los del Manual actual) — se versionan en Git, se pueden diffear en PRs, y heredan modo oscuro automáticamente.
- **Guía de estilo de escritura** (`meta/convenciones-de-documentacion`): tono, uso de "tú/usted", longitud recomendada de página, cuándo usar un Playbook vs. un Manual — evita que el handbook se sienta escrito por 4 personas distintas con 4 estilos distintos.
- **Evitar la "segunda fuente de verdad"**: si en el futuro se retoma Notion o cualquier otra herramienta para algo que ya vive en el handbook, se trata como una regresión a corregir, no como una alternativa válida.
- **Presupuesto de mantenimiento explícito**: reservar tiempo real (ej. dentro del sprint, no "cuando sobre tiempo") para documentación — de lo contrario el handbook crece rápido al inicio y se abandona en meses, el patrón más común de fracaso en este tipo de plataformas.

---

*Fin de la propuesta de arquitectura. Documento listo para discusión en Comité Técnico antes de iniciar cualquier implementación (sin código, según lo solicitado).*
