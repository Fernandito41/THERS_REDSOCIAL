# ADR-020 — Borrado de comentarios propios

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/ADR-020-comment-deletion.md` |
| Tipo | Architecture Decision Record (`HB-001` §11–12) |
| Fecha | 26/09/2026 |
| Estado | **Aceptada** — implementada en esta tarea (ver §Decisión) |
| Alcance | `backend/` — `DELETE /api/comments/<comment_id>`; `Frontend/` — acción "Eliminar" sobre comentarios propios en `CapsuleCard.jsx` |
| Autoridad sobre este documento | `/docs` oficial > estructura real observada en el código > este documento (mismo orden que `CLAUDE.md` §4) |

> Extiende `ADR-006-comments-minimal-model.md`, que creó `comments` sin ninguna operación de borrado. Cierra el ítem "Borrar un comentario propio" que `ADR-019-post-deletion.md` dejó en §Decisiones pendientes. No introduce ninguna entidad ni columna nueva.

---

## Contexto

`comments` existe desde `ADR-006` con dos operaciones: crear y listar. Un comentario, una vez publicado, no se puede quitar. Publicaciones (`ADR-019`) y mensajes (`ADR-014`) ya se pueden borrar; los comentarios eran la última superficie de contenido propio sin esa opción.

## Objetivos

- El autor de un comentario puede borrarlo; deja de existir para todos.
- El contador `comments_count` de la publicación refleja el borrado.
- Nadie puede borrar un comentario que no escribió, y el intento no revela si ese comentario existe.

## No objetivos (explícitamente fuera de este ADR)

- **No** permite que el **autor de la publicación** borre comentarios ajenos hechos en ella. Es una decisión de producto distinta (moderación del propio espacio) con su propio contrato de permisos; hoy solo borra quien escribió. Ver §Decisiones pendientes.
- **No** implementa editar un comentario.
- **No** deja un placeholder "comentario eliminado" ni borrado lógico — se borra la fila, mismo criterio que `ADR-014`/`ADR-019`.
- **No** retira la notificación "comentó tu publicación" ya generada (ver §Riesgos).

## Decisión

### `DELETE /api/comments/<comment_id>`

Borra un comentario propio (*hard delete*). Auth requerida. Solo su autor puede borrarlo: si el comentario no existe **o** existe pero es de otra persona, responde el mismo `404`, sin distinguir cuál de los dos pasó (mismo criterio que `ADR-014` y `ADR-019`).

```json
// Response 200
{ "deleted": true }
```
- `404` si `comment_id` no existe, o no le pertenece a quien hace la petición. Incluye cualquier segmento de URL que no sea un UUID válido (conversor `uuid` de Flask/Werkzeug).
- `401` estándar.

**No es idempotente**: borrar dos veces devuelve `200` y después `404`, igual que `DELETE /api/posts/<id>` (`ADR-019`).

**Ruta plana bajo `/comments/<comment_id>`**, no anidada bajo `/posts/<id>/comments/<comment_id>` — borrar depende de quién escribió el comentario, no de en qué publicación está (mismo razonamiento que `DELETE /api/messages/<id>`, `ADR-014`). Vive en el `comments_bp` existente.

### Sin cascada

`comments` no tiene tablas dependientes (`ADR-006` §No objetivos: sin hilos de respuestas), así que no hay `ON DELETE CASCADE` que ejercer. La publicación no se toca.

### Seguridad

- `author_id` sale exclusivamente de `get_jwt_identity()`; nunca del body ni de la URL.
- La pertenencia se verifica **en la misma sentencia** que confirma la existencia (`WHERE id = ... AND author_id = ...`) — sin ventana entre comprobar y actuar.
- El `404` indistinguible evita usar el endpoint para averiguar qué `comment_id` existen. El propio dueño de la publicación recibe `404` si intenta borrar un comentario ajeno (cubierto por prueba).

## Impacto en Frontend

- `CapsuleCard.jsx`: cada comentario propio dentro del panel gana una papelera, con el mismo `ConfirmDialog` que ya usan publicaciones y mensajes (no el cuadro nativo del navegador). Sin actualización optimista: el comentario sale del panel cuando el servidor confirma, igual que publicarlo; si falla, se queda y se avisa por Toast.
- `AppShell.jsx`: `handleDeleteComment` llama al endpoint y baja `comments_count` en `capsules`, espejo de `handlePostComment`.
- `Home.jsx`, `Profile.jsx`, `Search.jsx`: pasan la acción a `CapsuleCard`, igual que ya pasan `onPostComment`.

## Impacto en Backend

- `domain/comments/repositories.py`: `CommentRepository` gana `delete(comment_id, author_id)`.
- `domain/comments/exceptions.py` (nuevo): `CommentNotFoundError`.
- `application/comments/delete_comment_use_case.py` (nuevo).
- `infrastructure/persistence/repositories/comment_repository.py`: `SQLAlchemyCommentRepository` gana `delete(...)`.
- `interfaces/routes/comment_routes.py`: gana `DELETE /comments/<uuid:comment_id>`.
- Sin migración nueva. Tests de integración nuevos en `tests/test_comments.py`.

## Riesgos

- **Notificación huérfana de "comentó tu publicación":** `notifications` guarda `post_id` pero no el comentario que la originó (`ADR-008` §Modelo de datos), así que al borrar el comentario no hay forma de saber cuál de las notificaciones de ese autor sobre ese post retirar. La notificación permanece y apunta a una publicación que sigue existiendo, pero cuyo comentario ya no está. Es cosmético, no rompe nada. Solucionarlo exige una columna `comment_id` en `notifications` (migración + ADR propio); se deja señalado y no se resuelve por criterio propio acá.
- **Borrado irreversible:** mismo trade-off ya aceptado en `ADR-014`/`ADR-019`.
- **Sin límite de frecuencia:** coherente con el resto de endpoints (`API_CONTRACT.md` §9).

## Decisiones pendientes (cada una es su propio ADR futuro)

- Que el autor de una publicación pueda borrar comentarios ajenos en ella (moderación básica).
- Editar un comentario.
- Añadir `comment_id` a `notifications` para retirar la notificación al borrar el comentario.

## Consecuencias

- `DATABASE_ARCHITECTURE.md` no cambia.
- `API_CONTRACT.md` se actualiza el mismo día (`HB-001` §15.1) → v0.21.

## Referencias

- `docs/architecture/ADR-006-comments-minimal-model.md` — entidad `comments` que este ADR extiende.
- `docs/architecture/ADR-019-post-deletion.md` — precedente directo; su §Decisiones pendientes listaba este borrado.
- `docs/architecture/ADR-014-messages-ux-improvements.md` — origen del criterio (propio, *hard delete*, `404` indistinguible, ruta plana).
- `docs/architecture/ADR-008-notifications-minimal-model.md` — modelo de `notifications` (§Riesgos).
- `CLAUDE.md` — jerarquía de fuentes (§4), regla de alcance (§14).

---

## Cierre
