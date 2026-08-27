# THERS — Notion Project Context

| Campo | Valor |
|---|---|
| Documento | `docs/project-management/NOTION_PROJECT_CONTEXT.md` |
| Generado | 2026-08-25, por Claude Code, mediante inspección directa del repositorio |
| Propósito | Puente entre Claude Code (que tiene acceso al repositorio) y Claude Chat (que organizará Notion) — resume el estado real de THERS y propone la arquitectura de Notion |
| Complementa a | `docs/project-management/THERS_PROJECT_INVENTORY.md` (catálogo plano, con hallazgos numerados `INV-01`…`INV-08`, citados aquí como referencia) |
| Regla de uso | Este documento **describe y propone** — no ratifica ninguna decisión de arquitectura ni de organización por sí mismo. Todo lo marcado `PENDIENTE DE APROBACIÓN` sigue el proceso de `HB-001` §11–12 (ADR) antes de tratarse como cerrado |

---

## 1. Project Overview

**THERS** es una red social construida por un equipo autogestionado de 4 integrantes, sin jerarquía vertical (Dirección Técnica ejercida de forma colegiada vía Comité Técnico, `HB-001` §1). Repositorio monorepo: `backend/` (API Flask), `Frontend/` (producto — la red social, React), `handbook/` (documentación técnica interna del equipo, aplicación independiente) y `docs/` (documentación oficial versionada).

Stack confirmado (`HB-001`, portada): **React 19 · Vite 8 · Tailwind CSS 3 · Flask 3 · PostgreSQL 16 · JWT**.

La descripción funcional completa del producto (audiencia, propuesta de valor) **no está formalmente documentada** en `/docs` — el `README.md` raíz la describe, pero no es fuente oficial (`CLAUDE.md` §1). Por el nombre de la carpeta raíz (`THERS_REDSOCIAL_2026`) y el alcance funcional ya usado como insumo en `DATABASE_ARCHITECTURE.md` §4.B, THERS apunta a ser una red social completa: perfiles, posts con texto/imagen, likes/comentarios, seguidores, mensajería, notificaciones.

---

## 2. Current Project Status

THERS tiene **autenticación real end-to-end** (registro + login contra PostgreSQL, no contra credenciales de prueba) y un **prototipo visual completo del producto** (feed, descubrir, mensajes, notificaciones, perfil, ajustes, más un conjunto grande de páginas públicas/informativas) — pero el prototipo visual **no tiene backend detrás**: todos sus datos son mock (`Frontend/src/features/feed/data/mockData.js`).

Punto crítico de gobernanza: **la documentación oficial de arquitectura (`docs/architecture/*.md`) está más actualizada que `README.md` y `CLAUDE.md`** en lo referente al backend. Ambos (README y CLAUDE.md) fueron editados el 2026-08-16 a las 12:22, y afirman que no hay persistencia real ni endpoint de registro; los documentos de `docs/architecture/` se actualizaron esa misma tarde a las 22:28 para reflejar que sí existen. Y el código avanzó 9 días más desde entonces (feed, páginas públicas, footer, sistema de toast, dark mode) sin que `FRONTEND_ARCHITECTURE.md` se actualizara. Ver `THERS_PROJECT_INVENTORY.md` hallazgos `INV-01` y `INV-07`.

**Resumen de un vistazo:**

| Área | Estado |
|---|---|
| Autenticación (registro + login) | ✅ Implementado y probado contra PostgreSQL real |
| Prototipo visual del producto (feed, público, legal) | ✅ UI completa, 🔴 sin backend |
| Persistencia más allá de `users` | 🔴 No implementada — todo lo demás es candidato sin ratificar |
| Testing backend | ✅ 13 tests de integración | Testing Frontend | 🔴 Ninguno |
| CI | ✅ Build Frontend + tests backend contra Postgres real, en cada push/PR |
| Documentación de arquitectura | 🟡 Backend/DB/API al día; Frontend desactualizada; Frontend/README/CLAUDE.md desincronizados entre sí |
| DevOps (deploy, CI/CD más allá del build, dominios, monitoreo) | 🔴 Sin documentar — territorio no especificado |

---

## 3. Repository Structure

