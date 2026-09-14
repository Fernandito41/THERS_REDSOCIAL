# ADR-008 — Modelo mínimo de `notifications`

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/ADR-008-notifications-minimal-model.md` |
| Tipo | Architecture Decision Record (`HB-001` §11–12) |
| Fecha | 14/09/2026 |
| Estado | **Aceptada** — implementada en esta tarea (ver §Decisión) |
| Alcance | `backend/` — nueva entidad `notifications`, `GET /api/notifications`, `PATCH /api/notifications/<id>/read`, generación de notificaciones como efecto secundario de `POST /api/posts/<id>/like`, `POST /api/posts/<id>/comments` y `POST /api/users/<id>/follow` |
| Autoridad sobre este documento | `/docs` oficial > estructura real observada en el código > este documento (mismo orden que `CLAUDE.md` §4) |

> ⚠️ **Regla de alcance, explícita — mismo criterio que `ADR-004`/`ADR-005`/`ADR-006`/`ADR-007`.** `DATABASE_ARCHITECTURE.md` §4.B registra "Likes, Comentarios, Respuestas, Nuevos seguidores, Menciones, Mensajes, Actividad relevante" como **una sola** candidata (`notifications`, entidad con discriminador de tipo, no una tabla por tipo). Este ADR implementa esa entidad **solo para los tres eventos que el backend ya sabe generar hoy**: `like`, `comment`, `follow`. Respuestas a comentarios, menciones y mensajes no existen todavía como funcionalidad (`comments` no tiene hilos, `mentions`/`conversations` siguen sin ratificar) — no se inventan notificaciones para eventos que el propio backend no produce.

---

## Contexto

Con `posts`, `likes`, `comments` y `follows` ya ratificados, el backend genera constantemente eventos sociales reales (alguien le da like a tu post, alguien lo comenta, alguien empieza a seguirte) que hoy **no llegan a ningún lado**: `Notifications.jsx` (Frontend) sigue leyendo `mockNotifications`, una lista fija de 5 notificaciones inventadas que nunca cambia, sin importar lo que pase en la cuenta real del usuario. Es la brecha más visible entre lo que el backend ya puede hacer y lo que un usuario real ve en la app corriendo (detectada en la auditoría de esta tarea, `CLAUDE.md` §8.1/§12).

## Problema

Definir el modelo **mínimo** que permite que un usuario autenticado reciba y liste sus notificaciones reales, generadas automáticamente cuando otro usuario le da like a un post suyo, lo comenta, o empieza a seguirlo — sin notificaciones push/email, sin preferencias configurables, sin menciones ni mensajes (esos eventos no existen todavía).

## Objetivos

- Cuando un usuario A le da like a un post de un usuario B (siendo A ≠ B), se crea una notificación para B.
- Cuando A comenta un post de B (A ≠ B), se crea una notificación para B.
- Cuando A empieza a seguir a B, se crea una notificación para B.
- Un usuario autenticado puede listar sus propias notificaciones, más recientes primero.
- Un usuario autenticado puede marcar una notificación propia como leída, de forma idempotente (mismo criterio que `ADR-005`/`ADR-007`).
- Ningún usuario puede notificarse a sí mismo (dar like/comentar su propio post no genera notificación — seguirse a uno mismo ya es imposible desde `ADR-007`).
- Una repetición idempotente de un like o un follow (POST sobre un like/follow que ya existía) **no** duplica la notificación — solo la transición real (de "no" a "sí") notifica.

## No objetivos (explícitamente fuera de este ADR)

- **No** implementa notificaciones push ni por email — solo persistencia en PostgreSQL, consumida por `GET /api/notifications` (polling desde el Frontend, sin WebSockets ni Server-Sent Events).
- **No** implementa preferencias de notificación (`user_settings`/`notification_preferences`, `DATABASE_ARCHITECTURE.md` §4.B › Configuración) — todo evento notifica siempre, sin opción de silenciarlo.
- **No** genera notificaciones de "respuesta a un comentario" (`comments` no tiene hilos todavía, `ADR-006` §No objetivos), ni de menciones (`mentions` sigue sin ratificar), ni de mensajes (`conversations`/`messages` siguen sin ratificar) — cuando esas entidades existan, cada una decide si also dispara una notificación, no es un efecto colateral silencioso de este ADR.
- **No** implementa un endpoint de "marcar todas como leídas" — cada notificación se marca individualmente vía `PATCH /api/notifications/<id>/read`; el Frontend puede ofrecer esa acción en la UI iterando sobre las no leídas (ver §Impacto en Frontend), pero el backend no expone una operación batch en esta versión.
- **No** expone un contador de no leídas como endpoint propio (`GET /api/notifications/unread-count`) — el Frontend ya puede derivarlo contando `read: false` sobre la lista que `GET /api/notifications` devuelve, sin una consulta adicional.
- **No** borra notificaciones — no hay `DELETE /api/notifications/<id>` en esta versión; se acumulan indefinidamente (aceptable al volumen actual, sin paginación real, ver §Riesgos).
- **No** cambia el contrato de `POST /api/posts/<id>/like`, `POST /api/posts/<id>/comments` ni `POST /api/users/<id>/follow` — sus respuestas HTTP no ganan ningún campo nuevo; la notificación es un efecto secundario invisible para quien dispara la acción, visible solo para quien la recibe (vía `GET /api/notifications`).

## Opciones consideradas — forma del discriminador de tipo

| Opción | Descripción | Trade-off |
|---|---|---|
| **A — Una tabla `notifications` con columna `type` (elegida)** | Una sola entidad, `type` como `VARCHAR` corto (`'like'`/`'comment'`/`'follow'`), `post_id` nullable (solo aplica a like/comment) | Coincide exactamente con lo que `DATABASE_ARCHITECTURE.md` §4.B ya decía sobre esta candidata ("una sola entidad `notifications` con discriminador de tipo — no una tabla por tipo"). Agregar un tipo nuevo el día de mañana (p. ej. `'mention'`) es una fila más, no una tabla ni una migración estructural nueva |
| B — Una tabla por tipo de evento (`like_notifications`, `comment_notifications`, `follow_notifications`) | Cada tipo con su propia tabla y sus propias columnas | Descartada explícitamente por `DATABASE_ARCHITECTURE.md` §4.B ("una funcionalidad no equivale a una tabla"/"todos los tipos de notificación = una sola entidad") — tres tablas casi idénticas para el mismo concepto, sin ningún campo que realmente difiera |
| C — `type` como `ENUM` nativo de PostgreSQL en vez de `VARCHAR` | Mismo modelo que A, pero con un tipo enumerado a nivel de motor | Descartada: agregar un valor nuevo a un `ENUM` de PostgreSQL requiere `ALTER TYPE ... ADD VALUE` (no transaccional en versiones antiguas, y de todos modos una migración estructural) cada vez que el producto sume un tipo de notificación — más fricción que el valor que aporta frente a validar el conjunto permitido en `domain/`, mismo criterio ya aceptado para `content` de posts/comments (la forma se valida en la aplicación, no con una restricción de esquema) |

**Elegida: A**, con el conjunto de valores válidos (`'like'`, `'comment'`, `'follow'`) validado en la capa de aplicación (los tres casos de uso que llaman a `NotificationRepository.create()` son los únicos puntos que pueden generar una fila — no hay ningún endpoint que acepte `type` directamente del body, ver §Seguridad), no como `CHECK` de PostgreSQL en esta versión.

## Opciones consideradas — cuándo notificar sobre acciones idempotentes

| Opción | Descripción | Trade-off |
|---|---|---|
| **A — Notificar solo en la transición real (elegida)** | `LikeRepository.add()`/`FollowRepository.add()` devuelven si la fila se creó en esa llamada; el caso de uso solo notifica cuando `True` | Un segundo `POST .../like` sobre un post ya likeado (ya idempotente a nivel de contrato HTTP, `ADR-005`) no genera una segunda notificación — coincide con la expectativa de cualquier red social real (un "like" duplicado no produce dos avisos) |
| B — Notificar en cada llamada al endpoint, sin importar si hubo transición | Más simple de implementar (no requiere que `add()` devuelva nada) | Un doble clic accidental, o un cliente que reintenta un `POST` ya exitoso, generaría notificaciones duplicadas indefinidamente — mala experiencia para quien las recibe, sin ningún beneficio a cambio |

**Elegida: A.** `comments` no necesita esta decisión: crear un comentario nunca es un no-op idempotente (cada `POST /api/posts/<id>/comments` exitoso es una fila nueva, `ADR-006` §Decisión), así que siempre notifica.

## Decisión

Se crea una única entidad, `notifications`, siguiendo el mismo patrón de capas ya usado para `posts`/`likes`/`comments`/`follows`.

### Modelo de datos

| Columna | Tipo | Nulo | Justificación |
|---|---|---|---|
| `id` | `UUID`, `DEFAULT gen_random_uuid()` | No (PK) | Mismo patrón que el resto de entidades |
| `recipient_id` | `UUID`, FK → `users.id` | No | Quién recibe la notificación — siempre el autor del post (like/comment) o el usuario seguido (follow), nunca un valor del body |
| `actor_id` | `UUID`, FK → `users.id` | No | Quién generó el evento — siempre `get_jwt_identity()` de quien hizo la acción original (dar like, comentar, seguir) |
| `type` | `VARCHAR(20)` | No | Discriminador de tipo: `'like'` / `'comment'` / `'follow'` (§Opciones consideradas). Validado en `domain/`, no en el esquema |
| `post_id` | `UUID`, FK → `posts.id` | **Sí** | Post de origen — solo aplica a `'like'`/`'comment'`; en `'follow'` viaja `NULL` |
| `read_at` | `TIMESTAMPTZ` | **Sí** | `NULL` = no leída. Se expone en la API como booleano (`read`), nunca como el timestamp crudo — mismo criterio que `username_changed_at` nunca cruza la frontera HTTP (`API_CONTRACT.md` §5) |
| `created_at` | `TIMESTAMPTZ`, `DEFAULT now()` | No | Define el orden de la lista (más reciente primero, igual que el feed de posts) |

**Sin `updated_at`.** Igual que `likes`/`follows` (`ADR-005`/`ADR-007` §Modelo de datos): una notificación no se edita in place más allá de marcarse como leída (`read_at`), que tiene su propia semántica de "solo se fija una vez" (§Contrato API).

**Claves foráneas.** `recipient_id → users.id` y `actor_id → users.id` (ambas `ON DELETE CASCADE`, mismo placeholder que el resto de entidades — borrado de cuenta no existe todavía); `post_id → posts.id` (`ON DELETE CASCADE` — si el post se borra, no tiene sentido conservar notificaciones sobre un post inexistente; hoy borrar un post tampoco es una funcionalidad implementada, así que esta política no se ejerce en la práctica todavía).

**Sin restricciones de unicidad.** A diferencia de `likes`/`follows`, no hay una `UNIQUE` sobre `(recipient_id, actor_id, post_id, type)`: dos likes distintos de la misma persona sobre el mismo post en momentos distintos (like → unlike → like, §Opciones consideradas) generan dos notificaciones legítimas, no un duplicado a impedir.

**Sin `CHECK` de auto-notificación.** No hay ningún endpoint que cree una notificación directamente a partir de datos del usuario — las tres únicas vías de creación (`like_post_use_case`, `create_comment_use_case`, `follow_user_use_case`) ya comparan `actor_id`/`recipient_id` en la capa de aplicación antes de llamar a `create()` (§Objetivos). A diferencia de `follows` (`ck_follows_no_self_follow`), acá no hace falta una segunda línea de defensa a nivel de esquema porque ningún dato de entrada externo llega jamás a esta tabla — no hay superficie de ataque que una `CHECK` adicional esté cerrando.

**Índices.** `ix_notifications_recipient_id_created_at` (`recipient_id`, `created_at`), compuesto — `GET /api/notifications` filtra por `recipient_id` (siempre el usuario autenticado) y ordena por `created_at DESC`; mismo patrón que `ix_comments_post_id_created_at` (`ADR-006` §Índices, columna líder que también cubre el filtro sin escanear la tabla completa).

### Contrato API (documentado el mismo día en `API_CONTRACT.md`, `HB-001` §15.1)

**`GET /api/notifications`** — lista las notificaciones del usuario autenticado, más recientes primero. Auth requerida. Límite fijo de 50 (sin paginación real, mismo criterio que `GET /api/posts`).
```json
// Response 200
{
  "notifications": [
    {
      "id": "uuid",
      "type": "like",
      "actor": { "id": "uuid", "username": "sofia_r", "name": "Sofía Reyes" },
      "post_id": "uuid",
      "read": false,
      "created_at": "2026-09-14T16:03:39.291468+00:00"
    }
  ]
}
```
- `401` estándar (falta el header, token inválido/expirado).

**`PATCH /api/notifications/<notification_id>/read`** — marca como leída una notificación propia. Auth requerida. Idempotente.
```json
// Response 200
{ "read": true }
```
- `404` si `notification_id` no existe, **o** si existe pero pertenece a otro usuario — mismo mensaje/código en ambos casos, no se distingue cuál ocurrió (mismo criterio que `InvalidCredentialsError` en login no distingue email inexistente de password incorrecta).
- `401` estándar.

**Sin cambios en `POST /api/posts/<id>/like`, `POST /api/posts/<id>/comments` ni `POST /api/users/<id>/follow`** — sus contratos HTTP no ganan ningún campo; la notificación es un efecto secundario invisible en la respuesta de quien la dispara.

### Seguridad

- `recipient_id`/`actor_id` nunca se aceptan de ningún body — se derivan siempre del post/usuario objetivo y de `get_jwt_identity()` en las tres rutas que ya existían (`like_routes.py`, `comment_routes.py`, `follow_routes.py`), nunca en un endpoint nuevo que los reciba directamente.
- `GET /api/notifications` filtra siempre por el `recipient_id` del JWT — un usuario no puede pedir las notificaciones de otro cambiando ningún parámetro (no hay `user_id` en la URL de este endpoint, a diferencia de `follows`).
- `PATCH .../read` verifica pertenencia (`recipient_id == get_jwt_identity()`) en la misma sentencia SQL que confirma existencia — mismo principio que evita revelar si un recurso de otro usuario existe.

## Impacto en Frontend

- `AppShell.jsx`: `notifications` deja de inicializarse con `mockNotifications` — pasa a cargarse con `GET /api/notifications` en un `useEffect`, mismo patrón que ya usa `capsules` (`ADR-004` §Impacto en Frontend). `handleMarkRead(id)` deja de mutar un array en memoria y pasa a llamar `PATCH /api/notifications/<id>/read`, con el mismo patrón de optimistic update + rollback que `handleToggleLike` (`ADR-005`). `handleMarkAllRead()` no tiene un endpoint batch propio (§No objetivos) — itera sobre las notificaciones no leídas y llama al mismo handler individual para cada una.
- Nuevo `features/feed/lib/mapNotification.js`: traduce la forma cruda de la API (`type`/`actor`/`post_id`/`read`/`created_at`) a la forma que `Notifications.jsx` ya sabe renderizar (`actor` como string, `detail` como texto en español, `time` relativo vía `formatRelativeTime.js` ya existente, `important` calculado por tipo) — sin tocar `Notifications.jsx` más que lo estrictamente necesario para los tipos reales (`like`/`comment`/`follow` en vez de `reaction`/`mention`, este último nunca producido por el backend).
- `photo` de cada notificación **no** se completa con ninguna URL real — mismo motivo que `posts`/`comments`: no existe `avatar_url` ratificada todavía (`DATABASE_ARCHITECTURE.md` §4.B › Perfil, `PENDIENTE DE DECISIÓN`); `Avatar.jsx` ya renderiza iniciales cuando no recibe `photo`, sin necesitar ningún cambio.

## Impacto en Backend

- Nueva migración aditiva (`notifications`, tres FKs, un índice compuesto).
- `domain/notifications/` (nuevo): puerto `NotificationRepository`.
- `domain/notifications/exceptions.py` (nuevo): `NotificationNotFoundError`.
- `application/notifications/`: `list_notifications_use_case.py`, `mark_notification_read_use_case.py`, `notification_presenter.py`.
- `infrastructure/persistence/repositories/notification_repository.py`: `SQLAlchemyNotificationRepository`.
- `interfaces/routes/notification_routes.py` (nuevo blueprint `notifications_bp`).
- **Cambio de contrato interno (no HTTP) en `LikeRepository.add()`/`FollowRepository.add()`:** ambos pasan de no devolver nada a devolver `True`/`False` según si la fila se creó en esa llamada — nada fuera de `like_post_use_case.py`/`follow_user_use_case.py` consumía el valor de retorno anterior, así que este cambio no afecta ningún otro punto del código ni ningún contrato HTTP existente (verificado: ninguna prueba llamaba a `add()` esperando `None`).
- `application/likes/like_post_use_case.py`, `application/comments/create_comment_use_case.py`, `application/follows/follow_user_use_case.py`: cada uno gana un parámetro `notification_repository` y dispara `create()` según las reglas de §Objetivos/§Opciones consideradas.
- `interfaces/routes/like_routes.py`, `comment_routes.py`, `follow_routes.py`: instancian `SQLAlchemyNotificationRepository()` y la pasan a sus respectivos casos de uso.
- `tests/conftest.py`: `notifications` se agrega a la lista de tablas truncadas entre pruebas.
- Tests de integración nuevos (`tests/test_notifications.py`), mismo patrón que `test_likes.py`/`test_comments.py`/`test_follows.py`.

## Riesgos

- **Sin paginación real:** igual que el resto de listados del backend (feed, comentarios) — límite fijo de 50. Un usuario con mucha actividad entrante vería solo las 50 notificaciones más recientes; aceptable al volumen actual, revisar cuando el producto priorice paginación real en general (no solo para esta entidad).
- **Acumulación indefinida:** sin borrado ni expiración, la tabla crece sin límite superior. Mismo criterio que `likes`/`comments`/`follows` no implementan borrado tampoco — no es una decisión distinta para esta entidad, es la misma pendiente transversal (`DATABASE_ARCHITECTURE.md` §14).
- **Polling, no push:** `GET /api/notifications` requiere que el Frontend vuelva a pedir la lista (o que el usuario recargue/navegue) para ver una notificación nueva — no hay actualización en tiempo real. Aceptable dado que ningún otro punto del Frontend usa WebSockets/SSE todavía; introducir eso sería un cambio de infraestructura mucho mayor que el alcance de este ADR.

## Decisiones pendientes (quedan fuera, cada una es su propio ADR futuro)

- Notificaciones push/email.
- Preferencias de notificación configurables por el usuario.
- Notificaciones de respuestas a comentarios, menciones y mensajes (dependen de que esas entidades se ratifiquen primero).
- Endpoint de "marcar todas como leídas" a nivel de backend.
- Contador de no leídas como endpoint propio.
- Borrado o expiración de notificaciones antiguas.
- Actualización en tiempo real (WebSockets/SSE) en vez de polling.

## Consecuencias

- `notifications` es la sexta entidad del alcance objetivo del producto (`DATABASE_ARCHITECTURE.md` §4.B) en pasar de OBJETIVO a ratificada.
- Cierra la brecha más visible detectada en la auditoría de esta tarea: `Notifications.jsx` deja de mostrar datos 100% inventados y pasa a reflejar actividad real de la cuenta autenticada.
- `DATABASE_ARCHITECTURE.md`, `DATABASE_ERD.md` y `API_CONTRACT.md` se actualizan el mismo día que este contrato se implementa (`HB-001` §15.1).

## Referencias

- `CLAUDE.md` — jerarquía de fuentes (§4), regla de alcance (§14), reglas específicas para Claude Code (§8).
- `docs/architecture/ADR-004-posts-minimal-model.md`, `ADR-005-likes-minimal-model.md`, `ADR-006-comments-minimal-model.md`, `ADR-007-follows-minimal-model.md` — mismo proceso, mismo criterio de extender por entidades simples.
- `docs/architecture/DATABASE_ARCHITECTURE.md` §3 (principios de diseño), §4.B › Notificaciones (candidata `notifications`, discriminador de tipo), §8 (índices, sin especulación).
- `docs/architecture/organization/01_Manual_Organizacion/Source/HB-001-manual-organizacion.md.md` §11 (clasificación de impacto de decisiones), §15.1 (documentar endpoints el mismo día del PR).

---

## Cierre
