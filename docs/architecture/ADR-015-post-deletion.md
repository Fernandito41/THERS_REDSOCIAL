# ADR-015 — Borrado de publicaciones propias

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/ADR-015-post-deletion.md` |
| Tipo | Architecture Decision Record (`HB-001` §11–12) |
| Fecha | 26/09/2026 |
| Estado | **Aceptada** — implementada en esta tarea (ver §Decisión) |
| Alcance | `backend/` — `DELETE /api/posts/<post_id>`; `Frontend/` — acción "Eliminar" en `CapsuleCard.jsx` |
| Autoridad sobre este documento | `/docs` oficial > estructura real observada en el código > este documento (mismo orden que `CLAUDE.md` §4) |

> Extiende `ADR-004-posts-minimal-model.md`, que creó la entidad `posts` sin ninguna operación de borrado. No introduce ninguna entidad ni columna nueva.

---

## Contexto

`posts` existe desde `ADR-004` con solo dos operaciones: crear y listar. Una publicación, una vez hecha, no se puede quitar — ni por error de tipeo, ni por arrepentimiento. Es la contraparte que los mensajes ya tienen desde `ADR-014` (`DELETE /api/messages/<message_id>`), y el hueco está registrado explícitamente dentro del propio producto: el artículo de ayuda `editar-o-eliminar-publicaciones` (`Frontend/src/features/help/data/articles.js`) dice hoy que "no hay una opción para editar o eliminar una Cápsula después de publicarla".

Este ADR cubre **solo el borrado**. Editar una publicación ya hecha sigue sin existir y no forma parte de esta decisión.

## Objetivos

- El autor de una publicación puede borrarla; deja de existir para todos.
- Borrar una publicación no deja likes, comentarios ni notificaciones huérfanos apuntando a algo que ya no existe.
- Nadie puede borrar una publicación que no es suya, y el intento no revela si esa publicación existe.

## No objetivos (explícitamente fuera de este ADR)

- **No** implementa editar una publicación — es una operación distinta (contrato `PATCH`, historial de ediciones, qué pasa con los likes de una versión anterior) y merece su propio ADR.
- **No** deja un placeholder tipo "Esta publicación fue eliminada" — se borra la fila, sin rastro. Mismo criterio que `ADR-014` ya adoptó para mensajes.
- **No** implementa borrado lógico (`deleted_at`) ni papelera/deshacer — el borrado es inmediato y definitivo (ver §Opciones consideradas).
- **No** implementa moderación: un administrador no puede borrar la publicación de otra persona. No existe el concepto de rol administrador en el producto — `DATABASE_ARCHITECTURE.md` §4.B no registra ninguna candidata de roles/permisos ratificada.
- **No** implementa borrar comentarios propios — es otro recurso y otro contrato; lo cubre `ADR-016-comment-deletion.md`.

## Opciones consideradas — *hard delete* vs. borrado lógico

| Opción | Descripción | Trade-off |
|---|---|---|
| **A — `DELETE` real de la fila (elegida)** | Se borra la fila de `posts` filtrando por `id` y `author_id` a la vez; likes, comentarios y notificaciones caen por el `ON DELETE CASCADE` ya declarado | Es lo que ya hace `ADR-014` para mensajes — misma semántica para el usuario ("borrar es borrar") en las dos superficies del producto. No agrega columnas ni obliga a filtrar por `deleted_at` en cada consulta existente de `posts`/`likes`/`comments`/`notifications` |
| B — Borrado lógico (`posts.deleted_at`) | La fila queda, marcada como borrada, y todas las lecturas la filtran | Habilitaría "deshacer" y un placeholder "publicación eliminada", pero obliga a tocar cada consulta ya escrita sobre `posts` y sobre todo lo que cuelga de él (likes, comentarios, notificaciones, feed) — coste alto para una función que nadie pidió todavía. Si el equipo la pide, es un ADR propio, no un efecto colateral de este |
| C — Papelera con retención (borrado diferido) | La publicación se oculta y se borra de verdad tras N días | Exige un proceso programado que el proyecto no tiene — DevOps sigue sin documentación oficial (`CLAUDE.md` §15), no hay tareas periódicas ni CI/CD. Sobre-ingeniería para hoy |

**Elegida: A.** La más simple, y la única coherente con el borrado de mensajes que el producto ya expone.

## Decisión

### `DELETE /api/posts/<post_id>`

Borra una publicación propia (*hard delete*, sin placeholder). Auth requerida. Solo el autor puede borrar su propia publicación — mismo criterio que `DELETE /api/messages/<message_id>` (`ADR-014`) y que `PATCH /api/notifications/<id>/read` (`ADR-008`): si la publicación no existe **o** existe pero no es del usuario autenticado, responde el mismo `404`, sin distinguir cuál de los dos pasó.

```json
// Response 200
{ "deleted": true }
```
- `404` si `post_id` no existe, o existe pero no le pertenece a quien hace la petición. Incluye cualquier segmento de URL que no sea un UUID válido (el conversor `uuid` de Flask/Werkzeug ya lo descarta antes del handler).
- `401` estándar.

**No es idempotente**, a diferencia de `DELETE /api/posts/<id>/like` y `DELETE /api/users/<id>/follow` (`ADR-005`/`ADR-007`): borrar dos veces la misma publicación devuelve `200` y después `404`. Aquellos dos son idempotentes porque "no tener un like" es un estado válido y alcanzable; acá el segundo intento apunta a un recurso que ya no existe, que es exactamente lo que un `404` significa.

**Ruta plana bajo `/posts/<post_id>`**, no anidada — es el recurso mismo el que se borra, no un sub-recurso suyo (a diferencia de `/posts/<id>/like`).

### Efecto en cascada

Likes (`ADR-005`), comentarios (`ADR-006`) y notificaciones (`ADR-008`) ya declaran su clave foránea a `posts.id` con `ON DELETE CASCADE` — decisión tomada en cada uno de esos ADR como "placeholder razonable dado que borrado de post tampoco existe todavía". **Este ADR es el momento en que ese placeholder pasa a ejercerse de verdad**, y se ratifica tal como está: PostgreSQL borra las filas dependientes en la misma transacción, sin código que las recorra a mano. Sin migración nueva — el esquema no cambia.

### Seguridad

- `author_id` sale exclusivamente de `get_jwt_identity()`; nunca del body, de la query string ni de ningún header propio (mismo principio que el resto de endpoints protegidos).
- La pertenencia se verifica **en la misma sentencia** que confirma la existencia, no leyendo la fila y comparando después — no hay ventana entre comprobar y actuar.
- El `404` indistinguible evita que alguien use este endpoint para averiguar qué `post_id` existen.

## Impacto en Frontend

- `CapsuleCard.jsx`: cada publicación propia gana una acción "Eliminar" en su cabecera, con confirmación previa antes de mandarla — el borrado no se puede deshacer y arrastra likes y comentarios, así que se avisa. La acción no se dibuja sobre publicaciones ajenas; esa ocultación es una cortesía de interfaz, no el control de acceso — el control real es el `404` del backend.
- `AppShell.jsx`: `handleDeleteCapsule` con actualización optimista y rollback, mismo patrón que `handleToggleLike` (`ADR-005`). La tarjeta desaparece al instante y vuelve a su posición original si la petición falla. Tras un borrado exitoso recarga `GET /api/notifications`, porque las notificaciones de ese post desaparecieron en cascada del lado del servidor y la copia en memoria quedaría desactualizada.
- `Home.jsx`, `Profile.jsx`, `Search.jsx`: pasan la acción a `CapsuleCard`, igual que ya pasan `onToggleLike`/`onPostComment`/`onToggleFollowAuthor`. No se duplica lógica en ninguna de las tres.
- `features/help/data/articles.js`: el artículo `editar-o-eliminar-publicaciones` decía que borrar no estaba disponible. Se corrige para describir el borrado real; **editar sigue sin existir** y el artículo lo sigue diciendo.

## Impacto en Backend

- `domain/posts/repositories.py`: `PostRepository` gana `delete(post_id, author_id)`.
- `domain/posts/exceptions.py`: **sin cambios** — se reutiliza `PostNotFoundError`, que ya existía para `likes`/`comments`, en vez de crear una excepción equivalente.
- `application/posts/delete_post_use_case.py` (nuevo).
- `infrastructure/persistence/repositories/post_repository.py`: `SQLAlchemyPostRepository` gana `delete(...)`.
- `interfaces/routes/post_routes.py`: gana `DELETE /posts/<uuid:post_id>`, sobre el `posts_bp` existente.
- Sin migración nueva — el esquema de PostgreSQL no cambia.
- Tests de integración nuevos en `tests/test_posts.py`, mismo patrón que el resto del archivo.

## Riesgos

- **Borrado irreversible y sin aviso al resto:** quien comentó o dio like a una publicación la ve desaparecer sin explicación. Es el mismo comportamiento que `ADR-014` ya aceptó para mensajes; si el equipo prefiere un placeholder, es un cambio de esquema y una decisión de producto separada.
- **Pérdida de comentarios ajenos:** borrar una publicación borra también los comentarios que otras personas escribieron en ella. Es la consecuencia directa del `ON DELETE CASCADE` que `ADR-006` ya había decidido; se deja señalado porque hasta ahora ese camino no era alcanzable.
- **Sin límite de tiempo ni de frecuencia:** no hay ventana de arrepentimiento ni *rate limit* — coherente con el resto de endpoints del proyecto, que tampoco lo tienen (`API_CONTRACT.md` §9 ya registra el *rate limiting* como pendiente transversal).

## Decisiones pendientes (quedan fuera, cada una es su propio ADR futuro)

- Editar una publicación ya hecha.
- ~~Borrar un comentario propio (`ADR-006` no lo cubre).~~ — resuelto por `ADR-016-comment-deletion.md`.
- Placeholder "publicación eliminada" en vez de desaparición silenciosa.
- Borrado de cuenta, que arrastraría todo el contenido de una persona — el `ON DELETE CASCADE` sobre `users.id` de cada entidad ya está preparado, pero la funcionalidad no existe ni está decidida.

## Consecuencias

- `DATABASE_ARCHITECTURE.md` no cambia — ninguna tabla, columna ni restricción se modifica; lo único que cambia es que un `ON DELETE CASCADE` ya declarado pasa a ser alcanzable.
- `API_CONTRACT.md` se actualiza el mismo día que este contrato se implementa (`HB-001` §15.1).

## Referencias

- `docs/architecture/ADR-004-posts-minimal-model.md` — entidad `posts` que este ADR extiende.
- `docs/architecture/ADR-005-likes-minimal-model.md`, `ADR-006-comments-minimal-model.md`, `ADR-008-notifications-minimal-model.md` — los tres `ON DELETE CASCADE` sobre `posts.id` que este ADR pasa a ejercer.
- `docs/architecture/ADR-014-messages-ux-improvements.md` — precedente directo del criterio de borrado (propio, *hard delete*, `404` indistinguible).
- `CLAUDE.md` — jerarquía de fuentes (§4), regla de alcance (§14), reglas específicas para Claude Code (§8).

---

## Cierre