```
THERS_REDSOCIAL_2026/
├── backend/          # API Flask — Clean/Hexagonal (domain/application/interfaces/infrastructure)
├── Frontend/         # Producto — React 19 + Vite 8 + Tailwind 3 (features/{auth,legal,public,feed})
├── handbook/         # THERS Engineering Handbook — app independiente (React+Vite+MDX, SSG)
├── docs/             # Documentación oficial versionada (Markdown) + 2 docs .docx/.pdf sin procesar
├── docker-compose.yml   # PostgreSQL 16 para desarrollo local
├── .github/workflows/ci.yml
├── README.md         # Informativo, no autoritativo — actualmente desactualizado (ver §2)
└── CLAUDE.md         # Reglas operativas para Claude Code — actualmente desactualizado (ver §2)
```

`backend/`, `Frontend/` y `handbook/` son aplicaciones independientes: sin código compartido, sin `node_modules` compartidos, cada una con su propio `package.json` (`REPOSITORY_STRUCTURE.md` §2/§9). Detalle completo de rutas, componentes y endpoints: `THERS_PROJECT_INVENTORY.md`.

---

## 4. Frontend Status

**Implementado:**
- Autenticación completa (Login/Register conectados al backend real, recuperación de contraseña solo de UI).
- 4 features: `auth`, `legal`, `public` (9 páginas informativas estáticas), `feed` (6 páginas, 100% mock).
- Sistema de layout: `AppShell`/`NavRail`/`MobileNav` (para `feed`), `PublicLayout` + `Footer` (para páginas públicas).
- Sistema de notificaciones `Toast`, `Spinner`, dark mode (`useTheme`), tokens de diseño propios en `tailwind.config.js` (paleta `pulse`/`ember`/`canvas`/`surface`, con referencia colgante a un `PRODUCT_DESIGN_SYSTEM.md` inexistente — `INV-02`).
- Alias de imports (`@`, `@features`, `@shared`, `@assets`) ya en uso.

**Pendiente / no implementado:**
- Backend de `feed` (posts, comentarios, likes, follows, notificaciones, mensajes) — todo mock.
- Rutas protegidas — cualquiera puede navegar a `/feed` sin sesión.
- Estado global (Context/Redux/Zustand) — solo `useState` local.
- Testing (ningún framework instalado).
- Lint cableado (`@eslint/js` instalado pero sin `eslint.config.js` ni script `lint`).

Fuente detallada: `THERS_PROJECT_INVENTORY.md` §1–5. Fuente oficial de arquitectura: `FRONTEND_ARCHITECTURE.md` (⚠️ desactualizada, no cubre `feed`/`public`/tokens — `INV-01`).

---

## 5. Backend Status

**Implementado (v0.6 de `BACKEND_ARCHITECTURE.md`):**
- `POST /api/register` y `POST /api/login` contra PostgreSQL 16 real (SQLAlchemy + Flask-Migrate/Alembic + psycopg v3).
- Modelo `User`: `id` UUID (`gen_random_uuid()` generado en PostgreSQL), `email` `CITEXT` único case-insensitive, `password_hash` (`werkzeug.security`, scrypt), `created_at`/`updated_at` con trigger.
- Patrón Repository (puerto `UserRepository` en `domain/`, adaptador `SQLAlchemyUserRepository` en `infrastructure/`), composition root en `interfaces/routes/auth_routes.py`.
- JWT con `identity=user.id` (UUID, ya no email — cambio de impacto para cualquier endpoint futuro que use `get_jwt_identity()`).
- Credenciales hardcodeadas y comparación de contraseña en texto plano — **eliminadas por completo**.

**Pendiente:**
- Base de datos compartida por el equipo o de producción (hoy solo local vía Docker Compose).
- Ratificación formal por el Comité Técnico de las decisiones de persistencia (SQLAlchemy, UUID, CITEXT, patrón Repository) — indicadas por el Tech Lead Backend, no votadas por los 4 integrantes según el proceso de `HB-001` §11.1.
- Endpoints protegidos, expiración/refresh de JWT, roles/autorización, validación declarativa, manejo global de errores, configuración por ambiente.
- Hallazgos sin resolver: `backend/app.py` huérfano (`INV-03`), naming `_init_.py` (`INV-04`).

