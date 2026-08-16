# CLAUDE.md — THERS_REDSOCIAL_2026

Instrucciones globales para Claude Code en este monorepo. Este archivo es un **índice + reglas operativas**, no una copia de la documentación oficial. Ante cualquier duda, el documento fuente citado tiene prioridad sobre lo escrito aquí.

> Generado a partir de `/docs` y de la estructura real del repositorio (2026-08). No incluye decisiones que no estuvieran ya documentadas — la sección 15 lista explícitamente lo que falta.

---

## 1. Identidad y objetivo del proyecto

THERS es un proyecto de un equipo autogestionado de 4 integrantes (`HB-001` §1) que construye **una red social** (nombre del repositorio raíz, confirmado como hipótesis en `REPOSITORY_STRUCTURE.md` §1). La descripción funcional completa del producto — audiencia, features centrales — **no está formalmente documentada**; el único texto descriptivo detallado vive en el `README.md` raíz, que **no es una fuente oficial** (no vive en `/docs`) y contiene datos que contradicen la documentación oficial (ver §15).

Stack confirmado por `HB-001` (portada): **React · Vite · Tailwind CSS · Flask · PostgreSQL · JWT**.

El repositorio aloja tres aplicaciones independientes bajo un mismo monorepo (`backend/`, `Frontend/`, `handbook/`), más `docs/` como documentación oficial versionada. Cada una de las tres aplicaciones tiene hoy un documento de arquitectura propio o en construcción — ver §3.

---

## 2. Estructura del monorepo

Fuente: `docs/architecture/REPOSITORY_STRUCTURE.md`.

| Carpeta | Contenido | Estado de confirmación |
|---|---|---|
| `backend/` | API Flask. Estructura real observada: `app/domain/`, `app/application/`, `app/interfaces/routes/`, `app/config.py`, `app/extensions.py`, `run.py` (capas tipo Clean/Hexagonal) | Estructura consolidada en `BACKEND_ARCHITECTURE.md` (propuesta v0.2, pendiente de ratificación — ver §3) |
| `Frontend/` | Producto — la red social. `src/app/router/`, `src/features/{auth,legal}/{hooks,pages,index.js}`, `src/shared/{components,lib}` | Árbol verificado directamente contra el repositorio real. `src/app/providers/` y `src/app/store/` **no existen** todavía — son estructura futura propuesta, no implementada (`FRONTEND_ARCHITECTURE.md` §4/§8/§24) |
| `handbook/` | THERS Engineering Handbook. React + Vite + MDX, SSG, sin dependencia del backend | Implementación completa (Módulos 1–10, estado Release Candidate) — ver matiz de gobernanza en §3 |
| `docs/` | Documentación oficial versionada en Markdown (+ 2 documentos en `.docx`/`.pdf` sin analizar, ver §15) | Confirmada |

Reglas de organización (`REPOSITORY_STRUCTURE.md` §2, §8–9):
- `backend/`, `Frontend/` y `handbook/` son aplicaciones independientes: sin código compartido, sin `node_modules` compartidos, cada una con su propio `package.json`.
- `docs/` y `handbook/` nunca contienen código de producto; `backend/` y `Frontend/` nunca contienen documentos oficiales fuente.
- Nombres de carpeta en minúsculas salvo `Frontend/` (excepción ya documentada, no se corrige).
- Código, nombres de carpeta/archivo en inglés; documentación oficial en español.

---

## 3. Documentos de arquitectura

### 3.1 Producto (`backend/`, `Frontend/`, base de datos, API)

Cuatro documentos, todos en `docs/architecture/`, todos con el mismo formato y el mismo estado de gobernanza: separan explícitamente lo implementado de lo objetivo/propuesto de lo pendiente de aprobación, y ninguno se autoproclama cerrado.

