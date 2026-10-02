# READINESS — App Android de THERS

> **Estado: auditoría. No se escribió ni se integró código de la app móvil.**
> Fecha de verificación: 2026-10-01. Rama: `develop` (`2352a4d`, sin divergencia con `origin/develop`).
> Origen del encargo: `THERS_PROMPT_CLAUDE_ANDROID.md` v2.0 (raíz del repositorio).
>
> **Nota de gobernanza:** `THERS_PROMPT_CLAUDE_ANDROID.md` vive fuera de `/docs`, así que por
> `CLAUDE.md` §4.5 es informativo, **no autoritativo**. Agregar una cuarta aplicación al monorepo
> es una decisión de alto impacto → requiere ADR aprobado (`HB-001` §11–12). Ver
> `docs/architecture/ADR-016-mobile-stack.md` (propuesta, pendiente de ratificación).

---

## 0. Actualización — trabajo de preparación del 2026-10-01

Después de la auditoría inicial se ratificó `ADR-016` y se trabajó en cerrar huecos. Estado de cada
bloqueo que listaba este documento:

| Bloqueo original | Estado ahora |
|---|---|
| PostgreSQL caído / Docker sin arrancar | **RESUELTO** — Docker Desktop arriba, `thers_postgres_dev` healthy en 5433 |
| Migraciones sin aplicar | **RESUELTO** — `thers_dev` y `thers_test` en `a5c8e2d71f34 (head)` |
| Suite de pruebas sin ejecutar | **RESUELTO** — **292 passed, 0 failed** contra PostgreSQL 16 real |
| Backend inaccesible | **RESUELTO** — sirviendo en `0.0.0.0:5000`; contrato de error verificado por HTTP |
| `conftest.py` apuntaba al puerto 5432 (PostgreSQL **nativo**) | **RESUELTO** — ahora deriva el puerto de `POSTGRES_PORT`, la misma variable que usa Compose |
| `npm run lint` fallaba con 3 errores | **RESUELTO** — plugin `react-hooks` agregado; 0 errores, 3 warnings reales ahora visibles |
| `platforms/android-36` y NDK ausentes | **INSTALADOS en esta sesión** (ver `ANDROID_SETUP.md` §4) |
| `backend/.venv` roto (sin `PIL`/`boto3`) | **RESUELTO** — `.venv` eliminado; `backend/venv` queda como único entorno (§2.2) |
| JDK 17, `JAVA_HOME`, `ANDROID_HOME` | **RESUELTO (2026-10-02)** — Temurin 17.0.20.1; ver `ANDROID_SETUP.md` §2 |
| Regla de firewall para el puerto 5000 | **RESUELTO (2026-10-02)** — TCP, perfiles Privado y Público (la red es Pública; `ANDROID_SETUP.md` §5) |
| Dispositivo no conectado | **RESUELTO (2026-10-02)** — moto z3 por USB; el Samsung A16 5G sigue sin probarse |

**`mobile/` ya existe** (creada el 2026-10-01, después de ratificar `ADR-016`): Expo SDK 57 +
RN 0.86.3 + TypeScript, con login, perfil propio y logout contra la API real. Typecheck,
`expo-doctor` (21/21) y bundle de Android verificados. **Actualización 2026-10-02:** build nativa
compilada, instalada y probada en un teléfono real (login, perfil, SecureStore, persistencia, logout,
fallo de red, `401` y caso `403`); pendiente el Samsung A16 5G. El detalle de qué está probado y
qué no vive en `docs/mobile/VALIDATION.md` §1.3, y el operativo del entorno en `ANDROID_SETUP.md`.

---

## 1. Veredicto

**«Listo para preparar `mobile/`, con bloqueos concretos para la integración.»**

> Actualización del 2026-10-01: los bloqueos de **servicio** (base de datos, backend, pruebas) están
> resueltos y verificados (§0). Los que quedan son de **herramientas locales** y **dispositivo**, no
> del producto.

El lado del producto está más avanzado de lo que asume el documento v2.0: la API es madura
(32 rutas registradas, contrato en `API_CONTRACT.md` v0.19) y el Frontend web ya la consume
end-to-end. Lo que impide empezar hoy mismo la integración no es el código: son **4 huecos de
herramientas Android**, **1 servicio caído**, **0 dispositivos conectados** y **2 contratos de
backend que ningún framework móvil puede resolver por su cuenta** (§4).