Fuente detallada: `THERS_PROJECT_INVENTORY.md` §6–7. Fuente oficial: `BACKEND_ARCHITECTURE.md` v0.6 (al día con el código).

---

## 6. Database Status

Única entidad **implementada y ratificada**: `users`. Todo lo demás (posts, comentarios, likes, follows, mensajería, notificaciones, sesiones, OAuth, configuración de usuario) está registrado como **candidato objetivo** en `DATABASE_ARCHITECTURE.md` §4.B — el alcance funcional del producto está confirmado, pero su modelado (tablas, PK/FK, tipos) no. Nada de la capa objetivo se implementa sin ADR (`HB-001` §11–12).

Motor: **PostgreSQL 16** vía Docker Compose (`postgres:16-alpine`), verificado end-to-end (migración, UUID, CITEXT, trigger, downgrade/upgrade, reconstrucción desde volumen vacío) — reproducible por cualquier integrante del equipo, no todavía un entorno compartido/producción.

⚠️ Contradicción de datos menor entre documentos hermanos: `DATABASE_ARCHITECTURE.md` §11/§14 sigue listando `JWT_SECRET_KEY` como hardcodeado, pese a que `BACKEND_ARCHITECTURE.md` ya documenta esa corrección como resuelta (`INV-05`).

Fuente detallada: `THERS_PROJECT_INVENTORY.md` §8. Fuente oficial: `DATABASE_ARCHITECTURE.md` v0.4 + `DATABASE_ERD.md` (modelo ratificado) + `DATABASE_ERD_OBJETIVO.md` (modelo candidato, visual).

---

## 7. Testing Status

- **Backend:** 13 tests de integración (`backend/tests/test_auth.py`) contra PostgreSQL 16 real (BD `thers_test`, separada de `thers_dev`), framework `pytest` (elegido pragmáticamente, sin ratificación formal del Comité Técnico).
- **Frontend:** sin testing — ningún framework instalado.
- **Postman:** colección oficial `docs/api/postman/THERS.postman_collection.json` (`register`, `login`), con script de test en `login` (status, presencia de `token`/`user`) y seteo de variables de entorno.
- **CI:** `.github/workflows/ci.yml` corre en cada push/PR a `main`/`develop`/`feature/**` — build de Frontend (`npm run build`) y tests de backend (con Postgres de servicio, migración real vía `flask db upgrade`, luego `pytest`).

Fuente detallada: `THERS_PROJECT_INVENTORY.md` §9.

---

## 8. Design System

**No existe un Design System ratificado para el producto (`Frontend/`).** `DS-001` (el Design System del Handbook) declara textualmente en su §1.2 que no aplica al producto — ambos sistemas evolucionan de forma independiente salvo decisión de gobernanza explícita.

El código de `Frontend/` ya centraliza una paleta propia en `tailwind.config.js` (tokens `canvas`/`surface`/`ink`/`muted`/`line`/`pulse`/`ember`/`success`/`warning`, sombras, animaciones) con comentarios que citan un documento `PRODUCT_DESIGN_SYSTEM.md §2.3` — **ese archivo no existe en el repositorio** (`INV-02`). Es la señal más clara de que el equipo ya está pensando/diseñando un sistema de diseño propio del producto, pero el documento que lo formalizaría nunca se creó o se perdió.

**Recomendación (no una decisión tomada):** si el equipo confirma que quiere formalizar esos tokens, crear `docs/architecture/PRODUCT_DESIGN_SYSTEM.md` siguiendo el mismo formato que `BACKEND_ARCHITECTURE.md`/`FRONTEND_ARCHITECTURE.md` (separar implementado/propuesto/pendiente), o decidir explícitamente no hacerlo — pero no dejarlo como una referencia colgante en el código.

---

## 9. Git Workflow

Flujo real observado (coincide con `HB-001` §7–9):

```
feature/<nombre> | fix/<nombre> | chore/<nombre> | docs/<nombre> | hotfix/<nombre>
        ↓
   Pull Request → develop (título con prefijo Conventional Commits, vinculado a Issue)
        ↓
   Revisión (≥1 aprobación, el autor no se autoaprueba) + CI (build Frontend, tests backend)
        ↓
        Merge a develop
        ↓
   (periódicamente) PR de release: develop → main
```

