# ADR-010 — Recuperación de contraseña por código OTP de 6 dígitos

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/ADR-010-password-reset-otp-flow.md` |
| Tipo | Architecture Decision Record (`HB-001` §11–12) |
| Fecha | 16/09/2026 |
| Estado | **Aceptada** — implementada en esta tarea, reemplaza `ADR-009-password-reset-and-email-verification.md` en la parte de recuperación de contraseña (ver §Decisión) |
| Alcance | `backend/` — se reemplaza `password_reset_tokens` y los tres endpoints de recuperación; `Frontend/` — se conecta `ForgotPassword.jsx` por primera vez, se agrega `VerifyResetCode.jsx`, se adapta `ResetPassword.jsx`. La verificación de email (`email_verification_tokens`, `POST /api/send-verification-email`/`verify-email`) **no se toca**, es una entidad y un flujo distintos |
| Autoridad sobre este documento | `/docs` oficial > estructura real observada en el código > este documento (mismo orden que `CLAUDE.md` §4) |

> ⚠️ **Relación con ADR-009.** Este ADR **reemplaza** la parte de recuperación de contraseña de `ADR-009-password-reset-and-email-verification.md` (enlace con token en la URL) por un código OTP de 6 dígitos — decisión de producto explícita para acercar la experiencia a flujos ya familiares (Google, bancos). `ADR-009` sigue vigente sin cambios para todo lo demás: el servicio de correo centralizado (Resend, `EmailService`/`EmailSender`), la verificación de email, y los principios de seguridad generales (anti-enumeración, hashing, expiración, un solo uso) — este ADR los hereda y extiende, no los reinventa.

---

## Contexto

`ADR-009` ya daba a THERS recuperación de contraseña funcional: enlace con token de 256 bits en la URL, un clic, formulario de nueva contraseña. Funcionaba y estaba probado end-to-end con Resend real. El equipo pidió cambiar la experiencia a un flujo de código de 6 dígitos, tipo Google/2FA — el usuario nunca sale de la pestaña de THERS para hacer clic en un enlace de otra app (el correo); en cambio, mira el código en su bandeja y lo transcribe de vuelta en THERS.

## Problema

Rediseñar `POST /api/forgot-password`/`POST /api/reset-password` para que el paso intermedio sea un código de 6 dígitos verificado explícitamente, en vez de un token consumido directamente — sin abrir la puerta a que verificar el código alcance por sí solo para cambiar la contraseña de cualquiera (ver §Decisión, autorización temporal), y sin dejar `1.000.000` de combinaciones como la única defensa (§Seguridad).

## Objetivos

- `POST /api/forgot-password` genera un código de 6 dígitos, no un enlace — mismo endpoint, también sirve para "Reenviar código" (no hace falta un endpoint de resend separado).
- Nuevo `POST /api/verify-reset-code`: valida el código y, si es correcto, emite una autorización temporal de propósito específico — nunca un JWT de sesión normal.
- `POST /api/reset-password` consume esa autorización, no el código ni un enlace.
- Protección real de fuerza bruta: máximo de intentos, no solo expiración.
- A lo sumo un código activo por usuario en todo momento — reenviar invalida el anterior, incluso ante dos reenvíos simultáneos (condición de carrera).
- Se mantienen íntegras las protecciones ya ratificadas por `ADR-009`: anti-enumeración, cooldown de reenvío impuesto también en el backend (no solo en el Frontend), nada de información sensible en logs/URLs/respuestas.
- El Frontend queda conectado de punta a punta en la misma tarea (a diferencia de `ADR-009`, donde `ForgotPassword.jsx` había quedado fuera de alcance) — nueva pantalla `VerifyResetCode.jsx`, componente reutilizable de 6 casillas.

## No objetivos (explícitamente fuera de este ADR)

- **No** toca la verificación de email (`email_verification_tokens`, `POST /api/send-verification-email`/`verify-email`) — sigue exactamente como `ADR-009` la dejó, es una entidad y un flujo completamente separados.
- **No** implementa rate limiting a nivel de infraestructura (por IP, con una librería tipo Flask-Limiter) — el cooldown de 60s por usuario (ya existente desde `ADR-009`, reutilizado) sigue siendo la única defensa contra abuso de envío; una defensa más amplia queda como recomendación para una tarea futura (ver informe de esta tarea, §13).
- **No** implementa un endpoint de "Reenviar código" separado — `POST /api/forgot-password` ya cubre el caso (§Decisión).
- **No** cambia el algoritmo de hashing de `password_hash` (contraseñas de usuario) — sigue siendo `werkzeug.security`/scrypt, sin cambios; lo que sí cambia es que ese mismo algoritmo ahora también protege el código OTP (§Decisión, reutilización deliberada).
- **No** persiste ni expone el código en ningún lugar más allá de la fila hasheada y el correo enviado — nunca en logs, nunca en la respuesta JSON de ningún endpoint, nunca en una URL.

## Opciones consideradas — forma de la autorización temporal tras verificar el código

| Opción | Descripción | Trade-off |
|---|---|---|
| **A — Token opaco de propósito específico, misma fila (elegida)** | Al verificar el código, la misma fila de `password_reset_tokens` gana `reset_authorization_hash`/`_expires_at`; el Frontend recibe el valor crudo una vez, lo reenvía tal cual a `reset-password` | Un token opaco no es interpretable ni reutilizable fuera de este flujo — no es un JWT, no tiene claims, no sirve para autenticar nada más. Reutiliza el mismo mecanismo (`token_generator.generate_raw_token`/`hash_token`) que ya usaba el enlace de `ADR-009`, sin inventar un segundo |
| B — JWT de corta duración con un claim `purpose: "password_reset"` | `flask_jwt_extended` ya está integrado; sería reutilizar la infraestructura existente | Descartada, mismo motivo por el que `ADR-009` ya había descartado usar el JWT normal de login para el token de enlace: un JWT es stateless, no se puede invalidar individualmente tras un solo uso sin una lista de revocación aparte. Además, mezclar "tokens de sesión" con "autorizaciones de un paso muy específico" en el mismo mecanismo aumenta el riesgo de que a futuro alguien reutilice por error un JWT de este tipo en un endpoint que no debería aceptarlo |
| C — Verificar el código sirve por sí solo para cambiar la contraseña (email + code + password en la misma request) | Un solo endpoint, un solo paso | Descartada explícitamente (pedido por la tarea de origen): acoplar la verificación del código con el cambio de contraseña en la misma request significa que un atacante con acceso de red (o el propio código filtrado en un log/proxy) tendría una única request que hace ambas cosas -- separar en dos pasos, con una autorización intermedia de corta duración, reduce esa superficie y dan pie a la validación en dos tiempos que ya usan los flujos tipo Google |

**Elegida: A.**

## Opciones consideradas — hashing del código OTP

| Opción | Descripción | Trade-off |
|---|---|---|
| **A — Hash lento, scrypt (elegida)** | Reutiliza `domain/auth/auth_service.hash_password`/`verify_password` (`werkzeug.security`), el mismo algoritmo que ya protege `users.password_hash` | Un código de 6 dígitos tiene solo `10^6` combinaciones -- un hash rápido no protege nada ante una tabla filtrada (fuerza bruta offline instantánea, millones de hashes por segundo con hardware común). Un hash lento vuelve ese ataque costoso incluso con toda la tabla en mano. Reutilizar el hashing de contraseñas evita introducir un tercer algoritmo de hash a la base de código (ya hay dos: scrypt para contraseñas, SHA-256 para tokens de alta entropía) |
| B — SHA-256, igual que los tokens de enlace/autorización (`token_generator.hash_token`) | Ya está implementado, reutilizado en todo el resto de la app | Descartada explícitamente: SHA-256 está bien para valores con 256 bits de entropía propios (un token de enlace, esta misma autorización temporal), pero un código de solo `10^6` combinaciones bajo SHA-256 se rompe por fuerza bruta offline en milisegundos si la tabla se filtra -- no aporta ninguna protección real frente a ese escenario |

**Elegida: A** -- la autorización temporal (alta entropía) sigue usando SHA-256 (`hash_token`), el código OTP (baja entropía) usa scrypt (`hash_password`). Dos algoritmos para dos amenazas distintas, cada uno ya existente en la base de código, ninguno nuevo.

## Opciones consideradas — condición de carrera en reenvíos simultáneos

| Opción | Descripción | Trade-off |
|---|---|---|
| **A — Índice único parcial + reintento (elegida)** | `UNIQUE (user_id) WHERE used_at IS NULL` a nivel de PostgreSQL; el repositorio invalida+inserta, y ante un `IntegrityError` (dos requests concurrentes chocando) reintenta hasta 3 veces | Misma filosofía que el resto de THERS (`DATABASE_ARCHITECTURE.md` §3, "la base de datos como última línea de defensa", ya aplicada en `ck_follows_no_self_follow`): la garantía real vive en el esquema, no solo en la aplicación. El reintento acotado resuelve el caso legítimo (dos reenvíos casi simultáneos del mismo usuario) sin dejar nunca dos códigos activos a la vez |
| B — Solo lógica de aplicación (invalidar, luego insertar, sin índice) | Más simple de escribir | Descartada: sin una restricción a nivel de motor, dos transacciones concurrentes pueden intercalarse (ambas invalidan lo que ven, ambas insertan) y terminar con dos filas activas simultáneas -- exactamente el escenario que la tarea de origen pidió analizar y evitar |
| C — Lock explícito (`SELECT ... FOR UPDATE`) sobre las filas del usuario antes de invalidar | Evita el reintento, serializa directamente | Descartada por complejidad innecesaria frente al volumen real (un usuario pidiendo su propio reset, no un recurso de alto tráfico) -- el índice único parcial ya da la misma garantía de "nunca dos activos" sin necesitar gestionar locks explícitos ni el riesgo de dejar una transacción bloqueada más tiempo del necesario |

**Elegida: A.**

## Decisión

### Modelo de datos (reemplaza, no duplica, `password_reset_tokens` de `ADR-009`)

Una sola fila cubre las tres etapas del ciclo de vida de una solicitud de recuperación: **creada** (código emitido) → **verificada** (código correcto, autorización emitida) → **usada** (contraseña cambiada). No hay una tabla por etapa.

| Columna | Tipo | Nulo | Justificación |
|---|---|---|---|
| `id` | `UUID`, `DEFAULT gen_random_uuid()` | No (PK) | Mismo patrón que el resto de entidades |
| `user_id` | `UUID`, FK → `users.id`, `ON DELETE CASCADE` | No | Dueño de la solicitud |
| `code_hash` | `TEXT` | No | Hash **scrypt** del código de 6 dígitos (`domain/auth/auth_service.hash_password`) — nunca el valor crudo. `TEXT`, no `VARCHAR(64)`: el formato de salida de scrypt no tiene una longitud fija corta |
| `attempts` | `INTEGER`, `DEFAULT 0` | No | Intentos de verificación fallidos contra esta solicitud (§Seguridad) |
| `expires_at` | `TIMESTAMPTZ` | No | Vigencia del código en sí — 10 minutos desde su creación (`domain/auth/token_policy.PASSWORD_RESET_CODE_TTL_MINUTES`) |
| `verified_at` | `TIMESTAMPTZ` | **Sí** | `NULL` = código todavía no verificado correctamente. Se fija una sola vez, junto con la autorización |
| `reset_authorization_hash` | `VARCHAR(64)` | **Sí** | SHA-256 (`domain/auth/token_generator.hash_token`) de la autorización temporal emitida al verificar — `NULL` hasta ese momento |
| `reset_authorization_expires_at` | `TIMESTAMPTZ` | **Sí** | Vigencia de la autorización — 10 minutos desde la verificación (`PASSWORD_RESET_AUTHORIZATION_TTL_MINUTES`) |
| `used_at` | `TIMESTAMPTZ` | **Sí** | `NULL` = la contraseña todavía no se cambió con esta solicitud. Se fija una sola vez, al completar `POST /api/reset-password` |
| `created_at` | `TIMESTAMPTZ`, `DEFAULT now()` | No | Sostiene el cooldown anti-spam |

**Sin `updated_at`.** Mismo criterio que `likes`/`follows`/`notifications`: se crea y se marca en cada etapa, nunca se "edita" en el sentido de un `PATCH`.

**Constraints:**
- `ix_password_reset_tokens_user_id_created_at` (`user_id`, `created_at`) — cooldown de `forgot-password`.
- `ix_password_reset_tokens_reset_authorization_hash` — lookup de `reset-password` por la autorización (SHA-256, alta entropía, lookup directo por hash sigue siendo válido).
- **`uq_password_reset_tokens_active_user`** — índice único **parcial**: `UNIQUE (user_id) WHERE used_at IS NULL`. Primer índice parcial del esquema de THERS. Garantiza a nivel de motor que nunca hay más de una solicitud activa por usuario — la defensa real contra la condición de carrera de reenvíos simultáneos (§Opciones consideradas).

El código OTP en sí **nunca tiene su propio índice de búsqueda por hash** — a diferencia del token de enlace anterior (`SELECT ... WHERE token_hash = ?`), verificar un código hasheado con scrypt (salado por diseño) exige primero resolver la fila candidata por otra vía (`user_id`, vía `email`) y recién ahí comparar con `check_password_hash` — no se puede buscar directamente por el hash del código.

### Contrato API (documentado el mismo día en `API_CONTRACT.md`, `HB-001` §15.1)

Reemplaza el contrato de `forgot-password`/`reset-password` de `ADR-009`, agrega `verify-reset-code`. Ver `API_CONTRACT.md` §4.8 para el detalle completo request/response/errores de los tres endpoints.

- **`POST /api/forgot-password`** (público) — ya no genera un enlace, genera un código de 6 dígitos. Mismo mensaje genérico de siempre, mismo cooldown. También es el endpoint de "Reenviar código".
- **`POST /api/verify-reset-code`** (público, nuevo) — `{email, code}` → `{msg, reset_authorization}` en éxito. Mismo mensaje/código `400` sin importar cuál de los casos de rechazo ocurrió (email inexistente, sin solicitud activa, código expirado, intentos agotados, código incorrecto).
- **`POST /api/reset-password`** (público) — cambia de `{token, password, confirm_password}` a `{reset_authorization, password, confirm_password}`. Mismo comportamiento de aplicación de contraseña, hashing e invalidación que antes.

### Seguridad (§Fase 14 de la tarea)

- **Generación:** `secrets.choice` dígito por dígito (CSPRNG, no `random`) — `domain/auth/token_generator.generate_otp_code()`.
- **Expiración corta:** 10 minutos (código), 10 minutos (autorización tras verificar).
- **Hashing:** scrypt para el código (§Opciones consideradas), SHA-256 para la autorización (alta entropía).
- **Máximo de intentos:** 5 (`PASSWORD_RESET_MAX_ATTEMPTS`) — `5/1.000.000` (0.0005%) de probabilidad de acierto por fuerza bruta en toda la vida útil de un código. Agotar los intentos bloquea la solicitud (no borra la fila, no revela nada distinto en la respuesta).
- **Rate limiting / cooldown de reenvío:** 60s (`PASSWORD_RESET_REQUEST_COOLDOWN_SECONDS`, reutilizado de `ADR-009`), impuesto en el backend — una request directa por Postman que ignore el contador del Frontend recibe el mismo cooldown.
- **Invalidación de códigos anteriores:** a lo sumo un código activo por usuario (`uq_password_reset_tokens_active_user`), reforzado con reintento ante condición de carrera (§Opciones consideradas).
- **Autorización temporal de propósito específico:** nunca el JWT normal de sesión (§Opciones consideradas).
- **Un solo uso:** el código se consume al verificarse (no se puede volver a intentar la misma solicitud tras acierto), la autorización se consume al cambiar la contraseña.
- **Sin códigos en logs:** `NullEmailSender` (desarrollo sin `RESEND_API_KEY`, `ADR-009`) nunca imprime el cuerpo del correo, solo destinatario y asunto — el código nunca aparece en `stderr`.
- **Sin códigos en la respuesta JSON:** ningún endpoint devuelve el código, ni siquiera en un campo de depuración.
- **Sin códigos en URLs:** a diferencia del enlace anterior, el código se introduce a mano en un formulario — nunca viaja como query param.
- **Anti-enumeración:** heredada de `ADR-009`, extendida a `verify-reset-code` (§Decisión, InvalidResetCodeError unificado).

## Impacto en Backend

- `domain/auth/token_generator.py`: nueva `generate_otp_code()`.
- `domain/auth/token_policy.py`: `PASSWORD_RESET_TOKEN_TTL_MINUTES` (30) reemplazada por `PASSWORD_RESET_CODE_TTL_MINUTES` (10); nuevas `PASSWORD_RESET_MAX_ATTEMPTS` (5), `PASSWORD_RESET_AUTHORIZATION_TTL_MINUTES` (10). `PASSWORD_RESET_REQUEST_COOLDOWN_SECONDS` sin cambios.
- `domain/auth/password_reset_repository.py`: puerto reescrito (`create_code`, `find_active_by_user_id`, `increment_attempts`, `mark_verified`, `find_valid_by_reset_authorization_hash`, `mark_used`, `has_recent_unused_code`).
- `domain/auth/exceptions.py`: nueva `InvalidResetCodeError`; `InvalidOrExpiredResetTokenError` se reutiliza para la autorización (mismo nombre, nuevo significado: ya no es "el token del enlace", es "la autorización").
- `application/auth/forgot_password_use_case.py`: reescrito, genera código en vez de enlace.
- `application/auth/verify_reset_code_use_case.py` (nuevo).
- `application/auth/reset_password_use_case.py`: reescrito, consume la autorización.
- `application/email/templates.py`: `password_reset_email` (enlace) reemplazada por `password_reset_code_email` (código con buena visibilidad, `_code_box` con `letter-spacing`). `password_changed_email`/`email_verification_email` sin cambios.
- `application/email/email_service.py`: `send_password_reset_email` renombrado a `send_password_reset_code_email`.
- `infrastructure/persistence/models.py`: `PasswordResetToken` reescrito.
- `infrastructure/persistence/repositories/password_reset_repository.py`: adaptador reescrito, con el reintento ante `IntegrityError` del índice único parcial.
- `interfaces/routes/auth_routes.py`: `forgot_password_route` simplificada (ya no arma un enlace); nueva `verify_reset_code_route`; `reset_password_route` adaptada a `reset_authorization`.
- Nueva migración `f4b8c92a1d67`, que recrea `password_reset_tokens` (downgrade restaura la forma de `ADR-009`).
- Tests: `test_password_reset.py` reescrito (31 pruebas) — el código/autorización se inserta directamente con las mismas funciones de dominio que el código real usa, ya que ninguno de los dos lo devuelve la API.

## Impacto en Frontend

- `ForgotPassword.jsx`: **conectada por primera vez** (quedaba fuera de alcance en `ADR-009`) — llama a `POST /api/forgot-password` real y navega a `/verify-reset-code` con el email por router state.
- `VerifyResetCode.jsx` (nueva): pantalla de 6 casillas, cooldown de reenvío (60s, countdown visual), llama a `POST /api/verify-reset-code` y, en éxito, navega a `/reset-password` con la autorización por router state.
- `OtpCodeInput.jsx` (nuevo, `features/auth/components/`): input reutilizable de 6 casillas — solo dígitos, avance automático, Backspace, pegado de los 6 dígitos completos, envío con Enter (nativo del `<form>`), `autoComplete="one-time-code"` para autocompletado de SMS/email en navegadores compatibles.
- `maskEmail.js` (nuevo, `features/auth/lib/`): enmascara la parte local del email para mostrarlo en pantalla (`d*****@gmail.com`).
- `ResetPassword.jsx`: deja de leer `?token=` de la URL, lee `resetAuthorization` de router state; el body de `reset-password` cambia de `token` a `reset_authorization`.
- `app/router/router.jsx`: nueva ruta `/verify-reset-code`.
- `features/auth/index.js`: exporta `VerifyResetCode`.
- i18n (es/en): namespace `verifyResetCode` nuevo; `forgotPassword`/`resetPassword` actualizados (se quitan las claves `inProgress*` huérfanas, textos ajustados de "enlace" a "código"/"autorización").

## Riesgos

- **Scrypt es más costoso que SHA-256 en cada verificación** — aceptable: el volumen de `verify-reset-code` es bajo (un usuario recuperando su propia cuenta), y es exactamente el mismo costo que ya paga cada `POST /api/login`.
- **Autocompletado de OTP por SMS no aplica** (THERS no envía SMS, solo email) — `autoComplete="one-time-code"` igual ayuda en clientes de correo con integración nativa (algunos Mail apps de iOS/Android).
- **Sin rate limiting de infraestructura (por IP)** — el cooldown por usuario ya cubre el caso principal (spam de correos hacia una cuenta); un atacante con muchas cuentas de prueba podría, en teoría, generar volumen de envío repartido — mismo hueco que ya existía en `ADR-009`, sin agravarse acá. Recomendado como próximo paso (ver informe de esta tarea).
- **Downgrade de la migración pierde datos** — mismo criterio que toda migración de esta app que recrea una tabla: aceptable porque no hay datos de producción reales todavía.

## Decisiones pendientes (quedan fuera, cada una es su propio ADR futuro)

- Rate limiting de infraestructura (por IP/dispositivo) para todos los endpoints públicos sensibles, no solo este.
- Notificar por correo un intento de recuperación con demasiados códigos fallidos consecutivos (señal de posible ataque dirigido a una cuenta).
- Extender el patrón de "autorización temporal de propósito específico" a otros flujos sensibles futuros, si aparecen.

## Consecuencias

- `password_reset_tokens` sigue siendo la misma entidad (ratificada originalmente por `ADR-009`), ahora con un modelo distinto — no se crea una entidad nueva, se reemplaza la definición de una existente.
- La recuperación de contraseña de THERS queda con una experiencia de usuario familiar (código de 6 dígitos) y con dos capas de defensa contra el hecho de que un código corto tiene poca entropía (hashing lento + límite de intentos), en vez de depender solo de la expiración.
- `DATABASE_ARCHITECTURE.md`, `DATABASE_ERD.md` y `API_CONTRACT.md` se actualizan el mismo día que este contrato se implementa (`HB-001` §15.1).

## Referencias

- `CLAUDE.md` — jerarquía de fuentes (§4), regla de alcance (§14), reglas específicas para Claude Code (§8).
- `docs/architecture/ADR-009-password-reset-and-email-verification.md` — decisión que este ADR reemplaza parcialmente (recuperación de contraseña); sigue vigente para verificación de email y el servicio de correo centralizado.
- `docs/architecture/DATABASE_ARCHITECTURE.md` §3 (principios de diseño, "la base de datos como última línea de defensa"), §5.7 (definición anterior de `password_reset_tokens`).
- `docs/architecture/organization/01_Manual_Organizacion/Source/HB-001-manual-organizacion.md.md` §11 (clasificación de impacto de decisiones), §15.1 (documentar endpoints el mismo día del PR), §19.1 (nunca loguear secretos).

---

## Cierre