Distinción explícita del estado de la entrega:

| | Estado |
|---|---|
| Código móvil escrito | **SÍ** (`mobile/`: login, perfil, logout) |
| Build Android compilada | **SÍ** — APK debug (2026-10-02) |
| Prueba en teléfono realizada | **SÍ, parcial** — moto z3; falta repetir en el Samsung A16 5G |
| Integración externa verificada | **Ninguna** — Google Android, push y llamadas sin comprobar |

---

## 2. Matriz de auditoría

Leyenda de **Resultado**: `VERIFICADO` = comprobado en esta sesión con el comando citado ·
`NO COMPROBADO` = no se pudo o no se intentó · `BLOQUEO` = impide avanzar hasta resolverlo.

### 2.1 Repositorio y línea base

| Componente | Ruta / evidencia | Prueba ejecutada | Resultado |
|---|---|---|---|
| Estado de Git | `git status`, `git fetch --all` | `0 0` ahead/behind vs `origin/develop` | VERIFICADO — local al día |
| Trabajo sin commitear del equipo | 37 modificados + 9 sin seguimiento (ADR-015, media de perfil) | `git status --short` | VERIFICADO — **preservado, no se tocó nada** |
| Build del Frontend web | `Frontend/` | `npm run build` | VERIFICADO — `built in 2.14s`, 0 errores |
| Arranque del backend | `backend/app/__init__.py` | `create_app()` en subproceso | VERIFICADO con `backend/venv` — 32 rutas |
| Suite de pruebas del backend | `backend/tests/` | `python -m pytest` | **VERIFICADO (§0)** — **292 passed, 0 failed** contra PostgreSQL 16 real. Son 292 y no las 276 que cita `API_CONTRACT.md` v0.19 porque el trabajo sin commitear de ADR-015 agregó `test_profile_media.py` |
| Workspaces del monorepo | `package.json` raíz (solo `axios`, sin `workspaces`) | lectura | VERIFICADO — `mobile/` sería app independiente con su propio lockfile, igual que `backend/`, `Frontend/`, `handbook/` (`CLAUDE.md` §2) |

### 2.2 Dos virtualenvs — bloqueo local pequeño

| Componente | Evidencia | Prueba | Resultado |
|---|---|---|---|
| `backend/.venv` | falta `PIL`, falta `boto3` | `create_app()` | **BLOQUEO** — `ModuleNotFoundError: No module named 'PIL'` |
| `backend/venv` | todo presente (Flask, JWT, psycopg, resend, google-auth, Pillow, boto3, pytest) | `create_app()` | VERIFICADO — arranca bien |

El trabajo sin commitear de ADR-015 agregó `Pillow`/`boto3` a `requirements.txt`; `.venv` quedó
atrás. Quien use `.venv` no puede arrancar el backend. Arreglo: instalar `requirements.txt` en
`.venv`, o eliminarlo y quedarse con `venv`. **No ejecutado** (fuera del alcance de «no integrar
código»).

### 2.3 Backend de desarrollo accesible — RESUELTO

| Componente | Evidencia | Prueba | Resultado |
|---|---|---|---|
| `DATABASE_URL` configurada | `backend/.env` → `localhost:5433` | lectura (credenciales enmascaradas) | VERIFICADO |
| PostgreSQL en 5433 (Docker Compose) | `thers_postgres_dev`, `postgres:16-alpine` | `docker compose ps` | **VERIFICADO** — `Up (healthy)`, `0.0.0.0:5433->5432` |
| PostgreSQL nativo | servicio `postgresql-x64-18` | `netstat` | escuchando en **5432** — convive sin conflicto, pero es la causa del bug de `conftest.py` (§2.2b) |
| Migraciones | `backend/migrations/` | `flask db current` / `heads` | **VERIFICADO** — `a5c8e2d71f34 (head)` en `thers_dev` y `thers_test` |
| API sirviendo | `run.py` → `app.run(host="0.0.0.0", port=5000)` | `curl` | **VERIFICADO** — ver abajo |
| Contrato de error por HTTP | `app/interfaces/error_handlers.py` | 3 `curl` | **VERIFICADO** — sin token → `401 {"msg":"Falta el header de autorización"}`; ruta inexistente → `404 {"msg":"Recurso no encontrado"}` (JSON, no HTML); token basura → `401 {"msg":"Token inválido"}` |