`main` y `develop` son ramas protegidas — sin push directo, ambas exigen PR + ≥1 aprobación (`HB-001` §8.1). Commits en Conventional Commits (`feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`, `chore:`).

**Estado real ahora mismo:** `develop` está **78 commits por delante de `main`** — hay una release pendiente de PR. Existen además 3 ramas remotas no fusionadas que necesitan revisión del equipo (`origin/feature/update-readme`, `origin/chore/repo-hygiene`, `origin/feature/backend-foundation`) — ver `THERS_PROJECT_INVENTORY.md` §14 e hallazgo `INV-06`/`INV-08`.

Este documento **no modificó ninguna rama ni configuración de Git** — solo se inspeccionó `git log`/`git branch`/`git diff` en modo lectura.

---

## 10. Current Tasks

THERS no tiene un backlog formal fuera del repositorio (Notion, según `HB-001` §14, es donde debería vivir el Backlog/Sprints — hoy no hay forma de verificar su contenido desde el repositorio). Las tareas identificables **por evidencia de código** (features con UI pero sin backend, o con backend sin UI conectada) son:

| Tarea inferida | Evidencia | Área |
|---|---|---|
| Conectar `/feed` (posts, comentarios, likes) a un backend real | `mockData.js` + `DATABASE_ARCHITECTURE.md` §4.B "Contenido"/"Interacciones" candidatas | Backend + Frontend |
| Conectar recuperación de contraseña | `ForgotPassword.jsx`/`ResetPassword.jsx` existen sin endpoint correspondiente | Backend |
| Ratificar formalmente las decisiones de persistencia ya codificadas (SQLAlchemy, UUID, CITEXT, patrón Repository) | `BACKEND_ARCHITECTURE.md` §20.1, `DATABASE_ARCHITECTURE.md` §14 | Gobernanza (Comité Técnico) |
| Resolver o formalizar `PRODUCT_DESIGN_SYSTEM.md` | `INV-02` | Frontend / Design |
| Actualizar `FRONTEND_ARCHITECTURE.md` a la realidad del código | `INV-01` | Documentación |
| Sincronizar `README.md`/`CLAUDE.md` con `docs/architecture/*.md` | `INV-07` | Documentación |
| Decidir qué hacer con `backend/app.py` huérfano | `INV-03` | Backend |
| Corregir `_init_.py` → `__init__.py` | `INV-04` | Backend (bajo riesgo) |
| PR de release `develop` → `main` (78 commits pendientes) | `git log main..develop` | Gobernanza / Release |

Esto **no reemplaza** un backlog gestionado por el equipo — es lo que el propio repositorio revela como trabajo pendiente evidente. El Comité Técnico debe priorizar y asignar esto en Notion (ver §17–18).

---

## 11. Completed Work

- Setup inicial del monorepo (`backend/`, `Frontend/`, `handbook/`, `docs/`).
- Autenticación real: registro + login contra PostgreSQL 16, con migraciones, tests de integración, y corrección de las dos vulnerabilidades P0 originales (JWT secret hardcodeado, comparación de password en texto plano).
- Prototipo visual completo: feed, páginas públicas/informativas, footer, sistema de toast, dark mode, rediseño de auth con recuperación de contraseña (UI).
- CI funcional (build Frontend + tests backend contra Postgres real de servicio).
- Colección Postman oficial de autenticación.
- 4 documentos de arquitectura de producto (`BACKEND_ARCHITECTURE.md`, `DATABASE_ARCHITECTURE.md` + 2 ERD, `FRONTEND_ARCHITECTURE.md`, `API_CONTRACT.md`), todos siguiendo el mismo formato disciplinado (implementado/objetivo/pendiente).

---

## 12. In Progress

- Integración Frontend↔Backend más allá de auth (el feed sigue siendo mock).
- Ratificación formal de las decisiones de persistencia ya codificadas (implementadas por indicación del Tech Lead Backend, pendientes de consenso de los 4 integrantes).

---

## 13. Blocked

