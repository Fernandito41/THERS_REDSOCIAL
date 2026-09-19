# ADR-013 — Modelo mínimo de `messages` (mensajes directos)

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/ADR-013-messages-minimal-model.md` |
| Tipo | Architecture Decision Record (`HB-001` §11–12) |
| Fecha | 19/09/2026 |
| Estado | **Aceptada** — implementada en esta tarea (ver §Decisión) |
| Alcance | `backend/` — nueva entidad `messages`, `POST`/`GET /api/users/<user_id>/messages`, `GET /api/conversations` |
| Autoridad sobre este documento | `/docs` oficial > estructura real observada en el código > este documento (mismo orden que `CLAUDE.md` §4) |

> ⚠️ **Regla de alcance, explícita — mismo criterio que `ADR-004`/`ADR-005`/`ADR-006`/`ADR-007`/`ADR-008`.** `DATABASE_ARCHITECTURE.md` §4.B registra "Conversaciones (privadas y grupales), Participantes" como `conversations` + puente `conversation_participants` (pensado para cubrir 1:1 y grupo con la misma estructura) y "Mensajes" como entidad `messages`, ambas `OBJETIVO` con el modelado sin decidir. Este ADR implementa **solo** la mitad 1:1 de esa candidata — un mensaje directo entre dos usuarios reales — sin la tabla puente `conversation_participants` ni ningún soporte de conversación grupal. Ver §Opciones consideradas para por qué se difiere esa parte en vez de construirla ya "por las dudas".

---

## Contexto

Con `posts`, `likes`, `comments`, `follows` y `notifications` ya ratificados, el equipo probó THERS en una LAN entre amigos y la necesidad más pedida fue poder chatear directamente entre cuentas reales — hoy `Messages.jsx` (Frontend) no tiene ninguna fuente de datos real, y `Sidebar`/`Topbar` ya traen un badge `unreadMessages` que nunca recibe un número real (`ShellFrame.jsx` lo recibe como prop pero ningún llamador lo resuelve contra el backend).

## Problema

Definir el modelo **mínimo** que permite que dos usuarios autenticados se manden mensajes de texto directos entre sí y vean su historial — sin conversaciones grupales, sin archivos/fotos, sin tiempo real (WebSockets), sin borrar mensajes.

## Objetivos

- Un usuario autenticado puede mandarle un mensaje de texto a otro usuario real.
- Un usuario autenticado puede ver el historial de mensajes con otro usuario (ambos sentidos), en orden cronológico.
- Un usuario autenticado puede listar sus conversaciones (con quién habló, el último mensaje, y cuántos mensajes sin leer tiene de esa persona) — es lo que necesita `Messages.jsx` para dejar de estar vacío y lo que necesita el badge de no-leídos de `Sidebar`/`Topbar` para mostrar un número real.
- Un usuario no puede mandarse un mensaje a sí mismo.
- Abrir un hilo con otra persona marca como leídos los mensajes que esa persona te mandó (mismo criterio de "abrir = leer" que cualquier chat).

## No objetivos (explícitamente fuera de este ADR)

- **No** implementa conversaciones grupales ni la tabla puente `conversation_participants` que `DATABASE_ARCHITECTURE.md` §4.B anticipa para unificar 1:1 y grupo — ver §Opciones consideradas. Si el equipo confirma que quiere grupos, es su propio ADR (probablemente una migración real de `messages` hacia el modelo con participantes, no aditiva).
- **No** implementa fotos/archivos adjuntos en mensajes (`message_media`, `DATABASE_ARCHITECTURE.md` §4.B, `PENDIENTE DE DECISIÓN` — reutilización vs. entidad propia, sin resolver).
- **No** implementa tiempo real — el Frontend refresca por *polling* (pedir de nuevo cada pocos segundos), mismo criterio que `ADR-008` eligió para notificaciones. Introducir WebSockets/Flask-SocketIO es un cambio de infraestructura mayor que el alcance de este ADR.
- **No** implementa borrado de mensajes ni de conversaciones.
- **No** implementa "escribiendo..." ni confirmación de entrega/lectura estilo "visto" — solo un booleano agregado de no-leídos por conversación, no por mensaje individual expuesto al remitente.
- **No** cambia el contrato de ningún endpoint existente.

## Opciones consideradas — forma del modelo (1:1 directo vs. conversaciones+participantes)

| Opción | Descripción | Trade-off |
|---|---|---|
| **A — `messages` con `sender_id`/`recipient_id` directos (elegida)** | Una sola tabla, sin entidad `conversations` ni tabla puente. Una "conversación" es una vista derivada: todos los mensajes entre A y B, no una fila propia. | Coincide con el patrón ya establecido (`follows` tampoco modela "amistad" como concepto propio, solo la relación cruda) y con el volumen real de esta tarea (chatear entre amigos, no organizar chats grupales). Migrar a grupos después requeriría una tabla puente nueva y decidir qué pasa con los mensajes 1:1 ya existentes — costo real, pero pagado solo si el producto de verdad lo necesita. |
| B — `conversations` + `conversation_participants` + `messages`, como anticipa `DATABASE_ARCHITECTURE.md` §4.B | Construir ya la forma general que soporta 1:1 y grupo con la misma estructura | Más trabajo hoy (tres tablas en vez de una, resolver/crear la conversación antes de cada mensaje) para una función (grupos) que nadie pidió todavía — mismo argumento que `ADR-007` usó para no personalizar el feed "por si acaso" |

**Elegida: A.** Mismo criterio que las cinco entidades anteriores: la forma general candidata en `DATABASE_ARCHITECTURE.md` §4.B se implementa en su versión mínima verificable primero; la generalización a grupos queda como decisión de producto explícita, no un efecto colateral de este ADR.

## Opciones consideradas — cuándo se marca un mensaje como leído

| Opción | Descripción | Trade-off |
|---|---|---|
| **A — `GET` del hilo marca como leído (elegida)** | `GET /api/users/<id>/messages` marca automáticamente como leídos todos los mensajes que `<id>` le mandó al usuario autenticado, como efecto secundario de listarlos. | Un solo endpoint cubre "ver" y "leer" — mismo momento en cualquier chat real (abrís la conversación, ya la leíste). No necesita que el Frontend llame a un segundo endpoint después de renderizar. |
| B — `PATCH` explícito por mensaje, mismo patrón que `ADR-008` (`PATCH /api/notifications/<id>/read`) | El Frontend marca cada mensaje como leído individualmente | Más fiel al patrón ya usado para notificaciones, pero ahí cada notificación es un evento discreto que puede ignorarse; un hilo de chat siempre se lee completo al abrirlo, así que un `PATCH` por mensaje sería una llamada extra sin beneficio real. |

**Elegida: A.**

## Decisión

Se crea una única entidad, `messages`, siguiendo el mismo patrón de capas ya usado para `posts`/`likes`/`comments`/`follows`/`notifications`.

### Modelo de datos

| Columna | Tipo | Nulo | Justificación |
|---|---|---|---|
| `id` | `UUID`, `DEFAULT gen_random_uuid()` | No (PK) | Mismo patrón que el resto de entidades |
| `sender_id` | `UUID`, FK → `users.id` | No | Quién manda — siempre `get_jwt_identity()`, nunca un valor del body |
| `recipient_id` | `UUID`, FK → `users.id` | No | Quién recibe — viene de la URL (`user_id`), nunca del body |
| `content` | `TEXT` | No | Sin límite de longitud a nivel de esquema — validación de negocio (`MAX_CONTENT_LENGTH`) en `domain/messages/validators.py`, mismo criterio que `posts`/`comments` |
| `read_at` | `TIMESTAMPTZ` | **Sí** | `NULL` = no leído. Mismo criterio que `notifications.read_at` (`ADR-008`): nunca cruza la frontera HTTP como timestamp crudo |
| `created_at` | `TIMESTAMPTZ`, `DEFAULT now()` | No | Define el orden del hilo |

**Sin `updated_at`.** Un mensaje no se edita in place más allá de marcarse como leído (`read_at`) — mismo criterio que `Like`/`Follow`/`Notification`.

**Claves foráneas.** `sender_id → users.id` y `recipient_id → users.id`, ambas `ON DELETE CASCADE` — mismo placeholder ya aceptado en el resto de entidades (borrado de cuenta no existe todavía).

**Restricciones de negocio:**
- `CHECK (sender_id <> recipient_id)` (`ck_messages_no_self_message`) — un usuario no puede mandarse un mensaje a sí mismo, mismo criterio que `ck_follows_no_self_follow` (`ADR-007`).
- **Sin `UNIQUE`.** A diferencia de `likes`/`follows`, dos mensajes entre las mismas dos personas son eventos legítimos e independientes, no un duplicado a impedir — mismo criterio que `notifications` (`ADR-008` §Modelo de datos).

**Índices.** El hilo entre A y B se busca con `(sender_id = A AND recipient_id = B) OR (sender_id = B AND recipient_id = A)`, ordenado por `created_at` — ninguna `UNIQUE` cubre ese acceso, así que hacen falta dos índices compuestos explícitos para que PostgreSQL resuelva el `OR` sin escanear la tabla completa (`BitmapOr` sobre ambos):
- `ix_messages_sender_recipient_created` (`sender_id`, `recipient_id`, `created_at`)
- `ix_messages_recipient_sender_created` (`recipient_id`, `sender_id`, `created_at`)

### Contrato API (documentado el mismo día en `API_CONTRACT.md`, `HB-001` §15.1)

**`POST /api/users/<user_id>/messages`** — manda un mensaje a `user_id`. Auth requerida.
```json
// Request
{ "content": "Hola!" }
```
```json
// Response 201
{
  "message": {
    "id": "uuid",
    "sender_id": "uuid",
    "recipient_id": "uuid",
    "content": "Hola!",
    "created_at": "2026-09-19T10:00:00+00:00"
  }
}
```
- `400` si `content` está vacío, excede el límite, o `user_id` es el propio usuario autenticado.
- `404` si `user_id` no corresponde a ningún usuario real — incluye cualquier segmento de URL que no sea un UUID válido (conversor `uuid` de Flask, mismo criterio que `follow_routes.py`).
- `401` estándar.

**`GET /api/users/<user_id>/messages`** — historial de mensajes con `user_id`, orden cronológico ascendente (mensaje más viejo primero, como cualquier chat). Auth requerida. Límite fijo de 50 más recientes (sin paginación real, mismo criterio que el resto del backend). Efecto secundario: marca como leídos los mensajes que `user_id` le mandó al usuario autenticado (§Opciones consideradas).
```json
// Response 200
{ "messages": [ /* mismo objeto que arriba, con "read" agregado */ ] }
```
- `404` si `user_id` no existe.
- `401` estándar.

**`GET /api/conversations`** — lista las conversaciones del usuario autenticado, más reciente primero.
```json
// Response 200
{
  "conversations": [
    {
      "user": { "id": "uuid", "username": "sofia_r", "name": "Sofía Reyes" },
      "last_message": { "content": "Hola!", "sender_id": "uuid", "created_at": "..." },
      "unread_count": 2
    }
  ]
}
```
- `401` estándar.

### Seguridad

- `sender_id` nunca se acepta del body — siempre `get_jwt_identity()`. `recipient_id` siempre viene de la URL.
- `GET /api/users/<user_id>/messages` y `GET /api/conversations` filtran siempre por el usuario del JWT en ambos lados de la relación (`sender_id`/`recipient_id`) — un usuario no puede leer el hilo de otras dos personas cambiando ningún parámetro.

## Impacto en Frontend

- `Messages.jsx` deja de estar vacío/mock: lista `GET /api/conversations` y, al abrir una, `GET /api/users/<id>/messages` con *polling* simple (mismo criterio que `ADR-008` para notificaciones).
- `AppShell.jsx`/`ShellFrame.jsx`: `unreadMessages` pasa a calcularse sumando `unread_count` de `GET /api/conversations`, en vez de quedar en `0` fijo.
- Nuevo `features/feed/lib/mapMessage.js` (si hace falta adaptar la forma cruda de la API a lo que la UI ya espera), mismo patrón que `mapNotification.js` (`ADR-008`).

## Impacto en Backend

- Nueva migración aditiva (`messages`, dos FKs, un `CHECK`, dos índices compuestos).
- `domain/messages/` (nuevo): puerto `MessageRepository`, `exceptions.py` (`CannotMessageSelfError`), `validators.py` (`MAX_CONTENT_LENGTH`, `is_valid_content`).
- `application/messages/`: `send_message_use_case.py`, `list_thread_use_case.py`, `list_conversations_use_case.py`, `message_presenter.py`.
- `infrastructure/persistence/repositories/message_repository.py`: `SQLAlchemyMessageRepository`.
- `interfaces/routes/message_routes.py` (nuevo blueprint `messages_bp`).
- `tests/conftest.py`: `messages` se agrega a la lista de tablas truncadas entre pruebas.
- Tests de integración nuevos (`tests/test_messages.py`), mismo patrón que `test_follows.py`/`test_notifications.py`.

## Riesgos

- **Sin paginación real ni límite de longitud generoso:** mismo criterio transversal que el resto del backend (`DATABASE_ARCHITECTURE.md` §14) — aceptable al volumen actual.
- **`GET /api/conversations` es la consulta más cara de esta entidad** (agrupar por "la otra persona", último mensaje y conteo de no leídos por grupo) — aceptable al volumen de una prueba entre amigos; revisar si el número de conversaciones por usuario crece mucho.
- **Polling, no push:** mismo riesgo ya aceptado por `ADR-008` para notificaciones — introducir tiempo real real es un cambio de infraestructura mayor, fuera de este ADR.

## Decisiones pendientes (quedan fuera, cada una es su propio ADR futuro)

- Conversaciones grupales (`conversation_participants`).
- Fotos/archivos adjuntos en mensajes.
- Actualización en tiempo real (WebSockets/Flask-SocketIO) en vez de polling.
- Borrado de mensajes/conversaciones.
- Confirmación de lectura visible para el remitente ("visto").

## Consecuencias

- `messages` es la décima entidad del alcance objetivo del producto (`DATABASE_ARCHITECTURE.md` §4.B) en pasar de OBJETIVO a ratificada (parcialmente — solo la mitad 1:1 de la candidata).
- `DATABASE_ARCHITECTURE.md`, `DATABASE_ERD.md` y `API_CONTRACT.md` se actualizan el mismo día que este contrato se implementa (`HB-001` §15.1).

## Referencias

- `CLAUDE.md` — jerarquía de fuentes (§4), regla de alcance (§14), reglas específicas para Claude Code (§8).
- `docs/architecture/ADR-007-follows-minimal-model.md`, `ADR-008-notifications-minimal-model.md` — mismo proceso, mismo criterio de extender por entidades simples y de diferir generalización sin evidencia de que haga falta.
- `docs/architecture/DATABASE_ARCHITECTURE.md` §4.B › Mensajería (candidata `conversations`/`messages`), §8 (índices, sin especulación).
- `docs/architecture/organization/01_Manual_Organizacion/Source/HB-001-manual-organizacion.md.md` §11 (clasificación de impacto de decisiones), §15.1 (documentar endpoints el mismo día del PR).

---

## Cierre