El requisito del documento v2.0 §6 («backend de desarrollo accesible con autenticación y perfil
funcionales») **está satisfecho**. `run.py` ya escucha en `0.0.0.0`, así que un teléfono de la misma
red puede alcanzarlo — falta solo la regla de firewall (`ANDROID_SETUP.md` §5).

Nota de alcance: **no se creó ningún usuario de prueba por HTTP**. Con `RESEND_API_KEY` configurada,
registrar una cuenta dispara un correo real (`ADR-011` exige verificación por OTP antes del primer
login), y no corresponde generar correos a direcciones inventadas solo para una comprobación. La
cobertura de `register`/`login`/`GET /api/users/me` queda acreditada por las 292 pruebas de
integración, que corren contra PostgreSQL real con `NullEmailSender`.

### 2.2b Puerto de la base de datos de test — bug encontrado y corregido

`tests/conftest.py` tenía el puerto **5432 hardcodeado** para `thers_test`, mientras
`docker-compose.yml` publica el contenedor en `${POSTGRES_PORT:-5432}` y el `.env` de la raíz fija
`POSTGRES_PORT=5433`. En esta máquina el 5432 lo ocupa el **PostgreSQL 18 nativo**, así que
`python -m pytest` —el comando documentado en `CLAUDE.md` §11— se conectaba al motor equivocado en
vez de al del proyecto.

Corregido: `conftest.py` lee `POSTGRES_PORT` del `.env` de la raíz (la misma variable que usa
Compose), conservando el override por `TEST_DATABASE_URL`. **Verificado**: `python -m pytest` sin
ninguna variable a mano → 292 passed.

### 2.4 Contrato de sesión y autorización

| Componente | Ruta / evidencia | Prueba | Resultado |
|---|---|---|---|
| Login y token | `auth_routes.py` → `create_access_token(identity=user["id"])` | lectura | VERIFICADO — bearer JWT, `identity` = UUID |
| **Expiración del access token** | ninguna configuración en `config.py` | `app.config["JWT_ACCESS_TOKEN_EXPIRES"]` | VERIFICADO — **`0:15:00`** (default de la librería) |
| Refresh token | búsqueda de `create_refresh_token` → sin resultados | grep | VERIFICADO — **no existe** |
| Logout / blacklist | — | grep | VERIFICADO — no existe; un token robado vive hasta expirar |
| Errores de token homogeneizados | `app/extensions.py` | `API_CONTRACT.md` §4.2 | VERIFICADO — ausente/inválido/expirado → `401 {"msg": ...}` |
| Almacenamiento web actual | `AuthContext.jsx` → `localStorage` (`token`, `user`) | lectura | VERIFICADO — en móvil corresponde SecureStore para el token |
| Endpoint protegido de perfil | `GET`/`PATCH /api/users/me` | lectura + `url_map` | VERIFICADO — implementado y consumido por el web |
| Autorización sobre recursos de otro usuario | `@jwt_required()` + `get_jwt_identity()` en las rutas protegidas | lectura | NO COMPROBADO en ejecución (sin backend arriba) |

### 2.5 Endpoints realmente implementados (32 rutas, verificadas en `url_map`)

- **Auth:** `POST /api/register`, `/login`, `/auth/google`, `/forgot-password`,
  `/verify-reset-code`, `/reset-password`, `/verify-registration-code`, `/resend-registration-code`.
- **Perfil:** `GET`/`PATCH /api/users/me`, `POST`/`DELETE /api/users/me/avatar`,
  `POST`/`DELETE /api/users/me/cover` (ADR-015, todavía sin commitear).
- **Social:** `GET`/`POST /api/posts`, `POST`/`DELETE /api/posts/<id>/like`,
  `GET`/`POST /api/posts/<id>/comments`, `POST`/`DELETE /api/users/<id>/follow`.
- **Notificaciones:** `GET /api/notifications`, `PATCH /api/notifications/<id>/read`.
- **Mensajes:** `POST`/`GET /api/users/<id>/messages`, `GET /api/conversations`,
  `DELETE /api/messages/<id>`, `POST`/`GET /api/users/<id>/typing`.
- **Media:** `GET /api/media/<path>` (solo con `STORAGE_BACKEND=local`).