No se identificó ningún bloqueo técnico duro (nada impide que el equipo siga trabajando). Los bloqueos son de **gobernanza/documentación**, no de código:
- Cualquier feature nueva de persistencia (posts, follows, mensajería) está bloqueada por la falta de ratificación ADR de su modelado (`DATABASE_ARCHITECTURE.md` §4.C) — es una regla explícita del propio documento, no una suposición de esta tarea.
- Cualquier endpoint protegido futuro está bloqueado por la falta de decisión sobre estrategia de sesión (dónde vive el token, expiración) — `FRONTEND_ARCHITECTURE.md` §24 ítem 2, `BACKEND_ARCHITECTURE.md` §20 ítems 8–9.

---

## 14. Recommended Next Steps

No son decisiones tomadas — son recomendaciones a discutir y priorizar por el equipo (Sprint Planning, `HB-001` §17):

1. **Higiene de documentación (bajo esfuerzo, alto impacto):** actualizar `README.md` y `CLAUDE.md` para que reflejen que `register`/`login` ya usan persistencia real (`INV-07`), y actualizar `FRONTEND_ARCHITECTURE.md` para cubrir `feed`/`public`/tokens de diseño (`INV-01`).
2. **Cerrar el ADR de persistencia:** llevar a votación del Comité Técnico completo (los 4 integrantes) las decisiones ya codificadas por el Tech Lead Backend (SQLAlchemy, UUID, CITEXT, Flask-Migrate, patrón Repository) — hoy implementadas pero no ratificadas según `HB-001` §11.1.
3. **Decidir el destino de `PRODUCT_DESIGN_SYSTEM.md`:** formalizarlo (documentando los tokens ya en uso) o eliminar la referencia colgante del código (`INV-02`).
4. **Triage de ramas remotas no fusionadas:** revisar `origin/feature/update-readme`, `origin/chore/repo-hygiene`, `origin/feature/backend-foundation` (incluye `AUDITORIA_TECNICA.md` sin fusionar, `INV-06`) y decidir fusionar, rebasar o cerrar cada una.
5. **Preparar el PR de release** `develop → main` (78 commits acumulados).
6. **Priorizar la primera entidad objetivo a ratificar** (candidato natural: `posts`, ya que `feed` tiene UI completa esperando datos reales) vía ADR.
7. **Configurar Notion** siguiendo la estructura de §17–18 de este documento, alineada con `HB-001` §14/§16.

---

## 15. Documentation Index

| Documento | Ruta | Para qué sirve |
|---|---|---|
| Manual de Organización | `docs/architecture/organization/01_Manual_Organizacion/Source/HB-001-manual-organizacion.md.md` | Máxima autoridad — roles, git flow, ADR, reglas de IA |
| Estructura del repositorio | `docs/architecture/REPOSITORY_STRUCTURE.md` | Mapa del monorepo |
| Arquitectura Backend | `docs/architecture/BACKEND_ARCHITECTURE.md` | Capas, auth, persistencia, seguridad del backend |
| Arquitectura de Base de Datos | `docs/architecture/DATABASE_ARCHITECTURE.md` | Modelo de datos: implementado + objetivo + pendiente |
| ERD ratificado | `docs/architecture/DATABASE_ERD.md` | Diagrama de lo ya implementado (solo `users`) |
| ERD objetivo | `docs/architecture/DATABASE_ERD_OBJETIVO.md` | Diagrama candidato del alcance funcional completo |
| Contrato de API | `docs/architecture/API_CONTRACT.md` | Único catálogo de endpoints Frontend↔Backend |
| Arquitectura Frontend (producto) | `docs/architecture/FRONTEND_ARCHITECTURE.md` | ⚠️ Desactualizada — ver `INV-01` |
| Arquitectura del Handbook | `docs/architecture/ARC-001-handbook-architecture.md.md` | Solo para `handbook/`, no para el producto |
| Design System (Handbook) | `docs/architecture/design/design-system/source/DS-001-design-system.md.md` | Solo para `handbook/` — no aplica al producto (§1.2) |
| Wireframes / Prototipo visual (Handbook) | `docs/architecture/design/wireframes/...`, `docs/architecture/design/visual_prototype/...` | Solo Handbook |
| Especificación técnica Frontend (Handbook) | `docs/architecture/Frontend/FAS-001-Frontend-Architecture-Specification.md` | Solo `handbook/` — no confundir con `FRONTEND_ARCHITECTURE.md` |
| Colección Postman | `docs/api/postman/THERS.postman_collection.json` | Pruebas manuales de la API |
| Manual Operativo | `docs/architecture/organization/Manual_Operativo/` | ❓ NO VERIFICADO (`.docx`/`.pdf` no procesables en este entorno) |
| Plan Estratégico IA | `docs/architecture/organization/Plan_Estrategico/` | ❓ NO VERIFICADO (mismo motivo) |
| Inventario del proyecto | `docs/project-management/THERS_PROJECT_INVENTORY.md` | Catálogo plano de todo lo que existe, con hallazgos |

