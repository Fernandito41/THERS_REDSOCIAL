# ADR-007 — Modelo mínimo de `follows` (seguir / dejar de seguir)

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/ADR-007-follows-minimal-model.md` |
| Tipo | Architecture Decision Record (`HB-001` §11–12) |
| Fecha | 10/09/2026 |
| Estado | **Aceptada** — implementada en esta tarea (ver §Decisión) |
| Alcance | `backend/` — nueva entidad `follows`, `POST`/`DELETE /api/users/<user_id>/follow`, extensión aditiva de `GET`/`PATCH /api/users/me` y de `GET`/`POST /api/posts` |
| Autoridad sobre este documento | `/docs` oficial > estructura real observada en el código > este documento (mismo orden que `CLAUDE.md` §4) |

> ⚠️ **Regla de alcance, explícita — mismo criterio que `ADR-004`/`ADR-005`/`ADR-006`.** `DATABASE_ARCHITECTURE.md` §4.B registra "Seguir, Dejar de seguir, Seguidores, Seguidos" como **una sola** candidata (`follows`, tabla puente auto-referencial `users`↔`users`). Este ADR implementa esa tabla puente y sus contadores. Deliberadamente **no** personaliza el feed (`GET /api/posts` sigue siendo global, `ADR-004` §Opciones consideradas) — esa es una decisión de producto propia con trade-offs reales (¿qué ve un usuario nuevo con cero seguidos?) que merece su propia conversación, no un efecto colateral silencioso de este ADR.

---

## Contexto

Con `posts`, `likes` y `comments` ya ratificados, "seguir a alguien" es la pieza que falta para que el vínculo social entre usuarios exista en el backend — hoy el botón "Seguir" del Frontend (`Home.jsx`, panel de sugerencias) es un `Set` en memoria (`AppShell.jsx`, `followingIds`) que nunca toca el servidor, y `Profile.jsx` muestra `followers: 0` hardcodeado con el comentario explícito "de verdad: no existe la funcionalidad todavía".

## Problema

Definir el modelo **mínimo** que permite que un usuario autenticado siga o deje de seguir a otro usuario real, y que se puedan contar sus seguidores/seguidos — sin listar quién sigue a quién, sin notificaciones, sin personalizar el feed.

## Objetivos

- Un usuario autenticado puede seguir o dejar de seguir a otro usuario existente, de forma idempotente (mismo criterio que `ADR-005`: repetir la acción no falla).
- Un usuario no puede seguirse a sí mismo.
- `GET`/`PATCH /api/users/me` exponen `followers_count`/`following_count` reales del usuario autenticado — cierra el placeholder `followers: 0` de `Profile.jsx`.
- `GET`/`POST /api/posts` exponen `is_followed_by_me` en `author`, para que el Frontend pueda ofrecer "Seguir" directamente sobre el autor de un post real del feed — hoy la única fuente de usuarios reales visibles en la UI (`Discover`/sugerencias siguen siendo 100% mock, `DATABASE_ARCHITECTURE.md` §4.B "Búsqueda" sigue sin ratificar).

## No objetivos (explícitamente fuera de este ADR)

- **No** personaliza `GET /api/posts` — el feed sigue global (`ADR-004` §Opciones consideradas). Filtrar por seguidos es una decisión de producto separada (qué ve un usuario con cero seguidos) que queda para un ADR futuro si el equipo la confirma.
- **No** expone la lista de seguidores/seguidos de un usuario (`GET /api/users/<id>/followers`) — solo el conteo agregado, mismo criterio que `ADR-005` no lista quién dio like.
- **No** implementa notificaciones de "nuevo seguidor" — sigue como candidata separada (`notifications`, `DATABASE_ARCHITECTURE.md` §4.B).
- **No** implementa perfiles públicos de otros usuarios (`GET /api/users/<id>` completo) — `Profile.jsx` mismo señala que "los perfiles de otras personas todavía no tienen ruta propia en THERS"; ese alcance más amplio no es parte de este ADR.
- **No** conecta el panel de sugerencias de `Home.jsx` (`mockSuggestions`) — son personas inventadas, no usuarios reales; conectar un panel de sugerencias real depende de que exista búsqueda/descubrimiento de usuarios (`DATABASE_ARCHITECTURE.md` §4.B, sin ratificar). El Frontend de esta tarea conecta "Seguir" únicamente sobre autores reales de posts del feed.

## Opciones consideradas — restricción de auto-seguimiento

| Opción | Descripción | Trade-off |
|---|---|---|
| **A — `CHECK` a nivel de esquema (elegida)** | `CHECK (follower_id <> followed_id)` en la tabla `follows` | Coherente con `DATABASE_ARCHITECTURE.md` §3 ("las reglas de negocio expresables como restricciones de datos viven en el esquema, no solo en la aplicación") — imposible violarla ni siquiera con un INSERT directo. Primera `CHECK` constraint del esquema (hasta ahora solo había `UNIQUE`/`NOT NULL`/FK) |
| B — Solo validación en la capa de aplicación | La route rechaza `user_id == get_jwt_identity()` antes de llegar al repositorio | Más simple de escribir, pero la base de datos por sí sola permitiría el dato inconsistente — no cumple el principio de "la base como última línea de defensa" (§3) |

**Elegida: A**, combinada con B como primera línea (mensaje de error claro, `400`, sin depender de que el `CHECK` de PostgreSQL traduzca su violación a un mensaje entendible).

## Decisión

Se crea una única entidad, `follows`, siguiendo el mismo patrón de capas ya usado para `posts`/`likes`/`comments`.

### Modelo de datos

| Columna | Tipo | Nulo | Justificación |
|---|---|---|---|
| `id` | `UUID`, `DEFAULT gen_random_uuid()` | No (PK) | Mismo patrón que el resto de entidades |
| `follower_id` | `UUID`, FK → `users.id` | No | Quién sigue — siempre `get_jwt_identity()`, nunca un valor del body |
| `followed_id` | `UUID`, FK → `users.id` | No | A quién se sigue — viene de la URL (`user_id`), nunca del body |
| `created_at` | `TIMESTAMPTZ`, `DEFAULT now()` | No | Auditoría — sin uso funcional todavía (no hay orden ni listado de follows en esta versión) |

**Sin `updated_at`.** Igual que `likes` (`ADR-005` §Modelo de datos): una relación de "seguir" se crea o se borra, nunca se edita in place.

**Claves foráneas.** `follower_id → users.id` y `followed_id → users.id`, ambas `ON DELETE CASCADE` — mismo placeholder ya aceptado en `ADR-004`/`ADR-005`/`ADR-006` (borrado de cuenta no existe todavía como funcionalidad).

**Restricciones de unicidad y de negocio:**
- `UNIQUE (follower_id, followed_id)` (`uq_follows_follower_followed`) — un usuario no puede seguir dos veces al mismo usuario; sostiene la idempotencia de `POST .../follow` (mismo criterio que `ADR-005`).
- `CHECK (follower_id <> followed_id)` (`ck_follows_no_self_follow`) — un usuario no puede seguirse a sí mismo (§Opciones consideradas).

**Índices.** Además del que la propia `UNIQUE (follower_id, followed_id)` ya crea (columna líder `follower_id`, cubre "¿a quién sigo?"/`following_count`), se agrega **`ix_follows_followed_id`** — a diferencia de `likes` (`ADR-005` §Índices, que no necesitó un segundo índice), acá sí hace falta: `followers_count` y "¿me sigue esta persona?" filtran por `followed_id`, la columna *no* líder de la `UNIQUE`, que sin este índice haría un escaneo completo de la tabla.

### Contrato API (documentado el mismo día en `API_CONTRACT.md`, `HB-001` §15.1)

**`POST /api/users/<user_id>/follow`** — sigue a `user_id`. Auth requerida. Idempotente.
```json
// Response 200
{ "following": true }
```
- `400` si `user_id` es el propio usuario autenticado (`get_jwt_identity()`).
- `404` si `user_id` no corresponde a ningún usuario real — incluye cualquier segmento de URL que no sea un UUID válido (conversor `uuid` de Flask).
- `401` estándar.

**`DELETE /api/users/<user_id>/follow`** — deja de seguir a `user_id`. Auth requerida. Idempotente.
```json
// Response 200
{ "following": false }
```
- Mismos `401`/`404` que `POST`. Dejar de seguirse a uno mismo es un no-op inofensivo — no se trata como error (la restricción de auto-seguimiento solo importa para *empezar* a seguir).

**`GET`/`PATCH /api/users/me` — extensión aditiva:** el objeto `user` gana `followers_count`/`following_count` (enteros). No rompe el contrato existente.

**`GET`/`POST /api/posts` — extensión aditiva:** cada `post.author` gana `is_followed_by_me` (booleano). No rompe el contrato existente.

### Seguridad

Mismo patrón ya establecido: identidad de quien sigue exclusivamente de `get_jwt_identity()`, `followed_id` siempre de la URL, nunca del body — ningún endpoint de esta entidad acepta body.

## Impacto en Frontend

- `AppShell.jsx` gana un handler **nuevo** (`handleToggleFollowAuthor` o similar) que llama a `POST`/`DELETE /api/users/<id>/follow` con el mismo patrón de optimistic update + rollback que `handleToggleLike` (`ADR-005`) — actúa sobre `capsule.author.is_followed_by_me`, el estado real que ya viaja con cada post (§Contrato API).
- El `followingIds`/`handleToggleFollow` **existente** (un `Set` en memoria) **no se toca ni se reutiliza** para esto: sigue siendo exclusivo del panel de sugerencias mock de `Home.jsx` (§Impacto siguiente) — reutilizar el mismo handler para IDs reales y para las personas inventadas de `mockSuggestions` produciría `404` reales contra usuarios que no existen.
- `CapsuleCard.jsx`: gana un control "Seguir"/"Siguiendo" junto al nombre del autor — solo visible cuando `capsule.author.id !== currentUser.id`, usando el handler nuevo.
- `Profile.jsx`: `stats.followers`/`stats.following` pasan a leer `followers_count`/`following_count` reales de `currentUser` (vía `GET /api/users/me`) en vez de `0`/`followingIds.size`.
- El panel de sugerencias de `Home.jsx` (`mockSuggestions`) **no se toca** — sigue siendo decorativo hasta que exista descubrimiento real de usuarios (§No objetivos).

## Impacto en Backend

- Nueva migración aditiva (`follows`, FKs a `users`, `UNIQUE` compuesta, primer `CHECK` del esquema).
- `domain/follows/` (nuevo): puerto `FollowRepository`. Reutiliza `UserNotFoundError` (`domain/auth/exceptions.py`) para el 404 — el usuario objetivo no existe, mismo caso que ya cubre `GET /api/users/me`.
- `domain/follows/exceptions.py` (nuevo): `CannotFollowSelfError`.
- `application/follows/`: `follow_user_use_case.py`, `unfollow_user_use_case.py`.
- `application/auth/user_presenter.py`/`get_current_user_use_case.py`/`update_profile_use_case.py`: extendidos con `followers_count`/`following_count` (requiere `FollowRepository` inyectado).
- `application/posts/list_posts_use_case.py`/`post_presenter.py`: extendidos con `is_followed_by_me` en `author`, resuelto con una consulta agregada por página (mismo criterio anti-N+1 que `likes_count`/`comments_count`).
- `infrastructure/persistence/repositories/follow_repository.py`: `SQLAlchemyFollowRepository`.
- `interfaces/routes/follow_routes.py` (nuevo blueprint `follows_bp`).
- Tests de integración, mismo patrón que `test_likes.py`/`test_comments.py`.

## Riesgos

- **Condición de carrera en doble-follow simultáneo:** mismo mitigante que `ADR-005` — `UNIQUE` + `IntegrityError` capturado, idempotente por diseño.
- **`is_followed_by_me` en cada post del feed:** una consulta agregada más por página (además de la de likes y la de comentarios) — aceptable al volumen actual (sin paginación, límite fijo de 50 posts); si el número de extensiones por post sigue creciendo, consolidar estas consultas es una optimización futura, no parte de este ADR.

## Decisiones pendientes (quedan fuera, cada una es su propio ADR futuro)

- Personalizar el feed por seguidos (`GET /api/posts` dejaría de ser global).
- Listar seguidores/seguidos de un usuario.
- Notificaciones de "nuevo seguidor".
- Perfiles públicos de otros usuarios.
- Descubrimiento/búsqueda de usuarios (de donde saldrían sugerencias reales para seguir).

## Consecuencias

- `follows` es la cuarta entidad del alcance objetivo del producto (`DATABASE_ARCHITECTURE.md` §4.B) en pasar de OBJETIVO a ratificada, y la primera relación auto-referencial (`users`↔`users`) del esquema.
- `DATABASE_ARCHITECTURE.md`, `DATABASE_ERD.md` y `API_CONTRACT.md` se actualizan el mismo día que este contrato se implementa (`HB-001` §15.1).

## Referencias

- `CLAUDE.md` — jerarquía de fuentes (§4), regla de alcance (§14), reglas específicas para Claude Code (§8).
- `docs/architecture/ADR-004-posts-minimal-model.md`, `ADR-005-likes-minimal-model.md`, `ADR-006-comments-minimal-model.md` — mismo proceso, mismo criterio de extender por entidades simples.
- `docs/architecture/DATABASE_ARCHITECTURE.md` §3 (principios de diseño, consistencia vía constraints), §4.B (candidata `follows`), §8 (índices, sin especulación).
- `docs/architecture/organization/01_Manual_Organizacion/Source/HB-001-manual-organizacion.md.md` §11 (clasificación de impacto de decisiones), §15.1 (documentar endpoints el mismo día del PR).

---

## Cierre