| Documento | Versión | Estado | Cubre |
|---|---|---|---|
| `BACKEND_ARCHITECTURE.md` | 0.3 | Pendiente de ratificación formal (`HB-001` §11–12) | Capas del backend, flujo de una petición, autenticación, configuración, seguridad |
| `DATABASE_ARCHITECTURE.md` + `DATABASE_ERD.md` + `DATABASE_ERD_OBJETIVO.md` | 0.2 / 0.1 / 0.2 | Pendiente de ratificación formal | Modelo de datos en tres capas: implementado (solo `users`), objetivo del producto (candidatas sin modelado ratificado), pendiente de decisión |
| `FRONTEND_ARCHITECTURE.md` | 0.2 | Pendiente de ratificación formal | Stack, estructura, estado, routing, frontera con el backend, seguridad del Frontend del producto |
| `API_CONTRACT.md` | 0.1 | Pendiente de ratificación formal | Catálogo de endpoints, formato de request/response/error, autenticación — única fuente del contrato HTTP entre `Frontend/` y `backend/` |

Ninguno de los cuatro es todavía un documento oficial ratificado en el sentido de `HB-001` §11–12: son la mejor fuente disponible para su dominio, con las decisiones sin respaldo marcadas explícitamente como `PENDIENTE DE APROBACIÓN` dentro de cada uno. No copian contenido entre sí — cada decisión vive en un único documento y los demás la referencian.

### 3.2 Handbook (`handbook/`)

Cascada de autoridad interna: `ARC-001` (arquitectura de información/UX) → `DS-001` (Design System) → `WF-001` (wireframes) → `PV-001` (prototipo visual, subordinado y consolidador de los tres anteriores) → `FAS-001` (traducción técnica a React/Vite, subordinada a todo lo anterior).

Matiz de estado a tener en cuenta: `ARC-001` se autodeclara "Propuesta v0.1 — pendiente de aprobación del Comité Técnico", mientras que `DS-001` se autodeclara "Oficial — vinculante v1.0" pese a depender formalmente de `ARC-001` en esa misma cascada. El código del Handbook está implementado (Módulos 1–10, estado Release Candidate) independientemente de ese matiz de ratificación documental. No resolver esta discrepancia por criterio propio — señalarla si es relevante para la tarea en curso.

`FAS-001` vive en `docs/architecture/Frontend/` y es exclusivo del Handbook (confirmado en su propio §1, §3, §17) — no confundir con `FRONTEND_ARCHITECTURE.md` (§3.1), que es del producto. `FRONTEND_ARCHITECTURE.md` §2 documenta esta distinción con detalle.

Catálogo de componentes cerrado (`PV-001` Parte 7 §21): antes de crear un componente nuevo, verificar si el catálogo ya lo cubre. 25 extensiones al catálogo siguen pendientes de ratificación formal (`PV-001`, Anexo Fase 7) — no implementarlas dándolas por aprobadas.

### 3.3 Organización y repositorio

- `HB-001` — Manual de Organización. Máxima autoridad de gobernanza: roles, git flow, proceso de ADR, reglas de uso de IA, reglas innegociables.
- `REPOSITORY_STRUCTURE.md` — mapa del repositorio. Se autodeclara "borrador, parcialmente verificado".
- `DevOps` — sin documento propio. Ver §5.

---

## 4. Jerarquía de fuentes de verdad

1. **`HB-001`** — gobernanza, máxima autoridad para organización y proceso.
2. **Documentos de arquitectura de producto y del Handbook** (§3.1, §3.2) — mejor fuente disponible para su dominio, aunque casi todos siguen pendientes de ratificación formal. Entre ellos, dentro de cada dominio, ninguno duplica a otro: `BACKEND_ARCHITECTURE.md` para backend, `DATABASE_ARCHITECTURE.md` para datos, `FRONTEND_ARCHITECTURE.md` para el Frontend del producto, `API_CONTRACT.md` para el contrato HTTP entre ambos, `ARC-001`→`DS-001`→`WF-001`→`PV-001`→`FAS-001` para el Handbook.
3. **Estructura real observada en el código** — cuando ningún documento cubre el caso, la estructura ya implementada es la referencia de facto, pero se trata como "observada", no como "decidida".
4. **`REPOSITORY_STRUCTURE.md`** — mapa del repositorio; dependiente de los niveles anteriores.
5. **`README.md` raíz y otros archivos fuera de `/docs`** — informativos, **no autoritativos**. Ante conflicto con `/docs`, gana `/docs` siempre (ver contradicciones documentadas en §15).

Ningún cambio de arquitectura o diseño se decide de forma aislada dentro de una implementación puntual — sigue el proceso de gobernanza de `DS-001` §16 (Handbook) o el de decisiones de alto impacto de `HB-001` §11–12 (resto del proyecto, vía ADR).

