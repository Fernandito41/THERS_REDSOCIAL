# API_CONTRACT

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/API_CONTRACT.md` |
| Versión | 0.7 (Propuesta) |
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
> **v0.7 — validación de formato de `email` y longitud mínima de `password` en `POST /api/register` (cierra §9 ítem 2):** `domain/auth/validators.py` gana `is_valid_email()` (regex básica, sin verificar dominio real) e `is_valid_password()` (mínimo 8 caracteres, `MIN_PASSWORD_LENGTH`) — mismo patrón que los validadores ya existentes de `username`/`phone`/`country_code`/`birth_date`. Ambos umbrales son placeholders de producto explícitos y revisables (mismo criterio que `MIN_AGE_YEARS`, `ADR-002` §3), decididos como cambio técnico de bajo impacto (`HB-001` §11) por no alterar arquitectura, esquema ni ningún endpoint más allá de `register`. `POST /api/login` y `PATCH /api/users/me` **no cambian** — ninguno de los dos valida formato de credenciales (login no reformatea lo que ya existe; `PATCH` no permite editar `email`/`password`, `ADR-003`). Reflejado en §4.1 y §9. Verificado con 3 pruebas nuevas + la suite completa (59/59, ejecutada contra PostgreSQL 16 real).

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
| Estado | **IMPLEMENTADO** — actualizado en esta tarea (THERS Backend Fase 2.1) para incluir los campos de perfil ratificados por `ADR-002-user-profile-fields.md` |
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
    "phone": "string",
    "country_code": "string",
    "birth_date": "string (ISO yyyy-mm-dd)"
  }
}
```

**Response — error**

| Código | Causa | Body |
|---|---|---|
| `400` | Body vacío; alguno de `name`/`username`/`email`/`phone`/`country_code`/`birth_date`/`password`/`confirm_password` ausente; `email` con formato inválido; `password` ≠ `confirm_password`; `password` con menos de 8 caracteres; `username`/`phone`/`country_code`/`birth_date` con formato inválido; edad menor a 13 años | `{"msg": "..."}` |
| `409` | Ya existe un usuario con ese email (comparación case-insensitive, `CITEXT`) **o** con ese username | `{"msg": "..."}` |

**Notas de implementación:**
- `password_hash` se genera con `werkzeug.security.generate_password_hash` (scrypt) — nunca se persiste ni se devuelve la contraseña en claro.
- `id` lo genera PostgreSQL (`gen_random_uuid()`), nunca Python (`DATABASE_ARCHITECTURE.md` §5).
- `confirm_password` se valida (debe coincidir con `password`) y **nunca se persiste** — no existe como columna de `users`.
- Formato validado en el backend (`domain/auth/validators.py`, ver `ADR-002` §3): `username` (`^[a-zA-Z0-9_]{3,20}$`), `phone` (7–15 dígitos), `country_code` (`^\+[1-9]\d{0,3}$`), `birth_date` (ISO válida + edad mínima 13 años).
- **v0.7 — resuelto:** `email` (regex básica `^[^\s@]+@[^\s@]+\.[^\s@]+$`, sin verificar dominio real) y `password` (mínimo `MIN_PASSWORD_LENGTH = 8` caracteres, sin exigir mayúscula/número/símbolo) — ambos placeholders de producto explícitos, revisables (mismo criterio que `MIN_AGE_YEARS`).

#### `POST /api/login`

| Campo | Valor |
|---|---|
| Estado | **IMPLEMENTADO** — sin cambios de comportamiento en esta tarea; la respuesta expone ahora los campos de perfil nuevos |
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
    "phone": "string",
    "country_code": "string",
    "birth_date": "string (ISO yyyy-mm-dd)"
  }
}
```

**Response — error**

| Código | Causa | Body |
|---|---|---|
| `400` | Body vacío, o `email`/`password` ausentes | `{"msg": "..."}` |
| `401` | Credenciales inválidas — email inexistente **o** contraseña incorrecta, mismo mensaje en ambos casos deliberadamente, para no permitir enumerar emails registrados | `{"msg": "..."}` |

**Cambios respecto a la versión anterior de este documento:**
- La validación ya **no** compara contra una credencial hardcodeada — consulta la tabla `users` real vía `SQLAlchemyUserRepository` (`backend/app/infrastructure/persistence/repositories/user_repository.py`).
- El objeto `user` devuelto ahora incluye también `username`, `phone`, `country_code`, `birth_date` (`ADR-002`).
- **`identity` del JWT cambió de `email` a `user.id` (UUID, como string)** — cualquier endpoint protegido usa `get_jwt_identity()` y recibe un UUID de `users.id`, no un email. Ver `BACKEND_ARCHITECTURE.md` §9.
- El token sigue sin política de expiración explícita configurada (`PENDIENTE DE APROBACIÓN`, sin cambios en esta tarea).

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
    "phone": "string",
    "country_code": "string",
    "birth_date": "string (ISO yyyy-mm-dd)"
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
    "phone": "string",
    "country_code": "string",
    "birth_date": "string (ISO yyyy-mm-dd)"
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

## 5. Modelo de datos expuesto por la API

Este documento no define el modelo de datos (eso es `DATABASE_ARCHITECTURE.md`) pero sí documenta **qué forma tiene el dato tal como cruza la frontera HTTP**, que puede no coincidir 1:1 con el modelo de persistencia:

| Objeto | Campos expuestos hoy | Fuente |
|---|---|---|
| `user` (en response de register, login, `GET /api/users/me` y `PATCH /api/users/me`) | `id`, `username`, `email`, `name`, `phone`, `country_code`, `birth_date` | `ADR-002-user-profile-fields.md`; coincide con `users` en `DATABASE_ARCHITECTURE.md` §5, sin exponer `password_hash` (correcto — nunca debe exponerse). `username_changed_at` (`ADR-003-profile-update-contract.md`) existe en `users` pero **nunca** cruza la frontera HTTP — es un dato interno de soporte para el cooldown de `username`, no un campo del contrato |

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
