# ADR-003 — Contrato de actualización del perfil de usuario

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/ADR-003-profile-update-contract.md` |
| Tipo | Architecture Decision Record (`HB-001` §11–12) |
| Fecha | 28/08/2026 |
| Estado | **Aceptada** — ratificada el 28/08/2026 (ver nota de aprobación abajo). **Contrato no implementado todavía** (ver regla de alcance abajo): esta ratificación autoriza la implementación futura contra este contrato, no ejecuta código en esta tarea |
| Alcance | Decisión de arquitectura para `backend/` (modelo `users`, futuro endpoint `PATCH /api/users/me`) y su impacto de contrato en `Frontend/` — sin tocar código, esquema ni Frontend en esta tarea |
| Autor | Sesión de auditoría/arquitectura con IA, confirmada por Fernando Escalante (ver §Referencias) |
| Aprobado por | Fernando Escalante — 28/08/2026, sesión de trabajo con IA (ver §Referencias). Mismo criterio de excepción de proceso ya aplicado en `ADR-001` §Nota de desviación: ratificación registrada aquí en vez de en Notion (`HB-001` §12) |
| Autoridad sobre este documento | `/docs` oficial > estructura real observada en el código > este documento (mismo orden que `CLAUDE.md` §4) |

> ⚠️ **Regla de alcance de esta tarea, explícita.** Este documento es el **único entregable**. No se modificó código de `backend/` ni de `Frontend/`, no se crearon migraciones, no se tocó la base de datos. Toda afirmación de "estado actual" en este ADR proviene de lectura directa del código real (modelo `models.py`, migraciones `backend/migrations/versions/`, rutas, casos de uso, `Frontend/src/features/auth/`), no de suposiciones. Donde el código y `/docs` se contradicen, se aplica la jerarquía **código real > migraciones/DB real > tests > documentación** (regla de esta tarea) y la contradicción se registra explícitamente (ver §Estado actual).
>
> **Nota de aprobación.** Este ADR se ratifica priorizando en cada punto abierto la opción más conservadora en materia de seguridad, sobre las alternativas evaluadas en cada sección: `email`/`password` quedan fuera del contrato (evitan secuestro de cuenta vía cambio de identificador de login sin verificación), `avatar_url` se aprueba explícitamente **sin** aceptar URL libre desde el cliente (cierra el vector de phishing/tracking antes de que la columna exista siquiera), y el endpoint se aprueba condicionado a una whitelist explícita de campos (cierra mass assignment/overposting por diseño, no por revisión posterior). Ningún punto de este ADR queda aprobado con la opción menos segura disponible.

---

## Estado

**Aceptada.**

---

## Contexto

THERS tiene hoy autenticación completa y funcional: `POST /api/register`, `POST /api/login` y `GET /api/users/me` (`ADR-002-user-profile-fields.md`) operan contra la tabla `users` real en PostgreSQL, con 27 pruebas de integración pasando. El Frontend (`Register.jsx`, `AuthContext.jsx`) ya consume ese contrato de punta a punta (`API_CONTRACT.md` v0.4).

Lo que **no existe** es ninguna forma de que un usuario autenticado modifique sus propios datos. Sin embargo, `Frontend/src/features/feed/pages/Profile.jsx` ya construye la experiencia de "editar perfil" (nombre, username, bio, mood, intereses, música favorita) contra `localStorage` puro:

- `onUpdateUser({ name, username })` → `AuthContext.updateStoredUser()` (`AuthContext.jsx:89-96`) sobrescribe la sesión local, sin llamar al backend.
- `bio`/`mood`/`interests`/`favoriteTrack`/`banner`/`accent` se guardan en `localStorage` bajo la clave `thers_profile_<username>` (`Profile.jsx:23-34`), sin ninguna columna de base de datos que los respalde.

Esto produce un bug de experiencia ya detectado en la auditoría previa de este mismo repositorio (ver informe de auditoría del 2026-08-28): `AuthContext.loadCurrentUser()` llama a `GET /api/users/me` en cada montaje de la aplicación (`AuthContext.jsx:31-59`) y **sobrescribe** `localStorage["user"]` con la respuesta real del backend. Cualquier edición de `name`/`username` hecha solo con `updateStoredUser()` se pierde silenciosamente en el siguiente F5, porque el backend nunca la recibió.

No se puede resolver esto con una implementación puntual: hacerlo sin decidir primero **dónde vive el dato de perfil a mediano plazo** (¿sigue siendo `users`? ¿nace ya una tabla `profiles`?) arriesga exactamente lo que este proceso de ADR existe para evitar — una decisión de esquema tomada por conveniencia de una tarea aislada, que haya que deshacer cuando THERS tenga miles de usuarios y perfiles públicos.

## Problema

Definir, sin implementar, el contrato arquitectónico de `PATCH /api/users/me`:
1. ¿Qué campos son editables y por qué?
2. ¿El dato de perfil (actual y futuro: `bio`, `avatar_url`) pertenece a `users` o a una entidad nueva?
3. ¿Cómo se garantiza que la decisión de hoy no bloquee (ni obligue a reescribir) autenticación, perfiles públicos, búsqueda, seguidores, verificación de email/teléfono y moderación cuando esas funcionalidades existan?

## Objetivos

- Definir el contrato de `PATCH /api/users/me`: campos, validación, unicidad, privacidad, semántica, errores, response.
- Decidir la arquitectura de datos de perfil (`users` vs `profiles` vs alternativa) de forma sostenible, no solo para el alcance actual.
- Dejar explícitas las decisiones futuras condicionadas (email, teléfono, avatar, contraseña) sin resolverlas prematuramente.
- Mantener la arquitectura simple: sin tablas, entidades ni capas que la funcionalidad actual no justifique.

## No objetivos

- No implementar `PATCH /api/users/me`.
- No implementar verificación de email ni de teléfono (SMS).
- No implementar upload de avatar ni almacenamiento de medios.
- No implementar historial de contraseñas, sesiones, dispositivos ni auditoría de seguridad.
- No implementar perfiles públicos, búsqueda por username, seguidores ni ninguna funcionalidad social — solo se evalúa que esta decisión no las dificulte.
- No resolver el formato de error estándar de toda la API (`API_CONTRACT.md` §9 ítem 1) — este ADR hereda esa pendiente, no la cierra.

## Estado actual (investigación)

**Modelo `users` real** (`backend/app/infrastructure/persistence/models.py`, migraciones `a1b2c3d4e5f6_create_users_table.py` + `a1edcbff74d8_add_profile_fields_to_users.py`):

| Columna | Tipo real | Nulo | Único | Origen |
|---|---|---|---|---|
| `id` | `UUID`, `DEFAULT gen_random_uuid()` (generado por PostgreSQL) | No (PK) | — | Migración inicial |
| `name` | `VARCHAR(120)` | No | No | Migración inicial |
| `username` | `VARCHAR(30)` | No | Sí (`uq_users_username`) | `ADR-002` |
| `email` | `CITEXT` | No | Sí (`ix_users_email`, case-insensitive) | Migración inicial |
| `phone` | `VARCHAR(20)` | No | No | `ADR-002` |
| `country_code` | `VARCHAR(6)` | No | No | `ADR-002` |
| `birth_date` | `DATE` | No | No | `ADR-002` |
| `password_hash` | `TEXT` | No | No | Migración inicial |
| `created_at` / `updated_at` | `TIMESTAMPTZ`, `DEFAULT now()` | No | — | Migración inicial; `updated_at` mantenida por trigger `trg_users_updated_at` (`set_updated_at()`), no por SQLAlchemy |

**Ninguna columna `bio` ni `avatar_url` existe hoy en la base de datos real** — `DATABASE_ARCHITECTURE.md` §4.B las registra como `OBJETIVO`/`PENDIENTE DE DECISIÓN`, sin ADR propio. Este ADR no las crea.

**Capas del backend** (`domain/`, `application/`, `infrastructure/`, `interfaces/routes/`) ya establecen un patrón reutilizable y verificado en `register`/`login`/`me`:
- `domain/auth/validators.py` — validación pura de formato (`is_valid_username`, `is_valid_phone`, `is_valid_country_code`, `parse_birth_date`, `meets_minimum_age`), sin Flask ni SQLAlchemy.
- `domain/auth/repositories.py` — puerto abstracto `UserRepository` (`create`, `find_by_email`, `find_by_id`); la implementación SQLAlchemy vive en `infrastructure/persistence/repositories/user_repository.py` y traduce `IntegrityError` de PostgreSQL a excepciones de dominio (`UsernameAlreadyExistsError`/`EmailAlreadyExistsError`) inspeccionando `constraint_name` — **no** adivina por texto de mensaje.
- `application/auth/user_presenter.py` — `to_public_user()`, única función que decide qué campos de `User` cruzan la frontera HTTP; reutilizada por `register`, `login` y `me`.
- `interfaces/routes/` — composition root: único punto que conoce tanto el caso de uso como el repositorio concreto.

**Frontend** — `AuthContext.jsx` ya trata `GET /api/users/me` como fuente de verdad única de la identidad (`loadCurrentUser()`); `updateStoredUser()` (edición 100% local) es la única vía de "edición de perfil" que existe hoy, y es exactamente lo que este ADR debe reemplazar por un contrato real.

**Contradicción código-vs-documentación detectada (registrada, no corregida aquí):** `DATABASE_ARCHITECTURE.md` §11/§14 sigue advirtiendo `JWT_SECRET_KEY = "super-secret-key"` **hardcodeado** en `config.py` como hallazgo de seguridad pendiente. El código real (`backend/app/config.py:4-17`) ya no lo tiene hardcodeado: lee `JWT_SECRET_KEY` de entorno, con un fallback de desarrollo inseguro explícitamente advertido por `stderr`. Por la jerarquía de esta tarea (código real > docs), se toma el código como cierto; la corrección de `DATABASE_ARCHITECTURE.md` §14 queda fuera de alcance de este ADR — se señala para que se sincronice en una tarea de documentación aparte.

---

## Opciones consideradas

### Opción A — Extender `users` (elegida)

Agregar los futuros `bio`/`avatar_url` como columnas de `users`, igual que `ADR-002` ya hizo con `username`/`phone`/`country_code`/`birth_date`, y servir `PATCH /api/users/me` sobre esa misma tabla.

| | |
|---|---|
| **Ventajas** | Cero entidades nuevas; reutiliza el patrón ya probado (`UserRepository`, `to_public_user`, validadores puros); una sola fuente de verdad para "quién es este usuario"; sin JOIN para el caso de uso más frecuente (`GET /api/users/me`, login); consistente con la decisión ya tomada en `ADR-002` para un problema idéntico (columnas de perfil simples, sin relación propia) |
| **Desventajas** | `users` mezcla datos de autenticación (email, password_hash) con datos de perfil público (name, username, bio, avatar_url); si el perfil social crece mucho (preferencias, configuración, estadísticas), `users` puede volverse una tabla "todo-en-uno" difícil de mantener |
| **Impacto futuro** | Sostenible mientras el perfil siga siendo un puñado de columnas simples sin relaciones propias (ver criterio de reevaluación en §Decisión) |

### Opción B — `users` (auth) + `profiles` (social/público) desde ahora

Mover `name`, `username`, `bio`, `avatar_url` (y quizás `phone`/`country_code`/`birth_date`) a una tabla `profiles` 1:1 con `users`, dejando en `users` solo `id`, `email`, `password_hash`, timestamps.

| | |
|---|---|
| **Ventajas** | Separación conceptual limpia entre "credencial" y "perfil"; un futuro `GET /api/profiles/:username` público no necesitaría filtrar columnas sensibles de la misma tabla que usa el login |
| **Desventajas** | Requiere JOIN en **todo** flujo que hoy es una sola consulta (`login`, `register`, `me`) sin que exista todavía ninguna necesidad funcional que lo justifique (nadie consulta perfil sin sesión, no hay perfiles públicos implementados); introduce una relación 1:1 nueva, migraciones más complejas (mover columnas existentes con datos reales, no solo agregar), y dos repositorios/casos de uso donde hoy hay uno — contradice el principio de simplicidad que el propio `ADR-002` ya aplicó (`FAS-001` §2, citado explícitamente ahí) para un problema idéntico |
| **Impacto futuro** | Resuelve un problema que **todavía no existe** (perfiles públicos) al costo de complejidad real hoy — sobre-ingeniería según la regla explícita de esta tarea (§24 del prompt de origen) |

### Opción C — Entidad separada para datos sensibles (`auth_credentials`) + `users` como perfil

Invertir la Opción B: dejar `users` como la tabla "social" (name, username, bio, avatar_url, phone, country_code, birth_date) y mover `email`/`password_hash` a una tabla `auth_credentials` referenciada por `user_id`.

| | |
|---|---|
| **Ventajas** | Aislaría el dato más sensible (credenciales) del resto, útil si en el futuro se soportan múltiples métodos de auth (OAuth + password) sin forzar `email`/`password_hash` a ser nullable en `users` |
| **Desventajas** | El login **siempre** necesita `email` para identificar al usuario — separar `email` de `users` obliga a un JOIN en el flujo más frecuente y de mayor sensibilidad de latencia (login); no hay hoy ningún segundo método de autenticación (OAuth sigue `PENDIENTE DE DECISIÓN` en `DATABASE_ARCHITECTURE.md` §4.B) que justifique esta separación; sería exactamente el tipo de decisión "por si acaso" que `CLAUDE.md` §6 y `HB-001` prohíben tomar sin necesidad evidente |
| **Impacto futuro** | Si THERS agrega OAuth, el problema real a resolver es "un usuario, múltiples métodos de login" — eso se modela con una tabla `oauth_accounts` referenciando a `users` (ya candidata en `DATABASE_ARCHITECTURE.md` §4.B), **no** separando `email`/`password_hash` de `users`. Se descarta. |

---

## Decisión

**Se elige la Opción A: `users` permanece como la única entidad, extendida por columnas simples cuando se ratifiquen (`bio`, `avatar_url`), siguiendo exactamente el precedente ya sentado por `ADR-002`.**

La preocupación real detrás de la Opción B — que datos de autenticación y datos de perfil público **no deberían exponerse igual** cuando existan perfiles públicos — es legítima, pero es un problema de **capa de presentación** (qué campos cruzan la frontera HTTP en cada endpoint), no de **modelado de datos**. THERS ya tiene la pieza que resuelve exactamente esto: `application/auth/user_presenter.py`. La misma técnica que hoy separa "lo que se persiste" (`User`, con `password_hash`) de "lo que se expone" (`to_public_user()`, sin `password_hash`) es la que debe separar, el día que exista un perfil público, "lo que ve el propio usuario" (`to_public_user()`, actual) de "lo que ve un tercero" (un futuro `to_profile_view(user)` sin `email`/`phone`/`country_code`/`birth_date`). Esto no requiere una tabla nueva — requiere una segunda función *presenter*, del mismo tamaño y forma que la que ya existe.

**Criterio explícito de reevaluación (decisión futura condicionada, no un "depende" sin resolver):** esta decisión se revisita por un ADR nuevo si ocurre **cualquiera** de estas condiciones:
1. El número de columnas de perfil puramente social (más allá de `name`/`username`/`bio`/`avatar_url`) supera ~8–10 (p. ej. preferencias, estadísticas de actividad, configuración de privacidad detallada) — señal de que `users` se está volviendo una tabla "todo-en-uno".
2. Aparece una necesidad real de consultar/actualizar perfil público a **alta frecuencia e independiente** de autenticación (p. ej. un feed que lee miles de perfiles por segundo) que se beneficie de particionar o cachear perfil sin tocar la tabla de credenciales.
3. Se introduce un segundo método de autenticación (OAuth) que requiera que `email` dependa de un proveedor externo en vez de ser un campo propio de `users`.

Ninguna de las tres condiciones existe hoy — implementarla ahora sería la sobre-ingeniería que la regla de esta tarea prohíbe explícitamente.

---

## Modelo de datos

**Sin cambios de esquema en esta decisión.** `users` conserva exactamente las columnas de §Estado actual. `PATCH /api/users/me`, en su primera versión implementable, opera únicamente sobre columnas **que ya existen** en la base de datos real: `name`, `username`, `phone`, `country_code`, `birth_date`.

`bio`/`avatar_url` **no se agregan por este ADR**. Cuando el equipo decida ratificarlas, ese es un ADR de alcance acotado (mismo patrón que `ADR-002`) que:
- Agrega dos columnas nullable/con default vacío a `users` (una migración aditiva, sin backfill — mismo razonamiento que `ADR-002` §Consecuencias: no hay todavía una base compartida con datos reales que migrar).
- Extiende la whitelist de `PATCH /api/users/me` definida aquí, sin reabrir el resto de este contrato.

Este ADR deja **pre-declarado** (no vinculante hasta su propio ADR) el tipo esperado para no improvisar cuando llegue ese momento:

| Columna futura | Tipo propuesto | Nulo | Motivo |
|---|---|---|---|
| `bio` | `VARCHAR(280)` o `TEXT` con `CHECK (length(bio) <= 280)` | Sí, default `''` | Texto plano corto (§Reglas de validación); 280 es un placeholder de producto (mismo estilo que `MIN_AGE_YEARS`), no una decisión final |
| `avatar_url` | `TEXT`, nullable | Sí, default `NULL` | Ver §Evolución futura — no editable directamente por texto libre desde el cliente (razón de seguridad, no de tipo de dato) |

---

## Campos editables

| Campo | Editable | Motivo | Validación | Unicidad | Privacidad |
|---|---|---|---|---|---|
| `name` | ✅ Sí | Dato de perfil sin impacto en autenticación ni en URLs | No vacío tras `trim()`, longitud ≤ 120 (mismo límite que la columna) — reutiliza el criterio ya aplicado en `Register.jsx`/`auth_routes.py` | No | Privado hoy (`/me`); sería público en un futuro perfil público |
| `username` | ✅ Sí, máx. 1 cambio / 30 días (§Evolución futura) | Ya editable conceptualmente en la UI actual (`Profile.jsx`); no hay razón funcional para bloquearlo, pero sí para limitar su frecuencia (antiabuso, ver §Evolución futura) | Reutiliza `is_valid_username` (`^[a-zA-Z0-9_]{3,20}$`, `domain/auth/validators.py`) + verificación de `username_changed_at` | Sí — constraint `uq_users_username` (case-sensitive, mismo criterio que `ADR-002` §3) | Público por diseño (es el identificador social) |
| `phone` | ✅ Sí (junto con `country_code`, ver regla abajo) | Dato de perfil recolectado en registro; no interviene en login (que sigue siendo por email) | Reutiliza `is_valid_phone` (7–15 dígitos) | No (igual que hoy en `users`) | Privado — nunca expuesto en una futura API pública sin decisión explícita nueva |
| `country_code` | ✅ Sí (junto con `phone`) | Mismo motivo que `phone`; ambos representan un único dato lógico (teléfono internacional) | Reutiliza `is_valid_country_code` (`^\+[1-9]\d{0,3}$`) | No | Privado, igual que `phone` |
| `birth_date` | ✅ Sí | Recolectado en registro; sin mecanismo de verificación de identidad que lo vuelva "inmutable" hoy | Reutiliza `parse_birth_date` + `meets_minimum_age` (ISO válida, edad mínima 13 años) | No | Privado — nunca expuesto en una futura API pública |
| `email` | ❌ No (en esta versión) | Es el identificador de login; cambiarlo sin verificación permite secuestro de cuenta si el JWT de otra sesión sigue vivo, y rompe la garantía de "un email = una cuenta verificada" que hoy nadie verifica pero que un cambio silencioso debilitaría aún más. Se deja como decisión futura condicionada (§Evolución futura) | — | Ya única (`CITEXT`) | — |
| `password` / `password_hash` | ❌ No | Dato de seguridad, no de perfil — mismo argumento que `email`, más fuerte. Merece su propio endpoint (§Password) | — | — | Nunca se expone, nunca se acepta aquí |
| `bio` | ⏳ Futuro (no existe columna hoy) | Ver §Modelo de datos — se habilita cuando su propio ADR ratifique la columna | Texto plano, longitud acotada, sin HTML (§Evolución futura) | No | Público en un futuro perfil público |
| `avatar_url` | ⏳ Futuro, y **no** como string libre (ver §Evolución futura) | Requiere flujo de upload controlado antes de ser editable de forma segura | — | No | Público en un futuro perfil público |
| `id`, `created_at`, `updated_at` | ❌ No | Generados/gestionados por PostgreSQL (`gen_random_uuid()`, `DEFAULT now()`, trigger) — nunca por la aplicación | — | — | — |

---

## Reglas de validación

Todas reutilizan `domain/auth/validators.py` **tal como existen hoy** — este ADR no introduce reglas nuevas de formato, solo decide que se apliquen también en `PATCH`:

- `name`: no vacío tras `trim()`. (No hay validador dedicado hoy — `auth_routes.py` solo comprueba truthiness; `PATCH` hereda el mismo nivel de rigor, sin inventar uno nuevo.)
- `username`: `is_valid_username` (regex `^[a-zA-Z0-9_]{3,20}$`).
- `phone`: `is_valid_phone` (7–15 dígitos tras limpiar separadores).
- `country_code`: `is_valid_country_code` (regex `^\+[1-9]\d{0,3}$`).
- `birth_date`: `parse_birth_date` (ISO `yyyy-mm-dd` válida) + `meets_minimum_age` (≥ 13 años, mismo placeholder que `ADR-002` ya ratificó como regla real del servidor).

**`phone`/`country_code` como par atómico:** dado que representan un único dato lógico, `PATCH` debe exigir que si el body incluye uno, incluya el otro también (400 si llega solo uno) — evita guardar un `country_code` desincronizado del `phone` real.

## Reglas de unicidad

- `username`: la base de datos es la autoridad final (`uq_users_username`), igual que en `register`. Ante una violación de esa constraint durante un `UPDATE` concurrente, el patrón ya probado en `SQLAlchemyUserRepository.create()` (capturar `IntegrityError`, inspeccionar `constraint_name`, traducir a `UsernameAlreadyExistsError`) se replica en el método `update()` que este contrato requiere agregar al mismo repositorio — sin inventar un mecanismo de unicidad nuevo.
- **Concurrencia (dos requests simultáneos reclamando el mismo `username`):** exactamente uno gana el `UNIQUE` a nivel de PostgreSQL; el otro recibe `IntegrityError` → `409`. No se requiere locking optimista (columna de versión) para este caso — la constraint de base de datos ya es una garantía suficiente y atómica.
- `phone`/`email`: sin constraint de unicidad hoy (`phone` nunca la tuvo; `email` no es editable por este endpoint) — no se agrega ninguna en este ADR.

## Reglas de privacidad

Clasificación explícita de los datos de `users`, para cuando exista una API pública de perfil (no implementada, solo para guiar la separación por *presenter* de §Decisión):

| Categoría | Campos | Expuesto hoy en |
|---|---|---|
| Autenticación (nunca expuesto) | `password_hash` | Nada — ni `to_public_user()` lo incluye |
| Privado (solo el propio usuario, vía JWT) | `email`, `phone`, `country_code`, `birth_date` | `GET /api/users/me`, `register`, `login` (todos requieren ser el propio usuario o estar creando la cuenta) |
| Público (visible por cualquiera, cuando exista perfil público) | `id`, `name`, `username`, `bio`\*, `avatar_url`\* | Hoy: nada — no existe endpoint público. Futuro: un presenter nuevo, distinto de `to_public_user()` |

\* Pendientes de su propio ADR (§Modelo de datos).

`GET /api/users/me` sigue representando **exclusivamente** al usuario autenticado — este ADR no lo modifica. Una futura API pública de perfil (`GET /api/profiles/:username` o similar) es una decisión y un endpoint distintos, fuera de alcance aquí.

---

## Contrato PATCH

**Semántica general:**
- Solo los campos presentes en el body se modifican; los omitidos no se tocan (actualización parcial real, no un PUT disfrazado).
- `null` en cualquiera de los campos editables es inválido (`400`) — ninguna de las columnas editables hoy es nullable en el esquema; `PATCH` no puede usarse para "vaciar" un campo obligatorio.
- Un string vacío (`""`) en un campo editable es inválido (`400`) — mismo criterio que `register` (`not value` → falla la validación de "campo requerido").
- Un valor igual al actual es válido y se procesa igual que cualquier otro (no hay optimización de "no-op" — a esta escala no se justifica la complejidad de detectarlo).
- Campos no reconocidos en el body se ignoran silenciosamente (nunca se leen ni se pasan al modelo) — la ruta extrae explícitamente cada campo de la whitelist con `data.get(...)`, igual que `auth_routes.py` hace hoy; nunca se hace `**data` ni asignación masiva sobre el objeto `User`.
- Body vacío (`{}`) o sin ningún campo de la whitelist presente → `400` ("no se recibió ningún campo para actualizar"), mismo patrón que el `400` de "no se enviaron datos" en `register`/`login`.
- Atomicidad: un único `db.session.commit()` por request (igual que `SQLAlchemyUserRepository.create()`) — si varios campos vienen en el mismo `PATCH`, se persisten todos o ninguno.

### Request

```json
{
  "name": "string (opcional)",
  "username": "string (opcional)",
  "phone": "string (opcional, requiere country_code en el mismo body)",
  "country_code": "string (opcional, requiere phone en el mismo body)",
  "birth_date": "string ISO yyyy-mm-dd (opcional)"
}
```

Ejemplo mínimo válido — cambiar solo el username:
```json
{ "username": "nuevo_username" }
```

### Response

Mismo objeto público que `GET /api/users/me`, `register` y `login` — reutiliza `to_public_user()` sin crear un contrato paralelo:

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

### Errores

| Código | Causa | Body |
|---|---|---|
| `400` | Body vacío o sin ningún campo whitelisted; valor vacío/`null` en un campo editable; formato inválido (`username`/`phone`/`country_code`/`birth_date`); `phone` sin `country_code` o viceversa; edad resultante < 13 años | `{"msg": "..."}` |
| `401` | Sin `Authorization`, token inválido o expirado — mismo comportamiento ya homogeneizado en `app/extensions.py` para cualquier endpoint protegido | `{"msg": "..."}` |
| `403` | No aplica hoy — no existe ningún concepto de rol/permiso en el sistema (`API_CONTRACT.md` §2); no se documenta un caso de uso que no exista |
| `404` | El `id` del JWT no corresponde a ningún usuario real (mismo caso ya cubierto por `GET /me`, p. ej. cuenta borrada tras emitirse el token) | `{"msg": "..."}` |
| `409` | Conflicto de unicidad de `username` (constraint `uq_users_username`) | `{"msg": "..."}` |
| `422` | No aplica — este contrato no introduce ningún caso que produzca `422`; `flask_jwt_extended` ya se homogeneizó a `401` para tokens malformados (`extensions.py`) |
| `500` | Sin manejador global de excepciones (`API_CONTRACT.md` §3) — hueco heredado, no resuelto por este ADR |

---

## Seguridad

- Autenticación obligatoria: `@jwt_required()`, mismo patrón que `GET /api/users/me`.
- Identidad exclusivamente desde `get_jwt_identity()` — el `user_id` **nunca** se acepta del body, query string ni headers personalizados (mismo principio ya aplicado en `ADR-002` §3 para `/me`).
- **Whitelist explícita** de campos editables (§Campos editables) aplicada en la capa de `interfaces/routes/` o en el caso de uso — nunca asignación masiva (`**data`, `setattr` en bucle sobre las claves del body) sobre el modelo `User`. Esto es la defensa concreta contra mass assignment/overposting: aunque el cliente envíe `{"password_hash": "...", "id": "otro-uuid"}`, esos campos nunca se leen porque no están en la whitelist.
- `password_hash`, `id`, `created_at`, `updated_at`, `email` nunca se modifican por esta ruta bajo ninguna circunstancia — no hay "modo admin" ni excepción.
- La respuesta reutiliza `to_public_user()` — nunca puede filtrar `password_hash` porque esa función nunca lo incluye (misma garantía que ya protege a `register`/`login`/`me`).

## Password

**No se modifica mediante `PATCH /api/users/me`.** Es una decisión deliberada, no una omisión:
1. Cambiar contraseña es una operación de seguridad, no de perfil — mezclar sus errores/validaciones (contraseña actual, fuerza de la nueva) con los de `name`/`username` degradaría el contrato de ambos.
2. Un futuro endpoint dedicado (conceptual, **no implementado aquí**): `PATCH /api/users/me/password` o `POST /api/auth/change-password`, que exigiría `current_password` + `new_password` (+ `confirm_new_password`) y podría, en el futuro, invalidar sesiones/tokens existentes — una consecuencia que no tiene sentido para `name`/`username`.

---

## Evolución futura

- **`email`:** cambiar el email de una cuenta activa es, en la mayoría de productos, un flujo con verificación (enviar confirmación al email nuevo antes de aplicar el cambio). THERS no tiene hoy ningún mecanismo de envío de correo — implementarlo es una decisión de infraestructura nueva, fuera de alcance de este ADR. Cuando se decida, probablemente requiera una columna `pending_email` (o tabla de tokens de un solo uso, ya candidata en `DATABASE_ARCHITECTURE.md` §4.B) — no se prediseña aquí más allá de señalar que **no debe ser un campo más de este `PATCH`**.
- **`phone`:** si THERS decide en el futuro verificar teléfono por SMS, es la misma forma de problema que `email` — un flujo de verificación separado, no una edición directa. Este ADR no lo bloquea: `phone` sigue siendo editable sin verificación mientras el equipo no decida lo contrario.
- **`avatar_url`:** se recomienda explícitamente **no** aceptarlo como string de URL libre en `PATCH`, incluso cuando se ratifique la columna. Aceptar cualquier URL externa editable por el cliente abre riesgo de phishing/tracking (mostrar una imagen que apunta a un dominio no controlado) y no garantiza que la URL sea siquiera una imagen válida. El flujo recomendado para cuando se implemente:
  ```
  Frontend → POST /api/users/me/avatar (multipart/upload) → Backend valida
  y sube a almacenamiento controlado (propio o CDN) → Backend escribe
  avatar_url en users → Backend devuelve la URL final
  ```
  Es decir: `avatar_url` lo escribe siempre el backend, nunca el cliente directamente vía `PATCH`. Esto no se implementa aquí — se deja documentado para que la futura ratificación de `avatar_url` no reabra esta discusión de seguridad.
- **`bio`:** texto plano únicamente (recomendación por defecto de esta tarea, sin razón arquitectónica fuerte para HTML/Markdown). Sin sanitización de HTML porque no se acepta HTML — la superficie de XSS se cierra por diseño (nunca interpretar el campo como markup), no por sanitización posterior. Longitud acotada (placeholder `280`, igual de revisable que `MIN_AGE_YEARS`).
- **Cambios de `username`:** se **aprueba** un límite conceptual de **1 cambio cada 30 días** como regla de negocio, para no exponer desde el día uno un vector de abuso (username squatting/hijacking de menciones, relevante en cuanto existan URLs públicas `/@username` o `mentions`, `DATABASE_ARCHITECTURE.md` §4.B). **No se implementa en esta tarea.** Cuando se implemente `PATCH /api/users/me`, esta regla requiere una columna adicional (p. ej. `username_changed_at`, `TIMESTAMPTZ` nullable) — `updated_at` no sirve para esto porque cambia con cualquier campo, no solo `username`. Esa columna es una migración aditiva trivial (mismo patrón que `ADR-002`), a incluir en la misma tarea que implemente este contrato, no en un ADR nuevo — la regla de negocio ya queda decidida aquí.
- **`birth_date`:** editable sin restricción en esta versión porque no existe ningún mecanismo de verificación de identidad que la restricción pudiera respaldar. Si THERS introduce moderación basada en edad, permitir cambios ilimitados de `birth_date` debilita esa moderación — señalado como pendiente, no resuelto aquí.

---

## Impacto en Frontend

Lo que Frontend deberá hacer **después** de que este ADR se ratifique (no en esta tarea):
- Reemplazar `updateStoredUser()` en el flujo de "Editar perfil" de `Profile.jsx` por una llamada real a `PATCH /api/users/me`, actualizando `AuthContext` con la respuesta (mismo patrón que `login()` ya usa para `user`).
- Decidir la UX de error para `409` (username tomado) y `400` (formato inválido) reutilizando `getErrorMessage()` de `api.js`, extendiéndolo si hace falta un mensaje específico para conflicto de username (hoy `409` cae al mensaje genérico o al `data.msg` del backend — ya soportado por `api.js` desde el commit `199b587`).
- No tocar `bio`/`mood`/`interests`/`favoriteTrack` — siguen siendo locales hasta que exista su propio ADR de columnas.

## Impacto en Backend

Lo que Backend deberá hacer **después**:
- Migración aditiva para `users.username_changed_at` (`TIMESTAMPTZ`, nullable) — soporta la regla de 1 cambio/30 días ratificada en §Evolución futura; mismo patrón que `a1edcbff74d8_add_profile_fields_to_users.py`.
- Agregar `update()` al puerto `UserRepository` (`domain/auth/repositories.py`) y a `SQLAlchemyUserRepository`, replicando el manejo de `IntegrityError` ya probado en `create()`; el caso de uso rechaza el cambio de `username` con `429`/`400` (a definir en la implementación) si `username_changed_at` es menor a 30 días.
- Nuevo caso de uso `application/auth/update_profile_use_case.py` (o nombre equivalente) que reciba solo los campos ya validados por la ruta — mismo patrón de "la ruta valida formato, el caso de uso orquesta" que `register`/`me` ya siguen.
- Nueva ruta `PATCH /users/me` en `interfaces/routes/user_routes.py` (mismo blueprint que `GET /me`, ya protegido), aplicando la whitelist de §Campos editables.
- Documentar el endpoint en `API_CONTRACT.md` el mismo día del PR que lo implemente (`HB-001` §15.1) — este ADR no reemplaza esa obligación.

## Impacto en Base de Datos

Ninguno inmediato — no se agregan columnas ni migraciones en esta decisión. El único impacto futuro (cuando `bio`/`avatar_url` se ratifiquen) es una migración aditiva simple, descrita en §Modelo de datos.

## Compatibilidad futura

| Funcionalidad futura | ¿Esta decisión la dificulta? |
|---|---|
| OAuth | No — `email`/`password_hash` permanecen en `users`, sin cambios; OAuth se modela con `oauth_accounts` referenciando a `users` (ya candidata en `DATABASE_ARCHITECTURE.md` §4.B), independiente de este contrato |
| Recuperación de contraseña | No — password sigue fuera de `PATCH /me`, con su propio endpoint conceptual futuro |
| Verificación de email/teléfono | No — ambos quedan explícitamente fuera de este `PATCH`, dejando espacio para su propio flujo (§Evolución futura) |
| Perfiles públicos | No — la separación público/privado se resuelve por *presenter* (§Decisión), no por el modelo de datos; no hay que deshacer nada |
| Búsqueda por username | No — `username` ya es único e indexado (`uq_users_username`) |
| Seguidores/bloqueo/reportes | No — son tablas puente futuras que referencian `users.id`; no dependen de cómo se edite el perfil |
| Moderación | Parcialmente abierto — depende de decisiones de producto no tomadas (p. ej. restricción de cambios de `birth_date`), señaladas como pendientes, no bloqueadas por esta decisión |
| Auditoría | No — `updated_at` con trigger ya registra la última modificación; un historial completo de cambios sería una entidad futura (`DATABASE_ARCHITECTURE.md` §4.B, `security_events`), no afectada por esta decisión |

## Migraciones futuras

- **Ninguna en esta tarea.**
- Cuando `bio`/`avatar_url` se ratifiquen: una migración aditiva (`op.add_column`, nullable con default), sin backfill — mismo patrón y mismo razonamiento que `a1edcbff74d8_add_profile_fields_to_users.py` (`ADR-002`): no hay todavía una base compartida por el equipo con datos reales que migrar, solo `thers_dev`/`thers_test` locales reconstruibles.
- **Riesgo a vigilar cuando eso deje de ser cierto** (haya una base compartida/producción con usuarios reales): en ese momento, agregar columnas `NOT NULL` sin default ya no será seguro sin backfill — la migración futura deberá agregarlas como nullable o con un `server_default` explícito.

## Riesgos

- **Riesgo de UX:** si Frontend no actualiza `Profile.jsx` al mismo tiempo que Backend implementa este contrato, el bug ya detectado (edición local que se pierde en F5) persiste — este ADR no lo corrige por sí solo, solo lo habilita.
- **Riesgo de unicidad bajo concurrencia:** mitigado por constraint de base de datos (§Reglas de unicidad), pero requiere que la implementación futura realmente capture `IntegrityError` — si se omite, un conflicto de `username` produciría un `500` no controlado en vez de un `409`.
- **Riesgo de mass assignment:** mitigado por whitelist explícita — si una implementación futura usa `**data` "por conveniencia", reintroduce el riesgo que este ADR previene. Debe marcarse en code review.
- **Riesgo de alcance de `avatar_url`:** si se implementa como string libre "temporalmente, para no bloquear" sin el flujo de upload, se introduce el riesgo de seguridad ya señalado en §Evolución futura.

## Decisiones pendientes

- Si `birth_date` debería tener alguna restricción de cambio una vez establecida (no se resuelve; no hay verificación de identidad que lo respalde hoy — a diferencia de `username`, aquí no hay una regla de negocio evidente que ratificar sin esa verificación).
- Flujo de verificación de `email` y de `phone` (fuera de alcance; ninguno se implementa).
- Arquitectura de upload de `avatar_url` (almacenamiento propio vs CDN externo) — solo se fija que no es un campo de texto libre en `PATCH`.
- Formato de error estándar de toda la API (`API_CONTRACT.md` §9 ítem 1) — este contrato usa `{"msg": "..."}` por consistencia con lo existente, no porque el formato esté cerrado.
- Umbral exacto de longitud de `bio` (280 es un placeholder, igual que `MIN_AGE_YEARS` lo fue para edad mínima).

## Consecuencias

- `users` permanece como la única entidad del dominio de identidad/perfil — ninguna tabla nueva nace de este ADR.
- El día que se implemente, `PATCH /api/users/me` podrá editar `name`, `username`, `phone`+`country_code`, `birth_date` — nunca `email`, `password`, ni columnas que no existan todavía.
- `bio`/`avatar_url` siguen bloqueadas hasta su propio ADR — este documento no las habilita, solo prepara su llegada (tipos propuestos, regla de que `avatar_url` no será editable como texto libre).
- La separación "privado vs público" queda resuelta arquitectónicamente por *presenter*, no por tabla — cualquier implementación futura de perfil público debe seguir ese patrón, no reabrir la discusión `users` vs `profiles`.
- `API_CONTRACT.md`, `DATABASE_ARCHITECTURE.md` y `FRONTEND_ARCHITECTURE.md` deberán actualizarse el mismo día que este contrato se implemente (`HB-001` §15.1) — no antes, no como parte de este ADR.

## Referencias

- `CLAUDE.md` (raíz) — jerarquía de fuentes (§4), regla de alcance (§14), reglas específicas para Claude Code (§8).
- `docs/architecture/ADR-002-user-profile-fields.md` — precedente directo: mismo tipo de decisión (columnas simples de perfil vs entidad separada), misma conclusión (extender `users`), mismo proceso.
- `docs/architecture/API_CONTRACT.md` §4, §5, §6, §9 — contrato actual de `register`/`login`/`me`, formato de error, pendientes heredados.
- `docs/architecture/DATABASE_ARCHITECTURE.md` §4.B, §5, §7, §11, §14 — estado de `bio`/`avatar_url` como candidatas, convenciones de nombres de índice/constraint, hallazgo de `JWT_SECRET_KEY` (contradicho por el código real, ver §Estado actual).
- `docs/architecture/BACKEND_ARCHITECTURE.md` §17 — regla de capas (`domain/` sin SQLAlchemy/Flask).
- Código real: `backend/app/infrastructure/persistence/models.py`, `backend/migrations/versions/a1b2c3d4e5f6_create_users_table.py`, `backend/migrations/versions/a1edcbff74d8_add_profile_fields_to_users.py`, `backend/app/domain/auth/*.py`, `backend/app/application/auth/*.py`, `backend/app/infrastructure/persistence/repositories/user_repository.py`, `backend/app/interfaces/routes/*.py`, `backend/app/extensions.py`, `backend/app/config.py`; `Frontend/src/features/auth/context/AuthContext.jsx`, `Frontend/src/features/feed/pages/Profile.jsx`, `Frontend/src/features/auth/lib/validators.js`.
- Auditoría técnica previa (misma sesión de trabajo, 2026-08-28) — origen del hallazgo de UX que motiva §Problema.

---

## Cierre

Este documento **no implementa** ningún código, migración ni endpoint: define el contrato futuro de `PATCH /api/users/me` y ratifica que `users` sigue siendo la única entidad de identidad/perfil de THERS, extendiéndose por columnas simples cuando se justifiquen — mismo criterio que `ADR-002` ya validó. La separación entre datos privados y públicos, necesaria para cuando existan perfiles públicos, se resuelve por capa de presentación (*presenter*), no por división de tablas. Cualquier implementación futura de este contrato sigue el proceso de `HB-001` §11–12 igual que cualquier cambio de impacto medio/alto — este ADR es la decisión previa que lo habilita, no la implementación en sí.