---

## 5. Reglas de arquitectura por área

### Backend
- Fuente: `BACKEND_ARCHITECTURE.md` (§3.1) — propuesta v0.3, pendiente de ratificación.
- Capas observadas y consolidadas: `domain/`, `application/`, `interfaces/routes/`, `config.py`, `extensions.py`, `run.py` — mantenerlas por consistencia, sin tratarlas como contrato cerrado hasta su ratificación.
- Stack confirmado: Flask + JWT (`flask_jwt_extended`) + PostgreSQL (motor elegido, sin driver ni ORM integrado todavía).
- `backend/requirements.txt` ya existe, fijando las versiones en uso real (Flask, flask-cors, Flask-JWT-Extended) — no incluye SQLAlchemy a propósito, para no adoptar una decisión de persistencia sin ratificar. `pyproject.toml` sigue sin existir; el equipo no ha ratificado formalmente estas versiones como estándar oficial.
- `JWT_SECRET_KEY` se lee de variable de entorno (`backend/.env.example` documenta la variable; `backend/.gitignore` protege un `.env` real) — la gestión de secretos en un entorno desplegado sigue pendiente.

### Frontend (producto — `Frontend/`)
- Fuente: `FRONTEND_ARCHITECTURE.md` (§3.1) — propuesta v0.2, pendiente de ratificación.
- Organización por `features/` (`auth`, `legal`), cada una con `hooks/`, `pages/`, `index.js` como punto de entrada; `shared/` para código transversal; `app/router/` para el arranque de la aplicación.
- `VITE_API_URL` se lee de variable de entorno (`Frontend/.env.example` documenta la variable; `Frontend/.gitignore` protege un `.env` real) — con fallback advertido al valor de desarrollo local si no está definida.
- **No existe un Design System ratificado para este Frontend.** `DS-001` §1.2 declara textualmente que no aplica al producto — no extrapolar sus tokens sin que el equipo lo decida como cambio de gobernanza.
- Stack confirmado (`Frontend/package.json`): React 19, React Router 7, Tailwind v3 (no v4 — distinto del Handbook), Axios, react-icons.
- Alias de imports (`@`, `@features`, `@shared`, `@assets`) definidos en `vite.config.js` y ya en uso — documentados en `FRONTEND_ARCHITECTURE.md` §20.

### Base de Datos
- Fuente: `DATABASE_ARCHITECTURE.md` + `DATABASE_ERD.md`/`DATABASE_ERD_OBJETIVO.md` (§3.1) — propuesta v0.2/v0.1/v0.2, pendiente de ratificación.
- Única entidad con modelo implementado y ratificado: `users`. El resto del alcance funcional del producto está registrado como candidatas objetivo o pendientes de decisión — ninguna se implementa sin ratificación por ADR.
- No inventar esquema, convención ni entidad nueva sin confirmarlo con el equipo.

### API (Frontend ↔ Backend)
- Fuente: `API_CONTRACT.md` (§3.1) — propuesta v0.1, pendiente de ratificación.
- Único endpoint implementado: `POST /api/login`. `POST /api/register` es esperado por el Frontend pero no existe en el backend — no asumir que existe.
- Todo endpoint nuevo se documenta en `API_CONTRACT.md` el mismo día del PR (`HB-001` §15.1).

### DevOps
- **Sin documentación oficial.** Docker, CI/CD, deploy, SSL, dominios y monitoreo están fuera del alcance declarado de `HB-001` §0 y no aparecen en ningún otro documento de `/docs`. Cualquier trabajo en esta área debe tratarse como territorio no especificado (§15) y consultarse con el equipo antes de tomar decisiones estructurales.

### Handbook (`handbook/`)
- Código implementado (Módulos 1–10, estado Release Candidate). Fuente de verdad en cascada: `ARC-001` → `DS-001` → `WF-001`/`PV-001` → `FAS-001` (§3.2, con el matiz de ratificación documental ya señalado ahí).
- Catálogo de componentes cerrado (`PV-001` Parte 7 §21) — verificar antes de crear uno nuevo.

---

## 6. Reglas de desarrollo