**Corrección al documento v2.0 §2:** chat, publicaciones, likes, comentarios, follows,
notificaciones y media **no están «planeados o parcialmente implementados»: están implementados y
consumidos por el Frontend web.** Lo que no existe en absoluto es cualquier forma de llamadas.

### 2.6 Chat — el transporte no es el que supone el documento v2.0

| Componente | Evidencia | Prueba | Resultado |
|---|---|---|---|
| Flask-SocketIO | ausente de `requirements.txt`; búsqueda de `socketio`/`websocket`/`eventlet`/`gevent` sobre `backend/` → **0 resultados** | grep | VERIFICADO — **no se usa** |
| Transporte real | `Messages.jsx`: `setInterval(loadThread, THREAD_POLL_MS)` 4 s + `pollTypingStatus` 2 s | lectura | VERIFICADO — **polling HTTP** |
| Estado de «escribiendo» | `ADR-014`: memoria del proceso, sin tabla | lectura | VERIFICADO — no sobrevive un reinicio ni varios workers |

La guía de §8 («si usa Flask-SocketIO, verifica compatibilidad de protocolos…») no aplica. No hay
protocolos Socket.IO que contrastar: hay que **decidir el transporte móvil del chat** (§4.2).

### 2.7 Google Sign-In

| Componente | Evidencia | Prueba | Resultado |
|---|---|---|---|
| Backend `POST /api/auth/google` | `google_id_token_verifier.py` con la librería oficial `google-auth` | lectura | VERIFICADO como implementado — firma/`iss`/`aud`/`exp` verificados criptográficamente |
| `GOOGLE_CLIENT_ID` presente | `backend/.env`, `Frontend/.env` (`VITE_GOOGLE_CLIENT_ID`) | presencia, sin leer el valor | VERIFICADO — definidos |
| Audiencia aceptada | `verify_oauth2_token(credential, _HTTP_REQUEST, self._client_id)` | lectura | VERIFICADO — **una sola `aud`**: el Web client ID |
| Login real de Google (web) | las 30 pruebas de ADR-012 corren con Google **mockeado** | — | **NO COMPROBADO** — ninguna prueba contra Google real; el problema de origen que menciona el documento v2.0 sigue sin verificar |
| Cliente OAuth de Android | — | — | **NO COMPROBADO** — no es verificable desde el repositorio |

**Hallazgo útil:** el backend probablemente **no necesita cambios**. Google Sign-In en Android
(Credential Manager) pide el ID Token con el **Web** client ID como `serverClientId`, así que la
`aud` del token sigue siendo exactamente la que el verificador ya exige. Falta registrar un
cliente OAuth de **Android** en Google Cloud Console con los SHA-1 de las keystores de debug y de
release. El backend no valida `azp`, así que el cliente Android no lo rompe. **Hipótesis
fundamentada, no verificada** — exige una prueba real en dispositivo.

### 2.8 Herramientas Android en la máquina de desarrollo (Windows 11)

| Componente | Encontrado | Requerido (RN 0.86.3 / Expo SDK 57) | Resultado |
|---|---|---|---|
| Node | v24.14.0 | ≥ 20 | VERIFICADO — sirve |
| npm | 11.12.0 | — | VERIFICADO |
| `java` en PATH | **1.8.0_281 (JDK 8)** | JDK 17+ | **BLOQUEO** — Gradle no arranca con JDK 8 |
| `JAVA_HOME` | **sin definir** | definida | **BLOQUEO** |
| JDK alternativo | `Android Studio/jbr` → OpenJDK **25.0.2** | Gradle 9.3.1 | utilizable en principio; RN documenta JDK 17 — compatibilidad con 25 **NO COMPROBADA** |
| `ANDROID_HOME` / `ANDROID_SDK_ROOT` | **sin definir** | definida | **BLOQUEO** |
| Android SDK | `%LOCALAPPDATA%\Android\Sdk` | — | presente |
| Platforms instaladas | **solo `android-37.0`** | `compileSdk`/`targetSdk` **36** | **HUECO** — falta `platforms;android-36` |
| Build-tools | 36.0.0, 37.0.0 | — | VERIFICADO — cubierto |
| NDK | **ninguno** (no existe la carpeta `ndk/`) | **27.1.12297006** | **HUECO** |
| cmdline-tools | `latest` | — | VERIFICADO |
| Android Studio | instalado | — | VERIFICADO |
| Espacio en disco | **49 GB libres de 476 GB (90 % usado)** | ~15–20 GB entre SDK, NDK, Gradle y node_modules | AJUSTADO — alcanza, sin holgura |
| Dispositivo (Samsung A16 5G) | `adb devices` → **lista vacía** | — | **BLOQUEO para pruebas** — adb 1.0.41 funciona; no hay teléfono conectado ni depuración USB activa |

