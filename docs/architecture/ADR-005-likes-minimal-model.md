# ADR-005 — Modelo mínimo de `likes` sobre `posts`

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/ADR-005-likes-minimal-model.md` |
| Tipo | Architecture Decision Record (`HB-001` §11–12) |
| Fecha | 10/09/2026 |
| Estado | **Aceptada** — implementada en esta tarea (ver §Decisión) |
| Alcance | `backend/` — nueva entidad `likes`, `POST`/`DELETE /api/posts/<post_id>/like`, extensión aditiva de `GET /api/posts` |
| Autoridad sobre este documento | `/docs` oficial > estructura real observada en el código > este documento (mismo orden que `CLAUDE.md` §4) |

> ⚠️ **Regla de alcance, explícita — mismo criterio que `ADR-004`.** Este ADR decide deliberadamente **lo mínimo indispensable** para que un post pueda recibir "me gusta": una sola entidad, dos endpoints, sin tipos de reacción, sin notificaciones, sin listar quién dio like. `DATABASE_ARCHITECTURE.md` §4.B ya registraba esta candidata como `reactions` ("colapsa like y reacción, con tipo") — este ADR **no** implementa esa versión general; implementa únicamente el caso binario "like/no like", dejando la generalización a reacciones con tipo como decisión futura si el producto la necesita.

---

## Contexto

`ADR-004-posts-minimal-model.md` dejó "Reacciones/likes" explícitamente fuera de alcance, listada en `DATABASE_ARCHITECTURE.md` §4.B como candidata `reactions` (OBJETIVO, modelado sin decidir). Con `posts` ya ratificado y en producción, likes es la extensión más pequeña que da valor real al feed sin requerir `follows`, comentarios ni ninguna otra entidad todavía no ratificada.

## Problema

Definir el modelo **mínimo** que permite que un usuario autenticado marque "me gusta" en un post existente, lo pueda quitar, y que el feed (`GET /api/posts`) muestre cuántos likes tiene cada post y si el usuario actual ya lo likeó — sin modelar tipos de reacción, sin notificar a nadie, sin exponer la lista de quién dio like.

## Objetivos

- Un usuario autenticado puede dar like a un post existente y quitarlo, de forma idempotente (repetir la acción no falla ni duplica).
- `GET /api/posts` expone `likes_count` y `liked_by_me` por post, sin romper el contrato ya existente (`ADR-004` §Contrato) — son campos nuevos, no reemplazan ninguno.
- El modelo se mantiene deliberadamente pequeño: solo lo que esta funcionalidad concreta justifica (mismo principio que `ADR-002`/`ADR-003`/`ADR-004`).

## No objetivos (explícitamente fuera de este ADR)

- **No** implementa tipos de reacción (❤️/👍/😂/etc.) — la candidata general `reactions` de `DATABASE_ARCHITECTURE.md` §4.B sigue sin ratificar en esa forma; este ADR resuelve solo el caso binario.
- **No** implementa notificaciones ("a X le gustó tu post") — `notifications` sigue como candidata sin ratificar (`DATABASE_ARCHITECTURE.md` §4.B).
- **No** expone la lista de usuarios que dieron like a un post (`GET /api/posts/<id>/likes` u equivalente) — solo el conteo agregado y si el usuario actual ya likeó.
- **No** implementa comentarios — sigue siendo su propio ADR futuro, igual que `ADR-004` §Decisiones pendientes ya señalaba.
- **No** implementa paginación de likes ni de posts — hereda la misma limitación conocida y aceptada de `ADR-004` §No objetivos.

## Opciones consideradas — verbo HTTP e idempotencia

| Opción | Descripción | Trade-off |
|---|---|---|
| **A — `POST`/`DELETE` idempotentes (elegida)** | `POST /api/posts/<id>/like` da like (o no-op si ya existía); `DELETE /api/posts/<id>/like` lo quita (o no-op si no existía). Ambos devuelven `200` con el estado actual (`likes_count`, `liked_by_me`) | El Frontend nunca necesita manejar `409 Conflict` por "ya likeado" ni `404` por "no estaba likeado" — un doble clic accidental (doble tap, red lenta con reintento) no es un error |
| B — `POST` estricto (409 si ya existe) | Semántica REST más purista: un `POST` que falla si el recurso ya existe | Obliga al Frontend a tratar el doble-like como error y silenciarlo — complejidad extra sin beneficio real para un toggle de UI |
| C — Un único endpoint `PUT` con `{"liked": true/false}` en el body | Un solo endpoint en vez de dos | Menos alineado con el patrón ya establecido de verbos declarados explícitamente por ruta (`API_CONTRACT.md` §2, "Verbos HTTP... PENDIENTE DE APROBACIÓN" para el caso general) — este ADR no resuelve esa convención general, solo elige lo más simple para este caso puntual |

**Elegida: A.** Idempotencia evita una clase entera de errores de UI (doble tap, reintentos de red) sin costo real, y `POST`/`DELETE` para dar/quitar un like es una convención ampliamente reconocible.

## Decisión

Se crea una única entidad, `likes`, extendiendo el mismo patrón ya usado para `posts` (Repository con puerto en `domain/`, adaptador en `infrastructure/`, composition root en `interfaces/routes/`).

### Modelo de datos

| Columna | Tipo | Nulo | Justificación |
|---|---|---|---|
| `id` | `UUID`, `DEFAULT gen_random_uuid()` | No (PK) | Mismo patrón que `users.id`/`posts.id` |
| `post_id` | `UUID`, FK → `posts.id` | No | Post likeado |
| `user_id` | `UUID`, FK → `users.id` | No | Quién dio el like — siempre `get_jwt_identity()`, nunca un valor del body (mismo principio que `ADR-003`/`ADR-004`) |
| `created_at` | `TIMESTAMPTZ`, `DEFAULT now()` | No | Auditoría — sin uso funcional todavía (no hay orden ni listado de likes en esta versión) |

**Sin `updated_at`.** A diferencia de `users`/`posts`, un like no se edita — se crea o se borra, nunca se actualiza in place. Agregar `updated_at`+trigger sería especulativo sin un caso de uso real (mismo principio de "sin índices/columnas especulativas", `DATABASE_ARCHITECTURE.md` §8).

**Claves foráneas.** `post_id → posts.id` y `user_id → users.id`, ambas `ON DELETE CASCADE` — si se borra un post o un usuario, sus likes se borran con él. Mismo placeholder razonable que `ADR-004` §Decisión ya aceptó para `posts.author_id` (borrado de cuenta/post tampoco existe todavía como funcionalidad).

**Restricción de unicidad:** `UNIQUE (post_id, user_id)` (`uq_likes_post_user`) — un usuario no puede likear el mismo post dos veces; es también la base de la idempotencia de `POST .../like` (§Decisión, Opción A).

**Índices.** Ninguno además del que la propia `UNIQUE (post_id, user_id)` ya crea — su columna líder (`post_id`) ya cubre el patrón de acceso real (`COUNT(*) ... WHERE post_id = ...`, `WHERE post_id IN (...)`). Sin índices especulativos adicionales (`DATABASE_ARCHITECTURE.md` §8, mismo criterio que `ADR-004`).

### Contrato API (documentado el mismo día en `API_CONTRACT.md` §4.4, `HB-001` §15.1)

**`POST /api/posts/<post_id>/like`** — da like al post. Auth requerida. Idempotente.
```json
// Response 200
{ "likes_count": 3, "liked_by_me": true }
```
- `404` si `post_id` no corresponde a ningún post real (incluido un `post_id` con formato inválido — la ruta usa el conversor `uuid` de Flask, que ya produce `404` para cualquier valor que no sea un UUID válido, sin necesidad de validación manual).
- `401` si falta o es inválido el JWT.

**`DELETE /api/posts/<post_id>/like`** — quita el like del usuario actual sobre el post. Auth requerida. Idempotente.
```json
// Response 200
{ "likes_count": 2, "liked_by_me": false }
```
- Mismos `404`/`401` que el endpoint anterior.

**`GET /api/posts` — extensión aditiva, no rompe el contrato de `ADR-004`:**
```json
// Response 200
{ "posts": [ { "id", "author": {...}, "content", "created_at", "likes_count", "liked_by_me" }, ... ] }
```
- `likes_count` (`integer`): total de likes del post.
- `liked_by_me` (`boolean`): si el usuario autenticado que hace la request ya le dio like.
- Un post recién creado (`POST /api/posts`) también incluye ambos campos, en `0`/`false` — nadie pudo haberle dado like todavía.

### Seguridad

Mismo patrón ya establecido y probado en `auth`/`users`/`posts`:
- Identidad del usuario que da/quita el like exclusivamente de `get_jwt_identity()` — nunca del body.
- `POST`/`DELETE` no aceptan ningún campo de body — toda la información viene de la URL (`post_id`) y del JWT.
- No se expone qué usuarios dieron like (§No objetivos) — evita filtrar esa lista antes de que el producto decida si es información pública.

## Impacto en Frontend

Lo que Frontend haría **después** de que este ADR se ratifique (no en este documento):
- `CapsuleCard.jsx` consumiría `likes_count`/`liked_by_me` reales en vez del campo `likes` (número fijo) que `mockCapsules` ya simula, y llamaría `POST`/`DELETE /api/posts/<id>/like` al tocar el botón de like.
- Ningún otro componente cambia — `comments` sigue siendo mock/decorativo hasta su propio ADR.

## Impacto en Backend

- Nueva migración aditiva (`likes`, con FKs a `posts`/`users`).
- `domain/likes/` (nuevo): puerto `LikeRepository`.
- `domain/posts/exceptions.py` (nuevo): `PostNotFoundError` — primera excepción de dominio de `posts`, reutilizada por los casos de uso de likes para el `404` cuando `post_id` no existe.
- `domain/posts/repositories.py`: se agrega `get_by_id(post_id)` al puerto `PostRepository` (extensión aditiva, no cambia los métodos existentes).
- `application/likes/`: `like_post_use_case.py`, `unlike_post_use_case.py`.
- `application/posts/list_posts_use_case.py` y `post_presenter.py`: extendidos para incluir el resumen de likes por post (una sola consulta agregada, no N+1).
- `infrastructure/persistence/repositories/like_repository.py`: `SQLAlchemyLikeRepository`.
- `interfaces/routes/like_routes.py` (nuevo blueprint `likes_bp`).
- Tests de integración, mismo patrón que `test_posts.py`.

## Riesgos

- **Condición de carrera en doble-like simultáneo:** dos requests concurrentes del mismo usuario podrían intentar insertar el mismo `(post_id, user_id)` a la vez — la `UNIQUE` constraint hace que una de las dos falle con `IntegrityError`, capturada y tratada como éxito idempotente (mismo patrón que `SQLAlchemyUserRepository.create`/`update` ya usan para `email`/`username` duplicados).
- **Conteo por post sin caché:** `likes_count` se calcula con `COUNT(*)` en cada `GET /api/posts` — aceptable al volumen actual (sin paginación, límite fijo de 50 posts); si el volumen crece, desnormalizar un contador en `posts` es una optimización futura, no parte de este ADR.

## Decisiones pendientes (quedan fuera, cada una es su propio ADR futuro)

- Reacciones con tipo (más allá del binario like/no-like).
- Notificaciones de "a alguien le gustó tu post".
- Listar quién dio like a un post.
- Comentarios (`ADR-004` §Decisiones pendientes, sigue igual).
- `follows` — de quién es el feed (`ADR-004` §Decisiones pendientes, sigue igual).

## Consecuencias

- `likes` es la segunda entidad del alcance objetivo del producto (`DATABASE_ARCHITECTURE.md` §4.B) en pasar de OBJETIVO a ratificada, después de `posts`.
- `DATABASE_ARCHITECTURE.md`, `DATABASE_ERD.md` y `API_CONTRACT.md` se actualizan el mismo día que este contrato se implementa (`HB-001` §15.1).

## Referencias

- `CLAUDE.md` — jerarquía de fuentes (§4), regla de alcance (§14), reglas específicas para Claude Code (§8).
- `docs/architecture/ADR-004-posts-minimal-model.md` — mismo proceso, mismo criterio de extender por entidades simples en vez de sobre-modelar de una vez; `posts` es el prerrequisito directo de este ADR.
- `docs/architecture/DATABASE_ARCHITECTURE.md` §3 (principios de diseño, normalización), §4.B (candidata `reactions`), §8 (índices, sin especulación).
- `docs/architecture/organization/01_Manual_Organizacion/Source/HB-001-manual-organizacion.md.md` §11 (clasificación de impacto de decisiones), §15.1 (documentar endpoints el mismo día del PR).

---

## Cierre
