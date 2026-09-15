# ADR-009 — Recuperación de contraseña y verificación de email vía Resend

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/ADR-009-password-reset-and-email-verification.md` |
| Tipo | Architecture Decision Record (`HB-001` §11–12) |
| Fecha | 15/09/2026 |
| Estado | **Aceptada** — implementada en esta tarea (ver §Decisión) |
| Alcance | `backend/` — nuevo servicio de correo (Resend), nuevas entidades `password_reset_tokens`/`email_verification_tokens`, nueva columna `users.email_verified`, `POST /api/forgot-password`, `POST /api/reset-password`, `POST /api/send-verification-email`, `POST /api/verify-email` |
| Autoridad sobre este documento | `/docs` oficial > estructura real observada en el código > este documento (mismo orden que `CLAUDE.md` §4) |

> ⚠️ **Regla de alcance, explícita — mismo criterio que `ADR-004`–`ADR-008`.** `DATABASE_ARCHITECTURE.md` §4.B ya registraba "Verificación de correo, Recuperación de contraseña" bajo "Autenticación y cuenta" como `PENDIENTE DE DECISIÓN` ("tabla(s) de tokens de un solo uso o columnas + servicio externo"). Este ADR resuelve esa pendiente exacta: elige la forma de tokens de un solo uso (§Opciones consideradas) y la implementa. No toca login con Google, verificación por SMS, ni ninguna otra candidata de esa misma sección que siga sin ratificar.

---

## Contexto

THERS ya tenía dos pantallas del Frontend completamente construidas y a la espera de un backend: `ForgotPassword.jsx` y `ResetPassword.jsx` (`Frontend/src/features/auth/pages/`), cada una con su propio comentario explícito "INTEGRACIÓN PENDIENTE DEL BACKEND" — validación de formulario, estados de carga/éxito, lectura del token desde la URL (`?token=...`) ya resueltos, solo faltando el endpoint real. `register`/`login`/`GET`/`PATCH /api/users/me` ya persisten contra PostgreSQL real; esta tarea agrega la pieza de auth que faltaba: qué pasa cuando alguien olvida su contraseña, y si el email de una cuenta es real.

## Problema

Definir un mecanismo de correo saliente (vía Resend) y, sobre él, un flujo de recuperación de contraseña y uno de verificación de email — ambos con tokens de un solo uso, expirables, sin revelar información sobre qué cuentas existen.

## Objetivos

- Enviar correo transaccional a través de Resend, centralizado en una capa de servicio — ningún caso de uso ni ninguna route llama a Resend directamente.
- Un usuario puede pedir recuperar su contraseña con solo su email, sin poder usar esa respuesta para averiguar si ese email está registrado.
- El enlace de recuperación expira, es de un solo uso, y queda invalidado apenas la contraseña cambia (junto con cualquier otro enlace de recuperación pendiente de ese usuario).
- Un usuario autenticado puede pedir verificar su email; el sistema sabe si ya lo verificó (`email_verified`).
- Nada de esto rompe `register`/`login`/`GET`/`PATCH /api/users/me` ni ninguna otra entidad ya ratificada.
- El sistema funciona de punta a punta en desarrollo local sin depender de tener ya una cuenta de Resend (§Riesgos).

## No objetivos (explícitamente fuera de este ADR)

- **No** implementa notificaciones push ni SMS — solo correo, vía Resend.
- **No** implementa un endpoint de cambio de contraseña autenticado y separado (`PATCH /api/users/me/password` o similar) — `ADR-003-profile-update-contract.md` ya excluyó `password` del contrato de `PATCH /api/users/me` explícitamente; cambiar la contraseña sigue siendo, en esta versión, exclusivamente vía el flujo de recuperación (`POST /api/reset-password`). Si el producto llega a necesitar "cambiar mi contraseña estando ya logueado, sin pasar por email", es una decisión de alcance propia, no un efecto colateral de este ADR.
- **No** implementa los correos de seguridad adicionales que la tarea de origen anticipaba como arquitectura futura (inicio de sesión sospechoso, cambio de email, otros cambios de seguridad) — ver §Consecuencias para la recomendación de cuáles priorizar después.
- **No** implementa reenvío de verificación con un endpoint distinto a `send-verification-email` (ya sirve tanto el primer envío como el reenvío, con cooldown) — no hace falta un endpoint separado de "reenviar".
- **No** implementa `DELETE`/expiración automática de tokens vencidos (limpieza periódica) — se acumulan indefinidamente, igual que el resto de entidades del backend (`notifications`, etc.) no implementan borrado tampoco; es la misma pendiente transversal (`DATABASE_ARCHITECTURE.md` §14).
- **No** conecta `Frontend/src/features/auth/pages/ForgotPassword.jsx`/`ResetPassword.jsx` al backend real — esta tarea fue explícitamente de backend (ver alcance pedido); ambas páginas quedan exactamente como estaban, con su bloque "INTEGRACIÓN PENDIENTE" intacto, listas para conectarse en una tarea de Frontend separada.

## Opciones consideradas — proveedor de correo

| Opción | Descripción | Trade-off |
|---|---|---|
| **A — Resend (elegida)** | SDK oficial (`resend`, PyPI) sobre la API HTTP de Resend | Pedida explícitamente por la tarea. SDK oficial mantenido, tipado, sin dependencias pesadas (usa `requests` internamente, ya common en el ecosistema Python) |
| B — SMTP genérico (smtplib, stdlib) | Sin dependencia externa | Requeriría gestionar credenciales SMTP, reintentos, deliverability por cuenta propia — Resend ya resuelve eso; no había ninguna razón para no usar el proveedor pedido |

## Opciones consideradas — token de recuperación/verificación

| Opción | Descripción | Trade-off |
|---|---|---|
| **A — Token opaco de un solo uso, respaldado por tabla (elegida)** | `secrets.token_urlsafe(32)` (256 bits), se persiste solo su hash SHA-256; una fila por token, con `expires_at`/`used_at` | Invalidación real de un solo uso e individual — revocar un token no afecta a ningún otro. Estado explícito en la base, auditable |
| B — Reutilizar el JWT de login como token de recuperación | Sin tabla nueva -- un JWT de corta duración con un claim especial | Descartada explícitamente (pedido por la tarea de origen): un JWT es stateless, no hay forma de invalidarlo individualmente antes de su expiración sin una lista de revocación aparte -- que sería más trabajo que la tabla dedicada. Tampoco resuelve "un solo uso" de forma nativa |
| C | Token con expiración embebida y firmado (`itsdangerous.URLSafeTimedSerializer`, ya viene con Flask) sin persistir nada | Resolvería expiración sin tabla, pero no resolvería "un solo uso" (nada que marcar como usado) ni "invalidar todos los pendientes al cambiar la contraseña" (ambos exigidos por la tarea, FASE 4) sin, de nuevo, una tabla de todos modos -- la opción A ya cubre ambos casos con el mismo mecanismo |

**Elegida: A.** Hash SHA-256 (no un hash lento tipo scrypt/bcrypt como `password_hash`): el token ya tiene 256 bits de entropía propios, no es una contraseña de baja entropía elegida por una persona — SHA-256 alcanza para que una filtración de la tabla no permita reconstruir el token original.

## Opciones consideradas — una tabla de tokens vs. dos

| Opción | Descripción | Trade-off |
|---|---|---|
| **A — Dos tablas separadas (elegida)** | `password_reset_tokens` y `email_verification_tokens`, misma forma, sin relación entre sí | Sus políticas difieren (TTL de 30 min vs. 24 h, quién puede pedirlos — público vs. autenticado, qué pasa al usarlos — invalidar otros tokens pendientes vs. no) — mantenerlas separadas evita una columna `purpose`/`type` que tendría que ramificar esa lógica dentro del mismo caso de uso |
| B — Una tabla genérica `auth_tokens` con discriminador de propósito | Mismo patrón que `notifications` (`ADR-008`, un solo `type`) | Descartada: a diferencia de los tipos de notificación (que comparten exactamente la misma forma y comportamiento), estos dos tipos de token tienen TTL y reglas de invalidación distintas -- forzarlos a la misma tabla movería esa diferencia a un `if` dentro de cada caso de uso en vez de dejarla expresada en el nombre/módulo de cada repositorio |

## Decisión

### Arquitectura del servicio de correo

```
interfaces/routes/{auth_routes.py,user_routes.py}   (composition root)
        ↓
