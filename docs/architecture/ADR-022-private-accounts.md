# ADR-022 — Cuentas privadas y solicitudes de seguimiento

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/ADR-022-private-accounts.md` |
| Tipo | Architecture Decision Record (`HB-001` §11–12) |
| Fecha | 01/10/2026 |
| Estado | **Aceptada** — implementada en esta tarea (ver §Decisión) |
| Alcance | `backend/` — `users.is_private`, `follows.status`, `GET`/`PATCH /api/users/me/privacy`, `GET /api/follow-requests`, `POST /api/follow-requests/<user_id>/accept`, `DELETE /api/follow-requests/<user_id>`, y filtrado de visibilidad en feed/comentarios/likes; `Frontend/` — interruptor y bandeja de solicitudes en Configuración › Privacidad, botón de seguir con tres estados |
| Autoridad sobre este documento | `/docs` oficial > estructura real observada en el código > este documento (mismo orden que `CLAUDE.md` §4) |

> Extiende `ADR-007-follows-minimal-model.md`, que creó `follows` como un hecho binario sin estados. Es el primer ADR que **cambia la semántica de lectura de endpoints ya existentes**: `GET /api/posts`, `GET /api/posts/<id>/comments` y los dos de `like` dejan de devolver lo mismo a todo el mundo.

---

## Contexto

La pantalla de Privacidad del producto (REF-SET-02, `Frontend/src/features/feed/data/settingsSections.js`) tenía sus seis controles marcados como `pending`. El primero, "Cuenta privada", decía: *"Solo los usuarios aprobados podrían ver tus cápsulas y resonancias"*, con el motivo *"Requiere que el servidor filtre cada consulta por relación de seguimiento"*.

Ese motivo era exacto. Hasta ahora todo el contenido del producto es público para cualquier cuenta autenticada: `GET /api/posts` es un feed global (`ADR-004` §Opciones consideradas) y ni comentarios ni likes comprueban nada más que la existencia del post.

El propio texto del control fija el alcance: habla de usuarios **aprobados**, no solo de contenido oculto. Eso implica un flujo de aprobación, no un interruptor de visibilidad.

## Objetivos

- Una cuenta puede cerrarse: su contenido deja de ser visible para quien no la sigue.
- Seguir a una cuenta cerrada se convierte en **pedirlo**; el dueño aprueba o rechaza.
- Volverse privado no rompe nada de lo que ya existía: quien ya seguía, sigue.
- La regla de visibilidad existe en **un solo lugar** y todos los endpoints la obedecen igual.
- Un intento de ver contenido ajeno no revela si ese contenido existe.

## No objetivos (explícitamente fuera de este ADR)

- **No** oculta el perfil ni el `username` de una cuenta privada. No existe endpoint de perfil público (`GET /api/users/<id>` no está en el catálogo), así que no hay nada que cerrar todavía; lo que se protege es el **contenido**.
- **No** implementa bloquear a una persona. Bloquear es una relación negativa propia (impide interacción en los dos sentidos, no solo lectura) y sigue siendo `pending` en la pantalla de Seguridad.
- **No** oculta los contadores `followers_count`/`following_count` de una cuenta privada — solo se exponen en `GET /api/users/me`, que es siempre sobre uno mismo.
- **No** retira retroactivamente el acceso de los seguidores actuales al volverse privado (ver §Decisión).
- **No** filtra `GET /api/notifications`: una notificación ya generada apunta a contenido que, en el momento de generarse, el destinatario podía ver. Ver §Riesgos.
- **No** implementa listar seguidores/seguidos — heredado de `ADR-007` §No objetivos, sigue abierto.

## Opciones consideradas — dónde vive el estado de una solicitud

| Opción | Descripción | Trade-off |
|---|---|---|
| **A — Columna `status` en `follows` (elegida)** | La misma fila pasa de `'pending'` a `'accepted'` | Una solicitud y un follow son **el mismo hecho en dos momentos**, no dos entidades. La `UNIQUE (follower_id, followed_id)` que ya existe (`ADR-007`) garantiza gratis que nadie tenga a la vez una solicitud pendiente y un follow aceptado hacia la misma persona. Aceptar es un `UPDATE`, no un `INSERT` + `DELETE` en dos tablas |
| B — Tabla `follow_requests` aparte | La solicitud vive en su propia tabla y aceptar la mueve a `follows` | Obliga a mantener la invariante "no puede haber fila en las dos a la vez" a mano, en código, sin que el esquema ayude. Y cada consulta de visibilidad tendría que mirar las dos tablas para no confundir un pendiente con un seguidor |
| C — Sin estados: privado solo oculta, el follow es inmediato | `is_private` filtra lecturas pero seguir sigue siendo instantáneo | Mucho más simple, pero contradice el texto del propio control ("usuarios **aprobados**") y deja la función a medias: cerrar la cuenta no serviría de nada si cualquiera puede seguirla y entrar |

**Elegida: A.**

### Opciones consideradas — dónde se filtra el feed

El filtro de `GET /api/posts` va en el **`WHERE` de SQL**, no en Python después de traer la página. Filtrar después del `LIMIT` haría que una página de 50 devolviera 3 posts si las 47 restantes eran de cuentas privadas — y el Frontend no tiene paginación real con la que compensarlo (`ADR-004`). El coste es que la regla queda escrita dos veces (una como función pura, otra como expresión SQL); se mitiga nombrando cada una en el comentario de la otra.

### Opciones consideradas — qué pasa al volverse privado

| Opción | Trade-off |
|---|---|
| **A — Los seguidores actuales se mantienen (elegida)** | Es lo que cualquiera espera: cerrar la cuenta protege de la gente **nueva**. Degradar a cientos de seguidores a "pendiente" convertiría un interruptor en una tarea de horas |
| B — Todos los follows pasan a `'pending'` | Más estricto, pero castiga al usuario por usar la función y es irreversible (no hay forma de saber qué estaban aceptados antes) |

**Elegida: A.** `PATCH /api/users/me/privacy` no toca `follows`.

## Decisión

### `users.is_private` — `BOOLEAN NOT NULL DEFAULT false`

`false` preserva exactamente el comportamiento histórico. Ninguna cuenta se vuelve privada por efecto de la migración.

### `follows.status` — `VARCHAR(20) NOT NULL DEFAULT 'accepted'`

Dos valores (`domain/follows/follow_status.py`): `'accepted'` (relación efectiva) y `'pending'` (solicitud sin responder, solo alcanzable hacia una cuenta privada). El `server_default 'accepted'` hace de *backfill*: todo follow previo a esta migración se hizo hacia una cuenta pública, así que ya estaba aceptado de hecho.

Discriminador `VARCHAR(20)` validado en la aplicación, no `ENUM` de PostgreSQL — mismo criterio que `notifications.type` (`ADR-008`).

**Un pendiente no es un seguidor.** `is_following()`, `followers_count()`, `following_count()` y el filtro de visibilidad cuentan **solo** `'accepted'`. Si un pendiente contara como seguidor, el contador anunciaría gente que todavía no tiene acceso a nada.

### La regla de visibilidad, en un solo lugar

`domain/privacy/visibility.py :: can_view_content_of(...)` es función pura y la única definición:

```
visible  ⟺  el autor no es privado
          ∨  el espectador ES el autor
          ∨  el espectador tiene un follow 'accepted' hacia el autor
