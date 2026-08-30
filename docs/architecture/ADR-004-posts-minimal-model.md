# ADR-004 — Modelo mínimo de `posts` para conectar el feed a datos reales

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/ADR-004-posts-minimal-model.md` |
| Tipo | Architecture Decision Record (`HB-001` §11–12) |
| Fecha | 29/08/2026 |
| Estado | **Aceptada** — confirmada explícitamente por el usuario en la misma sesión de trabajo con IA, mismo criterio de excepción de proceso ya aplicado en `ADR-002`/`ADR-003` |
| Alcance | `backend/` (nueva entidad `posts`, endpoints `POST`/`GET /api/posts`) — implementado en esta tarea. Impacto de contrato en `Frontend/` (`Home.jsx`, `CreateCapsuleFlow.jsx`) queda para una tarea de Frontend aparte (ver informe de la tarea) |
| Autor | Sesión de arquitectura con IA, confirmada explícitamente por el usuario antes de implementar |
| Autoridad sobre este documento | `/docs` oficial > estructura real observada en el código > este documento (mismo orden que `CLAUDE.md` §4) |

> ⚠️ **Nota de proceso.** `HB-001` §11 clasifica "cambiar el modelo de datos" como decisión de **alto impacto**, que en teoría requiere consenso del Comité Técnico completo (los 4 integrantes). Este documento sigue la misma excepción pragmática ya aplicada en `ADR-001`/`ADR-002`/`ADR-003`: se redactó en sesión de trabajo con IA, quedó como **Propuesta**, y el usuario confirmó explícitamente el alcance exacto descrito abajo (feed global sin `follows`, solo texto, sin medios/reacciones/comentarios) antes de que se implementara ningún código — recién ahí pasó a **Aceptada**.
>
> **Regla de alcance, explícita.** Este ADR decide deliberadamente **lo mínimo indispensable** para que el feed deje de ser 100% mock: una sola entidad, dos endpoints, un solo campo de contenido. Todo lo que la UI mock ya muestra (mood, imagen, hashtags, ubicación, likes, comentarios) queda **fuera de alcance a propósito** — cada uno es su propia entidad candidata en `DATABASE_ARCHITECTURE.md` §4.B, y modelarlos todos juntos en un solo ADR repetiría exactamente el error que ese documento ya previene ("una funcionalidad no equivale a una tabla", §3: normalización).

---

## Contexto

`/feed`, `/discover`, `/messages`, `/notifications` son hoy 100% mock — `Frontend/src/features/feed/data/mockData.js`, consumido como estado local en `AppShell.jsx` (`useState(mockCapsules)`). `DATABASE_ARCHITECTURE.md` §4.B registra `posts` como **OBJETIVO** (confirmado como parte del alcance funcional, sin modelado ratificado) desde la primera versión de ese documento. El equipo confirmó que quiere avanzar en conectar el feed a datos reales ahora, priorizándolo sobre otras vías (verificación de email/teléfono).

**Lo que la UI mock ya asume sobre una "Cápsula" (post)** — `mockCapsules` en `mockData.js` — es mucho más rico de lo que este ADR va a ratificar: `type` (photo/thought/music/mood/video), `mood`, `image`, `text`, `hashtags`, `location`, `likes` (número), `comments` (array con autor+texto). Intentar modelar todo eso de una vez sería exactamente la sobre-ingeniería que `CLAUDE.md` §6 y `DATABASE_ARCHITECTURE.md` §3 piden evitar — cada pieza es una decisión de modelado propia (¿`reactions` es su tabla? ¿`comments` es auto-referencial para respuestas? ¿cómo se sube una imagen?), listada por separado en `DATABASE_ARCHITECTURE.md` §4.B.

## Problema

Definir el modelo **mínimo** de `posts` que permite que un usuario autenticado publique texto real y lo vea en un feed respaldado por PostgreSQL — sin bloquear esa primera entrega en decisiones que no son indispensables para ella (medios, reacciones, comentarios, hashtags, mood, ubicación, seguir/seguidores).

## Objetivos

- Un usuario autenticado puede crear un post de **solo texto** y que quede persistido en `posts` (PostgreSQL real, mismo patrón Repository que `users`).
- Existe un endpoint para listar posts recientes, ya respaldado por datos reales — el punto de partida para que `Home.jsx` dependa de un backend real en vez de `mockCapsules`.
- El modelo se mantiene deliberadamente pequeño: solo lo que esta funcionalidad concreta justifica (mismo principio que `ADR-002`/`ADR-003` ya aplicaron a `users`).

## No objetivos (explícitamente fuera de este ADR)

- **No** implementa reacciones/likes, comentarios, hashtags, mood, ubicación ni ningún tipo de media (imagen/video/audio) — cada uno queda como su propia entidad candidata en `DATABASE_ARCHITECTURE.md` §4.B, a resolver en un ADR futuro y acotado, mismo patrón que este.
- **No** implementa `follows` — no existe todavía ninguna relación "seguir" en el sistema (`DATABASE_ARCHITECTURE.md` §4.B, `OBJETIVO`, sin ratificar). El feed de este ADR **no puede** filtrar por seguidos porque esa entidad no existe — ver §Decisión, opción elegida.
- **No** implementa edición ni borrado de posts, ni visibilidad (`visibility`) — un post creado es público y permanente en esta primera versión.
- **No** implementa paginación real (cursor/offset) — `API_CONTRACT.md` §2 ya registra la paginación como pendiente de definición a nivel general; este ADR no la resuelve, usa un límite fijo pragmático (ver §Contrato).
- **No** toca `Discover`, `Messages`, `Notifications`, `Settings` — siguen 100% mock después de este ADR.

## Opciones consideradas — alcance del feed sin `follows`

| Opción | Descripción | Trade-off |
|---|---|---|
| **A — Feed global (elegida)** | `GET /api/posts` devuelve los posts de **todos** los usuarios, ordenados por fecha descendente, sin filtrar por relación social | Coherente con que `follows` no existe todavía; es exactamente lo que `mockCapsules` ya simula hoy (una mezcla de personas, no solo seguidos); simple de implementar y de probar |
| B — Solo mis propios posts | `GET /api/posts` solo devuelve los del usuario autenticado | Trivial de implementar, pero no prueba nada útil como "feed" — nadie más aparece |
| C — Esperar a tener `follows` | No implementar el feed hasta ratificar `follows` en un ADR previo | Bloquea indefinidamente el avance que el equipo pidió; `follows` es una decisión propia con su propio trade-off (política `ON DELETE`, tabla puente) que no debería mezclarse con la de `posts` |

**Elegida: A.** Es la que da valor real hoy sin inventar una relación social que no existe, y es la migración más simple el día que `follows` se ratifique (agregar un `WHERE author_id IN (...)` no cambia el modelo de `posts`).

## Decisión

Se crea una única entidad, `posts`, extendiendo el mismo patrón ya usado para `users` (Repository con puerto en `domain/`, adaptador en `infrastructure/`, composition root en `interfaces/routes/`).

### Modelo de datos

| Columna | Tipo | Nulo | Justificación |
|---|---|---|---|
| `id` | `UUID`, `DEFAULT gen_random_uuid()` | No (PK) | Mismo patrón que `users.id` — generado en PostgreSQL, nunca en Python |
| `author_id` | `UUID`, FK → `users.id` | No | Autor del post — siempre `get_jwt_identity()`, nunca un valor del body (mismo principio que `PATCH /api/users/me`, `ADR-003` §Seguridad) |
| `content` | `TEXT` | No | Texto del post. Longitud máxima placeholder: **2000 caracteres** — mismo criterio pragmático que `MIN_AGE_YEARS`/`MIN_PASSWORD_LENGTH`, revisable |
| `created_at` | `TIMESTAMPTZ`, `DEFAULT now()` | No | Define el orden del feed |
| `updated_at` | `TIMESTAMPTZ`, `DEFAULT now()`, mantenida por trigger | No | Mismo patrón que `users` (`set_updated_at`) — sin uso funcional todavía porque no hay edición (ver No objetivos), pero es la convención estándar de auditoría ya establecida (`DATABASE_ARCHITECTURE.md` §7) |

**Clave foránea.** `author_id → users.id`. Política `ON DELETE`: **`CASCADE`** (si se borra un usuario, se borran sus posts) — placeholder razonable dado que borrado de cuenta tampoco existe todavía como funcionalidad (`DATABASE_ARCHITECTURE.md` §4.B lo marca `PENDIENTE DE DECISIÓN`); revisar cuando esa funcionalidad se ratifique.

**Índice:** `ix_posts_created_at` (o compuesto con `author_id` si en el futuro se necesita filtrar por autor) — se agrega solo si `GET /api/posts` lo justifica en la implementación real, siguiendo el mismo principio de "sin índices especulativos" (`DATABASE_ARCHITECTURE.md` §8).

### Contrato API (a documentar en `API_CONTRACT.md` el mismo día de la implementación, `HB-001` §15.1)

**`POST /api/posts`** — crea un post. Auth requerida (`@jwt_required()`).
```json
// Request
{ "content": "string" }

