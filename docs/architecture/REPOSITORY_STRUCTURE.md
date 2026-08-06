# REPOSITORY_STRUCTURE

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/REPOSITORY_STRUCTURE.md` |
| Versión | 1.0 |
| Estado | Borrador — parcialmente verificado (ver nota de verificación) |
| Depende de | ARC-001, DS-001, WF-001, PV-001, HB-001 |
| Fuente de la estructura documentada | Captura de pantalla del explorador de archivos, raíz `THERS_REDSOCIAL_2026` |

> ⚠️ **Nota de verificación.** Este documento distingue explícitamente entre **estructura confirmada visualmente** (la carpeta `Frontend/`, completamente expandida en la captura recibida) y **estructura no confirmada** (`backend/`, `docs/` y `handbook/`, que aparecen colapsadas en la misma captura — se conoce su nombre y su ubicación en la raíz, no su contenido interno). Donde se describe contenido no confirmado, se marca explícitamente como tal y se indica la fuente de la inferencia (un documento oficial ya aprobado, nunca una suposición sin respaldo). Ninguna carpeta se documenta como si existiera sin haber sido vista o citada de una fuente ya aprobada.
>
> También se identificó, a partir del nombre de la carpeta raíz (`THERS_REDSOCIAL_2026`), que el producto de THERS es **una red social** — información que hasta ahora no estaba confirmada en `PROJECT_CONTEXT.md` (sección 1, marcada como pendiente). Se recomienda actualizar ese documento con este dato una vez confirmado el resto del alcance funcional.
>
> Por último: la tarea menciona "FAS" entre los documentos que esta estructura debe respetar. No hay ningún documento con ese identificador disponible en este contexto — no se incorporó contenido de él por no tener acceso a su contenido real. Se recomienda una revisión de este documento en cuanto "FAS" esté disponible.

---

## 1. Propósito del repositorio

`THERS_REDSOCIAL_2026` es el repositorio único (monorepo) del proyecto THERS: aloja el producto (una red social), su backend, y el THERS Engineering Handbook como aplicaciones independientes bajo una misma raíz — además de la documentación de soporte del propio repositorio. THERS Technologies trata este repositorio con el mismo estándar de organización que tendría el repositorio de una empresa de software real (STD-001, Manual de Organización), no como un proyecto académico informal.

`[Pendiente de confirmación]`: la descripción funcional completa del producto — a qué audiencia sirve la red social y cuáles son sus características centrales — sigue sin documentarse más allá de confirmar, por el nombre de la carpeta raíz, que se trata de una red social.

---

## 2. Principios de organización

- **Separación por responsabilidades:** `backend/`, `Frontend/` y `handbook/` son aplicaciones independientes, cada una en su propia carpeta de primer nivel, sin código compartido entre ellas visible en la raíz.
- **Independencia entre frontend, backend y documentación:** el Frontend del producto no depende de que el backend esté disponible para avanzar su desarrollo — mismo principio ya aplicado a la arquitectura del Handbook (ARC-001 §1), que tampoco depende del backend por ser una aplicación estática independiente.
- **Modularidad por dominio (Frontend):** dentro de `Frontend/src`, el código no se organiza por tipo de archivo, sino por dominio funcional — `features/auth`, `features/legal` — cada uno con sus propios `components/`, `hooks/`, `pages/` e `index.js` como punto de entrada del módulo.
- **Documentación como fuente de verdad, a nivel de primer orden:** `docs/` y `handbook/` existen como carpetas de primer nivel de la raíz, al mismo nivel jerárquico que el código de producto (`backend/`, `Frontend/`) — no como un anexo secundario dentro de alguna de las aplicaciones.
- **Escalabilidad:** la organización por features del Frontend está pensada para admitir nuevos dominios funcionales (además de `auth` y `legal`) sin reorganizar los ya existentes — cada feature nueva es una carpeta adicional dentro de `features/`, no una modificación de las actuales.

---

## 3. Árbol completo del repositorio

```
THERS_REDSOCIAL_2026/
│
├── backend/                     # No expandida en la captura de referencia — ver sección 6
│
├── docs/                        # No expandida en la captura de referencia — ver sección 7
│
├── Frontend/
│   ├── node_modules/
│   ├── public/
│   ├── src/
│   │   ├── app/
│   │   │   ├── providers/
│   │   │   ├── router/
│   │   │   │   └── router.jsx
│   │   │   └── store/
│   │   ├── assets/
│   │   ├── features/
│   │   │   ├── auth/
│   │   │   │   ├── components/
│   │   │   │   ├── hooks/
│   │   │   │   │   └── useAuth.js
│   │   │   │   ├── pages/
│   │   │   │   │   ├── AuthPage.jsx
│   │   │   │   │   ├── Login.jsx
│   │   │   │   │   └── Register.jsx
│   │   │   │   └── index.js
│   │   │   └── legal/
│   │   │       ├── pages/
│   │   │       └── index.js
│   │   ├── shared/
│   │   │   ├── components/
│   │   │   └── lib/
│   │   ├── App.css
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── .gitignore
│   ├── index.html
│   ├── package-lock.json
│   ├── package.json
│   ├── postcss.config.js
│   ├── tailwind.config.js
│   └── vite.config.js
│
└── handbook/                    # No expandida en la captura de referencia — ver sección 5
```

Todo lo mostrado dentro de `Frontend/` corresponde exactamente a lo visible en la captura de referencia — ningún archivo o carpeta fue agregado, renombrado ni reorganizado.

---

## 4. Descripción de cada carpeta principal

### `backend/`

- **Propósito:** alojar la API del producto (Flask, PostgreSQL, JWT — stack confirmado en `PROJECT_CONTEXT.md` §4).
- **Responsable:** Diego (Tech Lead Backend, STD-001 §2).
- **Contenido esperado:** código de la API, configuración de base de datos y autenticación.
- **Qué NO debe contener:** código del Frontend ni del Handbook, documentos oficiales fuente (esos viven en `docs/`).
- `[Pendiente de confirmación]`: contenido interno real — no expandida en la captura de referencia. Ver sección 6 para la organización esperada, marcada explícitamente como no verificada.

### `docs/`

- **Propósito:** alojar la documentación oficial del proyecto en formato Markdown.
- **Responsable:** compartido entre el equipo, con Fernando como coordinador de la documentación de organización y arquitectura (STD-001 §2).
- **Contenido esperado:** documentos oficiales versionados (`.md`), organizados por categoría — ver sección 7.
- **Qué NO debe contener:** código de ninguna de las tres aplicaciones.
- `[Pendiente de confirmación]`: contenido interno real — no expandida en la captura de referencia.

### `Frontend/`

- **Propósito:** aplicación del producto — la red social de THERS.
- **Responsable:** Piche (Tech Lead Frontend, STD-001 §2).
- **Contenido esperado:** código fuente de la aplicación React (Vite + Tailwind CSS), organizado por features (ver sección 5).
- **Qué NO debe contener:** documentación oficial fuente, código del backend, código del Handbook.

### `handbook/`

- **Propósito:** el THERS Engineering Handbook — plataforma de documentación técnica interna, ya diseñada por completo en ARC-001, DS-001, WF-001 y PV-001.
- **Responsable:** compartido — diseño liderado por Fernando, mantenimiento de contenido distribuido entre el equipo según ownership por documento (DS-001 §14).
- **Contenido esperado:** según ARC-001 §16, una aplicación independiente con su propio `src/`, `public/` y contenido MDX — arquitectura estática (SSG), sin dependencia del backend.
- **Qué NO debe contener:** código del producto (Frontend), lógica de negocio del backend.
- `[Pendiente de confirmación]`: contenido interno real — no expandida en la captura de referencia. Ver sección 5 para la relación entre `handbook/` y `docs/`, marcada explícitamente como no verificada.

---

## 5. Frontend

`Frontend/` y `handbook/` son **dos aplicaciones independientes** dentro del mismo dominio "frontend" del monorepo — comparten el tipo de tecnología de base (aplicaciones web con React) pero no comparten código, dependencias, ni ciclo de despliegue.

| | `Frontend/` (Red Social) | `handbook/` (Engineering Handbook) |
|---|---|---|
| Responsabilidad | Producto — la aplicación que usan los usuarios finales de THERS | Documentación técnica interna — la plataforma que usa el propio equipo |
| Depende del backend | Sí, para autenticación (JWT) y datos (features/auth ya visible en el árbol) | No — arquitectura estática (SSG), independiente por diseño (ARC-001 §1) |
| Confirmación de estructura | Completa (sección 3) | No expandida en la captura de referencia |

`[Pendiente de confirmación]`: la relación exacta entre `docs/` y `handbook/` no puede determinarse de la captura recibida, porque ambas carpetas están colapsadas. Como hipótesis de trabajo — no como hecho documentado — es razonable que `docs/` aloje el contenido MDX fuente y `handbook/` la aplicación que lo renderiza, siguiendo la misma separación entre capa de contenido y capa de aplicación ya definida en ARC-001 §16. Se recomienda una captura expandida de ambas carpetas para cerrar esta sección con precisión.

---

## 6. Backend

`[Pendiente de confirmación — sección completa]`: `backend/` no aparece expandida en la captura de referencia recibida, por lo que su organización interna no puede documentarse como estructura confirmada. Lo que sigue es la organización esperada según arquitectura hexagonal / Clean Architecture, tal como la solicita esta tarea — se presenta explícitamente como **propuesta a confirmar**, no como estructura ya verificada:

| Carpeta esperada | Propósito conceptual (Clean Architecture) |
|---|---|
| `application/` | Casos de uso — orquesta la lógica de negocio sin conocer detalles de infraestructura |
| `domain/` | Entidades y reglas de negocio puras, sin dependencias de framework |
| `interfaces/` | Adaptadores de entrada/salida — controladores HTTP, serializadores |
| `config/` | Configuración de la aplicación (variables de entorno, conexión a base de datos) |
| `extensions/` | Inicialización de extensiones de Flask (JWT, ORM, CORS, etc.) |
| `run.py` / `run/` | Punto de entrada de la aplicación |

**Antes de que esta sección se considere parte de la estructura documentada del repositorio, se necesita una captura expandida de `backend/` que confirme o corrija esta tabla.**

---

## 7. Documentación

`[Pendiente de confirmación parcial]`: `docs/` no aparece expandida en la captura de referencia. Lo que sigue no se documenta como estructura visualmente confirmada, sino como la categorización **ya aprobada** en ARC-001 (sitemap del Handbook, ARC-001 §2) — que es la fuente de verdad de cómo debe organizarse el contenido documental del proyecto, independientemente de si `docs/` es su carpeta de contenido o si esa categorización vive dentro de `handbook/`:

| Categoría | Contenido |
|---|---|
| `architecture/` | Documentos de arquitectura — incluye este mismo documento, según la ruta indicada en la tarea (`docs/architecture/REPOSITORY_STRUCTURE.md`), que es el único dato de ubicación confirmado directamente (no inferido) para esta carpeta |
| `design/` (Design System) | DS-001 y sus extensiones |
| `organization/` (Organización) | STD-001 (Manual de Organización, Manual Operativo) |
| `academy/` | Onboarding, glosario, tutoriales |
| `playbooks/` | Procedimientos operativos paso a paso |
| `roadmap/` | Roadmap del proyecto |

Esta tabla constituye la **fuente oficial del conocimiento del proyecto** en su capa documental, en el sentido de que ARC-001 ya la define como la única taxonomía aprobada — lo que falta confirmar es únicamente en qué carpeta física del repositorio (`docs/`, `handbook/`, o una combinación de ambas) se implementa.

---

## 8. Convenciones

- **Nombres de carpetas:** minúsculas en la gran mayoría de los casos (`backend`, `docs`, `handbook`, `src`, `features`, `shared`) — con una excepción visible y no normalizada en la captura: `Frontend/` con mayúscula inicial. Se documenta tal como existe, sin proponer corregirla (regla obligatoria de esta tarea).
- **Nombres de archivo:** componentes React en PascalCase (`AuthPage.jsx`, `Login.jsx`, `Register.jsx`, `App.jsx`); hooks en camelCase con prefijo `use` (`useAuth.js`); archivos de configuración en kebab-case (`tailwind.config.js`, `vite.config.js`, `postcss.config.js`) — patrón confirmado de forma consistente en todo `Frontend/`.
- **Idioma:** código, nombres de carpeta y de archivo en inglés (`auth`, `legal`, `shared`, `components`, `hooks`, `providers`); documentación oficial en español (confirmado por la totalidad de los documentos oficiales ya redactados — STD-001, ARC-001, DS-001, WF-001, PV-001).
- **Formato de documentación:** Markdown (GitHub Flavored Markdown), consistente con el resto de la documentación oficial del proyecto.
- **Versionado de documentos oficiales:** esquema `MAJOR.MINOR`, ya establecido en DS-001 §16 y aplicado a todos los documentos de la serie.
- **Ubicación de documentos oficiales:** dentro de `docs/`, en la subcarpeta correspondiente a su categoría (sección 7) — este mismo documento confirma la existencia de al menos `docs/architecture/`.

---

## 9. Reglas

- No crear carpetas fuera de la estructura ya aprobada en este documento.
- No mover documentos oficiales de su categoría dentro de `docs/` sin registrar el cambio (mismo estándar de trazabilidad ya exigido para decisiones técnicas, STD-001 §12).
- No mezclar documentación con código: `docs/` y `handbook/` nunca contienen código de producto; `backend/` y `Frontend/` nunca contienen documentos oficiales fuente.
- Cada aplicación (`backend/`, `Frontend/`, `handbook/`) mantiene su propio `package.json` (o equivalente) — confirmado para `Frontend/`, donde `package.json` vive dentro de la propia carpeta y no en la raíz del monorepo.
- Cada aplicación mantiene sus propias dependencias — no se comparten `node_modules` entre `Frontend/` y `handbook/`.
- `Frontend/node_modules/` (y su equivalente en `handbook/`, de aplicar) nunca se versiona — confirmado por la presencia de `.gitignore` dentro de `Frontend/`.

---

## 10. Escalabilidad futura

Carpetas que el repositorio podrá incorporar más adelante, sin que su llegada implique reorganizar la estructura actual — se documenta únicamente su propósito futuro, no se agregan ahora:

| Carpeta futura | Propósito |
|---|---|
| `database/` | Scripts de migración, semillas de datos y esquema versionado de PostgreSQL, hoy gestionados presumiblemente dentro de `backend/` |
| `docker/` | Definiciones de contenedores para entorno de desarrollo/despliegue reproducible de las tres aplicaciones |
| `.github/` | Workflows de CI/CD — validación automática de PRs, lint, tests, y los validadores de frontmatter/enlaces rotos ya previstos para el Handbook (ARC-001 §17) |
| `scripts/` | Utilidades de automatización de uso interno del equipo (setup de entorno, tareas recurrentes) |
| `tools/` | Herramientas de desarrollo compartidas entre aplicaciones que no encajen como dependencia de una sola |
| `tests/` | Suite de pruebas, si el equipo decide centralizarla fuera de cada aplicación en vez de mantenerla junto a `backend/` y `Frontend/` respectivamente |

---

## 11. Conclusión

La separación estricta entre `backend/`, `Frontend/`, `handbook/` y `docs/` — cada una como carpeta de primer nivel, independiente en dependencias y ciclo de vida — es lo que permite que el repositorio de THERS escale sin que el crecimiento de una aplicación obligue a reorganizar las demás. La organización por features dentro de `Frontend/` extiende ese mismo principio a nivel de código: un dominio funcional nuevo es una carpeta adicional, no una modificación de código existente.

Esta estructura facilita la colaboración porque cada integrante del equipo (Diego en backend, Piche en Frontend, el resto en documentación y QA) trabaja dentro de un límite claro sin pisar el trabajo de los demás, y facilita el onboarding de nuevos desarrolladores porque la ubicación de cualquier pieza del sistema es predecible por convención, no por memoria institucional. La misma predictibilidad es lo que hace que este documento — y el repositorio que describe — funcione como contexto confiable tanto para desarrolladores humanos como para asistentes de IA (Claude, Claude Code, Cursor, Codex): ninguno de los dos necesita explorar el árbol completo para saber dónde debería vivir o buscarse algo.

**Este documento no modifica la arquitectura del repositorio — la documenta tal como existe, con las secciones no verificadas señaladas explícitamente para una revisión posterior.**