```

El segundo caso no es redundante: nadie se sigue a sí mismo (`ck_follows_no_self_follow`, `ADR-007`), así que sin él una cuenta privada no vería **su propio** contenido.

Dos consumidores:
- **Endpoints sobre un post concreto** (`GET`/`POST .../comments`, `POST`/`DELETE .../like`) → el guard `application/privacy/post_visibility.py`, que traduce un "no" a `PostNotFoundError`.
- **El feed** → la expresión SQL equivalente en `SQLAlchemyPostRepository.list_recent`.

### `POST /api/users/<user_id>/follow` — cambia de respuesta

```json
{ "following": true|false, "follow_status": "accepted"|"pending"|null }
```
`following` se conserva con **exactamente el mismo significado** que tenía (`ADR-007`): relación efectiva. Una solicitud pendiente es `false` ahí. `follow_status` es el campo nuevo, y es lo que permite al Frontend dibujar el tercer estado del botón sin inferirlo.

Sigue siendo idempotente, y con un matiz nuevo: un `POST` repetido **no le pisa el estado** a la fila existente. Sin eso, repetir la llamada sobre un follow ya aceptado lo degradaría a `'pending'` solo porque la cuenta se volvió privada después.

Notifica `'follow'` si queda aceptado y `'follow_request'` si queda pendiente — dos eventos distintos: uno informa, el otro pide una acción.

### `DELETE /api/users/<user_id>/follow`

Borra la fila **sea cual sea su estado**: el mismo gesto sirve para dejar de seguir y para cancelar una solicitud sin responder. Son lo mismo desde el Frontend ("ya no quiero esta relación") y no merecen dos endpoints.

### `GET /api/follow-requests`

Las solicitudes dirigidas al usuario autenticado, más recientes primero, límite fijo de 50. **No lleva `user_id` en la URL** — mismo criterio que `GET /api/notifications` y `GET /api/conversations`: nadie puede listar las solicitudes de otro.

### `POST /api/follow-requests/<user_id>/accept` y `DELETE /api/follow-requests/<user_id>`

`<user_id>` es **quien pidió seguir**; quien responde sale del JWT.

- Aceptar → `200 {"accepted": true}`, pasa la fila a `'accepted'` y notifica `'follow_accepted'` al solicitante (sin eso no tendría forma de saber que ya puede ver el contenido).
- Rechazar → `200 {"rejected": true}`, **borra** la fila. No la marca como rechazada: así la persona puede volver a pedirlo y no queda un registro permanente de un "no". El efecto es idéntico a que nunca hubiera pedido. **No se notifica** — avisarle a alguien que lo rechazaste es información que no aporta y que invita a insistir.
- `404` si la solicitud no existe, ya se respondió, o está dirigida a otra persona — los tres indistinguibles.

Aceptar es `POST` (crea una relación nueva); rechazar es `DELETE` (la solicitud deja de existir). El `DELETE` solo toca filas `'pending'`, así que **nunca puede desaparecer a un seguidor ya aceptado**.

### `GET`/`PATCH /api/users/me/privacy`

Endpoint propio, no parte de `PATCH /api/users/me` (`ADR-003`) — ver `ADR-024` §Opciones consideradas, que lo decide para el conjunto de las siete preferencias. Acá transporta `is_private` y `pending_follow_requests_count`.

### Seguridad

- **`404`, nunca `403`,** al pedir contenido de una cuenta privada. Un `403` confirmaría que ese post existe y de quién es — exactamente lo que la cuenta no quiere revelar. Mismo criterio que el `404` indistinguible de `ADR-019`/`ADR-020`/`ADR-021`.
- La pertenencia de una solicitud se confirma **en el propio `WHERE` del `UPDATE`/`DELETE`** (`followed_id = <JWT>` y `status = 'pending'`), no leyendo la fila y comparando después.
- El estado de un follow lo decide el servidor a partir de `is_private` de la cuenta destino; **ningún campo del body puede influir en él**.
- `is_private` se expone en el objeto `user` (lo necesita el Frontend en cada arranque de sesión para saber si mostrar la bandeja); el resto de preferencias vive solo en su endpoint.

## Impacto en Frontend

- **`Configuración › Privacidad`**: el interruptor "Cuenta privada" pasa de `pending` a real, con el aviso de la pantalla reescrito — ya no dice que nada se aplica en el servidor.
- **`FollowRequestsRow.jsx`** (nuevo): bandeja de solicitudes con aprobar/rechazar. Vive dentro de Privacidad, junto al interruptor que las produce. **Se monta aunque la cuenta sea pública**, porque volver a pública no borra lo pendiente — esconderla dejaría solicitudes irrespondibles. Sin actualización optimista: una decisión sobre quién ve tu contenido no se muestra resuelta antes de que lo esté.
- **`CapsuleCard.jsx`**: el botón de seguir gana el tercer estado. Sobre una cuenta privada que no sigue dice "Solicitar"; con solicitud en vuelo, "Solicitado" (y tocarlo la cancela).
- **`AppShell.jsx`**: `handleToggleFollowAuthor` pasa a operar sobre `follow_status`. Mantiene la actualización optimista prediciendo el resultado con `author.is_private`, y después reconcilia con la respuesta del servidor, que es la única autoridad.
- **`mapNotification.js`**: `follow_request` y `follow_accepted` entran en el catálogo de tipos y en los "importantes".

## Impacto en Backend

- `migrations/versions/c3e7b1d9a482_add_private_accounts_and_follow_status.py` (nueva).
- `domain/follows/follow_status.py`, `domain/privacy/visibility.py`, `application/privacy/post_visibility.py` (nuevos).
- `domain/follows/exceptions.py`: `FollowRequestNotFoundError`.
- `domain/follows/repositories.py` + su adaptador: `get_status`, `set_status`, `remove_pending`, `list_pending_requests`, `pending_requests_count`; `followed_user_ids` se **reemplaza** por `follow_statuses` (devuelve el estado, no un sí/no, y resuelve los tres estados del botón en una sola consulta); `is_following`/`followers_count`/`following_count` pasan a contar solo `'accepted'`.
- `domain/posts/repositories.py` + adaptador: `list_recent` toma `viewer_id` y filtra en SQL.
- `application/follows/`: `follow_presenter.py`, `list_follow_requests_use_case.py`, `respond_follow_request_use_case.py` (nuevos); `follow_user`/`unfollow_user` reescritos.
- `application/privacy/privacy_presenter.py`, `privacy_settings_use_case.py` (nuevos, compartidos con `ADR-023`/`ADR-024`).
- Los cuatro casos de uso de comentarios/likes reciben `follow_repository` y llaman al guard.
- `interfaces/routes/follow_routes.py` (tres endpoints nuevos), `privacy_routes.py` (nuevo).
- Tests de integración nuevos en `tests/test_privacy.py`; cuatro aserciones de `tests/test_follows.py` actualizadas por el campo aditivo `follow_status`.

## Riesgos

- **Notificaciones que sobreviven a la privacidad.** `GET /api/notifications` no se filtra: si A le dio like a un post de B y B se vuelve privado, A sigue viendo la notificación. No filtra contenido (el `post_id` ya no se puede abrir), pero revela que algo pasó. Filtrarlo exige aplicar la regla de visibilidad a cada notificación, con su `post_id`, en cada lectura — coste alto para una fuga cosmética. Se deja señalado.
- **La regla vive en dos sintaxis.** La función pura y la expresión SQL tienen que decir lo mismo. Es el precio de filtrar en el `WHERE`; se mitiga con comentarios cruzados y con pruebas que cubren los tres caminos (`no privado` / `es el autor` / `seguidor aceptado`) en los dos consumidores.
- **Rendimiento del `EXISTS` por fila del feed.** Cada post evalúa un `EXISTS` sobre `follows`. Está cubierto por la `UNIQUE (follower_id, followed_id)`, así que es una búsqueda por índice, pero no se midió con volumen real — el proyecto no tiene entorno de carga (`CLAUDE.md` §15, DevOps sin documentar).
- **Sin límite de solicitudes.** Nada impide pedir, cancelar y volver a pedir en bucle, generando una notificación cada vez. Coherente con el resto del proyecto, que no tiene *rate limiting* (`API_CONTRACT.md` §9).

## Decisiones pendientes (cada una es su propio ADR futuro)

- Bloquear a una persona.
- Filtrar `GET /api/notifications` por visibilidad actual.
- Ocultar el perfil (no solo el contenido) de una cuenta privada, cuando exista un endpoint de perfil público.
- Listar seguidores/seguidos — heredada de `ADR-007`.
- *Rate limiting* de solicitudes (transversal).

## Consecuencias

- **`DATABASE_ARCHITECTURE.md` cambia** (`users.is_private`, `follows.status`) → v0.19.
- `API_CONTRACT.md` se actualiza el mismo día (`HB-001` §15.1) → v0.23. **Tres endpoints existentes cambian de comportamiento sin cambiar de forma** (feed, comentarios, likes), y `POST`/`DELETE .../follow` ganan un campo aditivo.
- `ADR-007` queda extendido, no reemplazado: `follows` sigue siendo la misma entidad con la misma `UNIQUE`.

## Referencias

- `docs/architecture/ADR-007-follows-minimal-model.md` — entidad `follows` que este ADR extiende.
- `docs/architecture/ADR-004-posts-minimal-model.md` — feed global que este ADR pasa a filtrar.
- `docs/architecture/ADR-019-post-deletion.md`, `ADR-020-comment-deletion.md`, `ADR-021-content-editing.md` — origen del criterio del `404` indistinguible.
- `docs/architecture/ADR-023-mentions.md`, `ADR-024-content-filters-and-privacy-preferences.md` — los otros dos ADR de la misma pantalla.
- `CLAUDE.md` — jerarquía de fuentes (§4), regla de alcance (§14).

---

## Cierre

El primer control de la pantalla de Privacidad pasa de `pending` a real, y con él aparece la primera regla de autorización de lectura del producto: hasta ahora el backend solo verificaba *quién sos*, nunca *qué podés ver*.
