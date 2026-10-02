# ADR-023 — Menciones con @username

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/ADR-023-mentions.md` |
| Tipo | Architecture Decision Record (`HB-001` §11–12) |
| Fecha | 01/10/2026 |
| Estado | **Aceptada** — implementada en esta tarea (ver §Decisión) |
| Alcance | `backend/` — entidad `mentions`, `users.who_can_mention`, resolución al crear/editar publicaciones y comentarios, notificación `mention`; `Frontend/` — `MentionText.jsx`, selector en Configuración › Privacidad |
| Autoridad sobre este documento | `/docs` oficial > estructura real observada en el código > este documento (mismo orden que `CLAUDE.md` §4) |

> Resuelve la candidata "Menciones" de `DATABASE_ARCHITECTURE.md` §4.B › Notificaciones y el control "Menciones y etiquetas" de REF-SET-02, que decía `pending` con el motivo *"No existe el modelo de menciones ni etiquetas"*. Extiende `ADR-008-notifications-minimal-model.md` con un cuarto tipo de evento.

---

## Contexto

El control de la pantalla de Privacidad prometía decidir *"qué usuarios pueden etiquetarte en cápsulas compartidas"*, pero no había nada que decidir: escribir `@alguien` en una publicación era texto plano. Ni se resolvía a una cuenta, ni se notificaba, ni se podía enlazar.

Mencionar es, además, la única forma que tiene el producto de dirigir contenido a una persona concreta fuera del chat — y por eso mismo es un vector de spam y de acoso si no tiene un permiso detrás. Las dos cosas (la función y su control de privacidad) se implementan juntas en este ADR; separarlas dejaría la función abierta a todo el mundo durante el tiempo que tardara el segundo ADR.

## Objetivos

- Escribir `@username` menciona a esa persona de verdad: queda registrado, le llega una notificación y el Frontend puede enlazarlo.
- Cada persona decide quién puede mencionarla.
- Una mención no autorizada no rompe la publicación: se ignora y el texto queda como texto plano.
- Editar un texto mantiene sus menciones coherentes, sin volver a molestar a quien ya estaba mencionado.

## No objetivos (explícitamente fuera de este ADR)

- **No** implementa etiquetar en imágenes o medios: no existen medios (`ADR-004` §No objetivos). "Etiquetas" en el título del control se interpreta como la mención textual, que es lo único que el producto puede soportar hoy.
- **No** implementa autocompletado de `@` mientras se escribe. Requiere un endpoint de búsqueda de usuarios que no existe (`DATABASE_ARCHITECTURE.md` §4.B, sin candidata ratificada) y es una mejora de interfaz, no parte del modelo.
- **No** permite quitarse una mención ajena ("destaguearse"). Es una acción distinta, sobre contenido de otra persona, con su propio contrato.
- **No** lista "las publicaciones donde me mencionaron". El modelo lo soporta (`mentions.mentioned_user_id` está indexado por target, no por usuario), pero el endpoint es su propio ADR.
- **No** menciona a nadie desde un mensaje directo: un chat de dos personas no necesita dirigir la atención.
- **No** notifica una mención a quien no puede ver el contenido. Ver §Riesgos.

## Opciones consideradas — persistir la mención o derivarla del texto

| Opción | Descripción | Trade-off |
|---|---|---|
| **A — Tabla `mentions` (elegida)** | Se resuelve al escribir y se guarda una fila por mención | El permiso (`who_can_mention`) se evalúa **una vez, al escribir**. Así una mención ya aceptada sigue siendo válida si después la persona cierra sus menciones, y un `@username` que nunca tuvo permiso no se convierte en mención retroactivamente al cambiar la preferencia. Además permite enlazar sin volver a resolver nada en cada lectura |
| B — Derivar del texto en cada lectura | No hay tabla; se busca `/@\w+/` y se resuelve al renderizar | Sin migración, pero el permiso pasaría a evaluarse al **leer**, así que el significado de un texto ya publicado cambiaría retroactivamente cada vez que alguien ajusta su preferencia. Y cada lectura del feed necesitaría resolver N usernames contra `users` |

**Elegida: A.**

### Opciones consideradas — una tabla o dos

`mentions` tiene `post_id` y `comment_id`, ambas nullable, con `CHECK ((post_id IS NULL) <> (comment_id IS NULL))`. La alternativa era `post_mentions` + `comment_mentions`: dos tablas con las mismas cuatro columnas, dos repositorios casi idénticos y dos presenters. Es el mismo hecho ("alguien fue mencionado en algo") con dos targets posibles, así que va en una tabla con la `CHECK` garantizando que siempre haya exactamente uno. **Tercera `CHECK` del esquema**, después de `ck_follows_no_self_follow` (`ADR-007`) y `ck_messages_no_self_message` (`ADR-013`).

## Decisión

### `users.who_can_mention` — `VARCHAR(20) NOT NULL DEFAULT 'everyone'`

Tres valores, del vocabulario compartido `domain/privacy/audience.py`: `'everyone'`, `'followers'`, `'nobody'`. Un único vocabulario para esta preferencia y para `who_can_message` (`ADR-024`) porque significan lo mismo — duplicarlo invitaría a que se desincronizaran.

`'everyone'` es el default porque es el comportamiento que había de hecho: no existían las menciones, así que nadie tenía una preferencia que respetar.

**Dirección de `'followers'`:** significa "solo quienes **me** siguen". Al evaluar una mención hay que preguntar si *el autor del texto* sigue *al mencionado*, no al revés. Es el error fácil de cometer y está cubierto por prueba.

### Tabla `mentions`

| Columna | Tipo | Nota |
|---|---|---|
| `id` | UUID PK | `gen_random_uuid()`, como el resto |
| `mentioned_user_id` | UUID → `users.id` | A quién se menciona |
| `author_id` | UUID → `users.id` | Quién la escribió. Redundante con `posts.author_id`/`comments.author_id`, pero evita un JOIN en cada lectura y deja la fila auto-explicativa |
| `post_id` | UUID → `posts.id`, nullable | Exactamente una de las dos |
| `comment_id` | UUID → `comments.id`, nullable | — |
| `created_at` | TIMESTAMPTZ | — |

Todas las FKs `ON DELETE CASCADE`: borrar el post, el comentario o la cuenta se lleva sus menciones.

**Sin `updated_at` ni `edited_at`:** una mención no se edita. Si se edita el texto que la contenía, las menciones se **recalculan**.

**Índices.** Dos `UNIQUE` **parciales** (`uq_mentions_user_post` con `WHERE post_id IS NOT NULL`, y su equivalente para comentarios) en vez de una `UNIQUE` sobre las tres columnas: en PostgreSQL dos filas con `NULL` en una columna del índice no se consideran duplicadas, así que la versión no parcial no impediría nada. Más `ix_mentions_post_id`/`ix_mentions_comment_id` para resolver "¿a quién menciona esto?" al renderizar.

### Resolución: tres pasos, al escribir

`application/mentions/resolve_mentions.py` es el único lugar que decide a quién se menciona, y lo usan los cuatro caminos de escritura (crear/editar publicación, crear/editar comentario):

1. **Extraer** candidatos del texto (`domain/mentions/parser.py`, función pura).
2. **Filtrar** por existencia y permiso, en **una sola consulta** por paso (no una por `@username`).
3. **Sincronizar** (`replace_for_post`/`replace_for_comment`: borra las que ya no están, crea las nuevas) y **notificar solo a las nuevas**.

**El parser.** `(?<![A-Za-z0-9_@])@([A-Za-z0-9_]{3,20})\b`. El patrón de username coincide con `is_valid_username` (`ADR-002` §3) a propósito: si divergieran, se podrían mencionar usernames que el registro no permite crear. El *lookbehind* evita el falso positivo clásico — `ada@example.com` no menciona a nadie. La comparación es **insensible a mayúsculas** aunque `users.username` sea *case-sensitive* en el esquema: escribir `@Ada` tiene que mencionar a `ada`.

**Tope de 10 menciones** por publicación/comentario (`MAX_MENTIONS_PER_CONTENT`). Las de más se ignoran **en silencio**: nadie debería perder lo que escribió por haber etiquetado a demasiada gente. Es el vector de spam obvio de esta función.

**Una mención no autorizada no es un error.** Si el `@username` no existe, o su dueño no lo autoriza, la publicación se crea igual y ese texto queda como texto plano. No hay `400`.

**Mencionarse a sí mismo siempre se puede**, incluso con `who_can_mention = 'nobody'`: la preferencia protege de los demás, no de uno mismo. Pero no genera notificación — nadie se notifica a sí mismo (mismo criterio que `ADR-008` para like/comment sobre contenido propio).

### Contrato: `mentions` en `post` y en `comment`

```json
"mentions": [ { "id": "UUID", "username": "string", "name": "string" } ]
```
Extensión **aditiva** en `POST`/`GET`/`PATCH` de publicaciones y comentarios. Siempre `[]`, nunca `null`.

**Por qué el Frontend la necesita:** el texto guarda el `@username` tal como se escribió, pero para enlazarlo hace falta el `id`. Sin esta lista, el Frontend tendría que adivinar qué `@algo` corresponde a una cuenta real — y se equivocaría justo en los casos que este ADR filtra. Un `@username` inexistente o no autorizado **no** debe parecer un enlace.

### Notificación `'mention'`

Cuarto tipo, junto a `like`/`comment`/`follow` (`ADR-008`). Lleva `post_id`; una mención en un comentario notifica apuntando al post que lo contiene, porque `notifications` no guarda `comment_id` (limitación que `ADR-020` §Riesgos ya había registrado) — y es además adónde hay que navegar para verla.

Al **editar**, solo se notifica a quien no estaba mencionado antes. Corregir un tipeo en un texto que ya mencionaba a alguien no vuelve a molestarlo.

### Seguridad

- `author_id` sale exclusivamente de `get_jwt_identity()`.
- La lista de menciones **no se acepta del body**: se deriva del texto. No hay forma de mencionar a alguien que no aparece escrito, ni de evitar la comprobación de permiso pasando ids a mano.
- `who_can_mention` solo se cambia desde `PATCH /api/users/me/privacy`, con su propia whitelist.

## Impacto en Frontend

- **`MentionText.jsx`** (nuevo): renderiza el texto enlazando **solo** las menciones que el servidor autorizó. Usa un único patrón con los usernames autorizados, ordenados de más largo a más corto — si existen `ana` y `ana_b`, buscar `ana` primero partiría `@ana_b`.
- **`CapsuleCard.jsx`**: cuerpo de la publicación y de cada comentario pasan por `MentionText`.
- **`Configuración › Privacidad`**: "Menciones y etiquetas" pasa de `pending` a un selector real de tres opciones.
- **`mapNotification.js`**: `mention` entra en el catálogo y en los "importantes".

## Impacto en Backend

- `migrations/versions/d5f9c3e1b764_create_mentions_table.py` (nueva).
- `domain/mentions/parser.py`, `domain/mentions/repositories.py`, `domain/privacy/audience.py` (nuevos).
- `infrastructure/persistence/models.py`: modelo `Mention`, columna `users.who_can_mention`.
- `infrastructure/persistence/repositories/mention_repository.py` (nuevo).
- `domain/auth/repositories.py` + adaptador: `find_by_usernames` (resolución en una consulta, insensible a mayúsculas).
- `application/mentions/resolve_mentions.py`, `mention_presenter.py` (nuevos).
- Los cuatro casos de uso de escritura de publicaciones/comentarios resuelven menciones; los dos de lectura las traen en lote.
- Tests de integración en `tests/test_privacy.py` (clase `TestMentions`).

## Riesgos

- **Una mención puede notificar contenido que el destinatario no puede ver.** Si una cuenta privada (`ADR-022`) menciona a alguien que no la sigue, la notificación llega pero el post no se abre. Las alternativas eran peores: no notificar (y que la mención fuera inútil) o conceder acceso implícito (y convertir la mención en una forma de saltarse la privacidad). Se deja como está y se señala.
- **Coincidencia por `username`, que puede cambiar.** `PATCH /api/users/me` permite cambiar el username (`ADR-003`, con cooldown). El texto guarda el `@username` viejo, así que tras un cambio el enlace sigue funcionando (la fila apunta al `id`) pero el texto visible queda desactualizado. Reescribir textos ajenos es peor que esto.
- **Coincidencia por subcadena en el patrón, no por identidad exacta.** Mitigado ordenando por longitud en el Frontend y con `\b` en el parser, pero no se puede descartar un caso raro con usernames muy solapados.
- **Sin *rate limiting*.** Diez menciones por publicación, pero nada limita cuántas publicaciones por minuto. Coherente con el resto del proyecto (`API_CONTRACT.md` §9).

## Decisiones pendientes (cada una es su propio ADR futuro)

- Autocompletado de `@` (necesita endpoint de búsqueda de usuarios).
- Quitarse una mención ajena ("destaguearse").
- Listar las publicaciones donde me mencionaron.
- Añadir `comment_id` a `notifications` para que una mención en un comentario apunte al comentario — heredada de `ADR-020`.
- Menciones en mensajes directos.

## Consecuencias

- **`DATABASE_ARCHITECTURE.md` cambia** (tabla `mentions`, `users.who_can_mention`) → v0.19.
- `API_CONTRACT.md` se actualiza el mismo día (`HB-001` §15.1) → v0.23. `mentions` es aditivo en cuatro endpoints; `'mention'` se suma al enum de `notification.type`.
- `ADR-008` queda extendido con un cuarto tipo de notificación.

## Referencias

- `docs/architecture/ADR-008-notifications-minimal-model.md` — entidad `notifications` que este ADR extiende.
- `docs/architecture/ADR-002-user-profile-fields.md` §3 — reglas de `username` que el parser replica.
- `docs/architecture/ADR-021-content-editing.md` — la edición que obliga a recalcular menciones.
- `docs/architecture/ADR-022-private-accounts.md` — de donde sale el vocabulario de audiencias y el caso de §Riesgos.
- `docs/architecture/ADR-024-content-filters-and-privacy-preferences.md` — el tercer ADR de la misma pantalla.
- `CLAUDE.md` — jerarquía de fuentes (§4), regla de alcance (§14).

---

## Cierre

Undécima entidad del alcance objetivo en pasar a ratificada, y la primera que nace con su control de privacidad incluido en el mismo ADR en vez de dejarlo para después.
