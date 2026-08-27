# THERS — Project Inventory

| Campo | Valor |
|---|---|
| Documento | `docs/project-management/THERS_PROJECT_INVENTORY.md` |
| Generado | 2026-08-25, por Claude Code, mediante inspección directa del repositorio (código real + `git log`/`git branch`), no de suposiciones |
| Propósito | Inventario clasificado de todo lo que existe en THERS (features, páginas, componentes, endpoints, modelos, documentos, tests, workflows, configuraciones) para alimentar Notion vía Claude Chat |
| Relación con otros documentos | Complementa a `NOTION_PROJECT_CONTEXT.md` (mismo directorio) — este documento es el catálogo plano; el otro es la narrativa de estado + puente hacia Notion |
| Alcance | Solo análisis y clasificación — **no modifica código, no borra documentación, no cambia configuración** |

## Leyenda de estado

| Símbolo | Significado |
|---|---|
| ✅ | Implementado y verificado en el código real |
| 🟡 | En progreso / parcialmente implementado |
| 🔴 | Pendiente — no existe todavía |
| ⚠️ | Necesita revisión (hallazgo, contradicción, código huérfano, deuda técnica) |
| ❓ | NO VERIFICADO — no se pudo comprobar con las herramientas disponibles en este entorno |

---

## 1. Frontend — Rutas / Páginas

Fuente: `Frontend/src/app/router/router.jsx` (verificado contra el árbol real de `Frontend/src`). **`FRONTEND_ARCHITECTURE.md` (v0.2, 2026-08-16) solo documenta 6 rutas de `auth`/`legal` — desactualizado respecto al código real, que ya tiene 22 rutas.** Ver hallazgo INV-01.

| Ruta | Página | Feature | Estado | Notas |
|---|---|---|---|---|
| `/` | `AuthPage` | `auth` | ✅ | Landing de autenticación |
| `/login` | `Login` | `auth` | ✅ | Conectado a `POST /api/login` real (`useAuth.js`) |
| `/register` | `Register` | `auth` | ✅ | Conectado a `POST /api/register` real |
| `/forgot-password` | `ForgotPassword` | `auth` | 🟡 | UI existe; no hay endpoint de backend para recuperación de contraseña (`DATABASE_ARCHITECTURE.md` §4.B: "PENDIENTE DE DECISIÓN") |
| `/reset-password` | `ResetPassword` | `auth` | 🟡 | UI existe; mismo estado que arriba |
| `/feed` | `Home` | `feed` | 🟡 | UI completa, datos 100% mock (`features/feed/data/mockData.js`) — sin backend de posts |
| `/discover` | `Discover` | `feed` | 🟡 | Mock |
| `/messages` | `Messages` | `feed` | 🟡 | Mock |
| `/notifications` | `Notifications` | `feed` | 🟡 | Mock |
| `/profile` | `Profile` | `feed` | 🟡 | Mock + datos reales de sesión (`useAuth.getStoredUser`) |
| `/settings` | `Settings` | `feed` | 🟡 | Mock |
| `/information` | `Information` | `public` | ✅ | Página informativa estática |
| `/information/how-it-works` | `HowItWorks` | `public` | ✅ | Estática |
| `/information/community` | `Community` | `public` | ✅ | Estática |
| `/information/security` | `Security` | `public` | ✅ | Estática |
| `/information/faq` | `Faq` | `public` | ✅ | Estática |
| `/blog` | `Blog` | `public` | ✅ | Estática ("coming soon") |
| `/help` | `HelpCenter` | `public` | ✅ | Estática |
| `/popular` | `Popular` | `public` | ✅ | Estática |
| `/locations` | `Locations` | `public` | ✅ | Estática |
| `/contacts/import` | `ImportContacts` | `public` | ✅ | Estática |
| `/terms` | `Terms` | `legal` | ✅ | Estática |
| `/privacy` | `Privacy` | `legal` | ✅ | Estática |
| `/cookies` | `Cookies` | `legal` | ✅ | Estática |