- No inventar arquitectura donde no la hay: si `/docs` no cubre el caso, decirlo explícitamente (§14–15), no improvisar una decisión de alto impacto.
- No duplicar componentes ni lógica — revisar primero si ya existe (regla explícita en `PV-001` §7/§21 para el Handbook; principio general de "Reutilización" y "Bajo acoplamiento" en `FAS-001` §2 para cualquier Frontend del proyecto).
- Reutilizar código existente antes de escribir uno nuevo equivalente.
- Respetar el Design System **donde exista** (Handbook: `DS-001`, vinculante — "ningún valor de color/tipografía/espaciado fuera de sus tokens"). Para `Frontend/` del producto, no hay tokens oficiales que respetar todavía; no inventarlos, señalarlo.
- Respetar la documentación oficial por encima de la preferencia individual del implementador (`FAS-001` §1: "el código sigue a la documentación, no al revés").
- No modificar decisiones arquitectónicas ya tomadas sin justificación registrada — decisiones de impacto medio/alto se documentan como ADR (`HB-001` §11–12) antes de implementarse, no después.
- No duplicar contenido entre los documentos de §3: cada decisión vive en un único documento; los demás la referencian, no la repiten.

---

## 7. Git Flow

Fuente: `HB-001` §7–9. Reglas vinculantes:

- **`main`** — producción/entregable estable. Sin push directo.
- **`develop`** — rama de integración. Sin push directo.
- Ambas exigen Pull Request + al menos 1 aprobación.
- **Ramas:** `feature/<nombre>`, `fix/<nombre>`, `chore/<nombre>`, `docs/<nombre>`, `hotfix/<nombre>`.
- **Commits (Conventional Commits):** `feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`, `chore:`.
- **Pull Requests:** un PR resuelve una sola cosa; título con el mismo prefijo que los commits; vinculado a su Issue (`Closes #N`); el autor no se autoaprueba; sin `.env`/credenciales; sin código de prueba olvidado (`console.log`, `print`).
- **Release:** `develop` → `main` periódicamente vía PR de release.

---

## 8. Reglas específicas para Claude Code

1. Revisar la documentación relevante (§3–4) antes de implementar cualquier cambio no trivial.
2. Identificar el alcance exacto de lo solicitado antes de tocar código — no expandirlo por iniciativa propia.
3. No modificar áreas fuera del alcance pedido, salvo pequeñas inconsistencias que el usuario autorice explícitamente a corregir.
4. Si el cambio toca un endpoint nuevo o existente, consultar y actualizar `API_CONTRACT.md` el mismo día (`HB-001` §15.1) — no dejarlo para después.
5. Ejecutar las verificaciones correspondientes tras cualquier cambio (build/lint del paquete afectado como mínimo; ver §11).
6. Reportar siempre: archivos creados, archivos modificados, componentes nuevos, verificaciones ejecutadas y su resultado.
7. No hacer commit ni push salvo que el usuario lo pida explícitamente en ese turno — una autorización previa no cubre turnos futuros.
8. El código generado por IA sigue el mismo proceso de PR/revisión humana que cualquier otro (`HB-001` §19) — nunca es el único revisor de sí mismo.
9. Nunca pegar ni loguear secretos reales (JWT secret, credenciales, datos de usuarios) — `HB-001` §19.1.

---

## 9. Reglas de trabajo por área

| Área | Reglas |
|---|---|
| **Frontend (producto)** | React 19 + Vite + Tailwind v3. Fuente: `FRONTEND_ARCHITECTURE.md`. Sin Design System propio ratificado — no asumir tokens de `DS-001` (es del Handbook). Seguir la organización por `features/` ya existente y los alias de import ya definidos en `vite.config.js`. |
| **Backend** | Python + Flask + API REST + JWT. Fuente: `BACKEND_ARCHITECTURE.md`. Estructura de capas consolidada pero no ratificada — mantenerla por consistencia, no como contrato cerrado. Seguridad: documentada en `BACKEND_ARCHITECTURE.md` §16 (no hay documento transversal de seguridad dedicado); `JWT_SECRET_KEY` ya se lee de entorno, sin gestión de secretos de producción todavía. |
| **Database** | PostgreSQL. Fuente: `DATABASE_ARCHITECTURE.md`. Solo `users` está implementado y ratificado; el resto del alcance funcional es candidato u objetivo, no esquema decidido — no inventar convención sin confirmarlo. |
| **API** | Fuente única del contrato HTTP: `API_CONTRACT.md`. Solo `POST /api/login` está implementado. |
| **DevOps** | Sin documentación oficial (Docker, CI/CD, deploy, SSL, dominios, monitoreo). Tratar cualquier tarea de esta área como territorio no especificado. |
| **Handbook** | Código implementado (Release Candidate, Módulo 10); ver matiz de ratificación documental en §3.2. Toda decisión visual/estructural pasa por `ARC-001`/`DS-001`/`WF-001`/`PV-001`/`FAS-001` en ese orden de precedencia. |