### 2.9 Compatibilidad de dependencias (consultada al registro npm, 2026-10-01)

| Paquete | Versión actual | Nota |
|---|---|---|
| `expo` | 57.0.26 | SDK estable |
| `expo-template-blank-typescript` | pinea `react 19.2.3`, `react-native 0.86.3`, `typescript ~6.0.3` | **La web usa `react ^19.2.4` → misma línea de React** |
| `react-native` | 0.87.1 (última publicada) | **No usar 0.87 con SDK 57** — el template pinea 0.86.3 |
| Cadena de build de RN 0.86.3 | Gradle 9.3.1 · Kotlin 2.1.20 · minSdk 24 · compile/target 36 · NDK 27.1.12297006 | fuente: template oficial de la comunidad |
| `expo-router` / `expo-secure-store` / `expo-notifications` | 57.0.24 / 57.0.4 / 57.0.21 | alineados al SDK 57 |
| `@livekit/react-native` | **3.0.0** (publicado 2026-09-11) | peers: `livekit-client ^2.19.0`, `@livekit/react-native-webrtc ^144.2.0` (existe, 144.2.0). Mantenimiento activo |
| Google en Android | `react-native-nitro-google-signin` 2.3.0 · `@react-native-google-signin/google-signin` 16.1.5 | elección pendiente de revisar licencia/mantenimiento (documento v2.0 §4, [S15]) |

Ningún conflicto de versiones detectado para el alcance de la primera entrega.

### 2.10 Código reutilizable sin DOM

Clasificados los 39 módulos `.js` de `Frontend/src` según usen `window`/`document`/
`localStorage`/`navigator`/`import.meta.env`:

- **33 son puros y portables tal cual**: `auth/lib/validators.js`, `auth/lib/dateUtils.js`,
  `maskEmail.js`, `usePasswordStrength.js`, `feed/lib/formatRelativeTime.js`,
  `mapNotification.js`, los 4 módulos de `shared/i18n/` + `locales/{es,en}.json`,
  `help/lib/searchHelp.js`, `useDebouncedValue.js`, los datos estáticos y `navigation.js`.
- **6 dependen del navegador** y necesitan equivalente móvil: `api.js` (`import.meta.env` →
  `process.env.EXPO_PUBLIC_*`), `googleIdentityServices.js` (reemplazo nativo completo),
  `profileStorage.js`, `settingsStorage.js`, `useArticleFeedback.js` (`localStorage` →
  AsyncStorage/SecureStore) y `useTheme.js`.
- **Los 120 archivos `.jsx` no son reutilizables**: DOM + clases de Tailwind.
- `shared/design/tokens.css`: **211 custom properties** — valores planos, portables a un módulo de
  constantes TS sin necesidad de NativeWind ni otra biblioteca visual.

**Corrección importante al documento v2.0:** el shell web **ya es responsive y tiene navegación
móvil** — `MobileNav.jsx`, `MobileDrawer.jsx`, `Sidebar` oculta bajo `lg:`, 137 usos de breakpoints
en `.jsx`. Eso **fortalece materialmente la alternativa Capacitor** respecto de cómo la pondera §3
del documento. Ver el análisis en `ADR-016`.

---

## 3. Qué corrige este audit respecto del documento v2.0

1. **El estado del producto está subestimado.** Chat, posts, likes, comentarios, follows,
   notificaciones y media de perfil están implementados y consumidos por el web, no «planeados».
2. **No hay Flask-SocketIO.** El chat es polling HTTP (4 s / 2 s), verificado por código.
3. **El web ya tiene UI móvil.** La premisa «hay que adaptar las pantallas web» sigue siendo
   cierta para React Native, pero el trabajo que Capacitor evita es **mayor** del que sugiere §3.
4. **Google en Android probablemente no requiere cambios de backend** (`aud` = Web client ID vía
   `serverClientId`), al contrario de lo que haría pensar «verifica la audiencia esperada».
5. **El bloqueo real no es el framework**: es el token de 15 minutos sin refresh (§4.1).

