# ADR-021 — Registro de sesiones y alertas de inicio de sesión

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/ADR-021-session-registry.md` |
| Tipo | Architecture Decision Record (`HB-001` §11–12) |
| Fecha | 01/10/2026 |
| Estado | **Aceptada** — implementada en esta tarea (ver §Decisión) |
| Alcance | `backend/` — entidad `sessions`, `users.login_alerts_enabled`, `token_in_blocklist_loader`, `GET`/`DELETE /api/sessions`, `DELETE /api/sessions/<id>`, `GET`/`PATCH /api/users/me/security`; `Frontend/` — `ActiveSessionsRow.jsx`, interruptor de alertas en Configuración › Seguridad |
| Autoridad sobre este documento | `/docs` oficial > estructura real observada en el código > este documento (mismo orden que `CLAUDE.md` §4) |

> **Es el ADR con el cambio arquitectónico más profundo del backend hasta ahora:** el JWT deja de ser puramente *stateless*. No agrega una entidad al margen — redefine qué significa que un token sea válido, y por eso afecta a **todos** los endpoints protegidos a la vez.

---

## Contexto

La pantalla de Seguridad (REF-SET-03, `Frontend/src/features/feed/data/settingsSections.js`) tenía tres controles marcados como `pending`:

| Control | Motivo que daba la pantalla |
|---|---|
| Ver y cerrar sesiones | "El JWT no se registra por dispositivo, así que no hay nada que listar ni revocar de verdad" |
| Alertas de inicio de sesión | "Requiere registro de sesiones, que no existe" |
| Activar 2FA | "No está implementado" → lo resuelve `ADR-022` |

Los dos primeros motivos eran exactos y el segundo señalaba la dependencia correcta: **sin registro de sesiones, las alertas no se pueden construir**, porque no hay forma de saber si un dispositivo es nuevo. Este ADR resuelve el primero y, con él, habilita el segundo.

Los otros dos controles de esa pantalla (el correo de cambio de contraseña, `ADR-010`, y la verificación de email, `ADR-011`) **ya funcionaban y no se tocan**.

El punto de partida: `create_access_token(identity=user["id"])` emitía un JWT firmado y autocontenido. Eso significa que el token es válido mientras no expire y **no existe ninguna operación que lo invalide**. No es un descuido: es exactamente la propiedad por la que se elige un JWT. Pero hace que "cerrar sesión en ese dispositivo" sea literalmente imposible de implementar.

## Objetivos

- Ver desde qué dispositivos hay sesión abierta, y cerrar cualquiera de ellos.
- Que cerrar una sesión invalide su token **de inmediato**, no al expirar.
- Avisar por correo de un acceso desde un dispositivo no visto antes, y poder desactivar ese aviso.
- Que cambiar la contraseña cierre todas las sesiones.
- Que ningún token pueda emitirse sin quedar registrado (si no, sería válido pero invisible e irrevocable).

## No objetivos (explícitamente fuera de este ADR)

- **No** implementa *refresh tokens* ni rotación. El token de acceso sigue siendo el único, con la misma vida que antes.
- **No** geolocaliza la IP ("Buenos Aires, Argentina"). Requiere un servicio externo de geolocalización que el proyecto no tiene, y una IP mal geolocalizada es peor que una IP cruda: haría dudar de un acceso legítimo.
- **No** parsea el `User-Agent` en el servidor (ver §Decisión).
- **No** limita cuántas sesiones puede tener una cuenta a la vez.
- **No** purga las filas revocadas. Crecen indefinidamente; ver §Riesgos.
- **No** avisa de un acceso desde una **IP** nueva, solo desde un dispositivo nuevo. Una IP cambia cada vez que alguien se mueve de red: alertar por eso sería ruido constante.
- **No** implementa 2FA — es `ADR-022`, que depende de este.

## Opciones consideradas — cómo se revoca un token

| Opción | Descripción | Trade-off |
|---|---|---|
| **A — Tabla `sessions` con el `jti`, comprobada en cada petición (elegida)** | El token sigue firmado y autocontenido, pero además su `jti` tiene que tener una fila viva | Es la única opción que cumple el objetivo real ("cerrar sesión en ese dispositivo" funciona de verdad, al instante). El coste es una consulta por petición protegida, por índice único. Además da gratis la lista de dispositivos, el "último uso" por sesión y la base de las alertas |
| B — Lista negra en memoria del proceso | Un `set` de `jti` revocados | Sin tabla ni consulta, pero se pierde al reiniciar (un token revocado volvería a valer) y no se comparte entre *workers*. Es el mismo defecto que `ADR-014` aceptó a conciencia para el indicador de "escribiendo" — ahí era tolerable porque es información efímera y cosmética; acá sería un agujero de seguridad |
| C — Bajar la expiración del token y rotar con *refresh tokens* | Un token de acceso muy corto limita la ventana de un token robado | Mitiga, no resuelve: entre revocar y expirar el token sigue sirviendo, y seguiría sin existir una lista de dispositivos que mostrar. Además es un rediseño del flujo de autenticación entero, mucho más invasivo que una tabla |
| D — Dejarlo `pending` | — | Es lo que había. El control prometía algo que no existía |

**Elegida: A.** Con una consecuencia asumida explícitamente: **el backend deja de ser *stateless* en autenticación.** Está documentado acá porque es exactamente el tipo de decisión que no debe descubrirse leyendo el código.

### Opciones consideradas — qué se guarda del dispositivo

El `User-Agent` se guarda **crudo**, sin parsear. El resumen ("Chrome en Windows") vive en el Frontend (`describeUserAgent.js`).

El motivo: el servidor no tiene una base de datos de user agents, y adivinar produciría etiquetas equivocadas **persistidas** — un Edge guardado como "Chrome" no se puede corregir después sin migrar datos. En el Frontend es presentación pura y se corrige cambiando una línea. Y cuando no se reconoce, se muestra el texto original: **un texto raro es más útil que una etiqueta equivocada**, porque alguien puede reconocer su propio user agent pero no puede reconocer un navegador que no usa.

La IP se guarda desde `X-Forwarded-For` cuando existe (detrás de un proxy, `remote_addr` es la del proxy). Es un header que el cliente puede falsificar, así que **solo se usa para mostrarlo, nunca para autorizar nada**.

### Opciones consideradas — revocar borra o marca

Revocar hace `UPDATE revoked_at`, no `DELETE`. La fila se conserva para que `has_seen_user_agent` siga sabiendo que ese dispositivo era conocido: si se borrara, cerrar sesión y volver a entrar desde el mismo navegador generaría una alerta de "dispositivo nuevo" que es falsa. Las revocadas **no se listan** — conservarlas es para el servidor, mostrarlas solo acumularía ruido.

## Decisión

### Tabla `sessions`

| Columna | Tipo | Nota |
|---|---|---|
| `id` | UUID PK | Lo que el cliente usa para revocar. **No** es el `jti` |
| `user_id` | UUID → `users.id`, CASCADE | — |
| `jti` | `VARCHAR(36)`, UNIQUE | El identificador que flask_jwt_extended ya pone en cada JWT. `VARCHAR` y no UUID nativo: es un valor que produce la librería, no el esquema |
| `user_agent` | `TEXT`, nullable | Crudo. Un cliente no está obligado a mandarlo |
| `ip_address` | `VARCHAR(45)`, nullable | 45 = máximo de una IPv6 en texto |
| `created_at` | `TIMESTAMPTZ` | Cuándo se inició |
| `last_used_at` | `TIMESTAMPTZ` | Con throttle de 5 min (ver abajo) |
| `revoked_at` | `TIMESTAMPTZ`, nullable | `NULL` = viva |

**Índices.** `uq_sessions_jti` cubre el acceso caliente (la comprobación por token en cada petición). `ix_sessions_user_id_created_at` cubre el otro (listar las de una persona), que lidera por otra columna.

### `token_in_blocklist_loader`: el JWT pasa a verificarse contra la base

Se usa el hook que `flask_jwt_extended` ya ofrece, en vez de un decorador propio que habría que recordar poner en cada endpoint (y que se olvidaría en el endpoint número veinte). Deniega si:
- el `jti` no tiene fila viva en `sessions`, **o**
- el token lleva el claim `purpose: "2fa_challenge"` (`ADR-022`).

Responde `401` con un mensaje propio, distinto de "token expirado": criptográficamente el token sigue siendo válido, lo que pasó es que esa sesión se cerró.

### Emisión: un solo camino

`_issue_session_token()` (en `auth_routes.py`) es el **único** lugar del backend que emite un token de sesión, y los tres caminos que lo producen pasan por él: `POST /api/login`, `POST /api/auth/google` y `POST /api/2fa/verify`. Centralizarlo es lo que garantiza la invariante "ningún token sin sesión".

### `GET /api/sessions`

Las sesiones vivas, más reciente primero, límite 50. **El `jti` nunca cruza la frontera HTTP** — es el identificador que valida cada petición, así que exponerlo convertiría la lista en una lista de identificadores de token. Para revocar se usa el `id` de la fila, que no autentica nada. `is_current` permite marcar "Este dispositivo".

### `DELETE /api/sessions/<id>` y `DELETE /api/sessions`

- **Una concreta** → `200 {"revoked": true, "was_current": bool}`. **Se permite cerrar la propia**: es lo mismo que cerrar sesión, y bloquearlo obligaría a explicar una excepción sin ganar nada. `was_current` le dice al Frontend que tiene que ir a `/login`, en vez de dejar la pantalla rota en el siguiente *fetch*. El `UPDATE` usa `RETURNING jti` para saberlo sin una segunda consulta.
- **Las demás** (sin id) → `200 {"revoked_count": n}`. **Nunca cierra la propia**: es la acción que alguien ejecuta justamente cuando sospecha que otro dispositivo tiene acceso; hacerlo salir también sería contraproducente.
- `404` si no existe, ya estaba cerrada o es de otra persona — indistinguibles.

### `last_used_at` con throttle

Lo actualiza el mismo hook `after_request` que ya marcaba `users.last_seen_at` (`ADR-020`), con el mismo throttle de 5 minutos **impuesto en el propio `WHERE`** y no en memoria del proceso — así funciona igual con varios *workers*. Sin throttle, el *polling* del chat (cada 4 s, `ADR-014`) escribiría en cada petición.

### Alertas de inicio de sesión

`users.login_alerts_enabled`, `BOOLEAN NOT NULL DEFAULT true`. **Nace activada**, a diferencia de casi todas las preferencias del proyecto: una alerta de seguridad que hay que descubrir y encender no protege a nadie. Sin `RESEND_API_KEY` el envío es un no-op registrado por log, así que activarla por defecto no rompe el desarrollo local.

Se manda cuando el `user_agent` **no se había visto antes** en esa cuenta (incluyendo sesiones ya revocadas). La comprobación ocurre **antes** de crear la fila — después, el propio `user_agent` que acabamos de guardar haría que cualquier dispositivo pareciera conocido.

El correo **no lleva enlaces de acción** ("no fui yo, bloquear"): un enlace accionable desde un correo es un vector de *phishing*, y exigiría un token de un solo uso propio. Dirige a la pantalla de Seguridad, donde la persona ya autenticada puede cerrar la sesión. Es además la primera plantilla que interpola un valor que el servidor no controla (el `User-Agent`), así que se añadió un `_escape()` explícito.

Un fallo de envío **nunca** impide el login: la alerta es un aviso, no un requisito de autenticación.

### `GET`/`PATCH /api/users/me/security`

Endpoint propio, separado de `/users/me/privacy` (`ADR-020`): privacidad es "quién ve qué", seguridad es "quién puede entrar". Comparten pantalla pero no dominio. Hoy transporta una sola preferencia, y es su lugar correcto — meterla en el de privacidad obligaría a la próxima persona a buscarla donde no está.

### Cambiar la contraseña cierra todas las sesiones

`POST /api/reset-password` llama a `revoke_all_for_user`. **Antes de este ADR era imposible**, y era un agujero concreto: quien restablecía su contraseña justamente porque sospechaba un acceso ajeno **no echaba a ese acceso**.

### Seguridad

- La pertenencia de una sesión se confirma **en el propio `WHERE`** del `UPDATE` (`user_id` + `revoked_at IS NULL`), no leyendo la fila y comparando después.
- `404` indistinguible para una sesión ajena — un `403` confirmaría que existe.
- `X-Forwarded-For` solo se muestra, nunca autoriza.
- El `jti` no sale de `application/`: el presenter no lo expone.

## Impacto en Frontend

- **`ActiveSessionsRow.jsx`** (nuevo): lista con "Este dispositivo", cerrar una y "cerrar las demás". Cerrar la propia pide confirmación (`ConfirmDialog`) y después hace `window.location.assign("/login")` — una recarga completa, para no dejar estado en memoria de una sesión que ya no existe. Cerrar otra no pide confirmación: es reversible volviendo a entrar en ese dispositivo.
- **`describeUserAgent.js`** (nuevo): resume el UA en el Frontend, con *fallback* al texto crudo.
- **`useSecuritySettings.js`** (nuevo): mismo patrón que `usePrivacySettings` (optimista con rollback, nada en `localStorage`).
- **`settingsSections.js`**: la sección de Seguridad se reescribe; su aviso pasa a `info`.

## Impacto en Backend

- `migrations/versions/f1a4c8e2d573_create_sessions_and_login_alerts.py` (nueva).
- `domain/sessions/repositories.py`, `domain/sessions/exceptions.py` (nuevos).
- `infrastructure/persistence/repositories/session_repository.py` (nuevo).
- `extensions.py`: `token_in_blocklist_loader` + `revoked_token_loader`.
- `application/sessions/`: `issue_session_use_case.py`, `manage_sessions_use_case.py`, `session_presenter.py` (nuevos).
- `application/email/templates.py`: `login_alert_email` + `_escape`; `email_service.py`: `send_login_alert_email`.
- `interfaces/activity_tracker.py`: también toca `sessions.last_used_at`.
- `interfaces/routes/security_routes.py` (nuevo, compartido con `ADR-022`); `auth_routes.py`: emisión centralizada.
- `application/auth/reset_password_use_case.py`: revoca todas las sesiones.
- Tests en `tests/test_security.py`; una aserción de `tests/test_users_me.py` actualizada (ver §Consecuencias).

## Riesgos

- **Una consulta a la base por cada petición protegida.** Va por índice único, pero es una ida al disco que antes no existía. Es el precio directo de poder revocar; no se midió con volumen real (el proyecto no tiene entorno de carga, `CLAUDE.md` §15).
- **Todo el mundo se desloguea una vez.** Los tokens emitidos antes de esta migración no tienen fila, así que dejan de valer. Inevitable y de una sola vez.
- **Las filas revocadas crecen sin límite.** Cada login suma una fila que nunca se borra. Con los volúmenes del proyecto no es un problema hoy; purgarlas exige un proceso programado que no existe (DevOps sin documentación oficial, `CLAUDE.md` §15).
- **La heurística de "dispositivo conocido" es gruesa.** Compara el `User-Agent` exacto: una actualización del navegador cambia la versión y genera una alerta falsa; dos personas con el mismo navegador y versión desde el mismo equipo no generan ninguna. Es la señal que hay sin registrar una huella del dispositivo (que sería más invasiva).
- **El `User-Agent` es texto del cliente.** Se guarda crudo y se escapa al interpolarlo en el correo, pero sigue siendo un valor arbitrario que aparece en la interfaz de la persona.
- **Sin *rate limiting*** en los endpoints nuevos, coherente con el resto del proyecto (`API_CONTRACT.md` §9).

## Decisiones pendientes (cada una es su propio ADR futuro)

- Purga periódica de sesiones revocadas (depende de que exista un proceso programado).
- *Refresh tokens* y rotación.
- Geolocalización aproximada de la IP.
- Alertas por IP nueva, además de por dispositivo nuevo.
- Límite de sesiones simultáneas.
- Bloquear a una persona — heredada de `ADR-018`, sigue abierta.

## Consecuencias

- **`DATABASE_ARCHITECTURE.md` cambia** (tabla `sessions`, `users.login_alerts_enabled`) → v0.20.
- `API_CONTRACT.md` → v0.24. **Ningún endpoint cambia de forma, pero TODOS los protegidos cambian de condición de validez**: un token sin sesión viva ya no autentica.
- **La rama `404` de `GET /api/users/me` quedó inalcanzable en la práctica.** `sessions.user_id` es una FK con `ON DELETE CASCADE`, así que si la cuenta se borra su sesión se borra con ella y el token cae en el `401` del *blocklist loader* antes de llegar al handler. La rama se conserva en el código como defensa, no porque haya un camino que la produzca; la prueba que la cubría se actualizó a `401` con esa explicación.
- `ADR-022` depende de este: el token de desafío de 2FA se rechaza en endpoints protegidos **precisamente porque** no tiene fila en `sessions`.

## Referencias

- `docs/architecture/ADR-022-two-factor-authentication.md` — el otro ADR de esta pantalla; depende de este.
- `docs/architecture/ADR-010-password-reset-otp-flow.md` — el flujo de contraseña que ya funcionaba y que este ADR solo extiende (revocar sesiones).
- `docs/architecture/ADR-014-messages-ux-improvements.md` — el caso en que una lista en memoria **sí** era aceptable, y por qué acá no.
- `docs/architecture/ADR-020-content-filters-and-privacy-preferences.md` — origen del hook `after_request` y del throttle en el `WHERE`.
- `CLAUDE.md` — jerarquía de fuentes (§4), regla de alcance (§14).

---

## Cierre

Dos de los tres controles `pending` de la pantalla de Seguridad pasan a funcionar, y el backend gana su primera noción de "sesión" como cosa que existe y se puede terminar. El coste —una consulta por petición y la pérdida del *statelessness*— está asumido a conciencia: era eso o seguir prometiendo un botón que no podía hacer nada.