application/auth/{forgot_password,reset_password,send_verification_email,verify_email}_use_case.py
        ↓
application/email/email_service.py                  ("Email Service" pedido por la tarea)
        ↓ usa
application/email/templates.py                       (HTML reutilizable, sin Jinja/Flask)
        ↓
domain/email/sender.py                                (puerto EmailSender, abstracto)
        ↓ implementado por
infrastructure/email/{resend_email_sender.py, null_email_sender.py}  (adaptadores)
        ↓
Resend (SDK oficial `resend`) / nada (NullEmailSender)
```

`EmailService` (`application/email/`) es la única pieza que sabe qué contenido va en cada correo (recuperación, contraseña cambiada, verificación) — ningún caso de uso ni ninguna route arma HTML. `infrastructure/email/factory.py` decide entre `ResendEmailSender` (si `RESEND_API_KEY` está definida) y `NullEmailSender` (si no) — este último solo imprime el intento por `stderr` (nunca el cuerpo del correo, que puede contener el token crudo) y no falla, para que el backend funcione de punta a punta en desarrollo local sin necesitar todavía una cuenta de Resend (§Riesgos).

### Modelo de datos

**`users` gana una columna:**

| Columna | Tipo | Nulo | Justificación |
|---|---|---|---|
| `email_verified` | `BOOLEAN`, `DEFAULT false` | No | Toda cuenta existente antes de esta migración queda sin verificar — no hay backfill posible. Expuesta en `to_public_user` (`register`/`login`/`GET`/`PATCH /api/users/me`), nunca escribible desde ningún body — solo `POST /api/verify-email` puede ponerla en `true` |

**`password_reset_tokens` (nueva):**

| Columna | Tipo | Nulo | Justificación |
|---|---|---|---|
| `id` | `UUID`, `DEFAULT gen_random_uuid()` | No (PK) | Mismo patrón que el resto de entidades |
| `user_id` | `UUID`, FK → `users.id`, `ON DELETE CASCADE` | No | Dueño del token |
| `token_hash` | `VARCHAR(64)`, `UNIQUE` | No | SHA-256 hex del token crudo (64 caracteres) — nunca se persiste el valor crudo |
| `expires_at` | `TIMESTAMPTZ` | No | 30 minutos desde su creación (`domain/auth/token_policy.PASSWORD_RESET_TOKEN_TTL_MINUTES`) |
| `used_at` | `TIMESTAMPTZ` | Sí | `NULL` = no usado. Se fija una sola vez, nunca se revierte |
| `created_at` | `TIMESTAMPTZ`, `DEFAULT now()` | No | Sostiene el cooldown anti-spam (`has_recent_unused_token`) |

**`email_verification_tokens` (nueva):** misma forma exacta que `password_reset_tokens`, TTL de 24 horas (`EMAIL_VERIFICATION_TOKEN_TTL_HOURS`).

Ninguna de las dos tiene `updated_at` (un token se crea o se marca usado, nunca se edita de otro modo — mismo criterio que `likes`/`follows`/`notifications`).

### Contrato API (documentado el mismo día en `API_CONTRACT.md`, `HB-001` §15.1)

Rutas planas bajo `/api`, sin prefijo `/auth/` — mismo criterio que `/api/register`/`/api/login` ya establecido, no el `/api/auth/...` que la tarea de origen sugería a modo de ejemplo (explícitamente invitaba a "adaptarlo si la API existente utiliza otra convención").

- **`POST /api/forgot-password`** (público) — siempre `200`, mismo mensaje genérico exista o no el email (§Seguridad).
- **`POST /api/reset-password`** (público) — `token` + `password` + `confirm_password`. `400` si el token no existe/expiró/ya se usó (mismo mensaje en los tres casos), o si las contraseñas no coinciden/no cumplen el formato ya vigente (`MIN_PASSWORD_LENGTH`, `domain/auth/validators.py`).
- **`POST /api/send-verification-email`** (protegido, `@jwt_required()`) — sin body, opera sobre el usuario del JWT.
- **`POST /api/verify-email`** (público) — `token`. Público porque quien hace clic en el enlace del correo puede no tener sesión iniciada en ese navegador/dispositivo.

Ver `API_CONTRACT.md` §4.8 para el detalle completo de cada endpoint (request/response/errores).

> **Nota sobre el nombre del campo del mensaje.** La tarea de origen (Fase 4) mostraba el mensaje genérico como `{"message": "..."}`. Se implementó como `{"msg": "..."}` en su lugar — `API_CONTRACT.md` §3 ya establece `msg` como el campo de texto uniforme de **toda** la API desde v0.6, y los cuatro endpoints nuevos de este ADR lo siguen sin excepción, igual que el resto. Señalado acá explícitamente por si el equipo prefiere `message` para este caso puntual — es un cambio de una palabra si así se decide.

### Seguridad (FASE 4)

- **Anti-enumeración:** `forgot_password_use_case.py` nunca distingue "el email existe" de "no existe" en su valor de retorno — la route siempre responde `200` con el mismo texto. Verificado por prueba (`test_password_reset.py::test_existing_and_nonexistent_email_return_identical_response`, compara las dos respuestas byte a byte).
- **Expiración:** `expires_at` en ambas tablas, verificado en cada `find_valid_by_hash`.
- **Un solo uso:** `used_at` se fija al consumir el token; una segunda llamada con el mismo token cae en el mismo `400` genérico.
- **Invalidación al cambiar la contraseña:** `reset_password_use_case.py` invalida el token usado **y** cualquier otro token de recuperación pendiente del mismo usuario (`invalidate_all_for_user`) — un enlace de un pedido anterior sin abrir deja de servir.
- **Hash, no texto plano:** solo `token_hash` (SHA-256) se persiste; el valor crudo vive únicamente en el enlace del correo y en la memoria de la request que lo consume.
- **Cooldown:** `PASSWORD_RESET_REQUEST_COOLDOWN_SECONDS`/`EMAIL_VERIFICATION_REQUEST_COOLDOWN_SECONDS` (60s cada uno, `domain/auth/token_policy.py`) — un pedido repetido dentro de la ventana no genera un token ni un correo nuevo, sin cambiar la respuesta genérica de `forgot-password`.
- **Sin información sensible en logs:** `NullEmailSender` (desarrollo sin `RESEND_API_KEY`) imprime destinatario y asunto, nunca el cuerpo del correo (que contiene el token crudo dentro del enlace) — mismo principio que nunca loguear `password_hash`/`JWT_SECRET_KEY` (`HB-001` §19.1).
- **Validación de la nueva contraseña:** mismo `is_valid_password`/`MIN_PASSWORD_LENGTH` ya usado por `POST /api/register` — sin una regla nueva ni distinta.
- **Mismo hashing que el resto de THERS:** `reset_password_use_case.py` usa `domain/auth/auth_service.hash_password` (scrypt vía `werkzeug.security`), igual que `register_use_case.py`.

## Impacto en Backend

- `requirements.txt`: nueva dependencia `resend==2.45.0` (trae `requests` transitivamente).
- `app/config.py`: `RESEND_API_KEY`, `EMAIL_FROM` (default `onboarding@resend.dev`, el remitente de pruebas que Resend documenta para no depender de un dominio verificado), `FRONTEND_URL` (default `http://localhost:5173`).
- `domain/auth/`: `token_generator.py`, `token_policy.py`, `password_reset_repository.py`, `email_verification_repository.py`; `exceptions.py` gana `InvalidOrExpiredResetTokenError`/`InvalidOrExpiredVerificationTokenError`.
- `domain/email/sender.py` (nuevo): puerto `EmailSender`.
- `application/email/`: `templates.py`, `email_service.py`.
- `application/auth/`: `forgot_password_use_case.py`, `reset_password_use_case.py`, `send_verification_email_use_case.py`, `verify_email_use_case.py`; `user_presenter.py` extendido con `email_verified`.
- `infrastructure/email/`: `resend_email_sender.py`, `null_email_sender.py`, `factory.py`.
- `infrastructure/persistence/models.py`: `User.email_verified`; nuevos modelos `PasswordResetToken`, `EmailVerificationToken`.
- `infrastructure/persistence/repositories/`: `password_reset_repository.py`, `email_verification_repository.py` (adaptadores SQLAlchemy).
- `interfaces/routes/auth_routes.py`: tres rutas nuevas. `interfaces/routes/user_routes.py`: una ruta nueva.
- Tres migraciones nuevas (`b8d4f2a917c3`, `c1f6a83d2e59`, `d3a9c47b1f68`).
- `tests/conftest.py`: las dos tablas nuevas se agregan al `TRUNCATE` entre pruebas.
- Tests de integración nuevos: `test_password_reset.py`, `test_email_verification.py` — 30 pruebas, contra PostgreSQL 16 real, sin mocks. El token crudo se inserta directamente con las mismas funciones de dominio que usa el código real (`generate_raw_token`/`hash_token`), ya que la API nunca lo devuelve (viaja solo por correo).

