# ADR-028 — Exportación de datos personales

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/ADR-028-data-export.md` |
| Tipo | Architecture Decision Record (`HB-001` §11–12) |
| Fecha | 01/10/2026 |
| Estado | **Aceptada** — implementada en esta tarea, a pedido del propietario del proyecto. Pendiente de la revisión humana que exige `HB-001` §19 |
| Alcance | `backend/` — entidad `data_exports`, `POST`/`GET /api/data-exports`, `GET /api/data-exports/<id>/download`; `Frontend/` — `DataExportRow.jsx` y la sección «Descarga de datos y archivo» de Configuración (REF-SET-09) |
| Autoridad sobre este documento | `/docs` oficial > estructura real observada en el código > este documento (mismo orden que `CLAUDE.md` §4) |

---

## Contexto

La sección «Descarga de datos y archivo» (REF-SET-09, `Frontend/src/features/feed/data/settingsSections.js`) tenía sus tres grupos marcados como `pending`:

| Control | Motivo que daba la pantalla |
|---|---|
| Solicitar mi archivo | «No existe el trabajo de exportación en el servidor» |
| Historial de solicitudes | «Sin exportaciones que registrar» |
| Protección del archivo | «No hay endpoint que lo aplique» |

Los tres motivos eran exactos. Este ADR crea lo que faltaba.

## Objetivos

- Que una persona pueda obtener un archivo real con los datos que THERS guarda sobre ella.
- Que quede un historial de lo pedido y de lo descargado.
- Que el archivo no sea accesible para nadie más que su dueño, y que caduque.

## No objetivos

- **No** cifra el ZIP ni lo protege con contraseña. `zipfile` de la biblioteca estándar no escribe ZIP cifrados, y el cifrado débil de ZipCrypto daría una sensación de protección que no existe. La pantalla lo dice tal cual («Sin cifrar»).
- **No** envía el archivo por correo ni un enlace por correo. El archivo se descarga con la sesión iniciada.
- **No** exporta el contenido de otras personas (sus publicaciones, sus comentarios en publicaciones ajenas).
- **No** purga las filas caducadas: se conservan como historial; solo se descarta el contenido.

## Opciones consideradas

| Opción | Trade-off |
|---|---|
| **A — Generación síncrona al pedirlo, ZIP guardado en la base (elegida)** | Sin infraestructura nueva. El volumen de datos de una cuenta es chico; la petición tarda lo que tarda recorrer sus tablas |
| B — Cola de trabajos (Celery/RQ) + notificación por correo | Es lo correcto a escala, pero exige Redis/worker, que no están en el stack ni en ningún documento de DevOps |
| C — Archivo en disco o almacenamiento de objetos | El proyecto no tiene almacenamiento de archivos; un volumen local se pierde o desincroniza con varios *workers* (mismo razonamiento que `rate_limit_buckets`, `ADR-027`) |
| D — Devolver el JSON directamente, sin guardar nada | No habría historial ni caducidad, que son justo lo que pide la pantalla |

## Decisión

### Tabla `data_exports`

| Columna | Tipo | Nota |
|---|---|---|
| `id` | UUID PK | — |
| `user_id` | UUID → `users.id`, CASCADE | Al borrarse la cuenta se borran sus archivos |
| `file_name` | VARCHAR(120) | `thers-datos-<username>-<AAAAMMDD>.zip` |
| `size_bytes` | INTEGER | — |
| `content` | BYTEA, NULL | El ZIP. **NULL = caducó y se descartó** |
| `created_at` / `expires_at` | TIMESTAMPTZ | `expires_at = created_at + 7 días` |
| `downloaded_at` / `download_count` | TIMESTAMPTZ NULL / INTEGER | Última descarga y cuántas |

Migración `c4d8e2a6f913`, escrita a mano como las anteriores.

### Reglas (`domain/data_exports/policy.py`)

- **Caducidad: 7 días.** Al listar el historial, el contenido vencido se pone en `NULL`; la fila queda como «caducado».
- **Cooldown: 1 solicitud por hora y por cuenta** (`429` con `Retry-After` y `retry_after_seconds`, mismo formato que `ADR-027`). Generar el archivo recorre todas las tablas del usuario: sin tope, pedirlo en bucle es una forma barata de cargar la base. Se calcula con la fecha de la última solicitud, no con `rate_limit_buckets`, porque lo que se limita es cuántos archivos existen, no cuántos intentos hubo.
- **Dueño exclusivo:** `user_id` sale solo del JWT. Pedir el archivo de otra cuenta devuelve el mismo `404` que un id inexistente.

### Qué contiene el ZIP

`LEEME.txt` + un JSON por sección: `profile`, `posts`, `comments`, `likes`, `following`, `followers`, `messages`, `notifications`, `muted_keywords`, `sessions`.

**Nunca incluye** el hash de contraseña, el secreto TOTP ni el `jti` de las sesiones (el identificador que valida cada petición). Hay una prueba que lo verifica sobre el archivo real.

## Riesgos asumidos

- **El archivo vive en la base.** Cada exportación ocupa la base hasta caducar; una cuenta con mucho contenido genera un ZIP grande. El cooldown y los 7 días lo acotan; no hay tope de tamaño por archivo.
- **La generación es síncrona**: una cuenta enorme bloquea un *worker* mientras se arma. Si el producto crece, la opción B es la evolución natural.
- **Sin cifrar.** Quien tenga el ZIP lo lee. Contiene el correo, el teléfono y los mensajes de la persona.
- **Los mensajes incluyen texto escrito por la otra parte** de cada conversación. Es parte de «tus mensajes», pero es contenido de un tercero.
- **Una descarga con un token robado** entrega todo el archivo. Es el mismo riesgo que ya tiene cualquier endpoint protegido (`ADR-025`); por eso el archivo no incluye nada que permita autenticarse.

## Verificación

`backend/tests/test_data_exports.py` — 7 pruebas contra PostgreSQL real: autenticación obligatoria, ZIP real y legible, ausencia de secretos, cooldown, historial con contador de descargas, aislamiento entre cuentas, y caducidad (`410` + contenido descartado).
