# ADR-006 — Modelo mínimo de `comments` sobre `posts`

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/ADR-006-comments-minimal-model.md` |
| Tipo | Architecture Decision Record (`HB-001` §11–12) |
| Fecha | 10/09/2026 |
| Estado | **Aceptada** — implementada en esta tarea (ver §Decisión) |
| Alcance | `backend/` — nueva entidad `comments`, `POST`/`GET /api/posts/<post_id>/comments`, extensión aditiva de `GET`/`POST /api/posts` |
| Autoridad sobre este documento | `/docs` oficial > estructura real observada en el código > este documento (mismo orden que `CLAUDE.md` §4) |

> ⚠️ **Regla de alcance, explícita — mismo criterio que `ADR-004`/`ADR-005`.** `DATABASE_ARCHITECTURE.md` §4.B registra "Comentarios + Respuestas a comentarios" como **una sola** candidata (`comments` auto-referencial, respuesta = comentario con `parent_comment_id`). Este ADR implementa deliberadamente **solo la mitad plana**: comentar un post. Las respuestas a comentarios (`parent_comment_id`, hilos) quedan explícitamente fuera — se resuelven en un ADR futuro si el producto los necesita, igual que `ADR-005` dejó fuera los tipos de reacción de `reactions`.

---

## Contexto

Con `posts` (`ADR-004`) y `likes` (`ADR-005`) ya ratificados, comentar un post es la siguiente pieza de interacción social más pequeña que sigue sin ratificar. `DATABASE_ARCHITECTURE.md` §4.B la registra como OBJETIVO desde su primera versión.

## Problema

Definir el modelo **mínimo** que permite que un usuario autenticado comente un post existente, en texto plano, y que otros usuarios lean esos comentarios — sin hilos de respuestas, sin edición/borrado, sin menciones dentro del comentario.

## Objetivos

- Un usuario autenticado puede comentar un post existente con texto plano.
- Existe un endpoint para listar los comentarios de un post, en orden cronológico (más antiguo primero — mismo criterio de lectura natural de un hilo de comentarios).
- `GET`/`POST /api/posts` exponen `comments_count` por post (extensión aditiva, mismo patrón que `likes_count` en `ADR-005`), para que el feed muestre cuántos comentarios tiene cada post sin tener que pedirlos todos.
- El modelo se mantiene deliberadamente pequeño — mismo principio que `ADR-002`/`ADR-003`/`ADR-004`/`ADR-005`.

## No objetivos (explícitamente fuera de este ADR)

- **No** implementa respuestas a comentarios (`parent_comment_id`, hilos anidados) — la candidata combinada de `DATABASE_ARCHITECTURE.md` §4.B se resuelve solo a medias aquí; la otra mitad queda para un ADR futuro y acotado.
- **No** implementa edición ni borrado de comentarios — mismo criterio que `ADR-004` ya aplicó a `posts`.
- **No** implementa menciones (`@usuario`) dentro de un comentario — sigue como candidata separada (`mentions`, `DATABASE_ARCHITECTURE.md` §4.B).
- **No** implementa notificaciones ("a X le comentaron su post") — mismo criterio que `ADR-005` §No objetivos.
- **No** implementa paginación real — límite fijo pragmático, mismo patrón que `posts`/`likes`.
- **No** cambia nada de `likes` — ambas entidades son independientes, cada una referencia a `posts`, no entre sí.

## Opciones consideradas — orden de listado

| Opción | Descripción | Trade-off |
|---|---|---|
| **A — Cronológico ascendente, más antiguo primero (elegida)** | `GET .../comments` devuelve los comentarios en el orden en que se escribieron | Es como se lee una conversación real — el primer comentario da contexto a los que siguen; mismo criterio que la mayoría de UIs de comentarios (no de feeds, que van al revés) |
| B — Más reciente primero (igual que el feed de posts) | Mismo orden que `GET /api/posts` | Coherente con el resto de la API, pero rompe la lectura de una conversación — el último comentario sin contexto de los anteriores |

**Elegida: A.** Un post y un comentario no son la misma clase de lista — el feed es "qué hay de nuevo", un hilo de comentarios es "qué se dijo, en orden".

## Decisión

Se crea una única entidad, `comments`, extendiendo el mismo patrón ya usado para `posts`/`likes` (Repository con puerto en `domain/`, adaptador en `infrastructure/`, composition root en `interfaces/routes/`).

### Modelo de datos

| Columna | Tipo | Nulo | Justificación |
|---|---|---|---|
| `id` | `UUID`, `DEFAULT gen_random_uuid()` | No (PK) | Mismo patrón que `users.id`/`posts.id`/`likes.id` |
| `post_id` | `UUID`, FK → `posts.id` | No | Post comentado |
| `author_id` | `UUID`, FK → `users.id` | No | Autor del comentario — siempre `get_jwt_identity()`, nunca un valor del body (mismo principio que `posts.author_id`) |
| `content` | `TEXT` | No | Texto del comentario. Longitud máxima placeholder: **1000 caracteres** — más corto que el límite de `posts` (2000, `ADR-004`) por ser un placeholder de producto pragmático y revisable, no una regla derivada |
| `created_at` | `TIMESTAMPTZ`, `DEFAULT now()` | No | Define el orden del hilo |
| `updated_at` | `TIMESTAMPTZ`, `DEFAULT now()`, mantenida por trigger | No | Convención de auditoría (misma que `posts`) — sin uso funcional todavía porque no hay edición (§No objetivos) |

**Claves foráneas.** `post_id → posts.id` y `author_id → users.id`, ambas `ON DELETE CASCADE` — mismo placeholder que `ADR-004`/`ADR-005` ya aceptaron (borrado de cuenta/post no existe todavía como funcionalidad).

**Índice:** `ix_comments_post_id_created_at` (compuesto) — justificado directamente por `GET .../comments` (`WHERE post_id = ... ORDER BY created_at ASC`), mismo criterio de "sin índices especulativos" que `ADR-004`/`ADR-005`.

### Contrato API (documentado el mismo día en `API_CONTRACT.md` §4.5, `HB-001` §15.1)

**`POST /api/posts/<post_id>/comments`** — crea un comentario. Auth requerida.
```json
// Request
{ "content": "string (1–1000 caracteres tras trim)" }

