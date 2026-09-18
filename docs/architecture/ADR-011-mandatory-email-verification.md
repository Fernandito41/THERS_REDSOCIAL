# ADR-011 — Verificación obligatoria de email al registrarse (OTP)

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/ADR-011-mandatory-email-verification.md` |
| Tipo | Architecture Decision Record (`HB-001` §11–12) |
| Fecha | 14/09/2026 |
| Estado | **Aceptada** — implementada en esta tarea, reemplaza `ADR-009-password-reset-and-email-verification.md` en la parte de verificación de email (ver §Decisión) |
| Alcance | `backend/` — se reemplaza `email_verification_tokens` y sus dos endpoints; `Frontend/` — se adapta `Register.jsx`, se agrega `VerifyRegistrationCode.jsx`, se adapta `Login.jsx`. La recuperación de contraseña (`password_reset_tokens`, `forgot-password`/`verify-reset-code`/`reset-password`, `ADR-010`) **no se toca**, es una entidad y un flujo distintos |
| Autoridad sobre este documento | `/docs` oficial > estructura real observada en el código > este documento (mismo orden que `CLAUDE.md` §4) |

> ⚠️ **Relación con ADR-009 y ADR-010.** Este ADR **reemplaza** la parte de verificación de email de `ADR-009-password-reset-and-email-verification.md` (enlace con token en la URL, verificación opcional tras el registro) por un código OTP de 6 dígitos **obligatorio antes de poder iniciar sesión** — mismo rediseño que `ADR-010` ya le aplicó a la recuperación de contraseña, aplicado ahora a la verificación de registro. `ADR-009` sigue vigente sin cambios para todo lo demás (el servicio de correo centralizado, los principios de seguridad generales); `ADR-010` sigue vigente sin cambios — ninguna de sus decisiones sobre `password_reset_tokens` se toca acá.

---

## Contexto

THERS ya tenía la columna `users.email_verified` (`ADR-009`) y un flujo para verificarla: un usuario que ya inició sesión podía pedir un correo con un enlace, hacer clic, y quedar verificado — pero nada exigía completar ese paso. Una cuenta sin verificar podía usar la red social exactamente igual que una verificada. El equipo pidió que THERS exija la verificación **antes** de poder usar la cuenta, con un código de 6 dígitos en vez de un enlace (mismo patrón ya adoptado por `ADR-010` para recuperación de contraseña), sin depender de heurísticas de DNS/SMTP para "confirmar" que un email existe — la única prueba válida es que la persona demuestre control real del correo introduciendo el código que THERS envió.

## Problema

Rediseñar el registro para que una cuenta nueva no pueda iniciar sesión hasta verificar su email por código OTP, sin:
- bloquear para siempre un email/username por un registro que nunca se completó (abandonar el formulario de verificación no debe dejar esa dirección inutilizable);
- crear dos formas de obtener una sesión (la normal y un atajo que saltee la verificación);
- mezclar el propósito de este código con el de recuperación de contraseña (`ADR-010`) de forma que uno pudiera usarse para lo del otro;
- duplicar la infraestructura de generación/hash/envío/rate-limiting de OTP que `ADR-010` ya construyó.

## Objetivos

- `POST /api/register` sigue creando la cuenta y devolviendo `201`, pero `email_verified` nace en `false` y de inmediato se envía un código de 6 dígitos — la cuenta queda en un estado "pendiente de verificar", no "inexistente" ni "completamente activa".
- Nuevo `POST /api/verify-registration-code`: verifica el código y, si es correcto, marca `email_verified = true` directamente — a diferencia de la recuperación de contraseña, no hay una acción sensible posterior que proteger con una autorización intermedia.
- Nuevo `POST /api/resend-registration-code`: "Reenviar código", mismo criterio que `forgot-password` (cooldown de 60s impuesto también en el backend).
- `POST /api/login` rechaza con `403` (nunca `401`) a una cuenta con credenciales correctas pero sin verificar, y **nunca** emite un JWT en ese caso.
- Reintentar el registro con un email que existe pero nunca se verificó actualiza esa misma cuenta (incluida la contraseña) y reenvía un código, en vez de bloquear el email para siempre o crear una fila duplicada.
- El código de registro y el de recuperación de contraseña quedan separados por estructura (tablas/repositorios propios), no solo por convención — uno nunca puede verificar el propósito del otro.
- Reutilizar, sin duplicar, la infraestructura de OTP que `ADR-010` ya construyó: generador de códigos, hashing scrypt, patrón de índice único parcial + reintento, `EmailService`/`EmailSender`.
- El Frontend queda conectado de punta a punta en la misma tarea: nueva pantalla `VerifyRegistrationCode.jsx` (reutiliza `OtpCodeInput`/`maskEmail`/`AuthCard` de `ADR-010`, sin duplicar ninguno de los tres), `Register.jsx` navega a ella en vez de a `/login`, `Login.jsx` distingue el `403` de cuenta sin verificar y redirige al mismo lugar.

## No objetivos (explícitamente fuera de este ADR)

- **No** toca la recuperación de contraseña (`password_reset_tokens`, `forgot-password`/`verify-reset-code`/`reset-password`) — sigue exactamente como `ADR-010` la dejó, es una entidad y un flujo completamente separados.
- **No** implementa verificación de dominio/MX — el formato de `email` se sigue validando con la regex existente (`domain/auth/validators.is_valid_email`), pero la prueba definitiva de que la cuenta controla el correo sigue siendo, siempre, el código OTP. Un email con formato y dominio perfectamente válidos (`alguien928372@gmail.com`, inventado) se trata exactamente igual que cualquier otro hasta que se verifica — nunca se asume control del correo por tener buena forma o un dominio conocido.
- **No** implementa rate limiting a nivel de infraestructura (por IP) — mismo criterio y mismo hueco ya documentado por `ADR-010` §Riesgos, sin agravarse acá.
- **No** crea una tabla de "registros pendientes" separada de `users` — ver §Opciones consideradas, Estrategia A vs. B.
- **No** cambia el algoritmo de hashing de contraseñas ni introduce un tercer algoritmo de hash — reutiliza scrypt (código) y la infraestructura de `ADR-010` tal cual.
- **No** persiste ni expone el código en ningún lugar más allá de la fila hasheada y el correo enviado — nunca en logs, nunca en la respuesta JSON de ningún endpoint.

## Opciones consideradas — cómo representar una cuenta "pendiente de verificar"

| Opción | Descripción | Trade-off |
|---|---|---|
| **A — Usuario pendiente vía `email_verified` (elegida)** | `POST /api/register` crea la fila en `users` de inmediato, con `email_verified = false` — la misma tabla, el mismo flag que `ADR-009` ya había dejado sin usar para gatear nada | `users.email_verified` ya existía, sentado sin cumplir ningún propósito real desde `ADR-009` — usarlo para esto es la reutilización más directa posible, cero esquema nuevo en `users`. Las constraints `UNIQUE` de `email`/`username` que ya protegen contra duplicados en `users` siguen protegiendo exactamente igual — no hay que reimplementar esa garantía en una segunda tabla. El riesgo real de esta opción (un registro abandonado "ocupa" el email para siempre) se resuelve con la semántica de reintento (§Decisión), no con una tabla paralela |
| B — Tabla `pending_registrations` separada, `users` solo se crea al verificar | Ningún dato "provisional" vive en `users` — una fila en `users` significa siempre "cuenta real, con email verificado o no, pero que ya completó el registro" | Descartada: reimplementa desde cero la unicidad de `email`/`username` que `users` ya garantiza (¿puede haber dos `pending_registrations` con el mismo email? ¿y si una ya es un `user` verificado? la lógica de "¿quién gana?" se vuelve una segunda fuente de verdad a mantener sincronizada con `users`). Además, todo el resto de THERS (posts, likes, comments, follows, notifications) referencia `users.id` con FKs — si la cuenta se crea recién al verificar, hay que decidir qué pasa con cualquier intento de usarla antes de eso, un problema que la Estrategia A no tiene porque la fila ya existe desde el registro. Mismo motivo por el que `ADR-010` prefirió una fila con etapas (creada→verificada→usada) sobre tres tablas separadas por etapa |

**Elegida: A.** `CLAUDE.md` §12/§6 pide explícitamente "no hacer cambios innecesariamente grandes" — la Estrategia A resuelve el problema completo reutilizando una columna que ya existía, sin tocar el modelo de `users` ni introducir una segunda fuente de verdad para unicidad de email/username.

### Cómo la Estrategia A evita que un registro abandonado bloquee un email para siempre

`register_use_case.py` distingue dos casos al recibir un email que ya existe en `users`:
- **Si la cuenta existente ya está verificada:** `409` real (`EmailAlreadyExistsError`) — comportamiento sin cambios respecto a antes de este ADR.
- **Si la cuenta existente nunca se verificó:** se trata como un reintento legítimo de la misma persona — se actualiza esa fila (`name`, `username`, `phone`, `country_code`, `birth_date`, `password_hash` nuevos) y se reenvía un código, en vez de bloquear con `409` o crear una segunda fila. Esto es lo que impide que alguien que abandonó el formulario de verificación (o que se equivocó de contraseña al registrarse) deje esa dirección de correo inutilizable permanentemente.

`username` sigue protegido por su propia `UNIQUE` — si el reintento pide un `username` que ahora pertenece a otra cuenta, `UsernameAlreadyExistsError` (`409`) se sigue lanzando igual que en un registro nuevo.

## Opciones consideradas — forma de la verificación (autorización intermedia vs. acción directa)

| Opción | Descripción | Trade-off |
|---|---|---|
| **A — El propio acierto del código marca `email_verified = true` (elegida)** | `POST /api/verify-registration-code` no emite nada más que un mensaje de éxito — no hay una "autorización temporal" que una request posterior deba consumir | Verificar el email no es, en sí misma, una acción sensible que alguien pueda explotar si el paso de verificación y el paso de "uso" quedaran separados — a diferencia de recuperar una contraseña (`ADR-010`), donde separar verificación de la acción final reduce una superficie de ataque real. Acá esa separación solo agregaría un endpoint y un estado intermedio sin ganar ninguna protección nueva |
| B — Mismo patrón de autorización temporal que `ADR-010` (verificar código → token opaco → un segundo endpoint "confirma" la verificación) | Consistencia mecánica total con el flujo de recuperación de contraseña | Descartada: no hay una "acción final" distinta de marcar el flag — forzar una autorización intermedia para un efecto que ya es inocuo (poner `email_verified = true`) agrega ceremonia sin beneficio de seguridad real, y complica innecesariamente el Frontend con un paso extra que no protege nada |

**Elegida: A.**

## Opciones consideradas — separación de propósito entre OTP de registro y OTP de recuperación

| Opción | Descripción | Trade-off |
|---|---|---|
| **A — Tablas y repositorios separados, sin discriminador de tipo compartido (elegida)** | `email_verification_tokens` y `password_reset_tokens` siguen siendo dos tablas distintas, cada una con su propio repositorio/caso de uso/excepción — exactamente como ya estaban desde `ADR-009` | Hace la separación de propósito una garantía **estructural**, no solo de política: un código insertado en `email_verification_tokens` no es una fila que `verify_reset_code_use_case.py` pueda consultar ni por accidente, porque ese caso de uso nunca hace `SELECT` sobre esa tabla — no existe el escenario "alguien reutiliza por error un código de un flujo en el otro", porque estructuralmente no hay una ruta de código que cruce ambas tablas |
| B — Una tabla `otp_codes` genérica con una columna `purpose` (`"registration"` / `"password_reset"`) | Menos tablas, un solo repositorio genérico para ambos flujos | Descartada explícitamente por el mismo motivo que `ADR-010` ya había descartado mezclar conceptos de vidas distintas: `email_verification_tokens` y `password_reset_tokens` tienen políticas que ya difieren hoy (la primera no tiene autorización temporal, la segunda sí) y podrían divergir más en el futuro (TTL, máximo de intentos) — un discriminador de tipo sobre una tabla compartida exigiría que cada query filtre siempre por `purpose`, dejando la separación de propósito dependiendo de que nadie olvide ese filtro, en vez de ser imposible de cruzar por diseño. Distinto del caso de `notifications` (`ADR-008`), donde los tres tipos (`like`/`comment`/`follow`) sí son comportamentalmente idénticos y comparten tabla con un discriminador — acá no lo son |

**Elegida: A** — mismos generadores (`generate_otp_code`), mismo hashing (`hash_password`/`verify_password`), mismo patrón de índice único parcial + reintento, reutilizados por ambos repositorios sin duplicar esa lógica; lo único que no se comparte es la tabla en sí, que es exactamente lo que debía quedar separado.

## Decisión

### Modelo de datos (reconstruye, no duplica, `email_verification_tokens` de `ADR-009`)

Mismo patrón exacto que `ADR-010` le aplicó a `password_reset_tokens`, sin las columnas de autorización temporal (no hacen falta, ver §Opciones consideradas de arriba):

| Columna | Tipo | Nulo | Justificación |
|---|---|---|---|
| `id` | `UUID`, `DEFAULT gen_random_uuid()` | No (PK) | Mismo patrón que el resto de entidades |
| `user_id` | `UUID`, FK → `users.id`, `ON DELETE CASCADE` | No | Dueño del código |
| `code_hash` | `TEXT` | No | Hash **scrypt** del código de 6 dígitos (`domain/auth/auth_service.hash_password`) — nunca el valor crudo, nunca SHA-256 (baja entropía, mismo motivo que `ADR-010` §Opciones consideradas) |
| `attempts` | `INTEGER`, `DEFAULT 0` | No | Intentos de verificación fallidos contra este código |
| `expires_at` | `TIMESTAMPTZ` | No | Vigencia del código — 10 minutos desde su creación (`domain/auth/token_policy.REGISTRATION_CODE_TTL_MINUTES`) |
| `used_at` | `TIMESTAMPTZ` | **Sí** | `NULL` = el código todavía no se verificó correctamente. Se fija una sola vez, al verificarse |
| `created_at` | `TIMESTAMPTZ`, `DEFAULT now()` | No | Sostiene el cooldown anti-spam de `POST /api/register`/`POST /api/resend-registration-code` |

**Sin `updated_at`.** Mismo criterio que `password_reset_tokens`.

**Constraints:**
- `ix_email_verification_tokens_user_id_created_at` (`user_id`, `created_at`) — sin cambios, ya existía desde `ADR-009`, sigue sosteniendo el cooldown.
- **`uq_email_verification_tokens_active_user`** — índice único **parcial**: `UNIQUE (user_id) WHERE used_at IS NULL`. Mismo patrón exacto que `uq_password_reset_tokens_active_user` (`ADR-010`) — garantiza a nivel de motor que nunca hay más de un código activo por usuario, incluso ante dos "Reenviar código" simultáneos o un reintento de registro concurrente con el mismo email. Reemplaza a `uq_email_verification_tokens_token_hash` (v0.13), que dejó de tener sentido al perderse `token_hash`.

### Contrato API (documentado el mismo día en `API_CONTRACT.md`, `HB-001` §15.1)

Ver `API_CONTRACT.md` §4.1 (cambios en `register`/`login`) y §4.8 (nuevos endpoints) para el detalle completo request/response/errores.

- **`POST /api/register`** — sin cambios de forma en el contrato (mismo body, mismo `201`), pero la cuenta nace sin verificar y con un código ya enviado; reintentar con un email existente-pero-no-verificado actualiza esa cuenta en vez de `409`.
- **`POST /api/login`** — gana un caso `403` (`{"msg": "...", "email_verified": false}`) para credenciales correctas sobre una cuenta sin verificar. El chequeo de `email_verified` ocurre **después** de validar la contraseña (nunca antes) — si la contraseña es incorrecta, sigue siendo `401` sin importar el estado de verificación, para no abrir un canal lateral nuevo que revelara "esta cuenta existe y está pendiente" antes de probar la contraseña.
- **`POST /api/verify-registration-code`** (público, nuevo) — `{email, code}` → `{msg, email_verified: true}` en éxito. Mismo mensaje/código `400` sin importar cuál de los casos de rechazo ocurrió (email inexistente, cuenta ya verificada, sin código activo, expirado, intentos agotados, código incorrecto).
- **`POST /api/resend-registration-code`** (público, nuevo) — `{email}` → mismo mensaje genérico `200` siempre, exista o no la cuenta, esté o no verificada, esté o no en cooldown.
- **Retirados:** `POST /api/send-verification-email` (protegido) y `POST /api/verify-email` (público) — ver razón en la nota de abajo.

> ⚠️ **Por qué se retiran, no se deprecan.** Con `POST /api/login` ya bloqueado para cuentas sin verificar, una cuenta sin verificar nunca puede obtener el JWT que `POST /api/send-verification-email` exigía (`@jwt_required()`) — el par queda permanentemente inalcanzable en la práctica: no hay ningún camino real para llegar a necesitarlo. Mantenerlos "por si acaso" sería exactamente el "mecanismo redundante sin justificación" que `ADR-010` ya identificó como antipatrón al retirar el flujo de enlace de recuperación de contraseña.

### Seguridad

- **Generación:** `secrets.choice` dígito por dígito (CSPRNG) — `domain/auth/token_generator.generate_otp_code()`, reutilizado tal cual de `ADR-010`.
- **Expiración corta:** 10 minutos (`REGISTRATION_CODE_TTL_MINUTES`).
- **Hashing:** scrypt (`hash_password`/`verify_password`, reutilizado tal cual de `ADR-010`) — nunca SHA-256 para el código.
- **Máximo de intentos:** 5 (`REGISTRATION_MAX_ATTEMPTS`) — mismo análisis de probabilidad que `ADR-010` §Seguridad (`5/1.000.000`, 0.0005% en toda la vida útil de un código). Agotar los intentos bloquea el código sin borrarlo ni revelar nada distinto en la respuesta.
- **Rate limiting / cooldown de reenvío:** 60 segundos (`REGISTRATION_CODE_REQUEST_COOLDOWN_SECONDS`), impuesto en el backend — una request directa por Postman que ignore el contador del Frontend recibe el mismo cooldown sin generar un código ni un correo nuevo.
- **Invalidación de códigos anteriores:** a lo sumo un código activo por usuario (`uq_email_verification_tokens_active_user`), reforzado con reintento ante condición de carrera (hasta 3 intentos ante `IntegrityError`, mismo patrón que `ADR-010`).
- **Un solo uso:** el código se consume al verificarse correctamente.
- **Separación de propósito:** estructural, no solo de política (§Opciones consideradas) — un código de `email_verification_tokens` nunca es una fila que `verify_reset_code_use_case.py` pueda leer, y viceversa.
- **Sin JWT mientras la cuenta no esté verificada:** `login_use_case.py` nunca llega a `create_access_token()` si `email_verified` es `false` — no existe ningún camino alternativo (otro endpoint, otro parámetro) que emita un token de sesión normal para una cuenta sin verificar.
- **Sin códigos en logs:** `NullEmailSender` (desarrollo sin `RESEND_API_KEY`) nunca imprime el cuerpo del correo, solo destinatario y asunto.
- **Sin códigos en la respuesta JSON:** ningún endpoint devuelve el código, ni siquiera en un campo de depuración.
- **Anti-enumeración:** `InvalidRegistrationCodeError` unifica el mensaje de `verify-registration-code` sin importar la causa real del rechazo; `resend-registration-code` siempre responde el mismo mensaje genérico, exista o no la cuenta.
- **Dominio/MX no verificado — decisión deliberada, no un hueco:** el formato de `email` se valida (`is_valid_email`), pero nunca se trata un dominio/formato válido como prueba de control del correo — esa prueba es, siempre, el código OTP correctamente verificado. Se evaluó agregar una verificación de registro MX (`dnspython`, no instalado hoy) y se descartó para esta tarea: agrega una dependencia nueva y una llamada de red durante el registro (latencia, posible fallo) sin aportar ninguna garantía que el OTP no dé ya de forma definitiva — el propio enunciado de la tarea de origen establece el OTP como la prueba obligatoria independientemente de cualquier validación de dominio.
- **Resend fallando durante el registro:** `EmailService` no atrapa excepciones de envío a propósito (mismo criterio que `ADR-009`/`ADR-010`) — si Resend falla, la excepción se propaga a un `500` genérico, pero `users` y el código ya se persistieron antes de intentar el envío (ambos en transacciones propias, ya confirmadas). El sistema queda en un estado recoverable: la cuenta existe, sin verificar, y la persona puede pedir un código nuevo más tarde vía `resend-registration-code` sin que el registro haya quedado a medias ni el email bloqueado. Verificado con una prueba que fuerza el fallo de envío y confirma el estado persistido (`TestResendFailureLeavesRecoverableState`, `tests/test_registration.py`) y, en esta misma tarea, reproducido contra Resend real (un dominio de prueba que el proveedor rechaza) sin dejar ningún estado inconsistente.

## Impacto en Backend

- `domain/auth/token_policy.py`: se retiran `EMAIL_VERIFICATION_TOKEN_TTL_HOURS`/`EMAIL_VERIFICATION_REQUEST_COOLDOWN_SECONDS`; nuevas `REGISTRATION_CODE_TTL_MINUTES` (10), `REGISTRATION_MAX_ATTEMPTS` (5), `REGISTRATION_CODE_REQUEST_COOLDOWN_SECONDS` (60).
- `domain/auth/email_verification_repository.py`: puerto reescrito (`create_code`, `find_active_by_user_id`, `increment_attempts`, `mark_used`, `has_recent_unused_code`) — mismas firmas que el puerto de `password_reset_repository.py`, minus las de autorización temporal.
- `domain/auth/exceptions.py`: se retira `InvalidOrExpiredVerificationTokenError`; nuevas `InvalidRegistrationCodeError`, `EmailNotVerifiedError`.
- `application/auth/send_registration_code_use_case.py` (nuevo): helper interno compartido por `register_use_case.py` y `resend_registration_code_use_case.py` — genera, hashea, persiste y envía el código, sin duplicar esa secuencia entre ambos.
- `application/auth/register_use_case.py`: reescrito — Estrategia A (actualiza la cuenta existente si nunca se verificó, crea una nueva en caso contrario), siempre termina enviando un código.
- `application/auth/resend_registration_code_use_case.py` (nuevo).
- `application/auth/verify_registration_code_use_case.py` (nuevo).
- `application/auth/login_use_case.py`: gana el chequeo de `email_verified`, después de validar la contraseña.
- `application/email/templates.py`: `email_verification_email` (enlace) reemplazada por `registration_code_email` (código, mismo diseño visual que `password_reset_code_email`).
- `application/email/email_service.py`: `send_registration_code_email` nuevo, reemplaza a `send_verification_email`.
- `infrastructure/persistence/models.py`: `EmailVerificationToken` reescrito.
- `infrastructure/persistence/repositories/email_verification_repository.py`: adaptador reescrito, mismo patrón de reintento ante `IntegrityError` que `password_reset_repository.py`.
- `interfaces/routes/auth_routes.py`: `register_route` pasa el repositorio de verificación y el `EmailService` al caso de uso; `login_route` gana el branch `403`; nuevas `verify_registration_code_route`/`resend_registration_code_route`.
- `interfaces/routes/user_routes.py`: se retira `send_verification_email_route` y sus imports/instancias ya muertas.
- Nueva migración `a7d3f6c1e8b9`, que recrea `email_verification_tokens` (downgrade restaura la forma de `ADR-009`).
- Eliminados: `application/auth/send_verification_email_use_case.py`, `application/auth/verify_email_use_case.py`.
- Tests: `tests/test_registration.py` (nuevo, 36 pruebas) reemplaza a `tests/test_email_verification.py` (retirado, probaba el flujo de enlace ya eliminado); `tests/conftest.py` gana `mark_email_verified(user_id)` (verifica directamente en la base, sin pasar por el flujo OTP real) para que el resto de la suite (posts, likes, comments, follows, notifications, password reset, etc.) siga probando sus propios flujos sin depender de resolver un código real; todos los archivos con un helper local `_register_and_login` se actualizaron para llamarla entre el registro y el login.

## Impacto en Frontend

- `Register.jsx`: en éxito, navega a `/verify-registration-code` con el email por router state, en vez de a `/login`.
- `VerifyRegistrationCode.jsx` (nueva): mismo patrón que `VerifyResetCode.jsx` (`ADR-010`) — reutiliza `OtpCodeInput`/`maskEmail`/`AuthCard` tal cual, sin duplicar ninguno. Llama a `POST /api/verify-registration-code` y, para "Reenviar código", a `POST /api/resend-registration-code`; en éxito navega a `/login`.
- `Login.jsx`: su `catch` distingue `error.response?.status === 403 && data.email_verified === false` — en ese caso, en vez del toast de error genérico, avisa y navega a `/verify-registration-code` con el email, igual que si acabara de registrarse.
- `shared/lib/api.js`: `getErrorMessage` gana un branch `403` genérico (para cualquier otro `403` que no sea el caso especial que `Login.jsx` ya maneja por su cuenta).
- `app/router/router.jsx`: nueva ruta `/verify-registration-code`.
- `features/auth/index.js`: exporta `VerifyRegistrationCode`.
- i18n (es/en): namespace `verifyRegistrationCode` nuevo (mismas claves que `verifyResetCode`, más `verifySuccess`/`backToRegister`); `login.emailNotVerified` nuevo.

## Riesgos

- **Una cuenta sin verificar nunca se borra automáticamente** — queda acumulándose en `users` si la persona nunca vuelve a verificarla. Mismo criterio de riesgo aceptado que `ADR-009`/`ADR-010` ya asumían para tokens vencidos: limpieza periódica queda como recomendación futura (§Decisiones pendientes), no bloqueante para esta tarea.
- **Sin rate limiting de infraestructura (por IP)** — mismo hueco ya heredado de `ADR-009`/`ADR-010`, sin agravarse acá.
- **Downgrade de la migración pierde datos** — mismo criterio que toda migración de esta app que recrea una tabla: aceptable porque no hay datos de producción reales todavía.
- **Retirar `send-verification-email`/`verify-email` es un cambio de contrato público** — mitigado: ambos quedaban inalcanzables en la práctica apenas `login` se gatea (§Decisión), así que ningún cliente real pudo haber construido un flujo que dependa de ellos entre que `ADR-009` los introdujo y esta tarea los retira.

## Decisiones pendientes (quedan fuera, cada una es su propio ADR futuro)

- Rate limiting de infraestructura (por IP/dispositivo) para todos los endpoints públicos sensibles, no solo `register`/`resend-registration-code`.
- Limpieza periódica de cuentas nunca verificadas y códigos vencidos.
- Verificación de dominio/MX como señal adicional (no sustituta) del OTP, si el equipo decide que vale la dependencia nueva.

## Consecuencias

- `email_verification_tokens` sigue siendo la misma entidad (ratificada originalmente por `ADR-009`), ahora con un modelo distinto — no se crea una entidad nueva, se reemplaza la definición de una existente, mismo patrón que `ADR-010` ya aplicó a `password_reset_tokens`.
- Ninguna cuenta de THERS puede usarse sin demostrar control real del correo asociado — la prueba es siempre el OTP, nunca una heurística de formato/dominio.
- `DATABASE_ARCHITECTURE.md`, `DATABASE_ERD.md` y `API_CONTRACT.md` se actualizan el mismo día que este contrato se implementa (`HB-001` §15.1).

## Referencias

- `CLAUDE.md` — jerarquía de fuentes (§4), regla de alcance (§14), reglas específicas para Claude Code (§8).
- `docs/architecture/ADR-009-password-reset-and-email-verification.md` — decisión que este ADR reemplaza parcialmente (verificación de email); sigue vigente para recuperación de contraseña (ya reemplazada por `ADR-010`) y el servicio de correo centralizado.
- `docs/architecture/ADR-010-password-reset-otp-flow.md` — mismo patrón de OTP de 6 dígitos, aplicado primero a la recuperación de contraseña; este ADR replica su enfoque para el registro, sin duplicar su infraestructura.
- `docs/architecture/DATABASE_ARCHITECTURE.md` §5.8 (definición anterior de `email_verification_tokens`).
- `docs/architecture/organization/01_Manual_Organizacion/Source/HB-001-manual-organizacion.md.md` §11 (clasificación de impacto de decisiones), §15.1 (documentar endpoints el mismo día del PR), §19.1 (nunca loguear secretos).

---

## Cierre
