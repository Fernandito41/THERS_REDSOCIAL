# FRONTEND_ARCHITECTURE

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/FRONTEND_ARCHITECTURE.md` |
| Versión | 0.2 (Propuesta) |
| Estado | **Pendiente de ratificación formal del equipo** (proceso de decisiones de alto impacto, `HB-001` §11–12) |
| Depende de | `HB-001` (Manual de Organización), `REPOSITORY_STRUCTURE.md` §3/§5, `BACKEND_ARCHITECTURE.md`, `DATABASE_ARCHITECTURE.md`, `CLAUDE.md`, código real de `Frontend/` |
| Autoridad sobre este documento | `/docs` oficial > estructura real observada en el código > este documento (mismo orden que `CLAUDE.md` §3) |

>  **Nota de estado.** No existía, previo a este documento, ninguna arquitectura Frontend oficial para el producto (`Frontend/`). `docs/architecture/Frontend/FAS-001-Frontend-Architecture-Specification.md` existe con un nombre similar y en una ruta que podría confundirse con esta, pero su propio contenido (§1, §3, §17) lo declara exclusivo del **THERS Engineering Handbook**, no del producto — ver §2 de este documento. Este documento sigue el mismo método ya validado por `BACKEND_ARCHITECTURE.md` y `DATABASE_ARCHITECTURE.md`: separa explícitamente **lo implementado**, **lo objetivo/propuesto** y **lo pendiente de aprobación**, y no se autoproclama cerrado. Toda sección que introduce una decisión no respaldada por código ni por documento previo se marca explícitamente como `PENDIENTE DE APROBACIÓN` (ver §24).
>
> **v0.2 — actualización tras introducir `VITE_API_URL` (pedida explícitamente por el equipo):** se resolvió la Open Architectural Decision #3 (§24) — `shared/lib/api.js` ya no tiene la URL de la API hardcodeada en un único valor; lee `import.meta.env.VITE_API_URL` con fallback advertido al valor de desarrollo local. Se agregaron `Frontend/.env.example` y la entrada `.env` en `Frontend/.gitignore`. Reflejado en las secciones 3, 9, 17, 21, 23 y 24. Ninguna otra sección cambió.
>
> Este documento no implementa, refactoriza ni modifica código de `Frontend/` por iniciativa propia, ni instala dependencias nuevas. Documenta lo que existe y propone, donde falta una decisión, el hueco explícito — nunca una arquitectura inventada.

---

## 1. Propósito y alcance

**Propósito.** Establecer el contrato técnico propuesto de la arquitectura Frontend del producto THERS (la red social): su stack, estructura, frontera con el backend, y las decisiones que el código ya asume implícitamente — de modo que la implementación futura siga la documentación y no al revés (mismo principio que `BACKEND_ARCHITECTURE.md` §1 y `FAS-001` §1 declaran para sus respectivas áreas: "el código sigue a la documentación, no al revés").

**Alcance.** Cubre exclusivamente `Frontend/`: su estructura interna, el código React/Vite ya implementado, sus dependencias, y las decisiones de arquitectura que ese código ya asume implícitamente.

**Fuera de alcance de este documento:**
- El THERS Engineering Handbook (`handbook/`) — arquitectura propia, ya cubierta por `ARC-001`/`DS-001`/`WF-001`/`PV-001`/`FAS-001`.
- Backend (`backend/`) y Base de Datos — arquitecturas propias, ya cubiertas por `BACKEND_ARCHITECTURE.md` y `DATABASE_ARCHITECTURE.md`; este documento las referencia solo en la frontera de integración (§6).
- Un Design System propio del producto — no existe y no se inventa aquí (§13).
- DevOps, Docker, CI/CD, despliegue — fuera del alcance declarado de `HB-001` §0 y sin ningún otro documento que los cubra; este documento solo señala qué información necesitará DevOps (§25).
- Catálogo de rutas/páginas futuras del producto (feed, perfiles, mensajería, etc.) — no implementadas hoy; no se diseñan por anticipado.

---

## 2. Relación con FAS-001

`FAS-001` vive en `docs/architecture/Frontend/`, la misma carpeta padre de este documento, y comparte parte del nombre ("Frontend Architecture"). Se deja constancia explícita de que **no son el mismo documento ni compiten entre sí**:

| | `FAS-001` | `FRONTEND_ARCHITECTURE.md` (este documento) |
|---|---|---|
| Aplica a | THERS Engineering Handbook (`handbook/`) | Producto — la red social (`Frontend/`) |
| Fuente que lo confirma | `FAS-001` §1, §3, §17 (texto literal) | `DS-001` §1.2 (confirma que el Handbook y el producto son sistemas separados) |
| Contenido | Capas conceptuales de un sitio documental estático (Markdown como dato) | Stack, estructura y frontera de una SPA con autenticación, estado y API real |
| Depende de | `HB-001`, `ARC-001`, `DS-001`, `WF-001`, `PV-001` | `HB-001`, `REPOSITORY_STRUCTURE.md`, `BACKEND_ARCHITECTURE.md`, `DATABASE_ARCHITECTURE.md` |

Ambos documentos pueden evolucionar de forma independiente. Si en el futuro el equipo decide unificar principios entre ambos Frontends, es una decisión de gobernanza (`HB-001` §11–12), no una consecuencia automática de ninguno de los dos documentos.

---

## 3. Stack Frontend

| Tecnología | Estado en `/docs` | Estado en el código | Observación |
|---|---|---|---|
| React | Confirmado (`HB-001` portada, §2 rol Tech Lead Frontend) | 19.2.4 (`Frontend/package.json`) | Implementado — toda la app |
| Vite | Confirmado (`HB-001` portada) | 8.0.1, con `@vitejs/plugin-react` 6.0.1 | Implementado |
| Tailwind CSS | Confirmado (`HB-001` portada) | 3.4.4 (v3, no v4 — distinto del handbook) | Implementado, **sin tokens propios**: valores hex sueltos en componentes (`bg-[#0f0f11]`, `bg-[#18181b]`), ver §13 |
| react-router-dom | No mencionado por nombre en `/docs` | 7.14.1 | Implementado — `BrowserRouter` con 6 rutas planas (§7) |
| axios | No mencionado por nombre en `/docs` | 1.18.1 | Implementado — un único wrapper (`src/shared/lib/api.js`), `baseURL` configurable vía `VITE_API_URL` (§9, §17) |
| react-icons | No mencionado por nombre en `/docs` | 5.6.0 | Implementado (`FcGoogle`, `IoClose`, `FaApple`) |
| Estado global | No documentado | **No instalado ni implementado** — ni Context API, ni Redux, ni Zustand | Ver §8 |
| Formularios / validación | No documentado | **No instalado** — `useState` manual por componente | Ver §11 |
| HTTP client alternativo (fetch nativo) | — | No usado — todo pasa por axios | — |
| Testing (Vitest/Jest/Playwright/Cypress) | No documentado (`CLAUDE.md` §9 ya confirma que no hay framework de testing en ningún `package.json` del repo) | **No instalado** | Ver §18 |
| ESLint | No documentado | `@eslint/js` 9.39.4 instalado como devDependency | **Instalado, no cableado**: no existe `eslint.config.js`/`.eslintrc*` en `Frontend/`, ni script `lint` en `package.json` (confirma `CLAUDE.md` §10) |
| Prettier | No documentado | No instalado en `Frontend/` (sí existe en `handbook/`, aplicaciones independientes) | Ver §19 |
| TypeScript | No documentado | `@types/react`/`@types/react-dom` instalados como devDependency, **sin `tsconfig.json`** | Tipos huérfanos — todo el código es `.jsx` puro, no se usa TypeScript |

**Distinción `instalado` vs. `realmente utilizado`:** solo React, Vite, Tailwind, react-router-dom, axios y react-icons están instalados **y** en uso real. `@eslint/js` y los paquetes `@types/*` están instalados sin estar cableados a ningún flujo de trabajo — no se deben tratar como decisiones activas del proyecto.

---

## 4. Arquitectura actual

**Patrón observado:** feature-based ligero, coherente con `REPOSITORY_STRUCTURE.md` §2 ("Modularidad por dominio"). No es atomic design, no es layered estricto, no es domain-driven en sentido formal — no se fuerza una clasificación más sofisticada de la que el código (2 features, 6 páginas) sostiene hoy.

- Cada feature (`auth`, `legal`) vive en `src/features/<dominio>/` y expone un `index.js` como barrel/punto de entrada único.
- No hay separación por capas dentro de cada feature más allá de `pages/`/`hooks/`. `auth` no tiene `components/` propio (usa `shared/components/Logo`); ninguna feature tiene `services/` propio — el único acceso a datos hoy es una llamada directa desde `useAuth.js` al cliente axios compartido.
- `shared/` aloja lo transversal: `components/` (hoy solo `Logo.jsx`) y `lib/` (hoy solo `api.js`).
- `app/` aloja el arranque de la aplicación: hoy **solo** `router/router.jsx`.

**`[CONFLICTO]` heredado de la auditoría previa — `RESUELTO`:** `REPOSITORY_STRUCTURE.md` §3 documentaba `app/providers/` y `app/store/` como carpetas existentes. La verificación directa del filesystem (`Frontend/src/app/`) confirmó que **no existen** — solo `app/router/` es real. `REPOSITORY_STRUCTURE.md` ya fue corregido para reflejar el árbol real (ver su nota de verificación). Este documento sigue tratando `providers/` y `store/` como `[PROPUESTO]` (§8), no como `[EXISTENTE]`, hasta que se implementen.

---

## 5. Estructura del proyecto

Estructura real verificada (no la documentada por el `README.md` raíz, que no es autoritativo — ver §22):

```
Frontend/
├── public/
├── src/
│   ├── app/
│   │   └── router/
│   │       └── router.jsx
│   ├── assets/
│   ├── features/
│   │   ├── auth/
│   │   │   ├── hooks/
│   │   │   │   └── useAuth.js
│   │   │   ├── pages/
│   │   │   │   ├── AuthPage.jsx
│   │   │   │   ├── Login.jsx
│   │   │   │   └── Register.jsx
│   │   │   └── index.js
│   │   └── legal/
│   │       ├── pages/
│   │       │   ├── Terms.jsx
│   │       │   ├── Privacy.jsx
│   │       │   └── Cookies.jsx
│   │       └── index.js
│   ├── shared/
│   │   ├── components/
│   │   │   └── Logo.jsx
│   │   └── lib/
│   │       └── api.js
│   ├── App.jsx, App.css
│   ├── index.css
│   └── main.jsx
├── index.html
├── vite.config.js
├── tailwind.config.js
└── postcss.config.js
```

**Regla de crecimiento (heredada de `REPOSITORY_STRUCTURE.md` §2 y por analogía de `FAS-001` §3, aplicable como principio general, no como contenido específico del Handbook):** una feature nueva es una carpeta adicional dentro de `features/`, no una reorganización de las existentes. No se fija aquí una estructura interna obligatoria de `services/`/`types/` por feature — es prematuro con solo 2 features (§24, ítem 7).

---

## 6. Frontera Frontend ↔ Backend ↔ Database

Regla heredada, ya respetada de facto por el código actual:

```
Frontend (Frontend/)
   ↓  HTTP/JSON, vía shared/lib/api.js
Backend API (backend/app/interfaces/routes/)
   ↓
Application / Domain (backend/app/application, domain)
   ↓
PostgreSQL (⚠️ no implementado — BACKEND_ARCHITECTURE.md §8)
```

- El Frontend **nunca** accede a PostgreSQL directamente ni conoce detalles de persistencia — regla heredada de `BACKEND_ARCHITECTURE.md` §17 y `DATABASE_ARCHITECTURE.md` §13. El código actual la cumple: el único acceso a datos es vía `axios` contra `http://127.0.0.1:5000/api`.
- El Frontend **no debe duplicar lógica de negocio** que pertenece al backend (validación real de credenciales, reglas de autorización) — principio general, aplicado aquí por analogía de `FAS-001` §2 ("bajo acoplamiento"), no como contenido específico del Handbook.
- **Estado real de la integración (honesto, no aspiracional):** el backend hoy solo expone `POST /api/login` (`BACKEND_ARCHITECTURE.md` §5, §19), sin persistencia real, sin endpoint de registro, sin endpoints protegidos con `@jwt_required()`. Esto significa que:
  - El formulario de `Register.jsx` no está conectado a ningún backend real (`handleRegister` solo hace `console.log(form)` y navega a `/login`).
  - El modelo de usuario que el Frontend puede asumir hoy es `{ email, name }` (`DATABASE_ARCHITECTURE.md` §4.A) — no `username`, `avatar_url` ni `bio`, que existen solo como candidatos objetivo, no implementados.
  - No existe hoy ningún caso real de "ruta protegida" que el Frontend pueda replicar como patrón validado.
- **Formato de error esperado del backend:** `{"msg": "..."}` (`BACKEND_ARCHITECTURE.md` §5, §11) — observado, no estandarizado ni siquiera en el propio backend. El Frontend no debe fijar un manejo de errores más sofisticado del que el backend puede producir hoy (§12).

---

## 7. Routing

- **Implementado:** `react-router-dom` 7.14.1, `BrowserRouter` con `Routes`/`Route`, definido en un único archivo (`src/app/router/router.jsx`).
- **Rutas actuales (6, todas públicas):** `/` (`AuthPage`), `/login`, `/register`, `/terms`, `/privacy`, `/cookies`.
- **No implementado:** rutas anidadas, rutas protegidas (`PrivateRoute`/`RequireAuth`), lazy loading de páginas, layouts compartidos entre rutas.
- Introducir rutas protegidas depende de que exista una estrategia de sesión ratificada (§10, §24 ítem 2) — no se propone una implementación concreta aquí para no adelantar esa decisión.

---

## 8. Estado (state management)

- **Implementado:** únicamente estado local por componente (`useState`) — en `App.jsx` (`loading`, `exit` del splash screen), `Login.jsx` (`input`), `Register.jsx` (`form`).
- **No implementado:** no existe ningún mecanismo de estado global (Context API, Redux, Zustand, Jotai). `app/store/` **no existe** en el código real — `REPOSITORY_STRUCTURE.md` §3 ya fue corregido para no documentarlo como existente (§4, conflicto resuelto).
- **Sesión de usuario:** no hay ningún estado de "usuario autenticado" accesible fuera del componente `Login`. El token se persiste en `localStorage` (§10, §16) pero no hay lectura de ese token al montar la aplicación (`App.jsx` no verifica sesión existente), ni contexto que exponga el usuario actual a otros componentes.
- **`PENDIENTE DE APROBACIÓN`** (§24, ítem 1): elegir una estrategia de estado global antes de que una feature nueva (p. ej. feed, perfil) necesite compartir estado entre páginas. Candidatos razonables dado el tamaño actual del proyecto — Context API (sin dependencia nueva) o una librería ligera — pero **no se decide aquí**.

---

## 9. Data fetching / API client

- **Implementado:** `src/shared/lib/api.js` — instancia única de `axios` con `baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:5000/api"`. **Corregido:** ya no está hardcodeado en un único valor — si `VITE_API_URL` no está definida, cae al valor de desarrollo local y lo advierte por consola (`console.warn`), mismo patrón que `backend/app/config.py` usa para `JWT_SECRET_KEY`.
- **Patrón de consumo:** cada feature que necesita datos importa `api` directamente (hoy, solo `useAuth.js`). No existe una capa `services/` por feature.
- **No implementado:** interceptores de axios (para adjuntar el token JWT automáticamente, o manejar `401` de forma centralizada), reintentos, cancelación de requests, cache de datos (React Query/SWR u otro).

---

## 10. Autenticación y autorización

Estado actual, sin proponer una solución más sofisticada de la que el backend puede sostener hoy (`BACKEND_ARCHITECTURE.md` §9):

- **Login:** `Login.jsx` llama a `useAuth().login({ email, password })`. En el código actual, `password` está **hardcodeada como `"123456" // temporal"`** dentro del propio componente — el campo de contraseña no existe en el formulario de login.
- **Token:** `useAuth.js` guarda el token recibido en `localStorage.setItem("token", ...)`. No hay lectura de ese token en ningún otro punto de la aplicación.
- **Registro:** `Register.jsx` recolecta `name`/`email`/`password`, pero `handleRegister` no llama a ningún endpoint — solo hace `console.log(form)` y navega a `/login` (comentario `// temporal` en el propio código). Coherente con que el backend no expone `/register` (`BACKEND_ARCHITECTURE.md` §9).
- **No implementado:** logout, verificación de expiración del token, refresh token, rutas protegidas, manejo de `401`/`403` centralizado, login con Google/Apple (los botones existen visualmente en `Login.jsx`/`Register.jsx`/`AuthPage.jsx` pero no tienen `onClick` conectado a ningún flujo OAuth).
- **`PENDIENTE DE APROBACIÓN`** (§24, ítem 2): dónde vive el token (localStorage vs. cookie httpOnly — ver riesgo en §16), cómo se verifica la sesión al cargar la app, y el mecanismo de rutas protegidas. Depende también de decisiones aún abiertas del propio backend (`BACKEND_ARCHITECTURE.md` §20, ítems 8–9: gestión de secretos y política de expiración/refresh de JWT).

---

## 11. Formularios y validación

- **Implementado:** formularios controlados manualmente con `useState` + `onChange`, sin librería (`Login.jsx`, `Register.jsx`).
- **Validación actual:** `Register.jsx` calcula `isValid` verificando que `name`/`email`/`password` no estén vacíos tras `.trim()` — sin validar formato de email ni requisitos de contraseña. `Login.jsx` no valida el campo `input` más allá de que no esté vacío (habilita/deshabilita el botón).
- **No implementado:** ninguna librería de formularios/validación (React Hook Form, Formik, Zod, Yup).
- No se propone adoptar una librería aquí — con 2 formularios el código manual es proporcional (principio de simplicidad, aplicado por analogía de `FAS-001` §2). Se marca como `PENDIENTE DE APROBACIÓN` de prioridad media (§24, ítem 5) para cuando el número de formularios crezca.

---

## 12. Manejo de errores y estados de carga

- **Implementado:** `Login.jsx` envuelve la llamada de login en `try/catch` y muestra el error con `alert("Error al iniciar sesión")` — sin distinguir tipos de error (red, credenciales inválidas, servidor caído).
- **No implementado:** estados de carga (spinners/skeletons) durante las llamadas a la API, estados vacíos (empty states), manejo de errores estandarizado o componente de notificación/toast.
- Este documento no propone un estándar de error/loading todavía porque el propio backend no tiene un formato de error unificado (`BACKEND_ARCHITECTURE.md` §11, §20 ítem 5) — definir uno en el Frontend antes de que el backend lo tenga arriesga tener que rehacerlo. `PENDIENTE DE APROBACIÓN`, dependiente de esa decisión de backend.

---

## 13. Design System

> ⚠️ Sección crítica — confirmado directamente en la fuente. `DS-001` §1.2 declara textualmente: **"No aplica al producto THERS en sí (la app React/Flask que el equipo desarrolla como proyecto). Ambos sistemas pueden evolucionar de forma independiente; si en el futuro se decide unificarlos, eso es una decisión de gobernanza (sección 16), no una consecuencia automática de este documento."**

- **No existe ningún Design System ratificado para `Frontend/`.** Este documento no extrapola `DS-001` ni inventa uno nuevo — ambas acciones están fuera de su alcance (regla explícita de la tarea que originó este documento).
- **Estado real del código:** cada componente define sus propios valores visuales sueltos — colores hex directos (`bg-[#0f0f11]`, `bg-[#18181b]`, `border-gray-800`), sin ningún token intermedio. Esto no es un error de implementación: es la consecuencia esperada de no tener un Design System que consumir.
- **`PENDIENTE DE APROBACIÓN`** (§24, ítem 4): si el equipo decide crear un Design System propio del producto, o proponer formalmente unificarlo con `DS-001` (proceso de gobernanza de `DS-001` §16), es una decisión de alto impacto que debe registrarse como ADR antes de tomarse — no se decide aquí.

---

## 14. Responsive y accesibilidad

- **Responsive:** uso de utilidades responsive de Tailwind observado puntualmente (`AuthPage.jsx` usa `hidden md:flex` para ocultar el panel izquierdo en mobile). No hay una estrategia documentada de breakpoints ni verificación sistemática en el resto de las páginas.
- **Accesibilidad:** no hay evidencia de atributos ARIA, `alt` en imágenes decorativas revisado sistemáticamente, ni verificación de contraste (no hay tokens que verificar — §13). No hay ningún estándar de accesibilidad documentado para el producto (a diferencia del Handbook, donde `DS-001` §12 exige WCAG 2.2 AA como piso mínimo — esa exigencia **no se hereda automáticamente** al producto).
- No se fija aquí un estándar de accesibilidad — sería inventar una decisión no respaldada. Se señala como gap, no se llena.

---

## 15. Performance

- **No evaluable de forma significativa hoy:** la aplicación tiene 6 rutas estáticas y ningún dato remoto más allá de un login. No hay code splitting, lazy loading de rutas, ni optimización de imágenes más allá de lo que Vite hace por defecto.
- Optimizar prematuramente sobre una app de este tamaño contradice el principio de simplicidad (aplicado por analogía de `FAS-001` §2 y §12) — no se proponen reglas de performance específicas en esta versión. Revisar cuando el catálogo de rutas y volumen de datos crezca (feed, medios).

---

## 16. Seguridad Frontend

Estado actual observado, sin proponer remediaciones como si fueran ya decididas (mismo estándar que `BACKEND_ARCHITECTURE.md` §16 y `DATABASE_ARCHITECTURE.md` §11 aplican a sus áreas):

| Área | Estado |
|---|---|
| Almacenamiento del token JWT | `localStorage` (`useAuth.js`) — expuesto a lectura por cualquier script que corra en la página (riesgo XSS). Alternativa común (cookie `httpOnly`) no evaluada ni decidida — `PENDIENTE DE APROBACIÓN` |
| Variables de entorno / secretos | No hay ningún secreto en el Frontend hoy (correcto: el Frontend nunca debe tener secretos — ver distinción `PUBLIC CONFIG` vs. `SECRET CONFIG` en §17). El `JWT_SECRET_KEY` vive (mal) en el backend, no en el Frontend — fuera de alcance de este documento (`BACKEND_ARCHITECTURE.md` §16) |
| Datos sensibles en código fuente | La contraseña `"123456"` hardcodeada en `Login.jsx` no es un secreto de sistema, pero es una credencial de prueba versionada en git — mismo espíritu de riesgo que `HB-001` §19.1 busca evitar, aunque técnicamente distinto de un secreto real |
| XSS | No hay uso de `dangerouslySetInnerHTML` ni inyección de HTML no confiable en el código actual — superficie de riesgo baja hoy, pero no hay política documentada para cuando exista contenido generado por usuarios (posts, comentarios) |
| CORS | Responsabilidad del backend (`CORS(app)` sin restricción — `BACKEND_ARCHITECTURE.md` §13); el Frontend no controla esto, solo lo consume |

**`PENDIENTE DE APROBACIÓN`** (§24, ítem 2, junto con la estrategia de sesión): decidir si el token JWT se mantiene en `localStorage` o migra a un mecanismo más seguro, cuando exista una razón real para decidirlo (antes de tener datos de usuario reales que proteger).

---

## 17. Variables de entorno

- **Estado actual — corregido:** `Frontend/.env.example` documenta `VITE_API_URL` (sin valores reales) y `Frontend/.gitignore` protege un `.env` real. `src/shared/lib/api.js` lee `import.meta.env.VITE_API_URL`, con fallback al valor de desarrollo local si no está definida (§9).
- **Distinción a mantener (regla de esta tarea, no violar):**
  - `PUBLIC CONFIG` (seguro de exponer en el bundle del cliente, prefijo `VITE_` requerido por Vite): hoy solo `VITE_API_URL`.
  - `SECRET CONFIG`: **nunca** debe vivir en el Frontend. Ningún secreto (JWT secret, credenciales de base de datos) pertenece a `Frontend/` bajo ninguna circunstancia — esos viven exclusivamente en el backend, y ahí tampoco deberían estar hardcodeados (`BACKEND_ARCHITECTURE.md` §12, §16).
- `VITE_API_URL` es hoy la única variable documentada — no hay todavía una lista más amplia porque no hay más configuración que el Frontend necesite externalizar.

---

## 18. Testing

- **Estado actual: no hay ningún framework de testing instalado ni configurado** en `Frontend/` (confirma `CLAUDE.md` §9, extendido aquí específicamente al producto).
- No hay carpeta `__tests__/`, ni archivos `*.test.jsx`/`*.spec.jsx`, ni configuración de Vitest, Jest, Playwright o Cypress.
- No se propone aquí una herramienta ni estrategia como si fuera decisión tomada — `CLAUDE.md` §4 exige confirmar dependencias con el equipo antes de asumirlas. `PENDIENTE DE APROBACIÓN` (§24, ítem 6).

---

## 19. Linting y formatting

- **ESLint:** `@eslint/js` 9.39.4 está instalado como devDependency, pero **no hay `eslint.config.js`** (ni `.eslintrc*` legado) en `Frontend/`, y no hay script `lint` en `package.json` — confirma textualmente lo que `CLAUDE.md` §10 ya señala. El lint no corre hoy en ningún flujo de trabajo.
- **Prettier:** no instalado en `Frontend/` (sí existe como devDependency en `handbook/`, aplicación independiente sin dependencias compartidas — `REPOSITORY_STRUCTURE.md` §2/§9).
- Activar lint (crear `eslint.config.js` + script `lint`) es de bajo riesgo y alto beneficio, pero **no se hace en este documento** (regla de la tarea: no instalar dependencias ni cambiar configuraciones). Se registra como Open Architectural Decision de prioridad baja (§24, ítem 8).

---

## 20. Convenciones de naming y estructura

Confirmadas por `REPOSITORY_STRUCTURE.md` §8 y verificadas contra el código real:

- Componentes React: PascalCase (`AuthPage.jsx`, `Login.jsx`, `Register.jsx`, `Logo.jsx`).
- Hooks: camelCase con prefijo `use` (`useAuth.js`).
- Archivos de configuración: kebab-case (`vite.config.js`, `tailwind.config.js`, `postcss.config.js`).
- Código, nombres de carpeta y archivo: inglés (`auth`, `legal`, `shared`, `components`, `hooks`).
- Organización por dominio funcional (`features/<dominio>/{hooks,pages}` + `index.js` como barrel), no por tipo de archivo.

**Alias de imports — `[EXISTENTE]`, no documentado hasta ahora en ningún otro lugar de `/docs` ni en `CLAUDE.md`:**

| Alias | Apunta a | Uso real verificado |
|---|---|---|
| `@` | `Frontend/src` | `@/assets/...` en `AuthPage.jsx` |
| `@features` | `Frontend/src/features` | `@features/auth`, `@features/legal` en `router.jsx` |
| `@shared` | `Frontend/src/shared` | `@shared/lib/api`, `@shared/components/Logo` |
| `@assets` | `Frontend/src/assets` | Definido en `vite.config.js`, sin uso confirmado fuera de `@/assets/...` |

Definidos en `Frontend/vite.config.js`. Se documentan aquí como parte del contrato de convenciones — no se modifican ni se amplían en este documento.

---

## 21. Entorno de desarrollo

Lo que hoy es reproducible de forma verificable, sin inventar pasos no confirmados:

```bash
cd Frontend
npm install
npm run dev       # servidor de desarrollo (Vite)
npm run build      # build de producción → dist/ (default de Vite, no confirmado explícitamente en config)
npm run preview     # sirve el build de producción
```

- **Node version:** no fijada en ningún `.nvmrc` ni `package.json engines` — `PENDIENTE DE APROBACIÓN`.
- **Package manager:** npm, confirmado por la presencia de `package-lock.json` (no hay `yarn.lock` ni `pnpm-lock.yaml`).
- **Variables de entorno:** copiar `Frontend/.env.example` a `Frontend/.env` y ajustar `VITE_API_URL` si el backend no corre en `http://127.0.0.1:5000` (§17). Sin ese archivo, `api.js` usa ese mismo valor por defecto y lo advierte por consola — el comportamiento por defecto sigue funcionando para desarrollo local sin configuración adicional.
- **Integración con Backend:** `backend/requirements.txt` ya existe (`BACKEND_ARCHITECTURE.md` §2) — un desarrollador Frontend nuevo puede instalar y levantar el backend localmente (`pip install -r requirements.txt`, `python run.py`) para probar el login end-to-end, sin coordinarse manualmente con otra persona del equipo.

---

## 22. Conflictos detectados

| # | Conflicto | Fuente A | Fuente B | Impacto | Estado |
|---|---|---|---|---|---|
| 1 | Motor de base de datos | `HB-001`/`BACKEND_ARCHITECTURE.md`/`DATABASE_ARCHITECTURE.md` → PostgreSQL | `README.md` raíz → MySQL | Bajo para Frontend en sí; alto para onboarding | PENDIENTE DE RATIFICACIÓN (ya reportado en `CLAUDE.md` §14) |
| 2 | Estructura de carpetas del Frontend | `README.md` raíz → `frontend/src/{components,pages,routes,context,services}` | Código real + `REPOSITORY_STRUCTURE.md` → `Frontend/src/{app,features,shared}` | Medio — estructuras incompatibles | PENDIENTE DE RATIFICACIÓN |
| 3 | `app/providers/` y `app/store/` documentados vs. inexistentes | `REPOSITORY_STRUCTURE.md` §3 | Filesystem real de `Frontend/src/app/` | Bajo pero directo | **RESUELTO** — `REPOSITORY_STRUCTURE.md` corregido para reflejar el árbol real |
| 4 | Alias de imports no documentados en `CLAUDE.md` | `CLAUDE.md` §9 ("sin alias documentado") | `vite.config.js` + uso real (§20) | Bajo — desactualización, no contradicción de fondo | Registrado aquí; no se modifica `CLAUDE.md` en esta tarea |
| 5 | Identificador `STD-001` referenciado pero inexistente como tal | `FAS-001`, `WF-001`, `PV-001`, `REPOSITORY_STRUCTURE.md` citan "STD-001" | El único Manual de Organización real tiene ID `HB-001` | Bajo — probable alias/nombre previo | PENDIENTE DE RATIFICACIÓN (no resuelto aquí) |

Ninguno de estos conflictos se resuelve por iniciativa propia de este documento (`CLAUDE.md` §13) — se listan para decisión del equipo.

---

## 23. Matriz de trazabilidad

| Decisión Frontend | Fuente | Estado | Evidencia |
|---|---|---|---|
| React | `HB-001` portada + `Frontend/package.json` | OFICIAL + EXISTENTE | React 19.2.4 |
| Vite | `HB-001` portada + `vite.config.js` | OFICIAL + EXISTENTE | Vite 8.0.1 |
| Tailwind CSS (v3) | `HB-001` portada + `tailwind.config.js` | OFICIAL + EXISTENTE | v3.4.4, sin tokens propios |
| React Router | Código real | EXISTENTE (no OFICIAL) | `react-router-dom` 7.14.1 |
| Axios | Código real | EXISTENTE | `shared/lib/api.js` |
| Organización por `features/` | `REPOSITORY_STRUCTURE.md` §2/§5 | OFICIAL (borrador) + EXISTENTE | `features/auth`, `features/legal` |
| Alias `@`/`@features`/`@shared`/`@assets` | Código real | EXISTENTE (no documentado hasta este documento) | `vite.config.js` + uso en imports |
| Design System | `DS-001` §1.2 | Explícitamente NO aplica | Texto literal de exclusión |
| Frontend ↔ Backend vía API HTTP/JSON | `BACKEND_ARCHITECTURE.md` §17 | HEREDADO | Regla de capas del backend |
| Frontend nunca accede a PostgreSQL directamente | `DATABASE_ARCHITECTURE.md` §13 | HEREDADO | Regla de capas de datos |
| Modelo de usuario disponible hoy (`{email, name}`) | `DATABASE_ARCHITECTURE.md` §4.A | HEREDADO | Única entidad ratificada |
| Estado global | — | PROPUESTO | Ausencia de Context/Redux/Zustand en código |
| Variables de entorno (`VITE_API_URL`) | Código real | EXISTENTE (no OFICIAL) | `Frontend/.env.example`, `shared/lib/api.js` |
| Testing | — | PROPUESTO | Ausencia de Vitest/Jest/Playwright |
| Rutas protegidas | — | PROPUESTO | Sin backend con endpoints protegidos que replicar |

---

## 24. Open Architectural Decisions

| # | Decisión | Prioridad | Por qué |
|---|---|---|---|
| 1 | Estrategia de estado global (Context API, Zustand, u otra) | **Alta** | Bloquea cualquier feature que necesite compartir estado entre páginas; `providers/`/`store/` ya aparecen documentados como si existieran (§4) |
| 2 | Estrategia de sesión/autenticación (dónde vive el token, expiración, refresh, rutas protegidas) | **Alta** | Bloquea toda feature más allá de login; depende también de decisiones pendientes del backend (`BACKEND_ARCHITECTURE.md` §20, ítems 8–9) |
| 3 | ~~Variables de entorno (`VITE_API_URL`)~~ | ~~Alta~~ | **Resuelto** — `Frontend/.env.example` + lectura vía `import.meta.env.VITE_API_URL` en `shared/lib/api.js` (§9, §17) |
| 4 | Design System propio del producto, o extensión formal de `DS-001` (decisión de gobernanza, `DS-001` §16) | **Media** | Sin esto, cada página seguirá introduciendo valores visuales sueltos, como ya ocurre |
| 5 | Librería de formularios/validación | **Media** | Bajo riesgo con 2 formularios hoy; crecerá con más features sociales |
| 6 | Framework y estrategia de testing | **Media** | Ningún paquete del monorepo lo tiene; no exclusivo de Frontend, pero bloquea calidad a futuro |
| 7 | Estructura interna definitiva de cada `feature/` (¿`services/`? ¿`types/`?) | **Baja** | Solo 2 features hoy; prematuro fijar más estructura de la necesaria |
| 8 | Activar lint (`eslint.config.js` + script `lint`) | **Baja** | Bajo riesgo, alto beneficio; no es una decisión arquitectónica de fondo |

---

## 25. Información que deberá consumir DevOps

- **Node version:** no fijada — `PENDIENTE`.
- **Package manager:** npm (`package-lock.json`).
- **Build command:** `npm run build` (`vite build`).
- **Output directory:** `dist/` (default de Vite — no confirmado explícitamente en `vite.config.js`).
- **Preview/health check:** `npm run preview`.
- **Variables de entorno de build:** ninguna hoy — depende de que se ratifique la Open Architectural Decision #3 (§24).
- **Docker:** sin Dockerfile ni requisito documentado — territorio no especificado (`CLAUDE.md` §4 DevOps).
- **Testing command:** no existe — bloqueante para cualquier gate de CI que dependa de tests (§24, ítem 6).
- **Dependencia de Backend en runtime:** el Frontend hoy asume `http://127.0.0.1:5000/api` — cualquier pipeline de CI/CD que pruebe el login end-to-end necesitará el backend corriendo en ese origen, o la variable de entorno de la Decisión #3 ya resuelta.

---

## 26. Fuentes consultadas

- `CLAUDE.md` (raíz) — índice de reglas operativas y jerarquía de fuentes.
- `docs/architecture/REPOSITORY_STRUCTURE.md` — estructura del monorepo, incluida la sección Frontend (§3, §5, §8).
- `docs/architecture/organization/01_Manual_Organizacion/Source/HB-001-manual-organizacion.md.md` — Manual de Organización (roles, stack, gobernanza, ADR, reglas de uso de IA).
- `docs/architecture/BACKEND_ARCHITECTURE.md` — arquitectura backend, usada para la frontera de integración (§6) y como modelo de formato para este documento.
- `docs/architecture/DATABASE_ARCHITECTURE.md` y `DATABASE_ERD.md` — modelo de datos, usados para §6 y §10.
- `docs/architecture/design/design-system/source/DS-001-design-system.md.md` — confirma textualmente (§1.2) que no aplica al producto (§13).
- `docs/architecture/Frontend/FAS-001-Frontend-Architecture-Specification.md` — confirma su propio alcance exclusivo al Handbook (§2).
- `README.md` (raíz) — fuente no oficial; usado solo para documentar las contradicciones registradas en §22.
- Código fuente completo de `Frontend/`: `package.json`, `vite.config.js`, `tailwind.config.js`, `src/App.jsx`, `src/main.jsx`, `src/app/router/router.jsx`, `src/shared/lib/api.js`, `src/features/auth/**`, `src/features/legal/index.js`, `src/shared/components/Logo.jsx`, `src/index.css`.
- Verificación directa del filesystem (`Frontend/src/app/`) para confirmar la ausencia de `providers/`/`store/` (§4, §22).

---

## 27. Cierre

Este documento **no modifica** el código de `Frontend/`, el backend, la base de datos ni el Handbook: define el contrato de arquitectura Frontend que la implementación futura deberá respetar, separando explícitamente **lo implementado**, **lo propuesto** y **lo pendiente de aprobación** (§24). Cualquier cambio a este contrato sigue el proceso de decisiones de impacto medio/alto de `HB-001` §11–12 (ADR), no el criterio individual de quien implementa.