---

## 10. Convenciones

- **Nombres:** componentes React en PascalCase, hooks en camelCase con prefijo `use`, archivos de configuración en kebab-case (`REPOSITORY_STRUCTURE.md` §8, confirmado en `Frontend/` y `handbook/`).
- **Estructura de archivos:** organización por dominio funcional (`features/<dominio>/{hooks,pages}` + `index.js`), no por tipo de archivo.
- **Imports:** el Handbook usa el alias `@ui` → `handbook/src/components/ui` (`vite.config.js`). El Frontend del producto usa los alias `@`, `@features`, `@shared`, `@assets`, definidos en `Frontend/vite.config.js` y documentados en `FRONTEND_ARCHITECTURE.md` §20 — usarlos en vez de rutas relativas para código nuevo dentro de `src/`.
- **Componentes:** en el Handbook, todo componente interactivo implementa el set completo de estados (`default/hover/focus-visible/disabled` según aplique — `PV-001` Parte 6 §8). En el Frontend del producto no hay un catálogo equivalente documentado.
- **APIs:** `API_CONTRACT.md` (§3.1) es la fuente única del contrato HTTP — no es una especificación OpenAPI/Swagger, es un catálogo ligero. Solo `POST /api/login` está implementado. Documentar cada endpoint nuevo en ese documento el mismo día del PR (`HB-001` §15.1), no retroactivamente.
- **Variables de entorno:** nunca se sube `.env` ni credenciales al repositorio (`HB-001` §20, regla innegociable). `backend/.env.example` documenta `JWT_SECRET_KEY` — no hay todavía una lista oficial completa ni variables de entorno del lado del Frontend.
- **Testing:** no hay framework de testing configurado en ningún `package.json` del repo, ni estrategia documentada en `/docs`. No asumir Jest/Vitest/pytest sin confirmarlo primero.

---

## 11. Comandos importantes

```bash
# Handbook (handbook/)
npm run dev            # servidor de desarrollo
npm run build           # build de producción (vite build)
npm run lint             # oxlint
npm run format            # prettier --write
npm run format:check       # prettier --check
npm run preview              # sirve el build de producción

# Frontend — producto (Frontend/)
npm run dev             # servidor de desarrollo
npm run build             # build de producción
npm run preview             # sirve el build de producción
# Nota: no hay script "lint" en Frontend/package.json pese a tener @eslint/js
# como devDependency — no está cableado todavía.
# Copiar Frontend/.env.example a Frontend/.env y ajustar VITE_API_URL si el
# backend no corre en http://127.0.0.1:5000; sin esa variable, api.js usa ese
# mismo valor por defecto y lo advierte por consola.

# Backend (backend/)
python -m venv venv
# Windows: venv\Scripts\activate — macOS/Linux: source venv/bin/activate
pip install -r requirements.txt   # backend/requirements.txt ya existe (Flask,
                                   # flask-cors, Flask-JWT-Extended); pyproject.toml
                                   # sigue sin existir
python run.py                     # punto de entrada
# Copiar backend/.env.example a backend/.env y definir JWT_SECRET_KEY antes de
# correr fuera de desarrollo local; sin esa variable, config.py usa un valor de
# desarrollo inseguro y lo advierte por stderr.
```

---

## 12. Protocolo antes de implementar

**ANALIZAR → CONSULTAR DOCS → PLANIFICAR → IMPLEMENTAR → VERIFICAR → REPORTAR**