---

## 16. Important Repository Links

- Rama de integración activa: `develop` (78 commits por delante de `main`).
- CI: `.github/workflows/ci.yml`.
- Entorno local de base de datos: `docker-compose.yml` (raíz) → `docker compose up -d`.
- Colección Postman: `docs/api/postman/THERS.postman_collection.json`.
- Migraciones: `backend/migrations/`.

Este documento no incluye URLs externas (repositorio remoto, tableros, Notion) porque no se confirmó ninguna en el código — cualquier enlace a GitHub/Notion debe agregarlo el equipo con la URL real.

---

## 17. Notion Workspace Architecture

`HB-001` §14 **ya prescribe** una estructura mínima de páginas en Notion (Inicio, Roadmap, Backlog, Sprints, Daily Log, Registro de Decisiones/ADR, Minutas de reuniones, Documentación técnica, Roles y responsabilidades). La estructura pedida para esta tarea (`THERS — Project Hub`) es una **versión enriquecida** de esa misma base — no la reemplaza, la extiende. La tabla siguiente mapea cada página propuesta a su base en `HB-001` (o marca dónde es una extensión nueva que el equipo debería confirmar):

| Página propuesta (`THERS — Project Hub`) | Corresponde a (`HB-001` §14) | Estado |
|---|---|---|
| 📊 Dashboard | Inicio | Coincide — enriquecer con métricas (ver §2 de este documento) |
| 📋 Tasks | Backlog + Sprints (unificadas en una sola base de datos con vistas) | Coincide — ver base de datos `Tasks` (§18) |
| 🛠️ Development Log | *(no existe en `HB-001`)* | **Extensión propuesta** — complementa, no reemplaza, al "Daily Log" de `HB-001` §14 (que es una nota diaria por persona; esto es un registro por commit/PR) |
| 🐛 Bug Tracker | *(no existe como página separada — `HB-001` trata los bugs como Issues con etiqueta `bug` en el mismo tablero)* | **Extensión propuesta** — el equipo puede decidir mantenerlo separado (como aquí) o fusionarlo con `Tasks` filtrando por `Area = Bug` |
| 🎯 Roadmap | Roadmap | Coincide exactamente |
| 🏗️ Architecture | Documentación técnica (subconjunto) | Coincide — enlaza a `docs/architecture/*.md`, no los duplica |
| 🎨 Design System | *(no existe en `HB-001`)* | **Extensión propuesta** — hoy no hay contenido que enlazar del lado del producto (§8); dejar preparada pero marcada como pendiente de completar |
| 🧪 Testing | *(no existe en `HB-001`)* | **Extensión propuesta** — bajo volumen de contenido hoy (§7); dejar preparada |
| 👥 Team | Roles y responsabilidades | Coincide exactamente |
| 📚 Documentation | Documentación técnica | Coincide exactamente |
| 📅 Meetings | Minutas de reuniones | Coincide exactamente |
| 🧠 Technical Decisions | Registro de Decisiones (ADR) | Coincide exactamente — usar la plantilla de ADR ya definida en `HB-001` §12.1 (ver §18) |
| 🔗 Resources | *(no existe en `HB-001`)* | **Extensión propuesta** — enlaces externos (repositorio, CI, Postman) |