## Riesgos

- **Sin cuenta de Resend en desarrollo:** cubierto por `NullEmailSender` — el flujo completo (token creado, expiración, un solo uso, invalidación) funciona y se prueba igual, solo no llega un correo real. Probar el envío real requiere una `RESEND_API_KEY` propia (de prueba o de producción, nunca hardcodeada) en `backend/.env`.
- **`EMAIL_FROM` por defecto (`onboarding@resend.dev`):** válido solo para pruebas según la propia documentación de Resend — cualquier entorno real necesita verificar un dominio propio y reemplazar este valor.
- **Acumulación de tokens vencidos:** sin limpieza periódica en esta versión (§No objetivos) — mismo criterio que el resto del backend no implementa borrado todavía.
- **Cooldown en memoria de la base, no distribuido:** si el backend corriera en múltiples instancias sin una base compartida, el cooldown seguiría siendo correcto igual (la fuente de verdad es la fila en PostgreSQL, no un estado en el proceso) — no hay riesgo real acá, se aclara para que quede explícito.

## Decisiones pendientes (quedan fuera, cada una es su propio ADR futuro)

- Conectar `ForgotPassword.jsx`/`ResetPassword.jsx` al backend real (tarea de Frontend).
- Endpoint de cambio de contraseña autenticado (sin pasar por email).
- Correos de seguridad adicionales: inicio de sesión sospechoso, cambio de email, otros cambios de seguridad (ver recomendación en el informe de esta tarea).
- Preferencias de notificación por correo configurables por el usuario.
- Limpieza periódica de tokens vencidos.
- Gestión de secretos de `RESEND_API_KEY` en un entorno desplegado (mismo hueco transversal que `JWT_SECRET_KEY`/`DATABASE_URL`, `DATABASE_ARCHITECTURE.md` §14).