---

## 4. Bloqueos que ningún framework móvil resuelve

### 4.1 Sesión de 15 minutos sin refresh — el bloqueo principal

`JWT_ACCESS_TOKEN_EXPIRES = 0:15:00` (default de `flask-jwt-extended`, verificado en ejecución),
sin refresh token y sin logout del lado del servidor. En el web se tolera: el usuario vuelve a
entrar. En una app móvil significa **volver a pedir la contraseña cada 15 minutos**, y rompe
cualquier registro de dispositivo para push asociado a la sesión.

`BACKEND_ARCHITECTURE.md` §20 ítem 9 ya lo registra como `PENDIENTE DE APROBACIÓN` («Política de
expiración y refresh de tokens JWT»), y `API_CONTRACT.md` lo repite. Por `CLAUDE.md` §14 **no se
resuelve por criterio propio**: es un ADR del equipo, previo o paralelo a la primera entrega móvil.
El documento v2.0 §7 dice «no inventes un refresh endpoint» — correcto, pero la consecuencia es
que la primera entrega móvil se probará con sesiones de 15 minutos.

### 4.2 El chat por polling no sobrevive en Android

Polling de 4 s con la app en primer plano es aceptable; en segundo plano Android lo detiene
(Doze y restricciones de servicios, [S13] del documento v2.0). Consecuencia: **push deja de ser
fase 4 y pasa a ser dependencia de la fase de chat**, o el chat móvil solo funciona con la app
abierta. Es una decisión de producto — queda planteada, no resuelta.

### 4.3 Gobernanza

Agregar `mobile/` toca `REPOSITORY_STRUCTURE.md` y la identidad del monorepo (`CLAUDE.md` §2:
tres aplicaciones independientes). Alto impacto → ADR aprobado antes de implementar
(`HB-001` §11–12). `THERS_PROMPT_CLAUDE_ANDROID.md`, al vivir fuera de `/docs`, no sustituye esa
aprobación.

---

## 5. Secuencia para desbloquear (no ejecutada)

1. Definir `JAVA_HOME` a un JDK 17+ y ubicarlo antes del JDK 8 en el `PATH`.
2. Definir `ANDROID_HOME` = `%LOCALAPPDATA%\Android\Sdk` y agregar `platform-tools` al `PATH`.
3. Instalar `platforms;android-36` y `ndk;27.1.12297006` con `sdkmanager`.
4. Arrancar Docker Desktop → `docker compose up -d` → `flask db upgrade` → `python run.py`.
5. Conectar el Samsung A16 5G con depuración USB y confirmarlo con `adb devices`.
6. Reparar o eliminar `backend/.venv` (§2.2).
7. Ratificar `ADR-016` (stack móvil) y abrir el ADR de política de sesión (§4.1).
8. Registrar el cliente OAuth de Android en Google Cloud Console con los SHA-1 de debug y release.

Solo después de 1–5 tiene sentido crear `mobile/`: antes, nada de lo que se escriba ahí puede
compilarse ni probarse en un teléfono.

---

## 6. Verificaciones ejecutadas en esta sesión

| Comando | Resultado |
|---|---|
| `git fetch --all --prune` + comparación con `origin/develop` | `0 0` — sin divergencia |
| `npm run build` (`Frontend/`) | OK, 2.14 s, 0 errores (genera `dist/`, ignorado por git) |
| `create_app()` con `backend/venv` | OK — 32 rutas, `JWT_ACCESS_TOKEN_EXPIRES = 0:15:00` |
| `create_app()` con `backend/.venv` | FALLA — `ModuleNotFoundError: No module named 'PIL'` |
| `curl http://127.0.0.1:5000/api/users/me` | sin respuesta (backend apagado) |
| `docker ps` | daemon no disponible |
| `adb devices` | lista vacía |
| `java -version`, `JAVA_HOME`, `ANDROID_HOME`, contenido del SDK | ver §2.8 |
| `npm view` de expo, react-native, el template, livekit, expo-router, secure-store y notifications | ver §2.9 |
| búsqueda de `socketio`/`websocket`/`eventlet`/`gevent` en `backend/` | 0 resultados |

**No se modificó nada en `backend/`, `Frontend/` ni `handbook/`.** Los archivos con cambios sin
commitear del equipo quedaron intactos. No se ejecutó `reset`, `clean`, `stash` ni `checkout`.