1. **Analizar** la solicitud y el código relevante ya existente (sin re-explorar todo el repo si el contexto ya lo cubre).
2. **Consultar** el documento oficial correspondiente según la jerarquía de la §4 antes de asumir cualquier decisión.
3. **Planificar** el cambio dentro del alcance exacto solicitado.
4. **Implementar** reutilizando componentes/código existente, sin duplicar.
5. **Verificar** con build/lint del paquete afectado (§11) y, si aplica, navegación/responsive/dark mode/accesibilidad.
6. **Reportar** archivos tocados y verificaciones realizadas — sin commit/push salvo pedido explícito.

---

## 13. Protocolo de seguridad

Nunca ejecutar comandos destructivos (`rm -rf`, `git reset --hard`, `git push --force`, eliminar directorios o archivos importantes) ni sobrescribir trabajo no confirmado sin aprobación explícita del usuario en ese turno. Ante duda sobre si una acción es reversible, preferir la alternativa no destructiva (mover/renombrar en vez de borrar) y preguntar.

---

## 14. Regla de alcance

Si una solicitud contradice la documentación oficial (`/docs`), **detenerse antes de implementar** y señalar la contradicción explícitamente al usuario, citando el documento y la sección. No resolver el conflicto por criterio propio ni priorizar silenciosamente una fuente sobre otra.

---

## 15. Regla de incertidumbre — qué falta documentar

Si `/docs` no tiene información suficiente, **no inventar la decisión**: señalar el hueco. Huecos ya identificados en esta revisión:

- **DevOps completo** (Docker, CI/CD, deploy, SSL, dominios, monitoreo) — `HB-001` §0 confirma que no está escrito aún.
- **Persistencia real de datos** — `BACKEND_ARCHITECTURE.md` y `DATABASE_ARCHITECTURE.md` existen como propuestas (§3.1), pero no hay driver de PostgreSQL, ORM ni tabla `users` real implementada todavía; el login sigue validando contra una única credencial hardcodeada en código (ya no en texto plano, ver §5 Backend).
- **Esquema de base de datos más allá de `users`** — el resto del alcance funcional está registrado como candidato u objetivo en `DATABASE_ARCHITECTURE.md` §4.B, sin modelado ratificado.
- **Design System del Frontend del producto** — no existe; `DS-001` §1.2 confirma textualmente que es exclusivo del Handbook.
- **Especificación de API completa** — `API_CONTRACT.md` existe (§3.1) pero es un catálogo ligero, no OpenAPI/Swagger, y documenta explícitamente varios puntos como pendientes (formato de error estándar, versionado, paginación, convención de endpoints protegidos).
- **Variables de entorno requeridas** — `backend/.env.example` documenta `JWT_SECRET_KEY` y `Frontend/.env.example` documenta `VITE_API_URL`. No hay todavía una lista oficial completa más allá de estas dos (p. ej. variables de conexión a base de datos, inexistentes porque la persistencia no está implementada).
- **Estrategia de testing** — no hay framework configurado ni documento de estrategia.
- **Dos documentos oficiales sin analizar:** `Manual_Operativo/THERS_Manual_Operativo_v1.0.docx` (+ `.pdf`) y `Plan_Estrategico/Plan_Estrategico_IA_THERS.docx` (+ `.pdf`) — el entorno actual no pudo procesar `.docx` ni renderizar el `.pdf` (falta `poppler-utils`). Requieren revisión manual o una herramienta capaz de leerlos antes de asumir que no contienen reglas relevantes.
- **Contradicción del `README.md` raíz — corregida.** El `README.md` describía MySQL, una estructura `frontend/`/`backend/` distinta a la real y una tabla de equipo distinta a `HB-001`; fue actualizado para coincidir con `/docs` y el código real (motor de base de datos, estructura de carpetas, stack, estado real de endpoints, tabla de equipo). El contenido no verificable contra un documento oficial (descripción del producto, roadmap, flujo de contribución) no se tocó — sigue siendo informativo, no autoritativo.
- **Matiz de gobernanza en la cascada del Handbook** — `ARC-001` se autodeclara "Propuesta, pendiente de aprobación" mientras `DS-001`, que depende de él, se autodeclara "Oficial, vinculante" (ver §3.2). No resuelto — señalar si es relevante para la tarea en curso.