**Recomendación:** tratar las 5 páginas marcadas "Extensión propuesta" como una decisión de impacto bajo/medio (`HB-001` §11 — "elegir estructura nueva... basta acuerdo de 2+ integrantes"), no como algo que requiera ADR formal, pero sí confirmarlo con el equipo antes de darlo por definitivo — coherente con la regla de no inventar decisiones de este proyecto.

Páginas que se dejan preparadas pero **marcadas como pendientes de completar** por falta de contenido real hoy: 🎨 Design System (§8: no existe nada del lado del producto todavía) y 🧪 Testing (§7: solo backend tiene tests).

---

## 18. Notion Databases Schema

### Tasks

| Propiedad | Tipo | Notas |
|---|---|---|
| Task | Title | — |
| Status | Select | `Backlog` / `To Do` / `En progreso` / `En revisión` / `Done` — mismas columnas que `HB-001` §16.1, para que el tablero de Notion y el de GitHub Projects (`HB-001` §8.4) se lean igual |
| Priority | Select | `Alta` / `Media` / `Baja` (`HB-001` §16.2) |
| Area | Select | `Backend` / `Frontend` / `Database` / `DevOps` / `Docs` / `Design` — alineado a las áreas de `CLAUDE.md` §9 |
| Assignee | Person | — |
| Sprint | Select o Relation | Semanal, según `HB-001` §13 (Sprint Planning los lunes) |
| Start Date | Date | — |
| Due Date | Date | — |
| Branch | Text | Nombre de la rama de trabajo (`feature/…`, `fix/…`) |
| Pull Request | URL | Enlace al PR — cumple la regla de vinculación de `HB-001` §9.1 |
| Dependencies | Relation (self) | Tareas bloqueantes |
| Description | Text | — |
| Acceptance Criteria | Text | Igual que `HB-001` §16.2 |

**Vistas recomendadas:** Tablero por `Status` (refleja `HB-001` §8.4/§16.1), Tablero por `Area`, Lista por `Sprint`, Calendario por `Due Date`.

### Development Log

| Propiedad | Tipo | Notas |
|---|---|---|
| Date | Date | — |
| Developer | Person | — |
| Area | Select | Igual que en `Tasks` |
| Branch | Text | — |
| Commit | Text | Hash corto o mensaje |
| Pull Request | URL | — |
| Status | Select | `En progreso` / `En revisión` / `Fusionado` / `Bloqueado` |
| Description | Text | — |
| Files Changed | Text o Number | — |
| Result | Text | Qué se logró |
| Next Step | Text | — |

**Vistas recomendadas:** Lista cronológica (por `Date` descendente), agrupada por `Developer`.

### Bug Tracker

| Propiedad | Tipo | Notas |
|---|---|---|
| Bug | Title | — |
| Status | Select | `Abierto` / `En progreso` / `En revisión` / `Resuelto` / `Cerrado` |
| Severity | Select | `Crítica` / `Alta` / `Media` / `Baja` |
| Area | Select | Igual que en `Tasks` |
| Assignee | Person | — |
| Reported Date | Date | — |
| Fixed Date | Date | — |
| Branch | Text | — |
| Pull Request | URL | — |
| Description | Text | — |
| Solution | Text | — |

**Vistas recomendadas:** Tablero por `Status`, filtrado por `Severity = Crítica/Alta` para triage rápido.

### Roadmap

| Propiedad | Tipo | Notas |
|---|---|---|
| Objective | Title | — |
| Phase | Select | Ej. "Auth", "Feed", "Mensajería", "Notificaciones" — alineado a `DATABASE_ARCHITECTURE.md` §4.B (dominios funcionales) |
| Status | Select | `No iniciado` / `En progreso` / `Completado` / `Bloqueado` |
| Priority | Select | `Alta` / `Media` / `Baja` |
| Owner | Person | — |
| Dependencies | Relation (self) | — |
| Target Date | Date | — |

**Vistas recomendadas:** Línea de tiempo (`Target Date`), Tablero por `Phase`.

### Technical Decisions (ADR)

Usar exactamente la plantilla ya definida en `HB-001` §12.1 — no inventar una nueva:

| Propiedad | Tipo | Notas |
|---|---|---|
| ID | Title | `ADR-001`, `ADR-002`, ... |
| Título | Text | — |
| Fecha | Date | `dd/mm/aaaa` |
| Estado | Select | `Propuesta` / `Aceptada` / `Reemplazada` |
| Contexto | Text | — |
| Opciones consideradas | Text | — |
| Decisión | Text | — |
| Consecuencias | Text | — |

**Primeras candidatas a registrar como ADR** (ya implementadas en código, pendientes solo de la ratificación formal descrita en §14 de este documento): persistencia con SQLAlchemy/UUID/CITEXT/Flask-Migrate, patrón Repository con puerto en `domain/`.

---

## CONTEXTO PARA CLAUDE CHAT

**Qué es THERS:** red social en desarrollo, monorepo con `backend/` (Flask + PostgreSQL + JWT), `Frontend/` (React 19 + Vite + Tailwind), `handbook/` (documentación técnica interna, app separada) y `docs/` (documentación oficial). Equipo de 4 personas autogestionado, sin jerarquía vertical, decisiones de alto impacto por consenso del Comité Técnico (`HB-001` §11).

**Arquitectura:** Clean/Hexagonal en el backend (`domain` → `application` → `interfaces`/`infrastructure`); Frontend organizado por `features/` (`auth`, `legal`, `public`, `feed`). Frontend nunca toca PostgreSQL directamente — todo pasa por la API HTTP/JSON del backend.

**Estado actual:** autenticación real y probada (registro + login contra PostgreSQL). El resto del producto (feed, mensajería, notificaciones) tiene UI terminada pero corre sobre datos mock — no hay backend detrás todavía. Solo la entidad `users` está ratificada en base de datos; todo lo demás (posts, comentarios, follows, etc.) es candidato sin ratificar.

**Funcionalidades:** ver `THERS_PROJECT_INVENTORY.md` para el catálogo completo (rutas, componentes, endpoints). Resumen: 22 rutas Frontend, 2 endpoints backend, 1 entidad de base de datos.

**Tareas:** no hay backlog formal fuera del repo — ver §10 de este documento para tareas inferidas por evidencia de código, y §14 para próximos pasos recomendados.

**Problemas activos (no bloqueantes de código, sí de gobernanza/documentación):** `README.md`/`CLAUDE.md` desactualizados respecto al backend real; `FRONTEND_ARCHITECTURE.md` desactualizado respecto al Frontend real; referencia colgante a un `PRODUCT_DESIGN_SYSTEM.md` que no existe; decisiones de persistencia implementadas pero no ratificadas formalmente por el Comité Técnico completo; 78 commits de `develop` sin liberar a `main`; 3 ramas remotas sin triage. Detalle completo: `THERS_PROJECT_INVENTORY.md` §16 (hallazgos `INV-01` a `INV-08`).

**Git workflow:** `feature/fix/chore/docs/hotfix` → PR a `develop` (≥1 aprobación, CI en verde) → periódicamente PR de release `develop → main`. Ninguna rama protegida acepta push directo.

**Documentación:** fuente de verdad jerárquica — `HB-001` (gobernanza) > documentos de arquitectura de producto/Handbook (pendientes de ratificación formal pero más confiables que el código cuando hay conflicto de intención) > estructura real observada en código > `REPOSITORY_STRUCTURE.md` > `README.md`/otros (informativos). Índice completo en §15 de este documento.

**Prioridades sugeridas:** (1) higiene de documentación (README/CLAUDE.md/FRONTEND_ARCHITECTURE.md), (2) ratificar formalmente las decisiones de persistencia ya codificadas, (3) decidir el destino de `PRODUCT_DESIGN_SYSTEM.md`, (4) triage de ramas remotas, (5) preparar release `develop → main`, (6) elegir y ratificar la primera entidad objetivo a implementar (candidato: `posts`, porque el feed ya tiene UI esperando datos reales).

**Próximos pasos:** configurar el workspace de Notion siguiendo §17–18 de este documento (ya alineado con la estructura que `HB-001` §14/§16 exige), y usar `THERS_PROJECT_INVENTORY.md` como fuente para poblar las bases de datos `Tasks`/`Bug Tracker`/`Roadmap` con el estado real inicial.
