# ADR-031 — Eliminación de cuenta

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/ADR-031-account-deletion.md` |
| Tipo | Architecture Decision Record (`HB-001` §11–12) |
| Fecha | 02/10/2026 |
| Estado | **PROPUESTO** — pendiente de aprobación del equipo. **Nada de esto está implementado.** Redactado por Claude Code a pedido del propietario del proyecto |
| Alcance | `backend/` — nueva tabla `account_deletion_codes`, `POST /api/account-deletion/request` y `/confirm`; `Frontend/` — Configuración › Seguridad y una página pública; `mobile/` — un acceso dentro de la app |
| Relacionado | `ADR-010` (código OTP), `ADR-017` (refresh tokens), `ADR-025` (sesiones), `ADR-026` (2FA), `ADR-027` (rate limiting), `ADR-028` (exportación), `ADR-032` (reportes), `docs/LAUNCH_CHECKLIST.md` |
| Autoridad sobre este documento | `/docs` oficial > estructura real observada en el código > este documento (mismo orden que `CLAUDE.md` §4) |

---

## Contexto

### Por qué hace falta

Google Play exige a toda app que permita **crear una cuenta** que ofrezca **dos caminos**: uno **dentro de la app** para eliminar la cuenta y sus datos, y un **recurso web** donde se pueda pedir esa eliminación sin tener la app instalada. Como alternativa a una eliminación completa dentro del móvil, admite un enlace dentro de la app que lleve a ese recurso web. Los datos que se retengan por seguridad, prevención de fraude o normativa **se declaran en la política de privacidad**, y el formulario «Seguridad de los datos» pregunta por la eliminación.
(Verificado el 2026-10-02 en la ayuda de Play Console, «Understanding Google Play's app account deletion requirements». **Reverificar al enviar la app**: las políticas cambian.)

### Qué hay hoy, verificado en `develop` (`8a213c0`)

| Hecho | Consecuencia |
|---|---|
| **No existe ninguna ruta ni caso de uso** que elimine una cuenta | No se puede cumplir el requisito |
| Las **22 claves foráneas a `users` son `ON DELETE CASCADE`** (posts, likes, comentarios, follows, notificaciones, mensajes, tokens, identidades de Google, menciones, silenciados, sesiones, códigos 2FA, exportaciones, restricciones, `refresh_tokens`) | Borrar la fila de `users` ya arrastra todos los datos **de la base**, sin código nuevo. Lo que falta es todo lo demás |
| `messages.sender_id` **y** `messages.recipient_id` son `CASCADE` | Borrar la cuenta borra los mensajes **también de la bandeja del otro lado** (ver decisión 2) |
| El avatar y la portada viven en el almacenamiento de objetos (`ADR-015`), no en la base | **El `CASCADE` no los borra**: quedarían huérfanos. `MediaStorage.delete(key)` ya existe |
| Las exportaciones (`ADR-028`) guardan el ZIP en la base (`BYTEA`) | Se borran con la cuenta, sin trabajo extra |
| `rate_limit_buckets` se identifica con una cadena `user:<id>`, **sin clave foránea** | Quedarían filas sueltas |
| Cuentas creadas solo con Google **no tienen contraseña** (`ADR-012`) | Pedir la contraseña para confirmar excluiría a esas cuentas |
| Existe un patrón de código por correo ya probado (`ADR-010`/`ADR-011`) y un `EmailService` | Reutilizable |
| La app móvil no tiene pantalla de Configuración | Hace falta al menos un acceso |

## Objetivos

- Que una persona pueda eliminar su cuenta y sus datos **desde la web, desde la app y sin sesión** (por ejemplo, si olvidó la contraseña).
- Que **nadie pueda eliminar la cuenta de otro**, ni siquiera con una sesión robada.
- Que la eliminación sea **completa**: base de datos y almacenamiento de objetos.
- Que no se pueda usar el endpoint para averiguar qué correos están registrados.
- Que una tabla nueva, agregada más adelante, **no deje de borrarse sin que nadie lo note**.

## No objetivos

- **No** hay período de gracia ni restauración (ver opción B).
- **No** se «desactiva» temporalmente la cuenta: es otra función.
- **No** se retienen datos por motivos legales. Si el equipo o su asesor legal concluye que hace falta, se declara en la política de privacidad y se decide aparte.
- **No** se ofrece apelar ni deshacer una eliminación ya hecha.

## Opciones consideradas

### Cuándo se borra

| Opción | A favor | En contra |
|---|---|---|
| **A — Borrado inmediato y definitivo (elegida para la v1)** | Simple. Cumple el requisito sin infraestructura nueva: **no necesita ningún proceso programado**. Es lo que el `CASCADE` ya hace en la base | Irreversible. Un error o un robo de cuenta no tiene vuelta atrás: por eso la confirmación es fuerte (decisión 1) |
| B — Marcar como eliminada y borrar a los N días | Permite arrepentirse y reduce el daño de un robo | Exige un trabajo programado que **hoy no existe** (`ADR-018` no está aprobado), ocultar la cuenta en todos los caminos de lectura (como `ADR-029`), y complica el cumplimiento: los datos siguen existiendo N días |
| C — Anonimizar en lugar de borrar | Conserva el contenido para los demás | Anonimizar bien es difícil, los datos no desaparecen y es lo contrario de lo que pide la política de Play |

### Cómo se prueba que la cuenta es de quien lo pide

| Opción | A favor | En contra |
|---|---|---|
| **A — Código de 6 dígitos al correo de la cuenta, más el segundo factor si lo tiene (elegida)** | Funciona para **todas** las cuentas, incluidas las de solo Google; funciona **sin sesión**; una sesión robada no basta (hace falta el correo) | Quien controla el correo puede iniciar el proceso, por eso se exige también la 2FA |
| B — Contraseña | Sencillo | Excluye las cuentas de solo Google y a quien olvidó la contraseña, que es justo quien más necesita el camino web |
| C — Re-login con Google | Cubre las cuentas de Google | No cubre las demás; depende de un tercero |

## Decisión

### 1. Flujo en dos pasos, público

| Paso | Endpoint | Auth |
|---|---|---|
| Pedir el código | `POST /api/account-deletion/request` `{email}` | Ninguna |
| Confirmar y eliminar | `POST /api/account-deletion/confirm` `{email, code, two_factor_code?}` | Ninguna |

- **`request`** responde siempre `200` con el **mismo mensaje**, exista o no la cuenta. Si existe, crea un código y lo envía. Mismo patrón que `forgot-password` (`ADR-010`): código de 6 dígitos con hash **scrypt**, vigencia **10 minutos**, **5 intentos**, *cooldown* de **60 segundos**, e índice único parcial para que haya **a lo sumo un código activo por cuenta**. Reutiliza una tabla nueva `account_deletion_codes` (no la de recuperación: un código de recuperación **nunca** debe servir para borrar la cuenta, mismo razonamiento que `ADR-011`).
- **`confirm`** verifica el código. Si la cuenta tiene **2FA activada**, exige además `two_factor_code` (TOTP o código de recuperación) y, si falta, responde `403` con `two_factor_required: true` **sin consumir el código**. Sin eso, quien solo controla el correo podría borrar una cuenta que la 2FA protege.
- Aplica los límites de `ADR-027` (nuevas reglas `ACCOUNT_DELETION_REQUEST` y `ACCOUNT_DELETION_CONFIRM`, por cuenta y por IP).
- Funciona también con la sesión abierta: la app y la web precargan el correo; el endpoint no cambia.
- **No hay token de sesión en el flujo**, así que una sesión robada por sí sola no permite eliminar.

### 2. Qué se elimina

Todo lo que cuelga de `users` por `CASCADE` (lista del Contexto), más lo que no cae solo:

| Dato | Cómo |
|---|---|
| Fila de `users` y todo lo que la referencia | `DELETE` en **una transacción** |
| Avatar y portada (`ADR-015`) | `MediaStorage.delete(key)` **después** de confirmar la transacción. Si falla, se registra la clave huérfana (sin datos personales) para barrerla después; **la eliminación no se revierte** |
| `rate_limit_buckets` con `user:<id>` | Se borran en la misma transacción |
| Sesiones y refresh tokens | Desaparecen por `CASCADE`: sin fila en `sessions`, el access token se rechaza **de inmediato** (`ADR-025`), no a los 15 minutos |
| Mensajes enviados **y recibidos** | **Se eliminan en los dos lados** (comportamiento actual de la base, sin cambios de esquema). Ver decisión 5 |
| Posts y comentarios propios | Se eliminan, junto con los comentarios de otras personas **sobre esos posts** |
| Menciones | Se eliminan las filas; el texto `@usuario` dentro de publicaciones **ajenas** queda como texto plano |

Se envía un correo de confirmación (`send_account_deleted_email`) a la dirección de la cuenta, **sin guardar copia** del correo ni del nombre después de enviarlo.

### 3. Dónde aparece

| Superficie | Qué hay |
|---|---|
| **Web, con sesión** | Configuración › Seguridad › «Eliminar cuenta». Ofrece **descargar antes el archivo de datos** (`ADR-028`) y exige escribir una palabra de confirmación |
| **Web, pública** | Página `/eliminar-cuenta` (nombre de la app visible, sin iniciar sesión). **Esta es la URL que se declara en Play Console** |
| **App móvil (v1)** | Un botón en el perfil que **abre la página web**. Play lo admite como alternativa a una eliminación completa dentro de la app |
| **App móvil (después)** | Eliminación nativa con las dos mismas llamadas: dos pantallas |

### 4. Garantía contra el olvido de tablas nuevas

Una prueba de integración **recorre `information_schema`** y exige que **toda clave foránea hacia `users` sea `CASCADE`** o figure en una lista explícita de excepciones tratadas por el caso de uso. Si alguien agrega una tabla con `RESTRICT` o sin `ON DELETE`, o una columna `user_id` sin clave foránea, **la suite falla**. Es el mismo criterio que protege el `TRUNCATE` de `conftest.py`.

### 5. Decisiones que necesitan al equipo

Quedan abiertas **a propósito**; la recomendación es mía, no una decisión tomada:

| # | Pregunta | Recomendación y motivo |
|---|---|---|
| 1 | ¿Borrado inmediato (A) o con período de gracia (B)? | **A para la v1.** B exige un trabajo programado que no existe y retrasa la eliminación real. Se puede añadir después |
| 2 | **Mensajes:** ¿se borran en los dos lados (hoy) o se conservan en la bandeja del otro, con el remitente anónimo? | **Borrar en los dos lados**, sin cambio de esquema. Conservar exige hacer nulo `messages.sender_id` y deja texto escrito por la persona que se fue. **Consultar con asesoría legal**, porque el mensaje también es dato de quien lo recibió |
| 3 | ¿Se **reserva** el `@usuario` unos días para evitar suplantaciones? | **No en la v1.** Reservarlo obliga a **guardar el nombre** de alguien que pidió su eliminación. Riesgo aceptado y escrito |
| 4 | **Copias de seguridad:** los datos eliminados siguen en ellas hasta que caducan (`ADR-018` propone 7 días con Supabase Pro) | Declararlo en la política de privacidad. Es el tipo de retención que Play exige explicar |
| 5 | ¿Se retiene algo por seguridad o normativa? | **Nada en la v1.** Si el asesor legal dice lo contrario, se declara y se decide en otro ADR |

## Seguridad

- **Sin enumeración de correos:** `request` responde igual exista o no la cuenta, con el mismo tiempo de respuesta razonable y el mismo cuerpo.
- **Código con hash lento (scrypt)**, 5 intentos y vigencia corta: seis dígitos son solo 10⁶ combinaciones (`ADR-010`).
- **El código no sirve para otra cosa:** tabla y repositorio propios.
- **Un `403 two_factor_required` solo se emite con el código ya verificado**, así no revela a un tercero que la cuenta tiene 2FA.
- **Sin datos personales en los registros** de la aplicación sobre la eliminación.
- **Correo previo** («alguien pidió eliminar tu cuenta») al enviar el código: si no fuiste tú, la persona se entera.

## Riesgos aceptados

- **Irreversible**, por la decisión de la opción A.
- **Quien controla el correo y no tiene 2FA puede eliminar la cuenta.** Es la misma exposición que ya tiene la recuperación de contraseña (`ADR-010`).
- **Archivos huérfanos** si el almacenamiento falla en ese instante; se mitiga registrando la clave.
- **Copias de seguridad** conservan los datos hasta que caducan.

## Implementación prevista (cuando se apruebe)

1. **Backend:** migración `account_deletion_codes`; `domain/account_deletion/`, `application/account_deletion/`, repositorio, dos rutas, dos reglas de `rate_limiting/policy.py`, dos métodos de `EmailService`.
2. **Pruebas:** código válido y expirado, intentos agotados, 2FA exigida, cuenta de solo Google, cuenta sin verificar, sin enumeración, access y refresh rechazados **inmediatamente** tras eliminar, archivos de avatar y portada borrados, y la prueba de las claves foráneas (decisión 4).
3. **Docs el mismo día** (`HB-001` §15.1): `API_CONTRACT.md` (sección nueva), `DATABASE_ARCHITECTURE.md`, `BACKEND_ARCHITECTURE.md`.
4. **Frontend:** fila en Seguridad y la página pública `/eliminar-cuenta`.
5. **Móvil:** botón que abre la página.
6. **No técnico, fuera del código:** actualizar la **política de privacidad** (qué se elimina, qué se retiene y las copias de seguridad) y completar las preguntas de eliminación del formulario «Seguridad de los datos».

## Fuentes consultadas

- Código de `develop` (`8a213c0`): `models.py` (claves foráneas), `domain/media/storage.py`, `application/email/email_service.py`.
- `ADR-010`, `ADR-011`, `ADR-012`, `ADR-015`, `ADR-018`, `ADR-025` a `ADR-029`.
- Play Console Help: *Understanding Google Play's app account deletion requirements* (2026-10-02).

## Implementación (2026-10-02) — corrección sobre mensajes y alcance

- **Mensajes de una cuenta eliminada:** se implementó el **borrado en las dos bandejas** (el `CASCADE` ya existente), no la conservación con «Usuario no encontrado» de la sección C. Motivo: conservar texto escrito por quien se fue exige anular `sender_id`/`recipient_id` y retener datos personales tras una eliminación, y esa lectura de la decisión del equipo no estaba confirmada. **Quien tenía la conversación recibe `404 «Usuario no encontrado»` al pedir ese hilo.** Si el equipo quiere conservarlos, es un cambio de esquema que requiere ADR propio y revisión jurídica.
- **Autenticación:** el flujo no usa contraseña (las cuentas de solo Google no tienen) ni sesión: el control del correo, el código y, si existe, el 2FA son la autenticación. Es la misma exposición que la recuperación de contraseña (`ADR-010`).
- **Suspensión voluntaria (sección B): NO implementada.** La advertencia final no la ofrece porque la función no existe; no se muestra un botón que no hace nada.
- Contrato: `API_CONTRACT.md` §4.18. Implementado en backend, web (`/eliminar-cuenta`) y móvil (pantalla dentro de la app).
