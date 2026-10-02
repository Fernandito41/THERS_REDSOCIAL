# ADR-029 — Cuentas bloqueadas y restringidas

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/ADR-029-blocked-and-restricted-accounts.md` |
| Tipo | Architecture Decision Record (`HB-001` §11–12) |
| Fecha | 01/10/2026 |
| Estado | **Aceptada** — implementada en esta tarea, a pedido del propietario del proyecto. Pendiente de la revisión humana que exige `HB-001` §19 |
| Alcance | `backend/` — entidad `user_restrictions` y su aplicación en feed, comentarios, likes, follows, mensajes, notificaciones y menciones; `GET`/`POST`/`DELETE /api/users/me/blocks` y `/api/users/me/restrictions`; `Frontend/` — `RestrictedAccountsRow.jsx`, menú de la tarjeta de publicación y la sección «Cuentas bloqueadas y restringidas» (REF-SET-10) |
| Autoridad sobre este documento | `/docs` oficial > estructura real observada en el código > este documento (mismo orden que `CLAUDE.md` §4) |

> **Es un ADR transversal:** a diferencia de `ADR-028`, no agrega una función aislada. Un bloqueo solo significa algo si **cada** camino que lee o escribe contenido lo respeta, así que toca feed, comentarios, likes, follows, mensajes, notificaciones y menciones a la vez.

---

## Contexto

La sección REF-SET-10 tenía dos controles `pending`: «Cuentas bloqueadas» («Requiere comprobación de acceso en el servidor, que no existe») y «Cuentas restringidas» («Sin modelo de restricción ni moderación de comentarios»). Los dos motivos eran exactos: ocultar a alguien solo en la interfaz no impide que acceda a tu contenido por la API.

## Objetivos

- **Bloquear:** la cuenta bloqueada no ve ni interactúa con la tuya, y tú dejas de ver la suya — aplicado en el servidor.
- **Restringir:** la cuenta restringida sigue viendo tu perfil e interactuando, pero sus comentarios en tus publicaciones quedan ocultos para los demás (REF-SET-10).
- Que ambas se gestionen desde Configuración y desde el menú de una publicación.

## No objetivos

- **No** hay endpoint de búsqueda de usuarios (no existe en el proyecto). Se bloquea por `@username` escrito o por `user_id` conocido desde una tarjeta.
- **No** se notifica al bloqueado ni al restringido. Restringir en particular es silencioso a propósito.
- **No** se mueven a «solicitudes» los mensajes de una cuenta restringida (lo hace otro producto): la restricción de este ADR es solo de comentarios, que es lo que dice la pantalla.
- **No** oculta el perfil: no existe un endpoint de perfil ajeno. Hoy solo se reconoce a una cuenta por sus publicaciones, y esas sí se ocultan.

## Opciones consideradas

| Opción | Trade-off |
|---|---|
| **A — Una tabla `user_restrictions` con `kind` (elegida)** | Una fila por par (dueño, destino). Una cuenta está bloqueada **o** restringida, nunca ambas: la `UNIQUE` lo garantiza en el motor. Mismo criterio que `Notification.type` y `Follow.status` |
| B — Dos tablas, `blocks` y `restrictions` | Permitiría estar en ambos estados a la vez, que no tiene sentido (bloquear ya contiene todo lo que restringe), y duplica repositorio, rutas y consultas |
| C — Solo filtrar en el Frontend | Es justo lo que la pantalla ya rechazaba: no impide nada a quien llama la API directamente |

## Decisión

### Tabla `user_restrictions`

| Columna | Tipo | Nota |
|---|---|---|
| `id` | UUID PK | — |
| `owner_id` | UUID → `users.id`, CASCADE | Quien bloquea o restringe |
| `target_id` | UUID → `users.id`, CASCADE | A quién |
| `kind` | VARCHAR(10) | `'block'` o `'restrict'`, validado en la aplicación (`domain/restrictions/kinds.py`) |
| `created_at` | TIMESTAMPTZ | — |

`UNIQUE (owner_id, target_id)`, `CHECK (owner_id <> target_id)` e índice `(target_id, kind)` para «¿alguien me bloqueó?». Migración `d9a3b7f1c5e2`, escrita a mano.

**Bloquear reemplaza a restringir** (UPSERT en una sentencia). **Restringir a quien está bloqueado devuelve `409`:** bajar la protección sin que nadie lo pida sería un error silencioso; hay que desbloquear primero.

### El bloqueo es simétrico a efectos de acceso

Si A bloquea a B, **ninguno de los dos** ve ni interactúa con el otro. La relación se guarda en una dirección (quién bloqueó importa para desbloquear y para los mensajes de error), pero toda comprobación de acceso mira ambos sentidos.

| Dónde se aplica | Qué ocurre |
|---|---|
| **Feed** (`GET /api/posts`) | Los posts del otro no aparecen. En el `WHERE`, no en Python: filtrar después del `LIMIT` devolvería páginas cortas (mismo motivo que `ADR-022`) |
| **Comentarios** (listar y contar) | Sus comentarios no aparecen y **no cuentan**. Contador y lista comparten una única definición del predicado, como en `ADR-024` |
| **Ver / comentar / dar like a un post** | `404`, el mismo que un post inexistente (guardia `assert_post_visible`, la misma de `ADR-022`) |
| **Seguir** | Se cortan los follows en **ambos sentidos** (aceptados y pendientes) al bloquear. Seguir queda prohibido |
| **Mensajes** | No se puede escribir; el hilo da `404`; las conversaciones desaparecen de la lista y **no suman al badge** de no leídos. No se borra nada: reaparece al desbloquear |
| **Escribiendo...** | El aviso se descarta en silencio |
| **Notificaciones** | Se ocultan las de cuentas bloqueadas, también en el `WHERE` |
| **Menciones** | Un `@usuario` con bloqueo en cualquier sentido no se resuelve como mención ni notifica |

### Qué se le dice a cada parte

Es la decisión de seguridad central: **el bloqueo no debe revelarse al bloqueado.**

| Quién actúa | Respuesta |
|---|---|
| El **bloqueado** intenta seguir o escribir a quien lo bloqueó | `404 Usuario no encontrado` — como si la cuenta no existiera |
| Quien **bloqueó** intenta seguir o escribir al bloqueado | `409` con el motivo («Tienes bloqueada a esta cuenta») — sabe lo que hizo y reintentar a ciegas no ayuda |
| Cualquiera sobre un post del otro | `404`, indistinguible de un post inexistente |

### Restricción

Los comentarios de la cuenta restringida **en publicaciones de quien la restringió** quedan ocultos para todos, **excepto**:

- su **autor** — no debe notar nada; si no, se daría cuenta de que está restringido y escribiría de nuevo pensando que falló (mismo razonamiento que `ADR-024` para los filtros);
- el **dueño de la publicación** — es quien restringió y necesita ver lo que esa persona escribe para moderarlo.

Alcance acotado: solo afecta a **las publicaciones de quien restringió**. Los comentarios de la cuenta restringida en el resto de publicaciones se ven con normalidad. Todo lo demás (ver, dar like, seguir, escribir mensajes) funciona igual.

## Riesgos asumidos

- **Más consultas en cada lectura de feed/comentarios:** una subconsulta `EXISTS` por fila sobre `user_restrictions`. Está cubierta por la `UNIQUE (owner_id, target_id)` y por el índice por `target_id`; el volumen de una tabla de bloqueos es muy chico frente a posts o comentarios.
- **Cada caso de uso que escribe o lee contenido nuevo tiene que acordarse de respetar el bloqueo.** No hay un punto único que lo imponga: es una guardia por camino (`assert_post_visible`, `blocked_ids_either_way`, el predicado SQL). Hay una prueba por camino en `tests/test_restrictions.py`, pero un endpoint futuro que se olvide de la guardia sería un agujero. **Es el riesgo principal de este ADR.**
- **Seguimiento por inferencia:** el `404` al seguir distingue «bloqueado» de «existe y me deja» para quien pruebe muchos ids, aunque no distingue «bloqueado» de «no existe». Se acepta.
- **Sin rate limit** en los endpoints de bloqueo (no son un vector de fuerza bruta ni envían correos).
- **Los datos previos permanecen:** un bloqueo no borra publicaciones, comentarios ni mensajes, solo los oculta. Desbloquear los restituye, **salvo los follows**, que se cancelaron.

## Contrato

Ver `API_CONTRACT.md` §4.14.

## Verificación

`backend/tests/test_restrictions.py` — 31 pruebas contra PostgreSQL real: los endpoints (autenticación, por `user_id` y por `username`, idempotencia, aislamiento entre cuentas, bloquear reemplaza restringir, restringir a un bloqueado es `409`), y la **aplicación del bloqueo en cada camino** (feed en ambos sentidos, like y comentario, hilo y contador de comentarios, follows en ambos sentidos, mensajes y conversaciones, notificaciones, menciones) y de la restricción (oculta a terceros, no a su autor ni al dueño, alcance solo a las publicaciones de quien restringió, el resto de interacciones intactas).
