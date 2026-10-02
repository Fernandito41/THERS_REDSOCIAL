# ADR-021 — Edición de contenido propio: publicaciones, comentarios y mensajes

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/ADR-021-content-editing.md` |
| Tipo | Architecture Decision Record (`HB-001` §11–12) |
| Fecha | 01/10/2026 |
| Estado | **Aceptada** — implementada en esta tarea (ver §Decisión) |
| Alcance | `backend/` — `PATCH /api/posts/<post_id>`, `PATCH /api/comments/<comment_id>`, `PATCH /api/messages/<message_id>`; `Frontend/` — edición en línea en `CapsuleCard.jsx` (publicaciones y comentarios) y `Messages.jsx` (mensajes) |
| Autoridad sobre este documento | `/docs` oficial > estructura real observada en el código > este documento (mismo orden que `CLAUDE.md` §4) |

> Extiende `ADR-004-posts-minimal-model.md`, `ADR-006-comments-minimal-model.md` y `ADR-013-messages-minimal-model.md`, que crearon las tres entidades sin ninguna operación de actualización. Cierra el ítem "Editar una publicación" de `ADR-019-post-deletion.md` §Decisiones pendientes, "Editar un comentario" de `ADR-020-comment-deletion.md` §Decisiones pendientes, y la edición de mensajes que `ADR-014` no cubrió. **Introduce una columna nueva (`edited_at`) en tres tablas** — es el único ADR de esta serie con migración.

---

## Contexto

Las tres superficies de contenido propio del producto se pueden crear y borrar, pero no corregir:

| Entidad | Crear | Listar | Borrar | **Editar** |
|---|---|---|---|---|
| `posts` | `ADR-004` | `ADR-004` | `ADR-019` | **este ADR** |
| `comments` | `ADR-006` | `ADR-006` | `ADR-020` | **este ADR** |
| `messages` | `ADR-013` | `ADR-013` | `ADR-014` | **este ADR** |

Hasta ahora, la única forma de corregir un error de tipeo era borrar y volver a publicar — lo que en una publicación significa perder sus likes y los comentarios que otras personas escribieron (`ADR-019` §Riesgos), y en un mensaje significa que la otra persona ve desaparecer el mensaje y aparecer otro. El propio producto lo registra: el artículo de ayuda `editar-o-eliminar-publicaciones` (`Frontend/src/features/help/data/articles.js`) decía que "no hay una opción para editar el texto de una Cápsula ya publicada", y recomendaba justamente ese camino destructivo.

Los tres ADR de borrado dejaron la edición explícitamente fuera por el mismo motivo: es una operación distinta, con contrato propio (`PATCH`), con preguntas propias (¿historial de versiones? ¿qué pasa con los likes de la versión anterior?) y con una columna nueva. Este ADR las responde.

### Por qué un solo ADR y no tres

`ADR-019` y `ADR-020` se separaron porque la semántica del borrado **difiere** por entidad: borrar una publicación ejerce tres `ON DELETE CASCADE`, borrar un comentario ninguno. Acá la decisión es **la misma** en las tres: mismo verbo, mismo body, mismo `404` indistinguible, misma columna, misma migración. Partirla en tres documentos obligaría a repetir el mismo razonamiento tres veces —  lo que `CLAUDE.md` §6 prohíbe explícitamente ("cada decisión vive en un único documento") — y dejaría la migración compartida colgando de uno de los tres de forma arbitraria.

## Objetivos

- El autor de una publicación, comentario o mensaje puede corregir su texto sin destruir nada de lo que ese contenido acumuló.
- Quien lo lee puede saber que el texto fue editado, para no quedar discutiendo con una versión que ya no existe.
- Nadie puede editar contenido que no escribió, y el intento no revela si ese contenido existe.
- Editar no puede ser un vector para cambiar nada más que el texto: ni el autor, ni el destinatario, ni la publicación a la que pertenece un comentario, ni si un mensaje fue leído.

## No objetivos (explícitamente fuera de este ADR)

- **No** guarda historial de versiones ni permite ver el texto anterior. La fila se sobrescribe; lo único que queda es que hubo una edición. Un historial exige una tabla nueva (`post_revisions` o equivalente) y es su propio ADR — ver §Decisiones pendientes.
- **No** expone *cuándo* se editó. `edited_at` se persiste pero la API solo expone el booleano `edited`; la UI dice «editado», nunca «editado hace 5 minutos» (ver §Opciones consideradas).
- **No** impone una ventana de tiempo para editar (del tipo "solo dentro de los primeros 15 minutos"). Coherente con el resto del proyecto, que no tiene *rate limiting* ni ventanas en ningún endpoint (`API_CONTRACT.md` §9).
- **No** permite editar contenido ajeno, ni al dueño de la publicación sobre los comentarios que recibió — mismo criterio que `ADR-020` ya fijó para el borrado.
- **No** notifica a nadie de una edición. Nadie se enterará de que un mensaje que ya leyó cambió, salvo que vuelva a mirarlo (ver §Riesgos).
- **No** permite editar nada que no sea el texto: ni agregar/quitar una imagen (no existen, `ADR-004`), ni mover un comentario a otra publicación, ni reasignar un mensaje.
- **No** toca `updated_at` como señal de edición (ver §Opciones consideradas).

## Opciones consideradas — cómo se sabe que algo fue editado

| Opción | Descripción | Trade-off |
|---|---|---|
| **A — Columna `edited_at` nullable, expuesta como booleano `edited` (elegida)** | NULL = nunca editado. La API expone `edited: true/false`, nunca el timestamp | Explícita y auto-documentada: una columna cuyo único significado es "hubo una edición". Es exactamente el idioma que el esquema ya usa (`messages.read_at`, `notifications.read_at`: NULL = no leído, y la API expone `read` como booleano — `ADR-008`/`ADR-013`). Cuesta una migración en tres tablas |
| B — Inferirlo de `updated_at > created_at` | `posts`/`comments` ya tienen `updated_at` con `server_default now()` | Sin migración para `posts`/`comments`, pero: (1) `messages` **no tiene** `updated_at` y su modelo lo dice explícitamente, así que haría falta migrar esa tabla igual; (2) la condición es implícita y frágil — cualquier escritura futura sobre la fila por otro motivo marcaría el contenido como "editado" sin que nadie lo hubiera editado; (3) depende de que las dos columnas nazcan exactamente iguales, lo que hoy es cierto solo porque `now()` es estable dentro de una transacción en PostgreSQL. Descartada |
| C — Exponer el timestamp de la edición (`edited_at` en el JSON) | La UI podría decir "editado hace 5 min" | Es más información, pero la convierte en información que hay que mantener consistente y traducir en la UI. El esquema ya tomó la decisión opuesta dos veces para `read_at` por el mismo motivo ("nunca cruza la frontera HTTP como timestamp crudo", `models.py`). Se descarta por consistencia; si el equipo la quiere, es una extensión aditiva del contrato, no un rediseño |
| D — Sin marca alguna: editar en silencio | Lo más simple | Permite reescribir lo que alguien ya leyó o respondió sin que quede rastro. Inaceptable en un mensaje directo o en una publicación con comentarios: convierte la edición en una herramienta para cambiar el sentido de una conversación. Descartada |

**Elegida: A.** La única que reutiliza un idioma que el esquema ya tiene, sin depender de una condición implícita.

### Opciones consideradas — orden del feed al editar

Editar **no** toca `created_at`, así que una publicación editada **no sube** en el feed (que ordena por `created_at` descendente, `ADR-004`). La alternativa — ordenar por "última actividad" — convertiría la edición en una forma de recuperar visibilidad, y cambiaría el contrato de `GET /api/posts` para todos. Descartada; no se evaluó más allá de eso porque nadie la pidió.

## Decisión

### `PATCH /api/posts/<post_id>`, `PATCH /api/comments/<comment_id>`, `PATCH /api/messages/<message_id>`

Reemplazan el texto de un contenido propio. Auth requerida. Los tres comparten exactamente la misma forma:

```json
// Request
{ "content": "string (1–N caracteres tras trim)" }
```
`N` es el límite que cada entidad ya tenía al crear, sin cambios y con el mismo validador: **2000** para posts (`ADR-004`) y mensajes (`ADR-013`), **1000** para comentarios (`ADR-006`). Editar no puede saltarse el límite que crear respeta.

**Response 200:** el recurso completo y actualizado, con la misma forma que devuelve su endpoint de creación — `{"post": {...}}`, `{"comment": {...}}`, `{"message": {...}}`. Devolver el recurso entero (y no, por ejemplo, `{"updated": true}`) permite al Frontend reemplazar el objeto en memoria por la respuesta del servidor, sin adivinar el resultado ni pedir el recurso otra vez.

- `400` si el body está vacío o `content` falta, queda vacío tras `trim()` o excede el límite. **`content` es obligatorio**, no opcional: a diferencia de `PATCH /api/users/me` (`ADR-003`), donde el `PATCH` elige entre varios campos, acá es el único campo editable y un `PATCH` sin él no tiene nada que hacer.
- `404` si el id no existe **o** existe pero no le pertenece a quien hace la petición — mismo mensaje y código en ambos casos, sin distinguir cuál ocurrió. Incluye cualquier segmento de URL que no sea un UUID válido (conversor `uuid` de Flask/Werkzeug). Mismo criterio que los tres `DELETE` equivalentes (`ADR-014`/`ADR-019`/`ADR-020`).
- `401` estándar.

**Verbo `PATCH`, no `PUT`:** se actualiza un campo de un recurso que tiene más campos, no se reemplaza el recurso entero. Es además el verbo que el proyecto ya usa para actualización parcial (`PATCH /api/users/me` §4.2, `PATCH /api/notifications/<id>/read` §4.7).

**Rutas planas**, no anidadas: `/comments/<id>` y no `/posts/<id>/comments/<id>`; `/messages/<id>` y no `/users/<id>/messages/<id>`. Editar depende de quién escribió el contenido, no del recurso donde está — mismo razonamiento que ya fijaron `DELETE /api/messages/<id>` (`ADR-014`) y `DELETE /api/comments/<id>` (`ADR-020`). Cada endpoint vive en el blueprint que ya tenía la entidad (`posts_bp`, `comments_bp`, `messages_bp`).

**Idempotente en su efecto observable:** repetir el mismo `PATCH` deja el mismo texto y `edited` sigue en `true`. Lo único que cambia es `edited_at`, que no se expone. A diferencia de `DELETE`, un segundo `PATCH` sobre contenido que sigue existiendo es `200`, no `404`.

### Modelo de datos — `edited_at`

Una columna nueva, idéntica en las tres tablas:

```
edited_at  TIMESTAMP WITH TIME ZONE  NULL
```
- **NULL = nunca editado.** Las filas que ya existían quedan en NULL sin *backfill* ni valor centinela.
- La escribe PostgreSQL (`now()`), no Python — mismo criterio que `created_at`/`read_at`.
- **Sin `coalesce`**, a diferencia de `read_at` en `NotificationRepository.mark_as_read`: ahí el `coalesce` existe para no renovar la marca en una segunda llamada (idempotente por diseño), mientras que acá cada edición es un evento nuevo y `edited_at` debe reflejar la última, no la primera.
- `messages` sigue **sin** `updated_at`, a diferencia de `posts`/`comments`: no hace falta un timestamp de "última escritura" genérico cuando las dos escrituras posibles sobre un mensaje (marcar leído, editar) ya tienen cada una su columna.

Una sola migración (`a2c6e9b3f571`) para las tres tablas: es la misma columna con la misma semántica.

### Lo que la edición deliberadamente **no** cambia

| Dato | Qué pasa al editar | Por qué |
|---|---|---|
| `id` de la fila | No cambia | Es lo que hace que likes y comentarios sigan colgando del mismo post (ver §Consecuencias) |
| `created_at` | No cambia | Editar no "revive" una publicación en el feed (ver §Opciones consideradas) |
| `likes_count`, `comments_count` | No cambian | Editar el texto no es un evento social; la respuesta del `PATCH` devuelve los contadores **reales**, no `0` |
| `messages.read_at` | No cambia | Editar un mensaje ya leído no lo devuelve a no leído: el separador de "mensajes no leídos" de `Messages.jsx` (`ADR-014`) no debe reordenarse porque alguien corrigió una palabra |
| `comments.post_id`, `messages.recipient_id`, `*.author_id`/`sender_id` | No cambian | No están en la *whitelist* del body (ver §Seguridad) |
| `notifications` | No se crea ninguna | La notificación "comentó tu publicación" (`ADR-008`) se emitió al crear el comentario; editarlo no es un evento social nuevo |

### Seguridad

- `author_id`/`sender_id` salen exclusivamente de `get_jwt_identity()`; nunca del body, de la query string ni de ningún header propio.
- La pertenencia se verifica **en el propio `WHERE` del `UPDATE`** (`WHERE id = ... AND author_id = ...`), no leyendo la fila y comparando después — no hay ventana entre comprobar y actuar. Mismo principio que los tres `DELETE`.
- **Whitelist explícita de un solo campo:** solo `content` se lee del body. `id`, `author_id`/`sender_id`, `recipient_id`, `post_id`, `created_at`, `edited_at` y `read` se ignoran si vienen — mismo principio anti *mass-assignment* que `POST /api/posts` y `PATCH /api/users/me` (`ADR-003` §Seguridad). Cubierto por prueba en las tres entidades.
- El `404` indistinguible evita usar estos endpoints para averiguar qué ids existen.

## Impacto en Frontend

Edición **en línea**, no en un modal: el contenido mismo se vuelve un formulario con «Guardar» y «Cancelar». **Sin confirmación previa**, a diferencia del borrado — una edición se puede volver a editar, así que no hay nada irreversible que confirmar, y el `ConfirmDialog` se reserva para lo que sí lo es.

En las tres superficies, «Guardar» queda deshabilitado si el texto no cambió: un guardado sin cambios marcaría el contenido como «editado» sin que nada hubiera cambiado. Si la petición falla, el editor queda abierto con lo escrito y se avisa por Toast — mismo criterio que el formulario de comentario ya tenía.

- **`CapsuleCard.jsx`**: lápiz en la cabecera de cada publicación propia y junto a cada comentario propio. La marca «editado» acompaña la hora en ambos. No se dibuja sobre contenido ajeno — esa ocultación es cortesía de interfaz, no el control de acceso; el control real es el `404` del backend.
- **`AppShell.jsx`**: `handleEditCapsule` y `handleEditComment`, mismo reparto que los de borrado (la petición acá, el estado del panel en `CapsuleCard`). **Sin actualización optimista**, a diferencia de `handleDeleteCapsule`: el servidor devuelve la publicación completa ya editada, así que se reemplaza con su respuesta en vez de adivinarla.
- **`Home.jsx`, `Profile.jsx`, `Search.jsx`**: pasan las dos acciones a `CapsuleCard`, igual que ya pasan las de borrado. Sin lógica duplicada en ninguna de las tres.
- **`Messages.jsx`**: lápiz junto a la papelera de cada mensaje propio, visible al pasar el mouse; la burbuja se convierte en un input en línea. `editDraft`/`editingId` son estado aparte de `thread`, así que el *polling* del hilo (4s, `ADR-014`) no borra lo que la persona está escribiendo. Tras guardar, resincroniza `GET /api/conversations` porque el resumen de la conversación muestra el texto del último mensaje, que pudo ser justo el editado.
- **`features/help/data/articles.js`**: el artículo `editar-o-eliminar-publicaciones` decía que editar no estaba disponible y recomendaba borrar y volver a publicar. Se corrige para describir la edición real.

## Impacto en Backend

- `domain/posts/repositories.py`, `domain/comments/repositories.py`, `domain/messages/repositories.py`: cada puerto gana `update_content(...)`.
- `domain/*/exceptions.py`: **sin cambios** — se reutilizan `PostNotFoundError`, `CommentNotFoundError` y `MessageNotFoundError`, que ya existían para el borrado, en vez de crear tres excepciones equivalentes.
- `application/posts/update_post_use_case.py`, `application/comments/update_comment_use_case.py`, `application/messages/update_message_use_case.py` (nuevos).
- `application/*/..._presenter.py`: los tres presenters ganan `"edited"`. Extensión **aditiva** — ningún campo existente cambia de nombre, tipo ni semántica, así que `POST`/`GET` de las tres entidades empiezan a devolver `edited` sin romper nada.
- `infrastructure/persistence/repositories/{post,comment,message}_repository.py`: cada adaptador implementa `update_content(...)`.
- `infrastructure/persistence/models.py`: `Post`, `Comment` y `Message` ganan `edited_at`.
- `interfaces/routes/{post,comment,message}_routes.py`: cada uno gana su `PATCH`, sobre el blueprint que ya tenía.
- `migrations/versions/a2c6e9b3f571_add_edited_at_to_posts_comments_messages.py` (nueva).
- Tests de integración nuevos en `tests/test_posts.py`, `tests/test_comments.py` y `tests/test_messages.py`, mismo patrón que el resto de cada archivo.

## Riesgos

- **Reescritura silenciosa de lo ya leído.** La marca «editado» dice *que* cambió, no *qué* cambió: alguien puede editar un mensaje o una publicación después de que se leyera o se le respondiera, y quien lo leyó no se enterará salvo que vuelva a mirar. Es el trade-off aceptado al descartar el historial de versiones (§No objetivos); la marca es la mitigación mínima, no una solución completa.
- **Likes y comentarios sobre una versión que ya no existe.** Quien dio like o comentó la versión anterior queda asociado a un texto distinto. Es la consecuencia directa de mantener el `id` de la fila (que es lo que evita perder esos likes y comentarios al corregir un tipeo) — exactamente la pregunta que `ADR-019` había dejado abierta, y se resuelve a favor de preservar el contenido acumulado. Si el equipo prefiere invalidar los likes al editar, es una decisión de producto separada.
- **Sin ventana de arrepentimiento ni límite de frecuencia.** Nada impide editar una publicación de hace un año, ni editarla cien veces. Coherente con el resto de endpoints del proyecto (`API_CONTRACT.md` §9 ya registra el *rate limiting* como pendiente transversal).
- **Sin bloqueo de concurrencia.** Si la misma persona edita el mismo contenido desde dos pestañas, gana la última escritura, sin aviso. No hay *optimistic locking* en ningún endpoint del proyecto; se deja señalado, no se resuelve acá.
- **`last_message` de `GET /api/conversations` no expone `edited`.** Es una vista derivada, no el mensaje: muestra el texto vigente (correcto) pero sin la marca. El Frontend muestra la marca en el hilo, donde el mensaje sí viaja completo. Se deja así a propósito; extenderlo es aditivo si el equipo lo pide.

## Decisiones pendientes (cada una es su propio ADR futuro)

- Historial de versiones y poder ver el texto anterior de una edición.
- Exponer `edited_at` como timestamp, para poder decir "editado hace 5 minutos".
- Ventana de tiempo para editar, y/o *rate limiting* (transversal, no solo de estos endpoints).
- Que el autor de una publicación pueda moderar (borrar/ocultar) comentarios ajenos en ella — heredada de `ADR-020`, sigue abierta.
- Añadir `comment_id` a `notifications` — heredada de `ADR-020`, sigue abierta.
- *Optimistic locking* para escrituras concurrentes.

## Consecuencias

- **`DATABASE_ARCHITECTURE.md` cambia** — a diferencia de `ADR-019`/`ADR-020`, este ADR agrega una columna a tres tablas ya implementadas. `posts`, `comments` y `messages` pasan a tener `edited_at`.
- `API_CONTRACT.md` se actualiza el mismo día que este contrato se implementa (`HB-001` §15.1) → v0.22, incluyendo el campo `edited` aditivo en las tres entidades.
- Ningún endpoint existente cambia de contrato en forma incompatible: `edited` es un campo nuevo en respuestas que ya existían.

## Referencias

- `docs/architecture/ADR-004-posts-minimal-model.md`, `ADR-006-comments-minimal-model.md`, `ADR-013-messages-minimal-model.md` — las tres entidades que este ADR extiende.
- `docs/architecture/ADR-019-post-deletion.md`, `ADR-020-comment-deletion.md`, `ADR-014-messages-ux-improvements.md` — los tres borrados cuyo criterio (propio, `404` indistinguible, ruta plana) este ADR replica, y cuyas §Decisiones pendientes listaban esta edición.
- `docs/architecture/ADR-003-profile-update-contract.md` — precedente de `PATCH` y del principio anti *mass-assignment*.
- `docs/architecture/ADR-008-notifications-minimal-model.md` — origen del idioma `read_at` NULL → booleano `read` que `edited_at`/`edited` reutiliza.
- `docs/architecture/DATABASE_ARCHITECTURE.md` — modelo de datos, actualizado por este ADR.
- `CLAUDE.md` — jerarquía de fuentes (§4), no duplicar contenido entre documentos (§6), regla de alcance (§14).

---

## Cierre

Las tres superficies de contenido propio del producto quedan con el ciclo completo: crear, listar, editar y borrar. La edición preserva todo lo que el contenido acumuló (likes, comentarios, estado de lectura, posición en el feed) y deja constancia de que hubo un cambio, sin pretender reconstruir qué cambió — eso queda registrado como decisión pendiente, no resuelto por criterio propio.