// Response 201
{
  "post": {
    "id": "string (UUID)",
    "author": { "id": "string (UUID)", "username": "string", "name": "string" },
    "content": "string",
    "created_at": "string (ISO 8601)"
  }
}
```
- Whitelist explícita: solo `content` se lee del body — nunca `author_id`, `id`, `created_at` (mismo patrón anti mass-assignment que `PATCH /api/users/me`).
- `400` si `content` está vacío/ausente o excede 2000 caracteres. `401` si falta o es inválido el JWT.

**`GET /api/posts`** — lista posts recientes. Auth requerida (mismo criterio que el resto de rutas del feed hoy — `AppShell` solo es alcanzable dentro de `ProtectedRoute`).
```json
// Response 200
{ "posts": [ { "id", "author": {...}, "content", "created_at" }, ... ] }
```
- Orden: `created_at DESC`.
- Límite fijo (placeholder: **50** posts más recientes) — sin paginación real en esta versión (ver No objetivos).

### Seguridad

Mismo patrón ya establecido y probado en `auth`/`users`:
- Identidad del autor exclusivamente de `get_jwt_identity()`.
- Whitelist explícita en la route, nunca `**data`.
- `to_public_author()` (o reutilizar una forma reducida de `to_public_user()`) para que la respuesta nunca exponga `email`, `password_hash` ni otros campos privados del autor — solo `id`/`username`/`name`.

## Impacto en Frontend

Lo que Frontend haría **después** de que este ADR se ratifique (no en este documento):
- `Home.jsx` consumiría `GET /api/posts` real, probablemente mezclado con (o reemplazando gradualmente a) `mockCapsules`.
- `CreateCapsuleFlow.jsx` necesitaría una ruta reducida que solo envíe `content` a `POST /api/posts` — sus campos de `mood`/imagen/hashtags/ubicación **no tendrían dónde persistirse** todavía y deberían quedar deshabilitados o seguir siendo puramente decorativos hasta sus propios ADRs.
- `CapsuleCard.jsx` tendría que tolerar posts reales sin `mood`/`image`/`hashtags`/`likes`/`comments` — requiere ajuste de UI, no solo de datos.
- `Discover`, `Messages`, `Notifications` no cambian.

## Impacto en Backend

- Nueva migración aditiva (`posts`, con la FK a `users`).
- `domain/posts/` (nuevo): validación de `content` (longitud, no vacío) — mismo patrón que `domain/auth/validators.py`.
- `application/posts/`: `create_post_use_case.py`, `list_posts_use_case.py`.
- `infrastructure/persistence/repositories/post_repository.py`: `SQLAlchemyPostRepository`.
- `interfaces/routes/post_routes.py` (nuevo blueprint `posts_bp`).
- Tests de integración, mismo patrón que `test_update_profile.py`.

## Riesgos

- **Desajuste de UI:** `CapsuleCard.jsx` está diseñado para el objeto rico de `mockCapsules` — conectar `GET /api/posts` real sin adaptar ese componente puede romper el render (campos `undefined`). Se reporta aquí para que la implementación lo contemple, no se resuelve en este documento.
- **Feed no personalizado:** sin `follows`, todo usuario ve los posts de todos — aceptado como limitación conocida de v1 (§Opciones), no un descuido.
- **`ON DELETE CASCADE` como placeholder:** si el equipo decide más adelante que borrar una cuenta debe conservar sus posts (borrado lógico del usuario, posts anonimizados, etc.), esta política cambia — señalado, no bloqueante hoy porque no existe borrado de cuenta.

## Decisiones pendientes (quedan fuera, cada una es su propio ADR futuro)

- Reacciones/likes (`DATABASE_ARCHITECTURE.md` §4.B — candidata `reactions`).
- Comentarios (`comments`, auto-referencial para respuestas).
- Hashtags (`hashtags` + `post_hashtags`).
- Medios: imagen/video/audio — requiere decisión de almacenamiento (mismo tipo de decisión que `ADR-003` ya dejó pendiente para `avatar_url`: nunca aceptar URL libre del cliente).
- `mood`, `location` como columnas de `posts` (o su propia forma).
- `follows` — de quién es el feed.
- Edición/borrado de posts, visibilidad.
- Paginación real.

## Consecuencias

- `posts` seria la primera entidad del alcance objetivo del producto (`DATABASE_ARCHITECTURE.md` §4.B) en pasar a ratificada, sentando el patrón de capas (Repository/UseCase/Route) para toda entidad social futura — el mismo que `users` ya validó.
- El feed deja de ser 100% mock, aunque con una fracción pequeña de lo que la UI mock aparenta hoy — se comunica así al equipo para evitar la expectativa de que "conectar el feed" signifique portar `mockCapsules` completo de una sola vez.
- `DATABASE_ARCHITECTURE.md`, `DATABASE_ERD.md` y `API_CONTRACT.md` deberán actualizarse el mismo día que este contrato se implemente (`HB-001` §15.1) — no antes, no como parte de este ADR.

## Referencias

- `CLAUDE.md` — jerarquía de fuentes (§4), regla de alcance (§14), reglas específicas para Claude Code (§8).
- `docs/architecture/DATABASE_ARCHITECTURE.md` §3 (principios de diseño, normalización), §4.B (Contenido — `posts`, `media`; candidatas relacionadas), §4.C (nada se implementa sin ADR), §8 (índices).
- `docs/architecture/ADR-002-user-profile-fields.md` y `ADR-003-profile-update-contract.md` — mismo proceso, mismo criterio de extender por columnas/entidades simples en vez de sobre-modelar de una vez.
- `docs/architecture/organization/01_Manual_Organizacion/Source/HB-001-manual-organizacion.md.md` §11 (clasificación de impacto de decisiones).
- Código real: `Frontend/src/features/feed/data/mockData.js` (`mockCapsules` — forma que la UI ya asume), `Frontend/src/app/layout/AppShell.jsx` (estado mock actual del feed).

---

## Cierre

Este documento define el contrato mínimo de `posts` necesario para que el feed deje de ser 100% mock, dejando explícitamente fuera — y listado — todo lo que la UI mock ya sugiere pero que corresponde a decisiones de modelado separadas. **Aceptada e implementada en esta misma tarea** (backend: migración, capas `domain`/`application`/`infrastructure`/`interfaces`, tests de integración) tras la confirmación explícita del usuario — el impacto en `Frontend/` (§Impacto en Frontend) queda para una tarea de Frontend aparte, no incluida aquí.
