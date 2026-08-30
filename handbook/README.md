# THERS Engineering Handbook — Frontend

Implementación del THERS Engineering Handbook. Proyecto **docs-as-code**:
el contenido vive en Markdown/MDX dentro del propio repositorio y se
construye con React + Vite + Tailwind CSS.

Este repositorio implementa la documentación oficial ya aprobada:
`HB-001` · `STD-001` · `ARC-001` · `DS-001` · `WF-001` · `PV-001` · `FAS-001`.
Ninguno de esos documentos se reinterpreta desde el código: el código los sigue.

## Stack

- **React 19** — UI
- **Vite** — build tool / dev server
- **Tailwind CSS v4** — utilidades de estilo (vía `@tailwindcss/vite`)
- **oxlint** — linting
- **Prettier** — formato de código

## Requisitos

- Node.js 20+
- npm 10+

## Instalación

\`\`\`bash
npm install
\`\`\`

## Scripts disponibles

| Comando                  | Qué hace                                            |
| ------------------------ | --------------------------------------------------- |
| \`npm run dev\`          | Levanta el servidor de desarrollo con hot-reload    |
| \`npm run build\`        | Genera el build de producción en \`dist/\`          |
| \`npm run preview\`      | Sirve localmente el build de producción ya generado |
| \`npm run lint\`         | Corre oxlint sobre el proyecto                      |
| \`npm run format\`       | Formatea todo el proyecto con Prettier              |
| \`npm run format:check\` | Verifica formato sin modificar archivos (uso en CI) |

## Estado actual

Proyecto en etapa de **preparación inicial**. Aún no contiene:

- Estructura de carpetas por capas (se define en un documento posterior,
  ver FAS-001 §"Alcance" — reservado para FAS-002 o un ADR de estructura).
- Design System (tokens, componentes) — DS-001.
- Layouts ni páginas (Home, Documento, Categoría) — PV-001.

## Convenciones

Todo cambio relevante de este repositorio sigue el flujo de trabajo de
HB-001 (ramas \`feature/\`, \`fix/\`, \`chore/\`..., Pull Request con al menos
una revisión aprobada, sin push directo a \`main\`/\`develop\`).