**Rutas protegidas: 🔴 ninguna existe.** Todas las rutas de `/feed`, `/discover`, etc. son navegables sin sesión — no hay `RequireAuth`/`PrivateRoute` (confirmado también en `FRONTEND_ARCHITECTURE.md` §7, aunque ese documento no lista estas rutas específicas por estar desactualizado).

---

## 2. Frontend — Features (`src/features/`)

| Feature | Estado | Contenido |
|---|---|---|
| `auth` | ✅ | `components/` (AuthCard, PasswordField, PasswordStrength, TextField), `hooks/` (useAuth, useOAuthNotice), `lib/validators.js`, `pages/` (AuthPage, Login, Register, ForgotPassword, ResetPassword) |
| `legal` | ✅ | `pages/` (Terms, Privacy, Cookies) — contenido estático |
| `feed` | 🟡 | `components/` (CapsuleCard, CreateCapsuleFlow, MomentViewer, MomentsRow, MoodBadge, PulseBar), `data/mockData.js`, `pages/` (Home, Discover, Messages, Notifications, Profile, Settings) — **100% prototipo visual, sin persistencia real** |
| `public` | ✅ | `components/` (ComingSoon, EditorialCard, InformationCta, InformationHero, MediaPlaceholder, PhoneMockup, RevealOnScroll), `data/informationContent.js`, `pages/` (9 páginas informativas) |

**Ninguna de estas 4 features (excepto `auth`/`legal`) está documentada en `FRONTEND_ARCHITECTURE.md`** (v0.2 solo conoce `auth`/`legal`). Ver hallazgo INV-01.

---

## 3. Frontend — Componentes compartidos (`src/shared/`)

| Componente | Estado | Notas |
|---|---|---|
| `AmbientGlow` | ✅ | Efecto visual |
| `Avatar` | ✅ | — |
| `Logo` / `BrandMark` | ✅ | — |
| `Spinner` | ✅ | Estado de carga — **no documentado en `FRONTEND_ARCHITECTURE.md` §12**, que afirma "no hay spinners/skeletons implementados" (desactualizado) |
| `Footer/` (Footer, FooterExpandableItem, FooterLink, FooterSection, InfoMediaTeaser + data) | ✅ | Sistema de footer completo para el layout público |
| `Toast/` (Toast, ToastContext) | ✅ | Sistema de notificaciones — **no documentado en `FRONTEND_ARCHITECTURE.md` §12**, que afirma que el manejo de errores es solo `alert()` (desactualizado; el código real usa Toast, ver `Login.jsx`) |
| `useTheme` (hook) | ✅ | Dark mode (`darkMode: "class"` en `tailwind.config.js`) — no documentado en ningún lugar de `/docs` |
| `lib/api.js` | ✅ | Cliente axios único + `getErrorMessage()` (traducción de errores HTTP→mensaje de usuario) |

---

## 4. Frontend — Layout (`src/app/layout/`)

| Componente | Estado | Notas |
|---|---|---|
| `AppShell` | ✅ | Shell con navegación (rail/FAB) para las rutas de `feed` |
| `MobileNav` | ✅ | Navegación móvil |
| `NavRail` | ✅ | Navegación desktop |
| `PublicLayout` | ✅ | Layout con Footer para páginas públicas/legales |

**Ninguno de los 4 existía cuando se escribió `FRONTEND_ARCHITECTURE.md`** (v0.2 solo documenta `app/router/`).

---

## 5. Frontend — Design tokens (`Frontend/tailwind.config.js`)