// Response 201
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
- Whitelist explícita: solo `content` se lee del body — nunca `post_id`/`author_id`/`id` (`post_id` viene de la URL, no del body).
- `400` si `content` está vacío/ausente o excede 1000 caracteres. `401` si falta o es inválido el JWT. `404` si `post_id` no corresponde a ningún post real (mismo criterio que `ADR-005`: el conversor `uuid` de Flask ya cubre el caso de formato inválido).

**`GET /api/posts/<post_id>/comments`** — lista los comentarios de un post. Auth requerida (mismo criterio que el resto del feed).
```json
// Response 200
{ "comments": [ { "id", "post_id", "author": {...}, "content", "created_at" }, ... ] }
```
- Orden: `created_at` ascendente (§Opciones consideradas). Límite fijo (placeholder: **100** comentarios). `404` si `post_id` no existe.

**`GET`/`POST /api/posts` — extensión aditiva:** cada post gana `comments_count` (entero), junto al `likes_count`/`liked_by_me` que `ADR-005` ya agregó. No rompe el contrato existente.

### Seguridad

Mismo patrón ya establecido y probado en `auth`/`users`/`posts`/`likes`:
- Identidad del autor exclusivamente de `get_jwt_identity()`.
- Whitelist explícita en la route, nunca `**data`.
- El autor se expone con la misma forma reducida que `posts.author` — nunca `email`/`password_hash`/otros campos privados.

## Impacto en Frontend

- `CapsuleCard.jsx` gana un control de comentarios (ícono + contador, mismo lenguaje visual que el botón de like) que expande un panel inline con la lista de comentarios (`GET .../comments`) y un campo para publicar uno nuevo (`POST .../comments`) — sin vista de hilo/respuestas, cada comentario es una fila plana.
- `AppShell.jsx` no necesita cargar comentarios de antemano (a diferencia de `likes_count`, que viaja con cada post) — se piden bajo demanda cuando el usuario abre el panel de un post, para no traer comentarios de posts que nadie abre.

## Impacto en Backend

- Nueva migración aditiva (`comments`, FKs a `posts`/`users`).
- `domain/comments/` (nuevo): puerto `CommentRepository`, `validators.py` (`is_valid_content`, `MAX_CONTENT_LENGTH = 1000`).
- `application/comments/`: `create_comment_use_case.py`, `list_comments_use_case.py`, `comment_presenter.py`.
- `application/posts/list_posts_use_case.py`/`post_presenter.py`: extendidos con `comments_count` (una consulta agregada más, mismo patrón que `likes_count`).
- `infrastructure/persistence/repositories/comment_repository.py`: `SQLAlchemyCommentRepository`.
- `interfaces/routes/comment_routes.py` (nuevo blueprint `comments_bp`).
- Tests de integración, mismo patrón que `test_likes.py`.

## Riesgos

- **Desincronización de conteo:** `comments_count` se calcula con `COUNT(*)` en cada `GET /api/posts`, igual que `likes_count` — mismo riesgo aceptado y mismo criterio de "optimizar cuando el volumen lo justifique" (`ADR-005` §Riesgos).
- **Sin moderación:** cualquier usuario autenticado puede comentar cualquier post, sin límite de longitud más allá del placeholder y sin revisión — aceptado como limitación conocida de v1, coherente con que `posts` tampoco tiene moderación todavía.

## Decisiones pendientes (quedan fuera, cada una es su propio ADR futuro)

- Respuestas a comentarios (`parent_comment_id`, hilos anidados).
- Edición/borrado de comentarios.
- Menciones dentro de comentarios.
- Notificaciones de "te comentaron".
- Paginación real de comentarios (hoy límite fijo de 100).

## Consecuencias

- `comments` es la tercera entidad del alcance objetivo del producto (`DATABASE_ARCHITECTURE.md` §4.B) en pasar de OBJETIVO a ratificada, después de `posts` y `likes`.
- `DATABASE_ARCHITECTURE.md`, `DATABASE_ERD.md` y `API_CONTRACT.md` se actualizan el mismo día que este contrato se implementa (`HB-001` §15.1).

## Referencias

- `CLAUDE.md` — jerarquía de fuentes (§4), regla de alcance (§14), reglas específicas para Claude Code (§8).
- `docs/architecture/ADR-004-posts-minimal-model.md`, `ADR-005-likes-minimal-model.md` — mismo proceso, mismo criterio de extender por entidades simples en vez de sobre-modelar de una vez.
- `docs/architecture/DATABASE_ARCHITECTURE.md` §3 (principios de diseño, normalización), §4.B (candidata combinada "Comentarios + Respuestas"), §8 (índices, sin especulación).
- `docs/architecture/organization/01_Manual_Organizacion/Source/HB-001-manual-organizacion.md.md` §11 (clasificación de impacto de decisiones), §15.1 (documentar endpoints el mismo día del PR).

---

## Cierre
