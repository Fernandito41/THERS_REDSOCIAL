# ADR-014 — Mejoras de UX sobre `messages`: borrado, corte de no-leídos, "escribiendo..."

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/ADR-014-messages-ux-improvements.md` |
| Tipo | Architecture Decision Record (`HB-001` §11–12) |
| Fecha | 19/09/2026 |
| Estado | **Aceptada** — implementada en esta tarea (ver §Decisión) |
| Alcance | `backend/` — `DELETE /api/messages/<message_id>`, `POST`/`GET /api/users/<user_id>/typing`; extensión de `GET /api/users/<user_id>/messages` |
| Autoridad sobre este documento | `/docs` oficial > estructura real observada en el código > este documento (mismo orden que `CLAUDE.md` §4) |

> Extiende `ADR-013-messages-minimal-model.md` a partir de feedback real del equipo probando el chat entre amigos — no introduce ninguna entidad nueva más allá de lo que ya explica cada sección de abajo.

---

## Contexto

Con `messages` ya en uso real entre el equipo (`ADR-013`), la prueba entre amigos dejó tres pedidos concretos: (1) que el chat se abra mostrando el mensaje más reciente, no el más viejo; (2) poder borrar un mensaje propio; (3) ver un indicador de "escribiendo..." cuando la otra persona está tipeando. El primero es un cambio exclusivo de Frontend (scroll automático, sin contrato nuevo) y no forma parte de este ADR. Los otros dos sí tocan el backend y se documentan acá.

## Objetivos

- Un usuario puede borrar un mensaje propio; deja de existir para ambas partes.
- `GET /api/users/<user_id>/messages` permite al Frontend dibujar un separador "Mensajes no leídos" en la posición correcta del hilo, sin que el propio efecto secundario de "abrir marca como leído" (`ADR-013`) borre esa información antes de que el Frontend la vea.
- Un usuario puede saber si la otra persona de un hilo está escribiéndole en este momento.

## No objetivos (explícitamente fuera de este ADR)

- **No** implementa "borrado solo para mí" (ocultar un mensaje ajeno sin borrarlo de verdad) — borrar es siempre borrar para los dos lados, y solo el remitente puede hacerlo.
- **No** deja un placeholder tipo "Este mensaje fue eliminado" — se borra la fila, sin rastro. Si el equipo pide después ese comportamiento, es una decisión de producto nueva, no un efecto colateral de este ADR.
- **No** implementa "escribiendo..." con WebSockets/Server-Sent Events — sigue siendo *polling*, igual que el resto del chat (`ADR-013` §No objetivos). Es, a propósito, una aproximación: se actualiza cada 2 segundos mientras el hilo está abierto, no al instante.
- **No** persiste el estado de "escribiendo" en PostgreSQL — vive en memoria del proceso del backend (ver §Opciones consideradas). Se pierde si el backend se reinicia, y no se comparte entre múltiples procesos/workers si el día de mañana el backend corre en más de uno — aceptable para un servidor de desarrollo único; revisar si el backend pasa a correr con varios workers (`gunicorn -w N`, `N > 1`).

## Opciones consideradas — dónde vive el estado de "escribiendo"

| Opción | Descripción | Trade-off |
|---|---|---|
| **A — En memoria del proceso, sin tabla (elegida)** | Un diccionario en el proceso de Flask, `(sender_id, recipient_id) → timestamp del último ping`, con una expiración de 3 segundos calculada al leer (sin limpieza periódica) | "Escribiendo" es información que deja de ser cierta a los pocos segundos — persistirla en PostgreSQL sería escribir y consultar la base por un dato que nunca hace falta recuperar después de que pasó. Coherente con no meter infraestructura nueva (Redis, WebSockets) para una función que hoy corre en un solo proceso |
| B — Tabla `typing_indicators` en PostgreSQL | Misma información, respaldada por una fila por par de usuarios | Escribiría a la base en cada tecla (mitigable con debounce del lado del Frontend, pero sigue siendo tráfico de escritura para un dato efímero) — sobre-ingeniería para lo que hace falta hoy |
| C — Redis / almacenamiento en memoria compartido | Serviría si el backend corriera en varios procesos/workers | Es exactamente el tipo de "servicio que hay que contratar" que se preguntó si hacía falta — no hace falta todavía porque el backend corre en un solo proceso de desarrollo. Si el día de mañana se despliega con varios workers, esta es la opción a la que migrar (§Riesgos) |

**Elegida: A.** Es la más simple que resuelve el problema real de hoy, sin agregar una dependencia nueva al proyecto.

## Decisión

### `DELETE /api/messages/<message_id>`

Borra un mensaje propio (hard delete, sin placeholder). Auth requerida. Solo el remitente puede borrar su propio mensaje — mismo criterio que `PATCH /api/notifications/<id>/read` (`ADR-008`): si el mensaje no existe **o** existe pero no es del usuario autenticado, responde el mismo `404`, sin distinguir cuál de los dos pasó.

```json
// Response 200
{ "deleted": true }
```
- `404` si `message_id` no existe, o existe pero no le pertenece a quien hace la petición.
- `401` estándar.

No anida bajo `/users/<id>/messages` porque borrar no depende de con quién es la conversación, solo de quién mandó el mensaje — mismo criterio que `GET /api/notifications` no anida bajo ningún recurso padre.

### Corte de "mensajes no leídos" en `GET /api/users/<user_id>/messages`

**Sin cambio de forma en la respuesta** — el campo `read` de cada mensaje (ya existente, `ADR-013` §Contrato API) ahora refleja el estado **antes** de que esta misma llamada los marque como leídos, no después. Antes de este ADR, por cómo SQLAlchemy expira los objetos tras un `commit()`, el propio `read` que la respuesta devolvía ya aparecía en `true` para los mensajes que la llamada acababa de marcar — inutilizando esa información para dibujar cualquier separador. Ahora `list_thread_use_case.py` arma la respuesta pública **antes** de llamar a `mark_thread_as_read`, así que el Frontend puede calcular "el primer mensaje con `read: false` y `sender_id` distinto del propio" para ubicar el separador, en la misma respuesta que ya recibía.

**Es una corrección de contrato, no un endpoint nuevo** — documentado acá porque cambia lo que `read` significa en la práctica (el momento exacto en que se evalúa), aunque el campo ya existía.

### `POST`/`GET /api/users/<user_id>/typing`

**`POST /api/users/<user_id>/typing`** — avisa que el usuario autenticado le está escribiendo a `user_id` en este momento. Auth requerida. Sin body.
```json
// Response 204 (sin contenido)
```
- `404` si `user_id` no corresponde a ningún usuario real.
- `401` estándar.

**`GET /api/users/<user_id>/typing`** — indica si `user_id` le está escribiendo al usuario autenticado en este momento. Auth requerida.
```json
// Response 200
{ "typing": true }
```
`typing` es `false` si nunca hubo un `POST` de esa persona, o si el último fue hace más de 3 segundos (`TYPING_INDICATOR_TTL_SECONDS`) — el Frontend hace *polling* de este endpoint cada 2 segundos mientras el hilo está abierto, más rápido que el *polling* general del chat (4s, `ADR-013`) porque "escribiendo" necesita sentirse más inmediato para no parecer roto.

### Seguridad

- `sender_id`/`recipient_id` de un `POST .../typing` nunca se aceptan del body — `sender_id` sale de `get_jwt_identity()`, `recipient_id` de la URL, mismo criterio que el resto del chat.
- Borrar un mensaje verifica pertenencia (`sender_id == get_jwt_identity()`) en la misma operación que confirma existencia — mismo principio que `PATCH /api/notifications/<id>/read`.

## Impacto en Frontend

- `Messages.jsx`: hace scroll automático al mensaje más reciente al abrir un hilo y al recibir uno nuevo (cambio exclusivo de Frontend, sin contrato nuevo).
- `Messages.jsx`: calcula el separador "Mensajes no leídos" una sola vez por hilo abierto (con la respuesta del primer `GET`, antes de que el *polling* posterior lo marque todo como leído) — no se recalcula en cada *poll* siguiente, para que no desaparezca mientras la persona sigue mirando la pantalla.
- `Messages.jsx`: cada mensaje propio gana una acción "Eliminar" (`DELETE /api/messages/<id>`), con confirmación antes de mandarla — un borrado no se puede deshacer.
- `Messages.jsx`: manda un `POST .../typing` con *debounce* mientras el usuario escribe en el campo de mensaje (a lo sumo uno cada 2 segundos, no en cada tecla), y hace *polling* de `GET .../typing` sobre el hilo abierto cada 2 segundos para mostrar "Escribiendo..." bajo el nombre de la persona.

## Impacto en Backend

- `domain/messages/repositories.py`: `MessageRepository` gana `delete(message_id, sender_id)`. Nuevo puerto `TypingRepository` (mismo archivo o uno propio): `ping(sender_id, recipient_id)`, `is_typing(sender_id, recipient_id)`.
- `domain/messages/exceptions.py`: gana `MessageNotFoundError`.
- `application/messages/`: `delete_message_use_case.py`, `send_typing_ping_use_case.py`, `get_typing_status_use_case.py`. `list_thread_use_case.py` se reordena (§Decisión) sin cambiar su firma.
- `infrastructure/persistence/repositories/message_repository.py`: `SQLAlchemyMessageRepository` gana `delete(...)`.
- `infrastructure/realtime/typing_indicator_repository.py` (nuevo, fuera de `persistence/` a propósito — no toca PostgreSQL): `InMemoryTypingIndicatorRepository`, diccionario de proceso con expiración por tiempo (§Opciones consideradas).
- `interfaces/routes/message_routes.py`: gana `DELETE /messages/<message_id>`, `POST`/`GET /users/<user_id>/typing`.
- Sin migración nueva — ninguna de las tres decisiones cambia el esquema de PostgreSQL.
- Tests de integración nuevos en `tests/test_messages.py`, mismo patrón que el resto del archivo.

## Riesgos

- **El indicador de "escribiendo" no sobrevive un reinicio del backend ni se comparte entre varios procesos** (§Opciones consideradas, Riesgo ya aceptado) — si el backend pasa a desplegarse con más de un worker, esta implementación deja de ser correcta (un ping a un worker no lo vería otro) y hay que migrar a un almacenamiento compartido (Redis u otro) — no es una decisión de esta tarea, queda señalado para cuando ese momento llegue.
- **Borrado sin placeholder:** si más adelante el equipo quiere que el destinatario vea "mensaje eliminado" en vez de que el mensaje desaparezca sin aviso, es un cambio de esquema (columna `deleted_at` en vez de `DELETE` real) — decisión de producto separada, no resuelta acá.
- **Polling cada 2 segundos para "escribiendo" además del polling de 4 segundos del hilo:** duplica el tráfico de peticiones mientras un chat está abierto — aceptable al volumen de esta prueba; si el número de chats simultáneos crece mucho, es candidato a resolverse con un mecanismo real de tiempo real (`ADR-013` §Riesgos ya señalaba lo mismo para los mensajes).

## Decisiones pendientes (quedan fuera, cada una es su propio ADR futuro)

- Borrado con placeholder ("mensaje eliminado") en vez de borrado silencioso.
- Borrado "solo para mí" (ocultar sin borrar).
- Reemplazar polling por WebSockets/Flask-SocketIO para mensajes y "escribiendo" (`ADR-013` ya lo dejaba pendiente).
- Migrar el estado de "escribiendo" a un almacenamiento compartido si el backend pasa a correr en más de un proceso.

## Consecuencias

- No se agrega ninguna entidad nueva a `DATABASE_ARCHITECTURE.md` — `messages` no cambia de esquema; el indicador de "escribiendo" es, a propósito, efímero y no persistido, así que no entra al modelo de datos.
- `API_CONTRACT.md` se actualiza el mismo día que este contrato se implementa (`HB-001` §15.1).

## Referencias

- `docs/architecture/ADR-013-messages-minimal-model.md` — entidad y contrato base que este ADR extiende.
- `CLAUDE.md` — jerarquía de fuentes (§4), regla de alcance (§14), reglas específicas para Claude Code (§8).

---

## Cierre