| Elemento | Estado | Notas |
|---|---|---|
| Paleta de color (`canvas`, `surface`, `ink`, `muted`, `line`, `pulse`, `ember`, `success`, `warning`) | ✅ | Tokens centralizados en Tailwind, con comentarios que citan explícitamente `PRODUCT_DESIGN_SYSTEM.md §2.3` |
| Sombras (`soft`, `lift`, `glow`) y animaciones (`marquee`, `capsule-in`, `pop-like`, `mood-glow`, `float-in`) | ✅ | — |
| `PRODUCT_DESIGN_SYSTEM.md` (documento citado en el código) | ⚠️ **NO EXISTE** | `grep` sobre todo el repositorio confirma que el archivo referenciado en `tailwind.config.js` nunca fue creado. Ver hallazgo INV-02. |

---

## 6. Backend — Endpoints

Fuente: `backend/app/interfaces/routes/auth_routes.py` + `docs/architecture/API_CONTRACT.md` v0.2 (única fuente ratificable del contrato).

| Método | Ruta | Estado | Notas |
|---|---|---|---|
| `POST` | `/api/register` | ✅ | Implementado v0.6 — persistencia real, `201`/`400`/`409` |
| `POST` | `/api/login` | ✅ | Implementado v0.6 — persistencia real, JWT con `identity=user.id` (UUID), `200`/`400`/`401` |
| — | Cualquier endpoint protegido (`@jwt_required()`) | 🔴 | Ninguno existe — confirmado en `BACKEND_ARCHITECTURE.md` §9 |
| — | Posts, comentarios, likes, follows, notificaciones, admin | 🔴 | No implementados — parte del alcance funcional objetivo, sin contrato ni código (`API_CONTRACT.md` §8, `DATABASE_ARCHITECTURE.md` §4.B) |

**`backend/app.py`** ⚠️ — segunda aplicación Flask mínima e independiente en la raíz de `backend/`, no conectada a la arquitectura por capas de `app/`, sin propósito documentado. Hallazgo reportado en `BACKEND_ARCHITECTURE.md` §2/§20 ítem 15. Ver hallazgo INV-03.

---

## 7. Backend — Capas / módulos

| Capa | Módulo | Estado |
|---|---|---|
| `interfaces/routes/` | `auth_routes.py` | ✅ Composition root — único punto que conoce `application/` e `infrastructure/` |
| `application/auth/` | `login_use_case.py`, `register_use_case.py` | ✅ |
| `domain/auth/` | `auth_service.py` (hash/verify), `exceptions.py` (`EmailAlreadyExistsError`, `InvalidCredentialsError`), `repositories.py` (puerto `UserRepository`, `abc.ABC`) | ✅ |
| `infrastructure/persistence/` | `models.py` (modelo `User`), `repositories/user_repository.py` (`SQLAlchemyUserRepository`) | ✅ |
| `config.py` | Lee `JWT_SECRET_KEY` y `DATABASE_URL` de entorno, con fallback inseguro documentado solo para JWT | ✅ |
| `extensions.py` | `jwt`, `db`, `migrate` inicializados | ✅ |

⚠️ **Hallazgo de nomenclatura** (`BACKEND_ARCHITECTURE.md` §3): los archivos marcador de paquete en `application/`, `application/auth/`, `domain/`, `domain/auth/` e `interfaces/routes/` se llaman `_init_.py` (un guion bajo a cada lado), no `__init__.py`. No rompe las importaciones (namespace packages implícitos) pero no cumplen su función real. Ver hallazgo INV-04.

---

## 8. Base de datos — Entidades

Fuente: `DATABASE_ARCHITECTURE.md` v0.4, `DATABASE_ERD.md` v0.2, `DATABASE_ERD_OBJETIVO.md` v0.2.