## Consecuencias

- `password_reset_tokens` y `email_verification_tokens` son la séptima y octava entidad del alcance objetivo del producto (`DATABASE_ARCHITECTURE.md` §4.B) en pasar de pendiente/objetivo a ratificada.
- THERS gana su primera integración con un servicio externo (Resend) — primer caso real del patrón puerto/adaptador (`domain/email/sender.py`) aplicado a algo que no es persistencia.
- `DATABASE_ARCHITECTURE.md`, `DATABASE_ERD.md` y `API_CONTRACT.md` se actualizan el mismo día que este contrato se implementa (`HB-001` §15.1).

## Referencias

- `CLAUDE.md` — jerarquía de fuentes (§4), regla de alcance (§14), reglas específicas para Claude Code (§8).
- `docs/architecture/ADR-002-user-profile-fields.md` a `ADR-008-notifications-minimal-model.md` — mismo proceso, mismo criterio de extender por entidades simples.
- `docs/architecture/DATABASE_ARCHITECTURE.md` §4.B › Autenticación y cuenta (candidata "Verificación de correo, Recuperación de contraseña"), §3 (principios de diseño).
- `docs/architecture/organization/01_Manual_Organizacion/Source/HB-001-manual-organizacion.md.md` §11 (clasificación de impacto de decisiones), §15.1 (documentar endpoints el mismo día del PR), §19.1 (nunca loguear secretos).
- Resend — documentación oficial del SDK Python y de `onboarding@resend.dev` como remitente de pruebas sin dominio verificado (resend.com/docs).

---

## Cierre
