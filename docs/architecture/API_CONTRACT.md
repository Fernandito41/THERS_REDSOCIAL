# API_CONTRACT

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/API_CONTRACT.md` |
| Versión | 0.18 (Propuesta) |
| Estado | **Pendiente de ratificación formal del equipo** (proceso de decisiones de alto impacto, `HB-001` §11–12) |
| Depende de | `BACKEND_ARCHITECTURE.md` (fuente directa del estado real del backend), `DATABASE_ARCHITECTURE.md` (modelo de datos disponible), `FRONTEND_ARCHITECTURE.md` (consumidor del contrato), `HB-001` §15.1 (exige documentar cada endpoint el mismo día del PR) |
| Autoridad sobre este documento | `/docs` oficial > estructura real observada en el código > este documento (mismo orden que `CLAUDE.md` §3) |

> ⚠️ **Nota de estado.** Este documento nace de un hueco identificado en la auditoría arquitectónica integral de THERS: no existía ninguna fuente única de verdad para el contrato entre Frontend y Backend, pese a que `HB-001` §15.1 ya exige documentar cada endpoint el mismo día de su PR. `BACKEND_ARCHITECTURE.md` §14 declara explícitamente fuera de su propio alcance "el catálogo completo de endpoints" — este documento es esa pieza separada, y hasta ahora no existía ninguna.
>
> Sigue el mismo método que `BACKEND_ARCHITECTURE.md`, `DATABASE_ARCHITECTURE.md` y `FRONTEND_ARCHITECTURE.md` ya validaron: separa explícitamente **lo implementado** (un único endpoint real, con limitaciones conocidas) de **lo pendiente de definición** (formato de error estándar, convención de paginación, versionado de API, etc.). No se inventa aquí ningún endpoint, contrato o convención que el código o la documentación oficial no respalden todavía.
>
> Este documento no implementa, refactoriza ni modifica ningún código de `backend/` ni de `Frontend/`. Documenta el contrato tal como existe hoy y, donde falta una decisión, señala el hueco explícito — nunca un contrato inventado.
>
> **v0.2 — integración de autenticación con persistencia real:** `POST /api/register` pasó de "esperado pero no implementado" a **implementado** (§4.1), y `POST /api/login` se actualizó para consultar `users` real en vez de una credencial hardcodeada, incluyendo el cambio de `identity` del JWT de `email` a `user.id` (UUID). Reflejado en §4, §5, §6, §9. El Frontend (`Register.jsx`, `useAuth.js`) todavía no consume este contrato — esa integración queda fuera del alcance de esta tarea, que fue exclusivamente de backend.
>
> **v0.3 — perfil completo de registro + primer endpoint protegido (THERS Backend Fase 2.1, `ADR-002`):** `POST /api/register` ahora requiere también `username`, `phone`, `country_code`, `birth_date` y `confirm_password` (ratificado por `ADR-002-user-profile-fields.md`, que cierra la contradicción que `DATABASE_ARCHITECTURE.md` §4.B/§14 tenía registrada sobre estas columnas). `POST /api/login` expone los mismos campos nuevos en su respuesta. Se agrega `GET /api/users/me` — primer endpoint protegido del backend (`@jwt_required()`), documentado en §4.2. El Frontend (`Register.jsx`) ya recolecta estos campos pero todavía no los envía (comentario `TODO BACKEND` en el propio archivo) — esa integración sigue fuera de alcance, exclusivamente de backend igual que v0.2.
>
> **v0.4 — integración real del Frontend (THERS Frontend Fase 2.1):** `Register.jsx` ya envía el payload completo (`name`, `username`, `email`, `phone`, `country_code`, `birth_date`, `password`, `confirm_password`) — el comentario `TODO BACKEND` mencionado arriba fue removido. `AuthContext.jsx` reemplazó su restauración de sesión simulada (leer el último `user` guardado en `localStorage`) por una llamada real a `GET /api/users/me` con el JWT guardado, tanto al montar la aplicación como para toda lectura de la identidad actual; un `401`/`404` limpia la sesión local. Verificado end-to-end contra el backend real (`register` → `login` → `GET /api/users/me`, incluidos los casos sin token y con token inválido) — ver informe de la tarea para el detalle. No cambia ningún contrato de este documento, solo actualiza el estado de la integración del lado del Frontend.
>
> **v0.5 — actualización de perfil (THERS Backend, `ADR-003-profile-update-contract.md`):** se agrega `PATCH /api/users/me` (§4.2), primer endpoint de escritura protegido del backend. Permite actualizar `name`, `username`, `phone`+`country_code` y `birth_date` sobre `users` (mismas columnas que `GET /api/users/me` ya expone) — `email`/`password` quedan fuera por decisión explícita de `ADR-003`. `username` está sujeto a un cooldown de 30 días entre cambios (`users.username_changed_at`, migración `b2f4a19c3d7e`). El Frontend (`Profile.jsx`) todavía no consume este endpoint — sigue editando `bio`/`mood`/`interests`/`favoriteTrack` en `localStorage` y `name`/`username` con `updateStoredUser()`; conectar `Profile.jsx` a este contrato queda fuera de alcance de esta tarea, que fue exclusivamente de backend.
>
> **v0.6 — manejador global de errores (cierra §9 ítem 1):** `app/interfaces/error_handlers.py` (nuevo, `BACKEND_ARCHITECTURE.md` §11/§18/§19 v0.10) traduce cualquier `404`, `405`, otro `HTTPException` de Werkzeug (incluido un body no-JSON en `POST /api/register`/`POST /api/login`, que antes producía HTML) y cualquier excepción no controlada (`500`) al mismo formato `{"msg": "..."}` que ya usaban los 4 endpoints — **se mantiene ese formato sin cambios**, no se introduce `{"error": {...}}`, así que ningún endpoint existente cambia de contrato. Reflejado en §2 y §3. Verificado con 4 pruebas nuevas + la suite completa (56/56, ejecutada contra PostgreSQL 16 real).
>
> **v0.8 — primer endpoint de una entidad social real (`ADR-004-posts-minimal-model.md`):** se agrega `POST`/`GET /api/posts` (§4.3) — primera entidad del alcance objetivo del producto (`DATABASE_ARCHITECTURE.md` §4.B) en pasar a implementada, más allá de `users`. Modelo deliberadamente mínimo: solo texto, sin mood/imagen/hashtags/ubicación/reacciones/comentarios (cada uno queda para su propio ADR). Feed **global** — `GET /api/posts` devuelve posts de todos los autores, sin filtrar por `follows` (esa relación no existe todavía). El Frontend (`Home.jsx`, `CreateCapsuleFlow.jsx`) todavía no consume este contrato — sigue mostrando `mockCapsules`; conectar el Frontend queda fuera de alcance de esta tarea, que fue exclusivamente de backend. Verificado con 12 pruebas nuevas + la suite completa (71/71, ejecutada contra PostgreSQL 16 real, incluido un ciclo de `flask db upgrade`/`downgrade`).
>
> **v0.7 — validación de formato de `email` y longitud mínima de `password` en `POST /api/register` (cierra §9 ítem 2):** `domain/auth/validators.py` gana `is_valid_email()` (regex básica, sin verificar dominio real) e `is_valid_password()` (mínimo 8 caracteres, `MIN_PASSWORD_LENGTH`) — mismo patrón que los validadores ya existentes de `username`/`phone`/`country_code`/`birth_date`. Ambos umbrales son placeholders de producto explícitos y revisables (mismo criterio que `MIN_AGE_YEARS`, `ADR-002` §3), decididos como cambio técnico de bajo impacto (`HB-001` §11) por no alterar arquitectura, esquema ni ningún endpoint más allá de `register`. `POST /api/login` y `PATCH /api/users/me` **no cambian** — ninguno de los dos valida formato de credenciales (login no reformatea lo que ya existe; `PATCH` no permite editar `email`/`password`, `ADR-003`). Reflejado en §4.1 y §9. Verificado con 3 pruebas nuevas + la suite completa (59/59, ejecutada contra PostgreSQL 16 real).
>
> **v0.9 — corrección retroactiva de estado de integración del Frontend (este documento quedó desactualizado, no el código):** `Profile.jsx` (`feature/frontend-profile-page-redesign`, PR #43) ya consume `PATCH /api/users/me` para `name`/`username`, contradiciendo la nota de v0.5 de que "todavía no consume este endpoint" — `bio`/`mood`/`interests`/`favoriteTrack` siguen en `localStorage`, correctamente, porque esas columnas no están ratificadas (`DATABASE_ARCHITECTURE.md` §4.B). El feed (`AppShell.jsx`, `feature/frontend-feed-posts-integration`, PR #39) ya consume `GET`/`POST /api/posts` en vez de `mockCapsules`, contradiciendo la nota de v0.8. Ninguno de los dos contratos cambió — solo se corrige el estado de integración documentado, que no se había actualizado el mismo día de esos PRs (`HB-001` §15.1).
>
> **v0.10 — likes sobre posts (`ADR-005-likes-minimal-model.md`):** se agregan `POST`/`DELETE /api/posts/<post_id>/like` (§4.4) — segunda entidad del alcance objetivo del producto (`DATABASE_ARCHITECTURE.md` §4.B, candidata `reactions`) en pasar a implementada, en su versión mínima binaria (like/no-like, sin tipos de reacción). `GET`/`POST /api/posts` se extienden de forma aditiva con `likes_count`/`liked_by_me` (§4.3, §5) — no rompen el contrato existente. Ambos endpoints nuevos son idempotentes por diseño (§4.4). El Frontend (`CapsuleCard.jsx`) ya consume este contrato en la misma tarea. Verificado con 18 pruebas nuevas + la suite completa (89/89, ejecutada contra PostgreSQL 16 real, incluido un ciclo de `flask db upgrade` sobre `thers_dev` y `thers_test`).
>
> **v0.11 — comentarios sobre posts (`ADR-006-comments-minimal-model.md`):** se agregan `POST`/`GET /api/posts/<post_id>/comments` (§4.5) — tercera entidad del alcance objetivo del producto (`DATABASE_ARCHITECTURE.md` §4.B, candidata combinada "Comentarios + Respuestas") en pasar a implementada, solo en su mitad plana: comentar un post, sin hilos de respuestas. `GET`/`POST /api/posts` se extienden de forma aditiva con `comments_count` (§4.3, §5), sumado a `likes_count`/`liked_by_me` de v0.10 — no rompen el contrato existente. A diferencia del feed, el listado de comentarios va en orden cronológico ascendente (§4.5). El Frontend (`CapsuleCard.jsx`) ya consume este contrato en la misma tarea — panel expandible que carga el hilo bajo demanda (`GET .../comments` al abrirse, no precargado con el feed) y publica comentarios nuevos (`POST .../comments`). Verificado con 22 pruebas nuevas + la suite completa (93/93, ejecutada contra PostgreSQL 16 real, incluido un ciclo de `flask db upgrade` sobre `thers_dev` y `thers_test`), más una prueba manual end-to-end contra el backend real.
>
> **v0.12 — seguir/dejar de seguir usuarios (`ADR-007-follows-minimal-model.md`):** se agregan `POST`/`DELETE /api/users/<user_id>/follow` (§4.6) — cuarta entidad del alcance objetivo del producto (`DATABASE_ARCHITECTURE.md` §4.B, candidata `follows`) en pasar a implementada. `GET`/`PATCH /api/users/me` se extienden con `followers_count`/`following_count` (§4.2, §5); `GET`/`POST /api/posts` se extienden con `author.is_followed_by_me` (§4.3, §5) — ninguna rompe el contrato existente. El feed **sigue global**, no se personaliza por seguidos (`ADR-007` §No objetivos — decisión de producto separada, no un efecto colateral de este ADR). El Frontend ya consume este contrato en la misma tarea: `CapsuleCard.jsx` gana "Seguir"/"Siguiendo" sobre el autor de un post real, `Profile.jsx` muestra `followers_count`/`following_count` reales. El panel de sugerencias mock de `Home.jsx` no se toca — sus personas no son usuarios reales. Verificado con 17 pruebas nuevas + la suite completa (124/124, ejecutada contra PostgreSQL 16 real, incluido un ciclo de `flask db upgrade` sobre `thers_dev` y `thers_test`), más una prueba manual end-to-end contra el backend real.
>
> **v0.15 — recuperación de contraseña por código OTP de 6 dígitos (`ADR-010-password-reset-otp-flow.md`, reemplaza el flujo de enlace de v0.14):** `POST /api/forgot-password` deja de generar un enlace y genera un código de 6 dígitos (también sirve como "Reenviar código"); se agrega `POST /api/verify-reset-code` (§4.8) que verifica el código y devuelve una autorización temporal de propósito específico (nunca un JWT de sesión); `POST /api/reset-password` cambia su body de `token` a `reset_authorization`. Protecciones nuevas: máximo 5 intentos por solicitud, hashing scrypt del código (no SHA-256, por su baja entropía), índice único parcial que garantiza a lo sumo un código activo por usuario incluso ante reenvíos simultáneos. `send-verification-email`/`verify-email` **no cambian** — siguen exactamente como en v0.14. El Frontend queda conectado de punta a punta: `ForgotPassword.jsx` (sin conectar hasta ahora), nueva pantalla `VerifyResetCode.jsx`, `ResetPassword.jsx` adaptada. Verificado con 31 pruebas nuevas + la suite completa (189/189, ejecutada contra PostgreSQL 16 real, incluido un ciclo de `flask db upgrade` sobre `thers_dev` y `thers_test`), más una prueba manual end-to-end contra el backend real (código incorrecto, código correcto, autorización de un solo uso, login con la contraseña nueva).
>
> **v0.17 — "Continuar con Google" (`ADR-012-google-sign-in.md`):** se agrega `POST /api/auth/google` (§4.9) — método de autenticación **adicional**, no reemplaza `register`/`login` tradicional. Recibe `{credential}` (ID Token de Google Identity Services), lo verifica criptográficamente (firma/`iss`/`aud`/`exp`, librería oficial `google-auth`), y crea/vincula/loguea según corresponda; nunca confía en datos que el Frontend diga que vienen de Google. `users` relaja `phone`/`country_code`/`birth_date`/`password_hash` a nullable (Google no entrega los primeros tres, y una cuenta Google-only no tiene contraseña local) — `register`/`login` tradicional siguen exigiendo todo igual que siempre, sin cambio de comportamiento. El objeto `user` (§5) gana `profile_completed` (si falta completar `phone`/`country_code`/`birth_date`, reutiliza `PATCH /api/users/me` sin endpoint nuevo) y `has_password` (booleano derivado). Account linking con una cuenta tradicional del mismo email: se vincula automático si esa cuenta ya estaba verificada, se "reclama" (anulando cualquier contraseña existente) si nunca se verificó — nunca por la sola coincidencia del email sin esa garantía. Una cuenta Google-only puede fijar su primera contraseña reutilizando `forgot-password`/`verify-reset-code`/`reset-password` (`ADR-010`) sin ningún cambio de código ahí. Verificado con 30 pruebas nuevas (`test_google_id_token_verifier.py` + `test_google_auth.py`, Google mockeado — nunca llamadas reales) + la suite completa (242/242, ejecutada contra PostgreSQL 16 real, incluido un ciclo de `flask db upgrade` sobre `thers_dev` y `thers_test`).
>
> **v0.16 — verificación obligatoria de email al registrarse (`ADR-011-mandatory-email-verification.md`, reemplaza `send-verification-email`/`verify-email` de v0.14):** `POST /api/register` (§4.1) sigue devolviendo `201` con el usuario creado, pero ahora `email_verified` nace en `false` y de inmediato se envía un código de 6 dígitos — la cuenta no puede iniciar sesión todavía. Registrar de nuevo con un email que existe pero nunca se verificó **actualiza esa misma cuenta** (incluida la contraseña) y reenvía un código, en vez de un `409` — el `409` real solo ocurre si el email ya pertenece a una cuenta verificada. `POST /api/login` (§4.1) gana un caso nuevo: credenciales correctas pero cuenta sin verificar responde `403` con `{"msg": "...", "email_verified": false}`, sin emitir ningún JWT. Se agregan `POST /api/verify-registration-code` y `POST /api/resend-registration-code` (§4.8) — mismo patrón que `verify-reset-code`/`forgot-password` (`ADR-010`): 6 dígitos, hash scrypt, máximo 5 intentos, cooldown de 60s, índice único parcial (a lo sumo un código activo por usuario). Un código de registro nunca sirve para verificar una recuperación de contraseña ni viceversa — viven en tablas/repositorios completamente separados, no un discriminador de tipo sobre una tabla compartida. **Se retiran** `POST /api/send-verification-email` y `POST /api/verify-email` (`ADR-009`, flujo de enlace) — con el login ya bloqueado para cuentas sin verificar, una cuenta sin verificar nunca puede obtener el JWT que el primero exigía, dejando ambos permanentemente inalcanzables. El Frontend queda conectado de punta a punta: `Register.jsx` navega a la nueva pantalla `VerifyRegistrationCode.jsx` en vez de a `/login`; `Login.jsx` distingue el `403` de cuenta sin verificar y redirige a la misma pantalla. Verificado con 36 pruebas nuevas (`test_registration.py`, reemplaza a `test_email_verification.py`) + la suite completa (212/212, ejecutada contra PostgreSQL 16 real, incluido un ciclo de `flask db upgrade` sobre `thers_dev` y `thers_test`).
>
> **v0.14 — recuperación de contraseña y verificación de email vía Resend (`ADR-009-password-reset-and-email-verification.md`):** se agregan `POST /api/forgot-password`, `POST /api/reset-password`, `POST /api/send-verification-email` y `POST /api/verify-email` (§4.8) — séptima y octava entidad del alcance objetivo del producto (`DATABASE_ARCHITECTURE.md` §4.B, candidata "Verificación de correo, Recuperación de contraseña") en pasar a implementadas. Rutas planas bajo `/api`, sin prefijo `/auth/` — mismo criterio que `/api/register`/`/api/login`. `forgot-password` nunca revela si un email está registrado (mismo mensaje `200` siempre); `reset-password`/`verify-email` usan tokens de un solo uso, expirables, con hash SHA-256 persistido (nunca el valor crudo). `GET`/`PATCH /api/users/me` y `register`/`login` se extienden de forma aditiva con `email_verified` (§4.2, §5) — no rompe el contrato existente. Nuevo servicio de correo centralizado (Resend, SDK oficial) detrás de un `EmailSender` abstracto — ningún endpoint llama a Resend directamente. Verificado con 30 pruebas nuevas + la suite completa (175/175, ejecutada contra PostgreSQL 16 real, incluido un ciclo de `flask db upgrade` sobre `thers_dev` y `thers_test`), más una prueba manual end-to-end contra el backend real (los cuatro endpoints, con `NullEmailSender` en desarrollo sin `RESEND_API_KEY`).
>
> **v0.18 — mensajes directos (`ADR-013-messages-minimal-model.md`):** se agregan `POST`/`GET /api/users/<user_id>/messages` y `GET /api/conversations` (§4.10) — décima entidad del alcance objetivo del producto (`DATABASE_ARCHITECTURE.md` §4.B, candidata `conversations`+`messages`) en pasar a implementada, solo en su mitad 1:1: mensaje directo entre dos usuarios reales, sin conversaciones grupales ni tabla `conversation_participants`. `GET .../messages` marca como leídos, como efecto secundario, los mensajes recibidos de esa persona — no hay un `PATCH .../read` separado (`ADR-013` §Opciones consideradas). Sin tiempo real: el Frontend refresca por *polling*, mismo criterio que `ADR-008` para notificaciones. Ningún endpoint existente cambia de contrato. El Frontend queda conectado en la misma tarea: `Messages.jsx` deja de estar vacío y consume `GET /api/conversations`/`GET .../messages`; `unreadMessages` de `Sidebar`/`Topbar` pasa a sumar `unread_count` real en vez de quedar en `0`. Verificado con 21 pruebas nuevas + la suite completa (263/263, ejecutada contra PostgreSQL 16 real, incluido un ciclo de `flask db upgrade` sobre `thers_dev` y `thers_test`).
>
> **v0.13 — notificaciones (`ADR-008-notifications-minimal-model.md`):** se agregan `GET /api/notifications` y `PATCH /api/notifications/<id>/read` (§4.7) — sexta entidad del alcance objetivo del producto (`DATABASE_ARCHITECTURE.md` §4.B, candidata `notifications`) en pasar a implementada. Cubre solo los tres eventos que el backend ya sabe generar: dar like a un post (`ADR-005`), comentarlo (`ADR-006`) y seguir a un usuario (`ADR-007`) — nunca al propio actor sobre su propio contenido, y nunca duplicada por una repetición idempotente de un like/follow ya existente (`ADR-008` §Opciones consideradas). `POST /api/posts/<id>/like`, `POST /api/posts/<id>/comments` y `POST /api/users/<id>/follow` **no cambian su contrato** — la notificación es un efecto secundario invisible en la respuesta de quien dispara la acción. El Frontend ya consume este contrato en la misma tarea: `AppShell.jsx` reemplaza `mockNotifications` por `GET /api/notifications` (mismo patrón que `capsules`/`posts`, `ADR-004`) y `handleMarkRead`/`handleMarkAllRead` llaman a `PATCH .../read` con optimistic update (mismo patrón que `handleToggleLike`, `ADR-005`); sin endpoint de "marcar todas" en el backend (`ADR-008` §No objetivos), `handleMarkAllRead` itera sobre las no leídas. Verificado con 21 pruebas nuevas + la suite completa (145/145, ejecutada contra PostgreSQL 16 real, incluido un ciclo de `flask db upgrade` sobre `thers_dev` y `thers_test`), más una prueba manual end-to-end contra el backend real con dos usuarios reales generando los tres tipos de evento.

---

## 1. Propósito y alcance

**Propósito.** Ser la única fuente de verdad del contrato HTTP entre `Frontend/` y `backend/`: qué endpoints existen, qué reciben, qué devuelven, cómo se autentican y cómo se comunican los errores — de modo que Backend y Frontend puedan implementar en paralelo contra el mismo contrato acordado, en vez de negociarlo ad-hoc en cada feature (que es lo que ha ocurrido hasta ahora: `Register.jsx` ya asume un endpoint `/register` que el backend no expone).

**Alcance.** Cubre exclusivamente el contrato HTTP expuesto por `backend/` bajo el prefijo `/api` y consumido por `Frontend/` a través de `shared/lib/api.js`. Incluye: catálogo de endpoints, formato de request/response, autenticación, formato de error, códigos HTTP y convenciones para endpoints futuros.

**Fuera de alcance de este documento:**
- Implementación interna del backend (capas `domain/`, `application/`, `interfaces/`) — cubierta por `BACKEND_ARCHITECTURE.md`.
- Modelo de datos y persistencia — cubierto por `DATABASE_ARCHITECTURE.md`.
- Cómo el Frontend consume el contrato internamente (hooks, componentes, estado) — cubierto por `FRONTEND_ARCHITECTURE.md`.
- Especificación formal OpenAPI/Swagger — se evalúa como evolución futura (§10), no se adopta en esta versión por ser desproporcionado frente a un único endpoint real (principio de simplicidad, mismo criterio que `FAS-001` §2 aplica por analogía en los otros documentos de THERS).
- Autorización por roles/permisos — no existe ningún concepto de rol en el sistema hoy (`BACKEND_ARCHITECTURE.md` §9); no se inventa aquí.

---

## 2. Convenciones generales

| Aspecto | Estado |
|---|---|
| Prefijo base | `/api` — todos los blueprints se registran bajo este prefijo (`create_app()`, `url_prefix="/api"`) |
| Formato de body | JSON exclusivamente, en request y response (`request.get_json()` / `jsonify(...)`) — sin excepción observada en el código actual |
| Autenticación | `Bearer <jwt>` en el header `Authorization` — **v0.3: ya verificada contra un endpoint protegido real** (`GET /api/users/me`, §4.2), usando `@jwt_required()`/`get_jwt_identity()` de `flask_jwt_extended` |
| Verbos HTTP | Declarados explícitamente por ruta (`methods=["POST"]`); **no hay convención documentada** todavía para operaciones futuras (GET de colección, PUT/PATCH de actualización, DELETE) — `PENDIENTE DE APROBACIÓN` (§9) |
| Versionado de API | **No existe.** No hay prefijo de versión (`/api/v1`) ni ningún mecanismo de versionado — `PENDIENTE DE APROBACIÓN` (§9) |
| Paginación | **No existe.** Ningún endpoint actual devuelve una colección — `PENDIENTE DE APROBACIÓN` (§9) |
| CORS | Habilitado globalmente sin restricción de origen (`CORS(app)`, `BACKEND_ARCHITECTURE.md` §13) — responsabilidad del backend, el Frontend no la controla |
| Manejo global de errores | **v0.6 — implementado.** `app/interfaces/error_handlers.py` (`BACKEND_ARCHITECTURE.md` §11/§18/§19) captura cualquier error no anticipado por una route específica (`404`, `405`, otros `HTTPException`, `500`) y responde con el mismo formato que el resto de la API — ver §3 |

---

## 3. Formato de error

**v0.6 — ya aplicado de forma uniforme a toda la API, no solo observado en un endpoint:**

```json
{ "msg": "<texto del error>" }
```

- Usado para validación fallida (`400`), credenciales inválidas (`401`), recurso no encontrado (`404`), conflicto de unicidad (`409`) — construidos explícitamente por cada route — **y ahora también** para cualquier error no anticipado por ninguna route: `404`/`405` genéricos, cualquier otro `HTTPException` de Werkzeug (p. ej. un body no-JSON en `POST /api/register`/`POST /api/login`, que antes de v0.6 producía HTML en vez de este formato) y `500` (excepción no controlada) — `app/interfaces/error_handlers.py`, `BACKEND_ARCHITECTURE.md` §11.
- No hay campo de código de error machine-readable, ni estructura anidada (`{"error": {"code": ..., "message": ...}}`) — decisión deliberada de v0.6: mantener el contrato existente en vez de introducir uno nuevo sin necesidad demostrada.
- **v0.6 — resuelto.** Ya existe un manejador global de excepciones (`@app.errorhandler`, vía `register_error_handlers()`) registrado en `create_app()` — un `500` o `404` no manejado responde `{"msg": "..."}`, nunca el comportamiento HTML por defecto de Flask. El `500` nunca expone traceback, tipo de excepción, ni datos sensibles (`DATABASE_URL`, `JWT_SECRET_KEY`) — verificado por prueba (`backend/tests/test_error_handlers.py`).

Sigue **`PENDIENTE DE APROBACIÓN`** (§9, degradado de prioridad tras v0.6): si el equipo quiere evolucionar `{"msg": "..."}` hacia un formato con código de error machine-readable — no hay ninguna necesidad actual que lo justifique, este documento no lo propone por iniciativa propia.

---

## 4. Catálogo de endpoints

### 4.1 Implementados

#### `POST /api/register`

| Campo | Valor |
|---|---|
| Estado | **IMPLEMENTADO** — semántica ampliada por `ADR-011-mandatory-email-verification.md`: la cuenta se crea sin verificar y no puede iniciar sesión hasta completar `POST /api/verify-registration-code` (§4.8) |
| Blueprint | `auth_bp` (`backend/app/interfaces/routes/auth_routes.py`) |
| Auth requerida | No (endpoint público) |

**Request body**
```json
{
  "name": "string",
  "username": "string",
  "email": "string",
  "phone": "string",
  "country_code": "string",
  "birth_date": "string (ISO yyyy-mm-dd)",
  "password": "string",
  "confirm_password": "string"
}
```

**Response — éxito (201)**
```json
{
  "user": {
    "id": "string (UUID)",
    "username": "string",
    "email": "string",
    "name": "string",
    "phone": "string | null",
    "country_code": "string | null",
    "birth_date": "string (ISO yyyy-mm-dd) | null",
    "followers_count": "integer",
    "following_count": "integer",
    "email_verified": "boolean",
    "profile_completed": "boolean",
    "has_password": "boolean"
  }
}
```

**Response — error**

| Código | Causa | Body |
|---|---|---|
| `400` | Body vacío; alguno de `name`/`username`/`email`/`phone`/`country_code`/`birth_date`/`password`/`confirm_password` ausente; `email` con formato inválido; `password` ≠ `confirm_password`; `password` con menos de 8 caracteres; `username`/`phone`/`country_code`/`birth_date` con formato inválido; edad menor a 13 años | `{"msg": "..."}` |
| `409` | Ya existe una cuenta **verificada** con ese email (comparación case-insensitive, `CITEXT`) **o** con ese username | `{"msg": "..."}` |

**Notas de implementación:**
- `password_hash` se genera con `werkzeug.security.generate_password_hash` (scrypt) — nunca se persiste ni se devuelve la contraseña en claro.
- `id` lo genera PostgreSQL (`gen_random_uuid()`), nunca Python (`DATABASE_ARCHITECTURE.md` §5).
- `confirm_password` se valida (debe coincidir con `password`) y **nunca se persiste** — no existe como columna de `users`.
- Formato validado en el backend (`domain/auth/validators.py`, ver `ADR-002` §3): `username` (`^[a-zA-Z0-9_]{3,20}$`), `phone` (7–15 dígitos), `country_code` (`^\+[1-9]\d{0,3}$`), `birth_date` (ISO válida + edad mínima 13 años).
- **v0.7 — resuelto:** `email` (regex básica `^[^\s@]+@[^\s@]+\.[^\s@]+$`, sin verificar dominio real) y `password` (mínimo `MIN_PASSWORD_LENGTH = 8` caracteres, sin exigir mayúscula/número/símbolo) — ambos placeholders de producto explícitos, revisables (mismo criterio que `MIN_AGE_YEARS`).
- **v0.16 — verificación obligatoria de email (`ADR-011-mandatory-email-verification.md`):** `email_verified` nace en `false`; el registro envía de inmediato un código de 6 dígitos por correo (mismo mecanismo que `verify-reset-code`, §4.8) y la cuenta no puede usar `POST /api/login` hasta verificarlo. Registrar de nuevo con un email que existe pero **nunca** se verificó actualiza esa misma fila (incluida la contraseña) y reenvía un código — no produce un `409` ni una fila duplicada; el `409` de email solo ocurre contra una cuenta ya verificada. La prueba definitiva de que la cuenta controla el correo es siempre el código OTP — el formato de `email` se valida, pero un dominio/formato con buena forma nunca se trata como verificación por sí solo.
- **v0.17 (`ADR-012-google-sign-in.md`):** este contrato de `POST /api/register` **no cambia** — sigue exigiendo `phone`/`country_code`/`birth_date`/`password`/`confirm_password` igual que siempre. La relajación a nullable de esas columnas en `users` (§5, `DATABASE_ARCHITECTURE.md`) es exclusiva de cuentas creadas vía `POST /api/auth/google` (§4.9) — el registro tradicional nunca las deja en `NULL` en la práctica.

#### `POST /api/login`

| Campo | Valor |
|---|---|
| Estado | **IMPLEMENTADO** — gana un caso de rechazo nuevo en `ADR-011-mandatory-email-verification.md`: cuenta sin verificar (§Cambios respecto a la versión anterior de este documento) |
| Blueprint | `auth_bp` (`backend/app/interfaces/routes/auth_routes.py`) |
| Auth requerida | No (endpoint público — emite el token) |

**Request body**
```json
{
  "email": "string",
  "password": "string"
}
```

**Response — éxito (200)**
```json
{
  "token": "string (JWT)",
  "user": {
    "id": "string (UUID)",
    "username": "string",
    "email": "string",
    "name": "string",
    "phone": "string | null",
    "country_code": "string | null",
    "birth_date": "string (ISO yyyy-mm-dd) | null",
    "followers_count": "integer",
    "following_count": "integer",
    "email_verified": "boolean",
    "profile_completed": "boolean",
    "has_password": "boolean"
  }
}
```

**Response — error**

| Código | Causa | Body |
|---|---|---|
| `400` | Body vacío, o `email`/`password` ausentes | `{"msg": "..."}` |
| `401` | Credenciales inválidas — email inexistente **o** contraseña incorrecta, mismo mensaje en ambos casos deliberadamente, para no permitir enumerar emails registrados | `{"msg": "..."}` |
| `403` | Email y contraseña correctos, pero la cuenta todavía no completó la verificación obligatoria de email (`ADR-011-mandatory-email-verification.md`) — se distingue deliberadamente de `401` porque la contraseña sí era correcta; el chequeo ocurre **después** de validar la contraseña, nunca antes, para no abrir un canal lateral nuevo. Nunca se emite un JWT en este caso | `{"msg": "Tu correo electrónico todavía no fue verificado.", "email_verified": false}` |

**Cambios respecto a la versión anterior de este documento:**
- La validación ya **no** compara contra una credencial hardcodeada — consulta la tabla `users` real vía `SQLAlchemyUserRepository` (`backend/app/infrastructure/persistence/repositories/user_repository.py`).
- El objeto `user` devuelto ahora incluye también `username`, `phone`, `country_code`, `birth_date` (`ADR-002`).
- **`identity` del JWT cambió de `email` a `user.id` (UUID, como string)** — cualquier endpoint protegido usa `get_jwt_identity()` y recibe un UUID de `users.id`, no un email. Ver `BACKEND_ARCHITECTURE.md` §9.
- El token sigue sin política de expiración explícita configurada (`PENDIENTE DE APROBACIÓN`, sin cambios en esta tarea).
- **v0.16:** nuevo caso `403` para cuenta sin verificar (`ADR-011-mandatory-email-verification.md` §Decisión) — `email_verified: false` explícito en el body (no solo en el mensaje) para que el Frontend lo distinga sin parsear texto y redirija a `POST /api/verify-registration-code` (§4.8).

### 4.2 Endpoints protegidos

#### `GET /api/users/me`

| Campo | Valor |
|---|---|
| Estado | **IMPLEMENTADO** — nuevo (THERS Backend Fase 2.1, `ADR-002` §3) |
| Blueprint | `users_bp` (`backend/app/interfaces/routes/user_routes.py`) |
| Auth requerida | **Sí** — `Bearer <jwt>` en el header `Authorization`. Identidad obtenida exclusivamente de `get_jwt_identity()` (`@jwt_required()`) — nunca de query string, body ni headers personalizados |

**Request:** sin body. Header `Authorization: Bearer <token>` obligatorio.

**Response — éxito (200)**
```json
{
  "user": {
    "id": "string (UUID)",
    "username": "string",
    "email": "string",
    "name": "string",
    "phone": "string | null",
    "country_code": "string | null",
    "birth_date": "string (ISO yyyy-mm-dd) | null",
    "followers_count": "integer",
    "following_count": "integer",
    "email_verified": "boolean",
    "profile_completed": "boolean",
    "has_password": "boolean"
  }
}
```

**Response — error**

| Código | Causa | Body |
|---|---|---|
| `401` | Falta el header `Authorization`, el token es inválido/está malformado, o expiró | `{"msg": "..."}` |
| `404` | El `id` del JWT no corresponde a ningún usuario real (p. ej. la cuenta fue eliminada después de emitirse el token) | `{"msg": "..."}` |

**Notas de implementación:**
- Primer endpoint protegido real del backend — fija el patrón que `BACKEND_ARCHITECTURE.md` §9/§14 señalaba como ausente.
- `flask_jwt_extended` distingue por defecto entre `401` (token ausente/expirado) y `422` (token malformado); se homogenizaron los tres casos a `401` con callbacks en `app/extensions.py` (`unauthorized_loader`/`invalid_token_loader`/`expired_token_loader`), para que cualquier endpoint protegido futuro herede el mismo comportamiento sin repetirlo.
- Nunca expone `password`, `password_hash`, `confirm_password`, `token` ni `secret` en la respuesta.
- `followers_count`/`following_count` agregados en v0.12 (`ADR-007-follows-minimal-model.md`, §4.6) — siempre reales para el usuario autenticado. En `POST /api/register`/`POST /api/login` estos mismos campos también viajan, siempre en `0`: una cuenta recién creada no puede tener seguidores/seguidos todavía.
- `email_verified` agregado en v0.14 (`ADR-009-password-reset-and-email-verification.md`, §4.8) — `false` en toda cuenta hasta que se complete `POST /api/verify-email`. A diferencia de `followers_count`/`following_count`, se lee directo de la columna (`users.email_verified`), sin consulta agregada aparte.

#### `PATCH /api/users/me`

| Campo | Valor |
|---|---|
| Estado | **IMPLEMENTADO** — nuevo (THERS Backend, `ADR-003-profile-update-contract.md`) |
| Blueprint | `users_bp` (`backend/app/interfaces/routes/user_routes.py`), mismo blueprint que `GET /api/users/me` |
| Auth requerida | **Sí** — `Bearer <jwt>` en el header `Authorization`. Identidad obtenida exclusivamente de `get_jwt_identity()` (`@jwt_required()`) — nunca de query string, body ni headers personalizados. El `user_id` del JWT es siempre el sujeto de la operación, no hay forma de editar el perfil de otro usuario |

**Semántica.** Actualización parcial real (PATCH, no un PUT disfrazado): solo los campos presentes en el body se modifican, los omitidos no se tocan. Un único `db.session.commit()` por request — si varios campos vienen en el mismo `PATCH`, se persisten todos o ninguno. Campos no reconocidos en el body se ignoran silenciosamente — nunca se leen ni se pasan al modelo (whitelist explícita en la route, sin `**data`, sin mass assignment).

**Request body** — todos los campos son opcionales, pero debe llegar al menos uno de la whitelist:
```json
{
  "name": "string (opcional)",
  "username": "string (opcional, máx. 1 cambio cada 30 días)",
  "phone": "string (opcional, requiere country_code en el mismo body)",
  "country_code": "string (opcional, requiere phone en el mismo body)",
  "birth_date": "string ISO yyyy-mm-dd (opcional)"
}
```

Ejemplo mínimo válido — cambiar solo el nombre:
```json
{ "name": "Fernando" }
```

**Campos NO editables por este endpoint** (ADR-003 §Campos editables): `id`, `email`, `password`/`password_hash`, `created_at`, `updated_at` — nunca se leen del body, bajo ninguna circunstancia. `bio`/`avatar_url` no existen todavía como columnas (`DATABASE_ARCHITECTURE.md` §4.B) — no forman parte de este contrato.

**Response — éxito (200)** — mismo objeto público que `GET /api/users/me`, `register` y `login`:
```json
{
  "user": {
    "id": "string (UUID)",
    "username": "string",
    "email": "string",
    "name": "string",
    "phone": "string | null",
    "country_code": "string | null",
    "birth_date": "string (ISO yyyy-mm-dd) | null",
    "followers_count": "integer",
    "following_count": "integer",
    "email_verified": "boolean",
    "profile_completed": "boolean",
    "has_password": "boolean"
  }
}
```

**Response — error**

| Código | Causa | Body |
|---|---|---|
| `400` | Body vacío o sin ningún campo whitelisted; valor vacío/`null`/formato inválido en `name`/`username`/`phone`/`country_code`/`birth_date`; `phone` sin `country_code` o viceversa; edad resultante < 13 años; `username` cambiado antes de que se cumplan 30 días desde el último cambio (`ADR-003` dejaba el código exacto "a definir en la implementación" entre `400`/`429` — se usa `400` para mantenerse dentro del catálogo de códigos ya documentado en este contrato, sin introducir `429`) | `{"msg": "..."}` |
| `401` | Falta el header `Authorization`, el token es inválido/está malformado, o expiró — mismos callbacks homogenizados que `GET /api/users/me` | `{"msg": "..."}` |
| `404` | El `id` del JWT no corresponde a ningún usuario real | `{"msg": "..."}` |
| `409` | Conflicto de unicidad de `username` (constraint `uq_users_username`) — mismo patrón de `IntegrityError` → excepción de dominio que `POST /api/register` ya usa | `{"msg": "..."}` |

**Notas de implementación:**
- Un `username` igual al actual **no** se trata como un cambio real: no actualiza `username_changed_at` ni consume la ventana de 30 días (`ADR-003` §5).
- `phone`/`country_code` se tratan como un único dato lógico — deben enviarse juntos en el mismo body si se quiere modificar cualquiera de los dos.
- Reutiliza los mismos validadores de formato que `POST /api/register` (`domain/auth/validators.py`) — sin reglas nuevas de formato, solo se aplican también aquí.
- Nunca expone `password`, `password_hash`, `confirm_password`, `token` ni `secret` en la respuesta (reutiliza `to_public_user()`, la misma función que `register`/`login`/`me`).
- `username_changed_at` no forma parte de la respuesta pública — es un dato interno que solo sostiene la regla de cooldown (`DATABASE_ARCHITECTURE.md` §5).

---

### 4.3 Contenido

#### `POST /api/posts`

| Campo | Valor |
|---|---|
| Estado | **IMPLEMENTADO** — nuevo (`ADR-004-posts-minimal-model.md`) |
| Blueprint | `posts_bp` (`backend/app/interfaces/routes/post_routes.py`) |
| Auth requerida | **Sí** — `Bearer <jwt>` en el header `Authorization`. `author_id` se obtiene exclusivamente de `get_jwt_identity()` — nunca del body |

**Semántica.** Crea un post de **solo texto** — primer endpoint de una entidad social real del producto, deliberadamente mínimo (`ADR-004` §No objetivos): sin mood, imagen, hashtags, ubicación, reacciones ni comentarios en esta versión.

**Request body**
```json
{ "content": "string (1–2000 caracteres tras trim)" }
```

**Response — éxito (201)**
```json
{
  "post": {
    "id": "string (UUID)",
    "author": {
      "id": "string (UUID)",
      "username": "string",
      "name": "string",
      "is_followed_by_me": "boolean"
    },
    "content": "string",
    "created_at": "string (ISO 8601)",
    "likes_count": "integer",
    "liked_by_me": "boolean",
    "comments_count": "integer"
  }
}
```
`likes_count`/`liked_by_me` agregados en v0.10 (`ADR-005-likes-minimal-model.md`, §4.4); `comments_count` agregado en v0.11 (`ADR-006-comments-minimal-model.md`, §4.5) — un post recién creado siempre los devuelve en `0`/`false`, nadie pudo haberle dado like ni comentado todavía. `author.is_followed_by_me` agregado en v0.12 (`ADR-007-follows-minimal-model.md`, §4.6) — en `false` para un post recién creado, porque el autor es siempre uno mismo y nadie se sigue a sí mismo (`ck_follows_no_self_follow`).

**Response — error**

| Código | Causa | Body |
|---|---|---|
| `400` | Body vacío; `content` ausente, vacío tras `trim()`, o mayor a 2000 caracteres | `{"msg": "..."}` |
| `401` | Falta el header `Authorization`, el token es inválido/está malformado, o expiró — mismos callbacks homogenizados que el resto de endpoints protegidos | `{"msg": "..."}` |

**Notas de implementación:**
- Whitelist explícita: solo `content` se lee del body — nunca `author_id`/`id`/`created_at` (mismo principio anti mass-assignment que `PATCH /api/users/me`, `ADR-003` §Seguridad; verificado por prueba).
- El objeto `author` reutiliza una forma reducida del mismo `to_public_user`-style presenter — nunca expone `email`, `phone`, `password_hash` ni otros campos privados del autor.

#### `GET /api/posts`

| Campo | Valor |
|---|---|
| Estado | **IMPLEMENTADO** — nuevo (`ADR-004-posts-minimal-model.md`) |
| Blueprint | `posts_bp`, mismo blueprint que `POST /api/posts` |
| Auth requerida | **Sí** — mismo criterio que el resto del feed hoy: solo alcanzable desde rutas protegidas del Frontend (`ProtectedRoute`, `FRONTEND_ARCHITECTURE.md` §7) |

**Semántica.** Feed **global**: devuelve los posts de **todos** los autores, no solo de quienes el usuario sigue. `follows` ya existe (`ADR-007-follows-minimal-model.md`), pero este endpoint **sigue sin filtrar por seguidos** — personalizar el feed es una decisión de producto separada, deliberadamente fuera de alcance de `ADR-007` (§No objetivos). Sin paginación real: límite fijo de **50** posts más recientes.

**Request:** sin body. Header `Authorization: Bearer <token>` obligatorio.

**Response — éxito (200)**
```json
{ "posts": [ { "id", "author": { "id", "username", "name", "is_followed_by_me" }, "content", "created_at", "likes_count", "liked_by_me", "comments_count" }, ... ] }
```
Orden: `created_at` descendente (más reciente primero). Lista vacía (`[]`) si no hay posts. `likes_count`/`liked_by_me` (v0.10), `comments_count` (v0.11) y `author.is_followed_by_me` (v0.12) son extensiones aditivas — no rompen el contrato existente.

**Response — error**

| Código | Causa | Body |
|---|---|---|
| `401` | Falta el header `Authorization`, el token es inválido/está malformado, o expiró | `{"msg": "..."}` |

---

### 4.4 Likes

#### `POST /api/posts/<post_id>/like`

| Campo | Valor |
|---|---|
| Estado | **IMPLEMENTADO** — nuevo (`ADR-005-likes-minimal-model.md`) |
| Blueprint | `likes_bp` (`backend/app/interfaces/routes/like_routes.py`) |
| Auth requerida | **Sí** — `Bearer <jwt>` en el header `Authorization`. Quién da el like se obtiene exclusivamente de `get_jwt_identity()` — nunca del body |

**Semántica.** Da like al post `post_id` en nombre del usuario autenticado. **Idempotente**: repetir la llamada no falla ni duplica el like (`ADR-005` §Decisión, Opción A) — pensado para que el Frontend no tenga que distinguir "primer like" de "doble tap accidental".

**Request:** sin body. `post_id` va en la URL, como UUID (conversor `uuid` de Flask/Werkzeug).

**Response — éxito (200)**
```json
{ "likes_count": "integer", "liked_by_me": true }
```

**Response — error**

| Código | Causa | Body |
|---|---|---|
| `401` | Falta el header `Authorization`, el token es inválido/está malformado, o expiró | `{"msg": "..."}` |
| `404` | `post_id` no corresponde a ningún post real — incluye cualquier segmento de URL que no sea un UUID válido (el conversor de ruta ya descarta esos casos antes de llegar al handler) | `{"msg": "..."}` |

#### `DELETE /api/posts/<post_id>/like`

| Campo | Valor |
|---|---|
| Estado | **IMPLEMENTADO** — nuevo (`ADR-005-likes-minimal-model.md`) |
| Blueprint | `likes_bp`, mismo blueprint que `POST .../like` |
| Auth requerida | **Sí** — mismo criterio que `POST .../like` |

**Semántica.** Quita el like del usuario autenticado sobre el post `post_id`. **Idempotente**: si el usuario no lo había likeado, no falla — devuelve el mismo estado que si acabara de quitarlo.

**Request:** sin body. Mismo formato de `post_id` que `POST .../like`.

**Response — éxito (200)**
```json
{ "likes_count": "integer", "liked_by_me": false }
```

**Response — error:** mismos `401`/`404` que `POST .../like`.

**Notas de implementación (ambos endpoints):**
- No aceptan ningún campo de body — toda la información viene de la URL (`post_id`) y del JWT (`ADR-005` §Seguridad).
- No exponen qué usuarios dieron like a un post — solo el conteo agregado y si el usuario que pregunta ya likeó (`ADR-005` §No objetivos).

---

### 4.5 Comentarios

#### `POST /api/posts/<post_id>/comments`

| Campo | Valor |
|---|---|
| Estado | **IMPLEMENTADO** — nuevo (`ADR-006-comments-minimal-model.md`) |
| Blueprint | `comments_bp` (`backend/app/interfaces/routes/comment_routes.py`) |
| Auth requerida | **Sí** — `Bearer <jwt>` en el header `Authorization`. `author_id` se obtiene exclusivamente de `get_jwt_identity()` — nunca del body |

**Semántica.** Comenta el post `post_id` en nombre del usuario autenticado, en texto plano — sin hilos de respuestas (`ADR-006` §No objetivos). Cualquier usuario autenticado puede comentar cualquier post, no solo el autor.

**Request body**
```json
{ "content": "string (1–1000 caracteres tras trim)" }
```
`post_id` va en la URL, como UUID (conversor `uuid` de Flask/Werkzeug).

**Response — éxito (201)**
```json
{
  "comment": {
    "id": "string (UUID)",
    "post_id": "string (UUID)",
    "author": { "id": "string (UUID)", "username": "string", "name": "string" },
    "content": "string",
    "created_at": "string (ISO 8601)"
  }
}
```

**Response — error**

| Código | Causa | Body |
|---|---|---|
| `400` | Body vacío; `content` ausente, vacío tras `trim()`, o mayor a 1000 caracteres | `{"msg": "..."}` |
| `401` | Falta el header `Authorization`, el token es inválido/está malformado, o expiró | `{"msg": "..."}` |
| `404` | `post_id` no corresponde a ningún post real — incluye cualquier segmento de URL que no sea un UUID válido (el conversor de ruta ya descarta esos casos antes de llegar al handler) | `{"msg": "..."}` |

#### `GET /api/posts/<post_id>/comments`

| Campo | Valor |
|---|---|
| Estado | **IMPLEMENTADO** — nuevo (`ADR-006-comments-minimal-model.md`) |
| Blueprint | `comments_bp`, mismo blueprint que `POST .../comments` |
| Auth requerida | **Sí** — mismo criterio que el resto del feed hoy |

**Semántica.** Lista los comentarios del post `post_id`, en orden **cronológico ascendente** (más antiguo primero — `ADR-006` §Opciones consideradas, a diferencia de `GET /api/posts` que va al revés). Sin paginación real: límite fijo de **100** comentarios.

**Request:** sin body. Mismo formato de `post_id` que `POST .../comments`.

**Response — éxito (200)**
```json
{ "comments": [ { "id", "post_id", "author": {...}, "content", "created_at" }, ... ] }
```
Lista vacía (`[]`) si el post no tiene comentarios.

**Response — error:** mismos `401`/`404` que `POST .../comments`.

**Notas de implementación (ambos endpoints):**
- Whitelist explícita: solo `content` se lee del body en `POST` — nunca `post_id`/`author_id`/`id` (`post_id` viene de la URL).
- El objeto `author` reutiliza la misma forma reducida que `posts.author` — nunca expone `email`, `phone`, `password_hash` ni otros campos privados.

---

### 4.6 Follows

#### `POST /api/users/<user_id>/follow`

| Campo | Valor |
|---|---|
| Estado | **IMPLEMENTADO** — nuevo (`ADR-007-follows-minimal-model.md`) |
| Blueprint | `follows_bp` (`backend/app/interfaces/routes/follow_routes.py`) |
| Auth requerida | **Sí** — `Bearer <jwt>` en el header `Authorization`. Quién sigue se obtiene exclusivamente de `get_jwt_identity()` — nunca del body |

**Semántica.** Sigue a `user_id` en nombre del usuario autenticado. **Idempotente**: repetir la llamada no falla ni duplica (mismo criterio que `ADR-005` §Decisión, Opción A). Un usuario no puede seguirse a sí mismo — impuesto tanto en la aplicación como en el esquema (`CHECK ck_follows_no_self_follow`).

**Request:** sin body. `user_id` va en la URL, como UUID (conversor `uuid` de Flask/Werkzeug).

**Response — éxito (200)**
```json
{ "following": true }
```

**Response — error**

| Código | Causa | Body |
|---|---|---|
| `400` | `user_id` es el propio usuario autenticado | `{"msg": "..."}` |
| `401` | Falta el header `Authorization`, el token es inválido/está malformado, o expiró | `{"msg": "..."}` |
| `404` | `user_id` no corresponde a ningún usuario real — incluye cualquier segmento de URL que no sea un UUID válido (el conversor de ruta ya descarta esos casos antes de llegar al handler) | `{"msg": "..."}` |

#### `DELETE /api/users/<user_id>/follow`

| Campo | Valor |
|---|---|
| Estado | **IMPLEMENTADO** — nuevo (`ADR-007-follows-minimal-model.md`) |
| Blueprint | `follows_bp`, mismo blueprint que `POST .../follow` |
| Auth requerida | **Sí** — mismo criterio que `POST .../follow` |

**Semántica.** Deja de seguir a `user_id`. **Idempotente**: si no lo seguía, no falla. Dejar de seguirse a uno mismo es un no-op inofensivo — la restricción de auto-seguimiento solo aplica para *empezar* a seguir, así que este endpoint no devuelve `400` en ese caso.

**Request:** sin body. Mismo formato de `user_id` que `POST .../follow`.

**Response — éxito (200)**
```json
{ "following": false }
```

**Response — error:** mismos `401`/`404` que `POST .../follow` (sin el `400` de auto-seguimiento).

**Notas de implementación (ambos endpoints):**
- No aceptan ningún campo de body — toda la información viene de la URL (`user_id`) y del JWT (mismo principio que `ADR-005`/`ADR-006`).
- No exponen la lista de seguidores/seguidos de nadie — solo el conteo agregado (`GET`/`PATCH /api/users/me`, §4.2) y si el usuario que pregunta ya sigue a un autor (`author.is_followed_by_me`, §4.3) — `ADR-007` §No objetivos.
- No personalizan `GET /api/posts` — el feed sigue global (§4.3).

---

### 4.7 Notificaciones

#### `GET /api/notifications`

| Campo | Valor |
|---|---|
| Estado | **IMPLEMENTADO** — nuevo (`ADR-008-notifications-minimal-model.md`) |
| Blueprint | `notifications_bp` (`backend/app/interfaces/routes/notification_routes.py`) |
| Auth requerida | **Sí** — `Bearer <jwt>` en el header `Authorization`. Solo lista las notificaciones del propio usuario autenticado — no hay `user_id` en la URL de este endpoint, a diferencia de `follows` |

**Semántica.** Lista las notificaciones del usuario autenticado, más recientes primero. Cubre solo tres tipos de evento, los únicos que el backend genera hoy: `like` (alguien le dio like a un post tuyo), `comment` (alguien comentó un post tuyo), `follow` (alguien empezó a seguirte) — nunca sobre tu propio contenido, nunca duplicada por una repetición idempotente de un like/follow ya existente (`ADR-008` §Opciones consideradas). Sin paginación real: límite fijo de **50**.

**Request:** sin body. Header `Authorization: Bearer <token>` obligatorio.

**Response — éxito (200)**
```json
{
  "notifications": [
    {
      "id": "string (UUID)",
      "type": "like | comment | follow",
      "actor": { "id": "string (UUID)", "username": "string", "name": "string" },
      "post_id": "string (UUID) | null",
      "read": "boolean",
      "created_at": "string (ISO 8601)"
    }
  ]
}
```
`post_id` es `null` para `type: "follow"` — ese evento no tiene ningún post de origen. Lista vacía (`[]`) si no hay notificaciones.

**Response — error**

| Código | Causa | Body |
|---|---|---|
| `401` | Falta el header `Authorization`, el token es inválido/está malformado, o expiró | `{"msg": "..."}` |

#### `PATCH /api/notifications/<notification_id>/read`

| Campo | Valor |
|---|---|
| Estado | **IMPLEMENTADO** — nuevo (`ADR-008-notifications-minimal-model.md`) |
| Blueprint | `notifications_bp`, mismo blueprint que `GET /api/notifications` |
| Auth requerida | **Sí** — mismo criterio que `GET /api/notifications`. Solo se puede marcar como leída una notificación propia |

**Semántica.** Marca como leída la notificación `notification_id`. **Idempotente**: si ya estaba leída, no falla — devuelve el mismo estado (mismo criterio que `ADR-005`/`ADR-007`).

**Request:** sin body. `notification_id` va en la URL, como UUID (conversor `uuid` de Flask/Werkzeug).

**Response — éxito (200)**
```json
{ "read": true }
```

**Response — error**

| Código | Causa | Body |
|---|---|---|
| `401` | Falta el header `Authorization`, el token es inválido/está malformado, o expiró | `{"msg": "..."}` |
| `404` | `notification_id` no existe, **o** existe pero pertenece a otro usuario — mismo mensaje/código en ambos casos, no se distingue cuál ocurrió (mismo criterio que `POST /api/login` no distingue email inexistente de password incorrecta); incluye cualquier segmento de URL que no sea un UUID válido | `{"msg": "..."}` |

**Notas de implementación (ambos endpoints):**
- Sin endpoint de "marcar todas como leídas" en el backend — cada notificación se marca individualmente (`ADR-008` §No objetivos); el Frontend puede ofrecer esa acción iterando sobre las no leídas.
- Sin endpoint de contador de no leídas — el Frontend ya puede derivarlo contando `read: false` sobre la lista que `GET /api/notifications` devuelve.
- `POST /api/posts/<id>/like`, `POST /api/posts/<id>/comments` y `POST /api/users/<id>/follow` **no cambian su contrato** — generar la notificación correspondiente es un efecto secundario invisible en la respuesta de quien dispara la acción, visible solo para quien la recibe.

---

### 4.8 Recuperación de contraseña y verificación de email

#### `POST /api/forgot-password`

| Campo | Valor |
|---|---|
| Estado | **IMPLEMENTADO** — reescrito en `ADR-010-password-reset-otp-flow.md` (reemplaza el flujo de enlace de `ADR-009-password-reset-and-email-verification.md`) |
| Blueprint | `auth_bp` (`backend/app/interfaces/routes/auth_routes.py`) |
| Auth requerida | No (endpoint público — quien lo llama todavía no tiene sesión) |

**Semántica.** Si `email` corresponde a una cuenta real, genera un código numérico de 6 dígitos (10 minutos de vigencia, un solo uso) y envía un correo mostrándolo. Si no corresponde a ninguna cuenta, no hace nada — en **ambos** casos la respuesta es idéntica (evita enumeración de usuarios). Sujeto a un cooldown de 60 segundos por usuario: un pedido repetido dentro de esa ventana no genera un código ni un correo nuevo, sin cambiar la respuesta. **También es el endpoint de "Reenviar código"** — el Frontend lo llama de nuevo con el mismo email; el código anterior queda invalidado, incluso ante dos reenvíos simultáneos (`ADR-010` §Opciones consideradas, índice único parcial).

**Request body**
```json
{ "email": "string" }
```

**Response — éxito (200), siempre el mismo mensaje**
```json
{ "msg": "Si existe una cuenta asociada a ese correo, enviaremos un código de recuperación." }
```

**Response — error**

| Código | Causa | Body |
|---|---|---|
| `400` | Body vacío, `email` ausente, o con formato inválido (`domain/auth/validators.is_valid_email`) | `{"msg": "..."}` |

#### `POST /api/verify-reset-code`

| Campo | Valor |
|---|---|
| Estado | **IMPLEMENTADO** — nuevo (`ADR-010-password-reset-otp-flow.md`) |
| Blueprint | `auth_bp`, mismo blueprint que `POST /api/forgot-password` |
| Auth requerida | No — la identidad la aporta `email` + el código correcto |

**Semántica.** Verifica el código de 6 dígitos emitido por `POST /api/forgot-password`. Si es correcto, marca la solicitud como verificada y devuelve una **autorización temporal** (10 minutos de vigencia, un solo uso, de propósito específico — nunca un JWT de sesión normal) que `POST /api/reset-password` exige a continuación. Máximo **5 intentos** por solicitud (`domain/auth/token_policy.PASSWORD_RESET_MAX_ATTEMPTS`) — agotarlos bloquea la solicitud sin borrarla, obligando a pedir un código nuevo. Todos los casos de rechazo (email inexistente, sin solicitud activa, código expirado, intentos agotados, código incorrecto) devuelven el **mismo** mensaje y código — no se distinguen, para no habilitar enumeración de usuarios ni un canal lateral que revelara "intentos agotados" solo para cuentas reales.

**Request body**
```json
{ "email": "string", "code": "string (6 dígitos)" }
```

**Response — éxito (200)**
```json
{ "msg": "Código verificado correctamente.", "reset_authorization": "string" }
```

**Response — error**

| Código | Causa | Body |
|---|---|---|
| `400` | Body vacío; `email`/`code` ausentes; email sin cuenta asociada; sin solicitud activa; código expirado; intentos agotados; código incorrecto — los seis casos comparten el mismo mensaje | `{"msg": "El código es incorrecto. Inténtalo nuevamente."}` |

#### `POST /api/reset-password`

| Campo | Valor |
|---|---|
| Estado | **IMPLEMENTADO** — reescrito en `ADR-010-password-reset-otp-flow.md` (reemplaza el consumo directo del token de enlace de `ADR-009`) |
| Blueprint | `auth_bp`, mismo blueprint que `POST /api/forgot-password` |
| Auth requerida | No — la identidad la aporta la autorización temporal, no un JWT |

**Semántica.** Aplica una nueva contraseña usando la autorización temporal emitida por `POST /api/verify-reset-code`. La autorización debe existir, provenir de una solicitud verificada, no haber expirado, y no haber sido usada antes. Al aplicarse con éxito, marca la solicitud como usada y envía un correo de confirmación ("contraseña actualizada") — no hace falta invalidar "otras solicitudes pendientes" por separado: solo puede existir una activa por usuario en todo momento (`ADR-010` §Decisión).

**Request body**
```json
{
  "reset_authorization": "string",
  "password": "string",
  "confirm_password": "string"
}
```

**Response — éxito (200)**
```json
{ "msg": "Tu contraseña fue actualizada correctamente." }
```

**Response — error**

| Código | Causa | Body |
|---|---|---|
| `400` | Body vacío; `reset_authorization`/`password`/`confirm_password` ausentes; `password` ≠ `confirm_password`; `password` no cumple el formato mínimo (mismo `MIN_PASSWORD_LENGTH` que `POST /api/register`); la autorización no existe, no proviene de una solicitud verificada, ya expiró, o ya fue usada — ninguno de estos casos se distingue en el mensaje | `{"msg": "La autorización para restablecer tu contraseña no es válida o expiró"}` |

#### `POST /api/verify-registration-code`

| Campo | Valor |
|---|---|
| Estado | **IMPLEMENTADO** — nuevo (`ADR-011-mandatory-email-verification.md`), reemplaza a `POST /api/verify-email` (`ADR-009`, retirado — ver nota debajo) |
| Blueprint | `auth_bp` (`backend/app/interfaces/routes/auth_routes.py`) |
| Auth requerida | No — quien lo llama todavía no puede iniciar sesión (la cuenta sigue sin verificar) |

**Semántica.** Verifica el código de 6 dígitos que `POST /api/register` (o un reenvío) ya envió por correo. Si es correcto, marca `users.email_verified = true` directamente — a diferencia de la recuperación de contraseña, verificar el código **es** la acción final, no hay un paso sensible posterior que proteger con una autorización intermedia. Máximo **5 intentos** por código (`domain/auth/token_policy.REGISTRATION_MAX_ATTEMPTS`) — agotarlos bloquea el código sin borrarlo, obligando a pedir uno nuevo (`resend-registration-code`). Todos los casos de rechazo (email inexistente, cuenta ya verificada, sin código activo, código expirado, intentos agotados, código incorrecto) devuelven el **mismo** mensaje y código — mismo criterio anti-enumeración que `verify-reset-code` (§4.8).

**Request body**
```json
{ "email": "string", "code": "string (6 dígitos)" }
```

**Response — éxito (200)**
```json
{ "msg": "Tu correo fue verificado correctamente.", "email_verified": true }
```

**Response — error**

| Código | Causa | Body |
|---|---|---|
| `400` | Body vacío; `email`/`code` ausentes; email sin cuenta asociada; cuenta ya verificada; sin código activo; código expirado; intentos agotados; código incorrecto — los siete casos comparten el mismo mensaje | `{"msg": "El código es incorrecto. Inténtalo nuevamente."}` |

#### `POST /api/resend-registration-code`

| Campo | Valor |
|---|---|
| Estado | **IMPLEMENTADO** — nuevo (`ADR-011-mandatory-email-verification.md`) |
| Blueprint | `auth_bp`, mismo blueprint que `verify-registration-code` |
| Auth requerida | No — mismo criterio que `forgot-password` (§4.8), quien lo llama todavía no puede iniciar sesión |

**Semántica.** "Reenviar código" en la pantalla de verificación de registro. Si `email` corresponde a una cuenta real y todavía sin verificar, invalida el código activo anterior (si lo hay) y envía uno nuevo — sujeto al mismo cooldown de 60 segundos por usuario que `forgot-password` (`domain/auth/token_policy.REGISTRATION_CODE_REQUEST_COOLDOWN_SECONDS`), impuesto en el backend, no solo en el contador del Frontend. Si el email no existe, ya está verificado, o está en cooldown, no hace nada — en **todos** los casos la respuesta es idéntica (mismo criterio anti-enumeración que `forgot-password`).

**Request body**
```json
{ "email": "string" }
```

**Response — éxito (200), siempre el mismo mensaje**
```json
{ "msg": "Si existe una cuenta pendiente de verificación con ese correo, enviaremos un código nuevo." }
```

**Response — error**

| Código | Causa | Body |
|---|---|---|
| `400` | Body vacío, `email` ausente, o con formato inválido | `{"msg": "..."}` |

> ⚠️ **Retirados en v0.16.** `POST /api/send-verification-email` (protegido) y `POST /api/verify-email` (público, `ADR-009`, flujo de enlace) fueron **eliminados**, no solo deprecados: con `POST /api/login` ya bloqueado para cuentas sin verificar (§4.1), una cuenta sin verificar nunca puede obtener el JWT que el primero exigía — el par quedaba permanentemente inalcanzable, mismo criterio que `ADR-010` ya aplicó al reemplazar el flujo de enlace de recuperación de contraseña.

**Notas de implementación (los seis endpoints de esta sección):**
- Servicio de correo centralizado (`application/email/email_service.py`) detrás de un puerto `EmailSender` (`domain/email/sender.py`) — ningún endpoint ni caso de uso llama a Resend directamente (`ADR-009` §Decisión).
- El código de registro y el de recuperación de contraseña viven en tablas/repositorios completamente separados (`email_verification_tokens`/`password_reset_tokens`) — un código de uno nunca verifica al otro, ni por accidente ni por un valor coincidente (`ADR-011` §Decisión, purpose separation).
- Solo se persiste el hash de cada código (scrypt, no SHA-256 — baja entropía, `ADR-010`/`ADR-011` §Seguridad); ninguno de los dos valores crudos vuelve a aparecer en ningún response, log, ni URL.
- Sin `RESEND_API_KEY` configurada, el backend usa un `EmailSender` nulo que no envía nada de verdad pero no rompe ningún flujo — pensado para desarrollo local sin cuenta de Resend todavía (`ADR-009` §Riesgos). Si el envío real falla (Resend caído, credenciales inválidas), la excepción se propaga a un `500` genérico — la cuenta y el código ya persistidos quedan intactos, la persona puede pedir un código nuevo más tarde (`ADR-011` §Riesgos).

### 4.9 Autenticación con Google (OAuth 2.0 / OpenID Connect)

#### `POST /api/auth/google`

| Campo | Valor |
|---|---|
| Estado | **IMPLEMENTADO** — nuevo (`ADR-012-google-sign-in.md`) |
| Blueprint | `auth_bp` (`backend/app/interfaces/routes/auth_routes.py`) |
| Auth requerida | No — es, en sí mismo, el mecanismo de autenticación. Google prueba la identidad, THERS emite su propio JWT a partir de ese resultado |

**Semántica.** Único endpoint para "Continuar con Google" desde Login **y** desde Register (FASE 3 de la tarea origen: es la misma operación, resuelve crear/vincular/loguear según corresponda). Recibe el ID Token (`credential`) que Google Identity Services le entregó al Frontend y lo verifica criptográficamente (firma, `iss`, `aud` contra `GOOGLE_CLIENT_ID`, `exp`) contra las claves públicas reales de Google — nunca confía en un email/nombre que el Frontend le pase por su cuenta. Según el resultado:

- Identidad de Google ya vinculada antes → login directo.
- Sin cuenta de THERS con ese email → cuenta nueva, `email_verified=true` (la garantía de Google reemplaza al OTP para este email), `profile_completed=false` (Google no entrega `phone`/`country_code`/`birth_date`; `username` nace con un valor provisorio que la persona debe reemplazar).
- Cuenta de THERS existente con ese email, ya verificada → se vincula la identidad de Google, la contraseña existente **no se toca** (Google se suma como método adicional).
- Cuenta de THERS existente con ese email, nunca verificada → se **reclama**: se vincula, se marca `email_verified=true`, y se **anula** cualquier contraseña existente (nadie había probado antes ser su dueño real — ver `ADR-012` §Decisión, account linking).
- Google indica `email_verified=false` en el propio ID Token → se rechaza, no se crea ni vincula nada.

**Request body**
```json
{ "credential": "string (ID Token de Google)" }
```

**Response — éxito (200)** — mismo shape que `POST /api/login`
```json
{
  "token": "string (JWT de THERS)",
  "user": {
    "id": "string (UUID)",
    "username": "string",
    "email": "string",
    "name": "string",
    "phone": "string | null",
    "country_code": "string | null",
    "birth_date": "string (ISO yyyy-mm-dd) | null",
    "followers_count": "integer",
    "following_count": "integer",
    "email_verified": "boolean",
    "profile_completed": "boolean",
    "has_password": "boolean"
  }
}
```

**Response — error**

| Código | Causa | Body |
|---|---|---|
| `400` | Body vacío; `credential` ausente; la credencial no pudo verificarse (firma inválida, `aud`/`iss` incorrectos, expirada, o simplemente no es un JWT bien formado — todos con el mismo mensaje, sin distinguir el motivo) | `{"msg": "No pudimos verificar tu cuenta de Google. Intentá de nuevo."}` |
| `400` | La propia Google indica `email_verified=false` para esa cuenta (caso raro) | `{"msg": "Tu cuenta de Google no tiene el correo verificado. THERS no puede usarla."}` |

**Notas de implementación:**
- El JWT emitido es idéntico en forma al de `POST /api/login` (`identity=user["id"]`, mismo `create_access_token`) — ningún endpoint protegido distingue si la sesión empezó por password o por Google.
- `GOOGLE_CLIENT_ID` (backend) y `VITE_GOOGLE_CLIENT_ID` (Frontend) deben ser el mismo valor — es el Client ID de OAuth creado en Google Cloud Console, no es secreto. `GOOGLE_CLIENT_SECRET` **no existe** como variable de este proyecto — este flujo (verificación de ID Token) no lo requiere.
- `PATCH /api/users/me` (§4.2, sin cambios de contrato) es la pantalla "Complete your profile" para una cuenta con `profile_completed=false` — sin endpoint nuevo.
- Ver `ADR-012-google-sign-in.md` para la política completa de account linking y el razonamiento de seguridad detrás de cada caso.

---

### 4.10 Mensajes

#### `POST /api/users/<user_id>/messages`

| Campo | Valor |
|---|---|
| Estado | **IMPLEMENTADO** — nuevo (`ADR-013-messages-minimal-model.md`) |
| Blueprint | `messages_bp` (`backend/app/interfaces/routes/message_routes.py`) |
| Auth requerida | **Sí** — `Bearer <jwt>` en el header `Authorization`. `sender_id` sale exclusivamente del JWT, `recipient_id` de la URL — ninguno de los dos se acepta del body |

**Semántica.** Manda un mensaje de texto de la persona autenticada a `user_id`. Nunca idempotente — cada llamada crea una fila nueva (mismo criterio que crear un comentario, `ADR-006`).

**Request body**
```json
{ "content": "string" }
```

**Response — éxito (201)**
```json
{
  "message": {
    "id": "string (UUID)",
    "sender_id": "string (UUID)",
    "recipient_id": "string (UUID)",
    "content": "string",
    "read": "boolean",
    "created_at": "string (ISO 8601)"
  }
}
```

**Response — error**

| Código | Causa | Body |
|---|---|---|
| `400` | Body vacío o sin JSON; `content` ausente, vacío tras `trim()`, o mayor a 2000 caracteres; `user_id` es el propio usuario autenticado | `{"msg": "..."}` |
| `401` | Falta el header `Authorization`, el token es inválido/está malformado, o expiró | `{"msg": "..."}` |
| `404` | `user_id` no corresponde a ningún usuario real; incluye cualquier segmento de URL que no sea un UUID válido | `{"msg": "..."}` |

#### `GET /api/users/<user_id>/messages`

| Campo | Valor |
|---|---|
| Estado | **IMPLEMENTADO** — nuevo (`ADR-013-messages-minimal-model.md`) |
| Blueprint | `messages_bp`, mismo blueprint que `POST` |
| Auth requerida | **Sí** — mismo criterio que `POST`. Solo se puede leer un hilo propio (donde la persona autenticada es remitente o destinatario) |

**Semántica.** Historial de mensajes con `user_id`, ambos sentidos, orden cronológico **ascendente** (mensaje más viejo primero — a diferencia del feed/notificaciones, que van más reciente primero). Sin paginación real: límite fijo de **50** más recientes. **Efecto secundario:** marca como leídos los mensajes que `user_id` le mandó a la persona autenticada (`ADR-013` §Opciones consideradas — no hay un `PATCH .../read` separado).

**Request:** sin body. Header `Authorization: Bearer <token>` obligatorio.

**Response — éxito (200)**
```json
{ "messages": [ /* misma forma que el objeto de POST */ ] }
```
Lista vacía (`[]`) si nunca hubo mensajes con esa persona.

**Response — error**

| Código | Causa | Body |
|---|---|---|
| `401` | Falta el header `Authorization`, el token es inválido/está malformado, o expiró | `{"msg": "..."}` |
| `404` | `user_id` no corresponde a ningún usuario real; incluye cualquier segmento de URL que no sea un UUID válido | `{"msg": "..."}` |

#### `GET /api/conversations`

| Campo | Valor |
|---|---|
| Estado | **IMPLEMENTADO** — nuevo (`ADR-013-messages-minimal-model.md`) |
| Blueprint | `messages_bp` |
| Auth requerida | **Sí** — solo lista las conversaciones de la propia persona autenticada, sin `user_id` en la URL (mismo criterio que `GET /api/notifications`) |

**Semántica.** Lista, para cada persona con la que la persona autenticada tiene al menos un mensaje (enviado o recibido), el último mensaje del hilo y cuántos mensajes sin leer le mandó esa persona. Más reciente primero, por fecha del último mensaje.

**Request:** sin body. Header `Authorization: Bearer <token>` obligatorio.

**Response — éxito (200)**
```json
{
  "conversations": [
    {
      "user": { "id": "string (UUID)", "username": "string", "name": "string" },
      "last_message": {
        "content": "string",
        "sender_id": "string (UUID)",
        "created_at": "string (ISO 8601)"
      },
      "unread_count": "integer"
    }
  ]
}
```
Lista vacía (`[]`) si nunca mandó ni recibió ningún mensaje.

**Response — error**

| Código | Causa | Body |
|---|---|---|
| `401` | Falta el header `Authorization`, el token es inválido/está malformado, o expiró | `{"msg": "..."}` |

**Notas de implementación (los tres endpoints):**
- No existe una entidad `conversation`/`conversation_participants` en el esquema — una "conversación" es una vista derivada de los mensajes entre dos usuarios, no una fila propia (`ADR-013` §Opciones consideradas). No hay soporte de conversaciones grupales en esta versión.
- Sin tiempo real (WebSockets/Server-Sent Events) — el Frontend debe volver a pedir `GET /api/conversations`/`GET .../messages` periódicamente (*polling*) para ver mensajes nuevos, mismo criterio que `ADR-008` para notificaciones.
- Sin fotos/archivos adjuntos, sin borrado de mensajes, sin confirmación de lectura visible para el remitente ("visto") en esta versión.

---

## 5. Modelo de datos expuesto por la API

Este documento no define el modelo de datos (eso es `DATABASE_ARCHITECTURE.md`) pero sí documenta **qué forma tiene el dato tal como cruza la frontera HTTP**, que puede no coincidir 1:1 con el modelo de persistencia:

| Objeto | Campos expuestos hoy | Fuente |
|---|---|---|
| `user` (en response de register, login, `POST /api/auth/google`, `GET /api/users/me` y `PATCH /api/users/me`) | `id`, `username`, `email`, `name`, `phone` (nullable desde v0.17), `country_code` (nullable desde v0.17), `birth_date` (nullable desde v0.17), `followers_count`, `following_count`, `email_verified`, `profile_completed` (v0.17), `has_password` (v0.17) | `ADR-002-user-profile-fields.md` + `ADR-007-follows-minimal-model.md` (`followers_count`/`following_count`, v0.12) + `ADR-009-password-reset-and-email-verification.md` (`email_verified`, v0.14) + `ADR-012-google-sign-in.md` (`profile_completed`/`has_password`, `phone`/`country_code`/`birth_date` nullable, v0.17); coincide con `users` en `DATABASE_ARCHITECTURE.md` §5, sin exponer `password_hash` (correcto — `has_password` es un booleano derivado, nunca el hash en sí). `username_changed_at` (`ADR-003-profile-update-contract.md`) existe en `users` pero **nunca** cruza la frontera HTTP — es un dato interno de soporte para el cooldown de `username`, no un campo del contrato |
| `post` (en response de `POST`/`GET /api/posts`) | `id`, `author` (`id`/`username`/`name`/`is_followed_by_me`, forma reducida de `user`), `content`, `created_at`, `likes_count`, `liked_by_me`, `comments_count` | `ADR-004-posts-minimal-model.md` + `ADR-005-likes-minimal-model.md` (`likes_count`/`liked_by_me`, v0.10) + `ADR-006-comments-minimal-model.md` (`comments_count`, v0.11) + `ADR-007-follows-minimal-model.md` (`author.is_followed_by_me`, v0.12); coincide con `posts` en `DATABASE_ARCHITECTURE.md` §5. Sin `updated_at` en la respuesta — no hay edición todavía (`ADR-004` §No objetivos), así que exponerlo no aporta nada hoy |
| `like` — no se expone como objeto propio; solo el resumen agregado (`likes_count`/`liked_by_me`) embebido en `post` | — | `ADR-005-likes-minimal-model.md` §No objetivos: no se lista quién dio like a un post |
| `comment` (en response de `POST`/`GET /api/posts/<id>/comments`) | `id`, `post_id`, `author` (misma forma reducida que en `post`), `content`, `created_at` | `ADR-006-comments-minimal-model.md`; coincide con `comments` en `DATABASE_ARCHITECTURE.md` §5. Sin `updated_at` — mismo motivo que `post` |
| `follow` — no se expone como objeto propio; solo `{"following": bool}` en `POST`/`DELETE .../follow`, y el resumen agregado (`followers_count`/`following_count` en `user`, `is_followed_by_me` en `post.author`) | — | `ADR-007-follows-minimal-model.md` §No objetivos: no se lista quién sigue a quién |
| `notification` (en response de `GET /api/notifications`) | `id`, `type` (`like`/`comment`/`follow`), `actor` (misma forma reducida que en `post`/`comment`), `post_id` (nullable), `read` | `ADR-008-notifications-minimal-model.md`; coincide con `notifications` en `DATABASE_ARCHITECTURE.md` §5. `read` se deriva de `read_at` (internamente un timestamp) — se expone como booleano, nunca como el timestamp crudo, mismo criterio que `username_changed_at` nunca cruza la frontera HTTP |
| `password_reset_token` (OTP) — no se expone como objeto propio; el código viaja una única vez por correo, la autorización temporal viaja una única vez en `reset_authorization` (respuesta de `verify-reset-code`) | — | `ADR-010-password-reset-otp-flow.md` §Seguridad: solo se persisten `code_hash` (scrypt) y `reset_authorization_hash` (SHA-256), ninguno de los dos valores crudos vuelve a aparecer en ningún response |
| `email_verification_token` (OTP de registro) — no se expone como objeto propio; el código viaja una única vez por correo, nunca en un response JSON | — | `ADR-011-mandatory-email-verification.md` §Seguridad (reemplaza el token de enlace de `ADR-009`): solo se persiste `code_hash` (scrypt), el valor crudo nunca cruza la frontera HTTP; estructuralmente separado de `password_reset_token` (tabla y repositorio propios) — un código nunca verifica el propósito del otro |
| `user_identity` — no se expone como objeto propio; el `credential` (ID Token) que la origina viaja una única vez, en el body de `POST /api/auth/google` (nunca en la respuesta) | — | `ADR-012-google-sign-in.md`: solo se persisten `provider`/`provider_subject` (el claim `sub`, nunca el email como identificador); ningún endpoint lista las identidades vinculadas de un usuario todavía |
| `message` (en response de `POST`/`GET /api/users/<id>/messages`) | `id`, `sender_id`, `recipient_id`, `content`, `read`, `created_at` | `ADR-013-messages-minimal-model.md`; coincide con `messages` en `DATABASE_ARCHITECTURE.md` §5. `read` se deriva de `read_at` (internamente un timestamp) — mismo criterio que `notification.read` |
| `conversation` (en response de `GET /api/conversations`) — no es una entidad propia, es una vista derivada de `messages` agrupada por "la otra persona" | `user` (misma forma reducida que `actor`/`author`), `last_message` (`content`/`sender_id`/`created_at`), `unread_count` | `ADR-013-messages-minimal-model.md` §Opciones consideradas: sin tabla `conversations`/`conversation_participants` en esta versión |

`avatar_url`/`bio` (`DATABASE_ARCHITECTURE.md` §4.B) siguen sin ratificar — no forman parte de este catálogo todavía. Cuando se ratifiquen por su propio ADR, este catálogo deberá actualizarse el mismo día en que el endpoint correspondiente las exponga (`HB-001` §15.1) — no antes, no por anticipación.

---

## 6. Autenticación y autorización

- **Mecanismo:** JWT emitido por `flask_jwt_extended`, `create_access_token(identity=user["id"])` — `identity` es el `id` (UUID, como string) de `users`, no el email (cambiado en esta tarea; ver `BACKEND_ARCHITECTURE.md` §9).
- **Convención de envío:** header `Authorization: Bearer <token>` — verificada contra código real desde v0.3 (`GET /api/users/me`, §4.2).
- **Almacenamiento en el Frontend:** `localStorage` (`useAuth.js`) — decisión ya registrada como `PENDIENTE DE APROBACIÓN` en `FRONTEND_ARCHITECTURE.md` §16, no se repite la discusión aquí.
- **Autorización (roles/permisos):** no existe ningún concepto en el sistema — no se documenta lo que no existe.

---

## 7. Errores de red y disponibilidad (responsabilidad del Frontend)

- El Frontend hoy maneja fallos de la llamada de login con `try/catch` + `alert()` (`Login.jsx`) — sin distinguir error de red, timeout, o error de servidor. Documentado en `FRONTEND_ARCHITECTURE.md` §12, no se repite aquí como contrato porque no es parte del contrato HTTP en sí, sino de cómo el Frontend reacciona a él.
- Este documento no impone un estándar de manejo de errores en el cliente — esa es responsabilidad de `FRONTEND_ARCHITECTURE.md`.

---

## 8. Qué NO cambia con este documento

- No se ratifica un formato de error nuevo — el actual (`{"msg": "..."}`) ya se aplica de forma uniforme a toda la API desde v0.6 (§3), sin agregar campos nuevos (código machine-readable) que nadie necesita hoy.
- No se adopta OpenAPI/Swagger en esta versión.
- No se define el contrato de ningún endpoint futuro más allá de `/register` y `/login` (ya implementados) — se señala su ausencia, no se inventa su forma.

---

## 9. PENDIENTES DE APROBACIÓN

Decisiones que este documento **no toma** porque no están respaldadas por código ni por documentación oficial ratificada. Cada una debe resolverse como ADR (`HB-001` §11–12) antes de implementarse:

1. ~~Formato estándar de error para toda la API~~ — **avanzado en v0.6** (heredado de `BACKEND_ARCHITECTURE.md` §20, ítem 5): `{"msg": "..."}` ya es el formato aplicado uniformemente, incluidos los casos antes no cubiertos (`404`/`405`/`500` genéricos, §3). Sigue pendiente únicamente si el equipo quiere agregar un código de error machine-readable — no decidido, no necesario hoy.
2. ~~Contrato de `POST /api/register`~~ — **resuelto e implementado**, incluidos los campos de perfil (§4.1, `ADR-002`). ~~Longitud mínima de contraseña y validación de formato de email~~ — **resuelto en v0.7** (§4.1: `is_valid_email`/`is_valid_password`, `domain/auth/validators.py`) — la unicidad de email/username ya estaba resuelta, la impone el esquema vía `CITEXT UNIQUE`/`uq_users_username`.
3. **Convención de verbos HTTP** para operaciones futuras (colecciones, borrado). Parcialmente resuelto: `PATCH` es ya el verbo real usado para actualización parcial (`PATCH /api/users/me`, §4.2, `ADR-003`) — sigue sin ratificarse como convención formal para futuros endpoints de escritura.
4. **Versionado de API** (`/api/v1` u otro mecanismo) — o la decisión explícita de no versionar todavía.
5. **Paginación** — formato (offset/limit, cursor) para cuando exista el primer endpoint de colección (p. ej. feed).
6. ~~Convención de endpoints protegidos~~ — **resuelto: primer caso real implementado** (`GET /api/users/me`, §4.2, `ADR-002`), incluida la homogenización de errores JWT a `401` (`app/extensions.py`).
7. **Especificación formal (OpenAPI/Swagger)** y su ubicación — evaluar cuando el catálogo de endpoints crezca lo suficiente para justificar el costo de mantenerla (`HB-001` §15.1 menciona esta opción sin decidirla, igual que `BACKEND_ARCHITECTURE.md` §14).

---

## 10. Evolución de este documento

Cada endpoint nuevo se documenta aquí **el mismo día de su PR** (`HB-001` §15.1, regla ya vigente, sin excepción). Este documento crece por adición de secciones en §4, sin reestructurarse — mismo principio de escalabilidad por adición que `REPOSITORY_STRUCTURE.md` §2 y `DATABASE_ARCHITECTURE.md` §3 ya aplican en sus respectivos dominios.

Si el catálogo de endpoints crece lo suficiente para que un Markdown plano deje de ser manejable, migrar a OpenAPI/Swagger es una decisión de impacto medio (§9, ítem 7) — no una consecuencia automática de este documento.

---

## Fuentes consultadas

- `CLAUDE.md` (raíz) — índice de reglas operativas y jerarquía de fuentes.
- `docs/architecture/BACKEND_ARCHITECTURE.md` — fuente directa del estado real del único endpoint implementado (§5, §6, §9, §11, §14).
- `docs/architecture/DATABASE_ARCHITECTURE.md` — modelo de datos disponible para exponer (§4.A, §5).
- `docs/architecture/FRONTEND_ARCHITECTURE.md` — consumidor del contrato (§9, §10, §12, §16).
- `docs/architecture/organization/01_Manual_Organizacion/Source/HB-001-manual-organizacion.md.md` — §15.1 (documentar endpoints el mismo día del PR), §11–12 (proceso de ADR).
- `docs/architecture/ADR-002-user-profile-fields.md` — decisión que ratifica `username`/`phone`/`country_code`/`birth_date` en `users` y `GET /api/users/me`.
- `docs/architecture/ADR-003-profile-update-contract.md` — decisión que ratifica el contrato de `PATCH /api/users/me` (§4.2): campos editables, unicidad, cooldown de `username`, semántica PATCH, errores.
- Código fuente: `backend/app/interfaces/routes/auth_routes.py`, `backend/app/interfaces/routes/user_routes.py`, `backend/app/application/auth/*.py`, `backend/app/domain/auth/*.py`, `backend/app/extensions.py`, `backend/app/__init__.py`; `Frontend/src/features/auth/pages/Register.jsx`, `Frontend/src/features/auth/lib/validators.js`.

---

## Cierre

Este documento **no modifica** el backend ni el Frontend: define el contrato de API que ambos deben respetar hacia adelante, separando explícitamente **lo implementado** (§4.1), **lo esperado pero ausente** (§4.2) y **lo pendiente de aprobación** (§9). Cualquier cambio a este contrato sigue el proceso de decisiones de impacto medio/alto de `HB-001` §11–12 (ADR), no el criterio individual de quien implementa. A partir de su ratificación, Backend y Frontend deben implementar contra este documento — no negociar el contrato de forma ad-hoc en cada feature.