| Entidad | Estado | Capa |
|---|---|---|
| `users` | ✅ Implementada y en uso real (`register`/`login`) | 4.A — ratificada |
| `oauth_accounts`, `sessions`, `devices` | 🔴 Candidata | 4.B — objetivo (Autenticación/Seguridad) |
| `username`, `avatar_url`, `bio` (columnas de `users`) | 🔴 Candidata | 4.B — objetivo (Perfil); contradicción registrada: el alcance funcional las confirma, pero `users` no las tiene todavía |
| `user_settings` | 🔴 Pendiente de decisión | 4.B — Configuración |
| `posts`, `media` | 🔴 Candidata | 4.B — Contenido |
| `reactions`, `comments`, `saves`, `mentions`, `hashtags`/`post_hashtags` | 🔴 Candidata/pendiente | 4.B — Interacciones |
| `follows`, `blocks`, `restrictions` | 🔴 Candidata/pendiente | 4.B — Relaciones sociales |
| `conversations`, `conversation_participants`, `messages`, `message_media` | 🔴 Candidata/pendiente | 4.B — Mensajería |
| `notifications` | 🔴 Candidata | 4.B — Notificaciones |
| `password_changes`, `security_events` | 🔴 Pendiente de decisión | 4.B — Seguridad |

**Ninguna entidad de la capa 4.B se implementa sin ratificación por ADR** (`DATABASE_ARCHITECTURE.md` §4.C, `HB-001` §11–12).

⚠️ `DATABASE_ARCHITECTURE.md` §11/§14 sigue listando `JWT_SECRET_KEY` como "hardcodeado en `config.py`" — esto ya fue corregido (confirmado en `BACKEND_ARCHITECTURE.md` §12/§16 y en el código real, que lee `os.environ`). Inconsistencia entre documentos hermanos de la misma revisión (ambos v0.x del 2026-08-16 22:28). Ver hallazgo INV-05.

---

## 9. Testing

| Área | Estado | Detalle |
|---|---|---|
| Backend — integración | ✅ | `backend/tests/test_auth.py` (13 tests) + `conftest.py`, contra PostgreSQL 16 real (Docker, BD `thers_test`), no mocks. Framework: `pytest==8.3.4` (`requirements-dev.txt`) — elegido pragmáticamente, **sin ratificación formal** (`BACKEND_ARCHITECTURE.md` §15/§20 ítem 12) |
| Backend — unitarios puros de `domain/` | 🔴 | No existen (serían triviales — envoltorios de `werkzeug.security`) |
| Frontend | 🔴 | Sin framework instalado (ni Vitest, ni Jest, ni Playwright/Cypress); sin carpeta `__tests__/` ni archivos `*.test.jsx` (`FRONTEND_ARCHITECTURE.md` §18) |
| Postman | ✅ | `docs/api/postman/THERS.postman_collection.json` — colección "01_AUTH" con `register` y `login`; `login` incluye script de test (status 200, presencia de `token`/`user`/`id`/`email`/`name`) y setea variables de entorno `jwt_token`/`user_id` |
| CI | ✅ | `.github/workflows/ci.yml` — job `frontend` (`npm ci` + `npm run build`) y job `backend` (Postgres 16 de servicio, `flask db upgrade`, `pytest`), en push/PR a `main`/`develop`/`feature/**` |

---

## 10. DevOps / Configuración

| Elemento | Estado | Notas |
|---|---|---|
| `docker-compose.yml` (raíz) | ✅ | Un servicio, `postgres:16-alpine`, puerto configurable (`POSTGRES_PORT`), healthcheck, volumen persistente, `./docker/postgres-init` para scripts de init |
| `docker/postgres-init/01-create-test-db.sql` | ✅ | Crea la BD `thers_test` separada de `thers_dev` |
| `backend/migrations/` (Flask-Migrate/Alembic) | ✅ | Una migración (`a1b2c3d4e5f6_create_users_table`), escrita a mano — crea extensión `citext`, tabla `users`, índice único, trigger `set_updated_at` |
| Dockerfile de aplicación (backend/Frontend) | 🔴 | No existe — sin containerización de las apps, solo de PostgreSQL |
| Documentación de DevOps | 🔴 | **Sin documento oficial** — Docker, CI/CD, deploy, SSL, dominios, monitoreo son territorio no especificado (`HB-001` §0, `CLAUDE.md` §5) |
| Variables de entorno documentadas | 🟡 | `JWT_SECRET_KEY`, `DATABASE_URL` (backend), `VITE_API_URL` (Frontend) — sin lista oficial completa más allá de estas tres |

---

## 11. Documentación oficial (`docs/`)

| Documento | Versión | Estado de ratificación | Última actualización observada |
|---|---|---|---|
| `HB-001-manual-organizacion.md.md` | — | Máxima autoridad de gobernanza | ❓ no fechado explícitamente en el cuerpo leído |
| `REPOSITORY_STRUCTURE.md` | 1.0 | Borrador, parcialmente verificado | 2026-08-16 22:28 |
| `BACKEND_ARCHITECTURE.md` | 0.6 | Pendiente de ratificación formal | 2026-08-16 22:28 — **al día con el código** |
| `DATABASE_ARCHITECTURE.md` | 0.4 | Pendiente de ratificación formal | 2026-08-16 22:28 — al día con el código, con la excepción del hallazgo INV-05 |
| `DATABASE_ERD.md` | 0.2 | Borrador | 2026-08-16 22:28 |
| `DATABASE_ERD_OBJETIVO.md` | 0.2 | Propuesta candidata, no ratificada | 2026-08-14 20:49 |
| `API_CONTRACT.md` | 0.2 | Pendiente de ratificación formal | 2026-08-16 22:28 — al día con el código |
| `FRONTEND_ARCHITECTURE.md` | 0.2 | Pendiente de ratificación formal | 2026-08-16 12:21 — ⚠️ **desactualizado**, ver INV-01 |
| `ARC-001-handbook-architecture.md.md` | — | Propuesta v0.1, pendiente de aprobación del Comité Técnico | 2026-08-16 12:21 |
| `DS-001-design-system.md.md` (Handbook) | — | "Oficial — vinculante v1.0" (pese a depender de `ARC-001`, no ratificado) | ❓ |
| `WF-001` (wireframes) | — | ❓ | ❓ |
| `PV-001` (prototipo visual) | — | ❓ | ❓ |
| `FAS-001-Frontend-Architecture-Specification.md` | — | Exclusivo del Handbook, no del producto | ❓ |
| `THERS_Manual_Operativo_v1.0.docx`/`.pdf` | — | ❓ **NO VERIFICADO** — `.docx` no procesable, `.pdf` requiere `poppler-utils` (no instalado en este entorno) | — |
| `Plan_Estrategico_IA_THERS.docx`/`.pdf` | — | ❓ **NO VERIFICADO** — mismo motivo | — |

**Documento fuera de `develop`/`main`, existe solo en la rama remota sin fusionar `origin/feature/backend-foundation`:** `docs/architecture/AUDITORIA_TECNICA.md` (187 líneas, commit `03f9885 docs: add backend technical audit (read-only)`). No forma parte de la documentación oficial vigente porque nunca se fusionó. Ver hallazgo INV-06.

---

## 12. Postman / API tooling

| Elemento | Estado |
|---|---|
| `docs/api/postman/THERS.postman_collection.json` | ✅ Colección "01_AUTH" (register, login) — declara explícitamente que "debe mantenerse alineada con `API_CONTRACT.md`" |
| Environment de Postman (variables `base_url`, `test_email`, `test_password`) | 🟡 Referenciadas en la colección (`{{base_url}}`, `{{test_email}}`, `{{test_password}}`) pero el archivo de environment en sí no se encontró en `docs/api/postman/` — probablemente vive fuera del repo (local de cada integrante) |

---

## 13. Handbook (`handbook/`) — resumen

Fuera del foco principal de este inventario (el Handbook es una aplicación de documentación interna, no el producto), pero se registra su estado por completitud:

| Elemento | Estado |
|---|---|
| Código (Módulos 1–10) | ✅ Release Candidate (según `CLAUDE.md` §3.2 — no re-verificado línea por línea en esta tarea) |
| Stack | React 19.2.8 + Vite 8.2.0 + Tailwind CSS **v4** (distinto de la v3 del producto) + MDX (`@mdx-js/rollup`) |
| Componentes UI (`src/components/ui/`) | ✅ Alert, Badge, Breadcrumbs, Button, Callout, Card, CodeBlock, Footer, PrevNext, SearchModal, ThemeToggle, Timeline |
| Cascada de gobernanza documental | `ARC-001` → `DS-001` → `WF-001`/`PV-001` → `FAS-001` — con el matiz ya señalado en `CLAUDE.md` §3.2 (ARC-001 "propuesta pendiente" pero DS-001, que depende de él, "oficial vinculante") |

---

## 14. Git — Ramas

| Rama | Estado |
|---|---|
| `main` | Rama protegida, producción — 78 commits detrás de `develop` en este momento (release pendiente) |
| `develop` | Rama de integración activa, HEAD actual |
| `chore/devops-git-ci`, `docs/api-auth-collections`, `docs/architecture`, `docs/database-architecture`, `docs/general`, `feature/backend-auth`, `feature/backend-auth-persistence`, `feature/backend-database-foundation`, `feature/frontend-api`, `feature/frontend-auth-integration`, `feature/frontend-auth-ui`, `feature/frontend-public-pages`, `feature/frontend-setup`, `feature/integrate-feed`, `feature/update-readme` (local, distinta de la remota), `fix/backend-auth-security`, `fix/backend-auth-validation`, `inicio-proyecto` | ✅ Ya fusionadas a `develop` — historial, no trabajo pendiente |
| `feature/frontend-shared-components` (local) | ⚠️ 1 commit no fusionado (`fff61af`), probablemente superado por un commit posterior equivalente ya en `develop` |
| `origin/feature/update-readme` | ⚠️ 4 commits no fusionados ("Actualiza README") — no se sabe si siguen vigentes o quedaron obsoletos |
| `origin/chore/repo-hygiene` | ⚠️ 2 commits no fusionados, pero la rama está muy desactualizada respecto a `develop` (le faltan ~127 archivos que sí existen en `develop`) — parece abandonada, no lista para fusionar tal cual |
| `origin/feature/backend-foundation` | ⚠️ 1 commit no fusionado (`docs/architecture/AUDITORIA_TECNICA.md`, ver INV-06) |

---

## 15. Equipo (identidades Git observadas)

❓ **NO VERIFICADO como mapeo oficial** — `HB-001` §2 define roles genéricos sin nombres propios; el mapeo persona↔rol de abajo proviene de `REPOSITORY_STRUCTURE.md` §4/§11 (documento "borrador, parcialmente verificado") cruzado con los autores reales de `git log`.

| Identidad Git | Rol sugerido (`REPOSITORY_STRUCTURE.md` §4/§11) |
|---|---|
| Fernando Escalante (`Fernandito41`, autor de casi todos los merges de PR) | Coordinador de documentación de organización/arquitectura; también autor de la mayoría del código en el historial reciente |
| Diego (`diegomdne`, Diego Medina) | Tech Lead Backend |
| Oscar "Piche" Pineda Piche | Tech Lead Frontend |
| `Nombre del compañero <email@ejemplo.com>` | ⚠️ Commit con identidad Git placeholder sin configurar — el 4to integrante del equipo (`HB-001` confirma "4 integrantes") no tiene su `git config user.name/email` real establecido en al menos un commit del historial |

---

## 16. Hallazgos consolidados (⚠️ necesitan revisión del equipo)

| ID | Hallazgo | Severidad | Dónde se reporta |
|---|---|---|---|
| INV-01 | `FRONTEND_ARCHITECTURE.md` (v0.2, 2026-08-16 12:21) no documenta las features `feed`/`public`, el layout (`AppShell`/`PublicLayout`/`NavRail`/`MobileNav`), los tokens de diseño de `tailwind.config.js`, el sistema de `Toast`, `Spinner`, `useTheme` (dark mode), ni la integración real de `Register`/`Login` con el backend — todo esto se agregó en commits posteriores a esa versión del documento. El documento describe una app de 6 rutas/2 features; el código real tiene 22 rutas/4 features. | Alta | Este inventario (§1–5) |
| INV-02 | `Frontend/tailwind.config.js` cita `PRODUCT_DESIGN_SYSTEM.md §2.3` en dos comentarios, pero ese archivo no existe en ningún lugar del repositorio (confirmado por búsqueda global). Es una referencia colgante — o el documento nunca se creó, o se perdió antes de comprometerse. | Media | Este inventario (§5) |
| INV-03 | `backend/app.py` es una segunda app Flask mínima, sin conexión a la arquitectura por capas, sin propósito documentado, coexistiendo con `backend/run.py` (el entry point real). Ya reportado en `BACKEND_ARCHITECTURE.md` §2/§20 ítem 15, sin resolver. | Media | `BACKEND_ARCHITECTURE.md` §2, §20.15 |
| INV-04 | Archivos marcador de paquete Python nombrados `_init_.py` (un guion bajo) en vez de `__init__.py` en `application/`, `domain/`, `interfaces/routes/`. No rompe la app (namespace packages implícitos) pero no cumplen su función. Ya reportado en `BACKEND_ARCHITECTURE.md` §3/§20 ítem 16, sin resolver. | Baja | `BACKEND_ARCHITECTURE.md` §3, §20.16 |
| INV-05 | `DATABASE_ARCHITECTURE.md` §11 y §14 siguen listando `JWT_SECRET_KEY` como "hardcodeado en `config.py`" pese a que `BACKEND_ARCHITECTURE.md` (mismo día, misma tarea) ya documenta esa corrección como resuelta desde su v0.2, y el código real (`backend/app/config.py`) confirma que se lee de `os.environ`. Desincronización entre dos documentos hermanos actualizados en la misma sesión de trabajo. | Baja | `DATABASE_ARCHITECTURE.md` §11, §14 vs. `BACKEND_ARCHITECTURE.md` §12, §16 |
| INV-06 | `docs/architecture/AUDITORIA_TECNICA.md` existe únicamente en la rama remota no fusionada `origin/feature/backend-foundation` (commit `03f9885`) — no forma parte de la documentación oficial vigente en `develop`/`main`. Puede contener información relevante que el equipo decidió no fusionar, o simplemente quedó huérfana. | Media | `git log develop..origin/feature/backend-foundation` |
| INV-07 | `README.md` raíz y `CLAUDE.md` (ambos con última edición 2026-08-16 12:22) describen el backend como "sin persistencia real, sin endpoint de registro" — desactualizado desde la misma tarde del 16 de agosto (`docs/architecture/*.md` se actualizó a las 22:28 de ese mismo día para reflejar la persistencia real ya implementada). El repositorio real, a fecha de este inventario (2026-08-25), tiene 9 días adicionales de commits sobre eso. | Alta | Comparación directa `README.md`/`CLAUDE.md` vs. `docs/architecture/*.md` vs. código |
| INV-08 | Rama `origin/chore/repo-hygiene` tiene 2 commits no fusionados a `develop`, pero estructuralmente representa un estado muy anterior del repositorio (le faltan ~127 archivos/features que ya existen en `develop`) — no es un simple "adelanto" pendiente de mergear, sino una rama probablemente abandonada o que necesita rebase completo antes de considerarse. | Baja | `git diff develop origin/chore/repo-hygiene --stat` |

Ninguno de estos hallazgos se resolvió en esta tarea (fuera de alcance — solo análisis y documentación, `CLAUDE.md` §9 de esta tarea).
