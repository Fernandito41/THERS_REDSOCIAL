# ADR-026 — Verificación en dos pasos (2FA) con TOTP

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/ADR-026-two-factor-authentication.md` |
| Tipo | Architecture Decision Record (`HB-001` §11–12) |
| Fecha | 01/10/2026 |
| Estado | **Aceptada** — implementada en esta tarea (ver §Decisión) |
| Alcance | `backend/` — `users.totp_secret`/`two_factor_enabled`, entidad `two_factor_recovery_codes`, `GET /api/2fa`, `POST /api/2fa/setup`/`confirm`/`disable`/`recovery-codes`, `POST /api/2fa/verify`, desafío en `login`/`auth/google`; `Frontend/` — `TwoFactorRow.jsx`, `TwoFactorChallenge.jsx` |
| Autoridad sobre este documento | `/docs` oficial > estructura real observada en el código > este documento (mismo orden que `CLAUDE.md` §4) |
| Depende de | **`ADR-025-session-registry.md`** — el token de desafío se rechaza en endpoints protegidos precisamente porque no tiene fila en `sessions` |

> Resuelve el control "Activar 2FA" de REF-SET-03, que decía `pending` con el motivo *"No está implementado. Mostrarlo como activo sería afirmar una protección inexistente (archivo maestro §10.2)"*.

---

## Contexto

Entrar a una cuenta de THERS requiere un solo factor: la contraseña (o una identidad de Google, `ADR-012`). El control de la pantalla de Seguridad prometía un segundo factor y era honesto al decir que no existía.

El proyecto ya tiene infraestructura de códigos de un solo uso por correo (`ADR-010` para recuperar la contraseña, `ADR-011` para verificar el email): generación con CSPRNG, hash scrypt, expiración, cooldown de reenvío. Reutilizarla era la opción obvia desde el punto de vista del esfuerzo.

## Opciones consideradas — qué segundo factor

| Opción | Trade-off |
|---|---|
| **A — TOTP, app autenticadora (elegida)** | Es un factor **realmente independiente**: vive en el teléfono, no en un canal que ya controla la cuenta. Requiere una dependencia nueva (`pyotp`), generar un QR y mantener códigos de recuperación |
| B — Código de un solo uso por correo | Reutiliza todo lo que ya existe, sin dependencias. **Pero el correo no es un segundo factor independiente de esta cuenta:** la recuperación de contraseña va al mismo buzón (`ADR-010`), así que quien controle el correo entra igual. Añade un paso, no seguridad — y mostrarlo como "verificación en dos pasos" sería exactamente lo que el motivo original de la pantalla quería evitar: afirmar una protección que no es la que parece |
| C — Las dos, TOTP preferente | El doble de superficie, y el nivel de protección real lo marca el método más débil: si el correo siempre es una alternativa válida, en la práctica protege como el correo |

**Elegida: A**, decidida por el propietario del proyecto al plantearle explícitamente el argumento de la opción B.

## Objetivos

- Un segundo factor real al iniciar sesión, con cualquier app autenticadora estándar.
- Que perder el teléfono no signifique perder la cuenta.
- Que "Continuar con Google" no sea una puerta que saltee el segundo factor.
- Que un alta a medias no deje a nadie afuera de su propia cuenta.
- Que el token intermedio del login no sirva para nada más que completar ese login.

## No objetivos (explícitamente fuera de este ADR)

- **No** implementa 2FA obligatorio, ni por rol ni para todos. Es opcional y por cuenta.
- **No** implementa SMS como segundo factor. `users.phone` existe (`ADR-002`) pero no hay proveedor de SMS, y el SMS es el método más débil de los tres habituales (*SIM swapping*).
- **No** implementa llaves de seguridad (WebAuthn/FIDO2). Es el método más fuerte y sería un ADR propio: cambia el flujo de login entero y necesita soporte del navegador.
- **No** implementa "recordar este dispositivo 30 días". Reduce la fricción pero exige una entidad de dispositivos de confianza con su propia revocación.
- **No** cifra `totp_secret` en reposo. Ver §Riesgos.
- **No** exige el segundo factor para operaciones sensibles ya dentro de la sesión (cambiar email, borrar la cuenta). Hoy esas operaciones piden contraseña donde corresponde.
- **No** permite desactivar el 2FA con un código TOTP (ver §Decisión).

## Opciones consideradas — cómo se guarda el secreto

`users.totp_secret` se guarda **recuperable, no hasheado**, y es **inevitable**: verificar un código TOTP exige recalcularlo a partir del secreto, así que un hash lo haría inservible.

Es la diferencia estructural con los OTP de `ADR-010`/`ADR-011`, que sí se hashean con scrypt: allí el código viaja una vez y solo hay que **compararlo**, no reconstruirlo. Conviene tenerlo claro porque a primera vista parecen el mismo problema y no lo son.

Los **códigos de recuperación** sí se hashean con scrypt (`two_factor_recovery_codes.code_hash`), porque sí son del segundo tipo.

## Opciones consideradas — el token intermedio del login

Con 2FA, el login tiene dos pasos y hace falta algo que autorice el segundo. Tres caminos:

| Opción | Trade-off |
|---|---|
| **A — JWT corto con un claim `purpose` (elegida)** | Sin tabla nueva. Y **gracias a `ADR-025` sale gratis que no sirva para nada más**: el *blocklist loader* exige que el `jti` tenga fila en `sessions`, y este token no la tiene, así que cualquier endpoint protegido lo rechaza sin necesidad de código extra. El endpoint que sí lo acepta lo decodifica a mano y comprueba `purpose` explícitamente |
| B — Token opaco en una tabla, estilo `reset_authorization` (`ADR-010`) | Es el patrón que el proyecto ya usa para "autorizar la etapa siguiente". Más seguro en abstracto (revocable, de un solo uso), pero exige otra tabla para algo que vive cinco minutos, y la propiedad clave (que no sirva en endpoints protegidos) ya la da la opción A |
| C — Reutilizar el JWT de sesión y pedir el código después | Inaceptable: emitiría una sesión válida **antes** del segundo factor. El 2FA no protegería nada |

**Elegida: A.** La comprobación de `purpose` es imprescindible en los dos sentidos: sin ella, un token de sesión normal podría usarse en `/2fa/verify` para emitirse sesiones nuevas sin el segundo factor.

## Decisión

### Modelo

- `users.totp_secret` — `TEXT`, nullable. Base32, generado con CSPRNG.
- `users.two_factor_enabled` — `BOOLEAN NOT NULL DEFAULT false`.

**Están separados a propósito.** Durante el alta existe un secreto **todavía no confirmado**: la persona escaneó el QR pero no probó aún que su app genera códigos correctos. Sin esa separación, escanear y abandonar (o escanear mal) dejaría la cuenta exigiendo un código que nadie puede producir — se quedaría afuera de su propia cuenta sin haber terminado de configurar nada.

- Tabla `two_factor_recovery_codes`: `user_id` (FK, CASCADE), `code_hash` (scrypt), `created_at`, `used_at` (nullable). Sin `UNIQUE` sobre `code_hash`: scrypt usa sal, así que una `UNIQUE` no garantizaría nada.

### Alta en dos pasos

1. **`POST /api/2fa/setup`** → genera el secreto, lo guarda **sin activar**, y devuelve `{secret, provisioning_uri}`. El `otpauth://` lleva el secreto en claro, así que el endpoint es protegido y el valor **nunca se registra en un log**. Un `setup` repetido genera un secreto nuevo y descarta el anterior. `409` si ya está activo.
2. **`POST /api/2fa/confirm`** con un código válido → activa el 2FA y devuelve los **10 códigos de recuperación**. Es la única vez que existen en claro. Si el código no coincide: `400` y **el secreto no se borra**, para poder reintentar con el siguiente sin volver a escanear.

`400` en `confirm` y no `401` porque la identidad ya está probada (el endpoint es protegido); lo que falla es el dato. En el login el mismo error sí es `401`.

### Login en dos pasos

`POST /api/login` (y `POST /api/auth/google`) devuelven, cuando la cuenta tiene 2FA:

```json
{ "two_factor_required": true, "two_factor_token": "<jwt corto>" }
```

**`200`, no un `4xx`:** nada salió mal — las credenciales eran correctas y falta el segundo paso. **No se emite token de sesión ni se registra ninguna sesión**: hasta que el segundo factor valide, no hay sesión.

Google pasa por el mismo desafío. Si no, "Continuar con Google" sería una puerta que lo saltea.

**`POST /api/2fa/verify`** con `{two_factor_token, code}` → emite la sesión real. `code` acepta **o** un TOTP de 6 dígitos **o** un código de recuperación; se prueba el TOTP primero porque es el caso normal. Un código de recuperación se consume (`mark_used` con la condición en el `WHERE`, así que dos peticiones simultáneas con el mismo código no lo consumen las dos).

**Un solo error para los dos formatos.** Decir "ese no era un TOTP pero lo probé como recuperación" revelaría qué espera el servidor y en qué estado está la cuenta.

### Códigos de recuperación

10 códigos de 10 caracteres de un alfabeto base32 **sin ambigüedades visuales** (sin `I`/`L`/`O`/`0`/`1`), con un guion cada cinco para que se puedan transcribir. ~48 bits de entropía: mucho más que un OTP de 6 dígitos, porque un código de recuperación **no expira** — vive hasta que se usa, así que no puede depender de una ventana de tiempo corta para ser seguro.

Al comparar se normalizan (mayúsculas, sin guion ni espacios): que alguien lo escriba en minúsculas o sin el guion no debería dejarlo fuera de su propia cuenta. Se hashea la forma **normalizada**, que es la misma contra la que se compara.

Regenerar (`POST /api/2fa/recovery-codes`) invalida los anteriores en la misma operación: si no, quedarían dos juegos válidos y la persona no sabría cuál tiene anotado.

### Desactivar: pide **contraseña**, no un código

`POST /api/2fa/disable` exige la contraseña. **Si exigiera un código TOTP, quien perdió el dispositivo quedaría atrapado con el 2FA puesto para siempre.** La contraseña es lo que ya protegía la cuenta antes.

Desactivar además: borra el secreto, borra los códigos de recuperación (si no, se podría entrar con un código de recuperación de un 2FA que ya no existe) y **cierra todas las sesiones, incluida la actual** — bajar el nivel de protección de la cuenta es exactamente el momento de forzar un login nuevo.

Es `POST` y no `DELETE` aunque "apague" algo: además de desactivar, borra y revoca. No es la eliminación de un recurso, es una operación con efectos.

Una cuenta creada solo con Google no tiene contraseña (`ADR-012`), así que no puede desactivar por esta vía; se responde con el mismo `401` genérico que un login fallido, sin revelar que la cuenta es Google-only. Es una limitación conocida (ver §Decisiones pendientes).

### `pyotp`, confinado a infraestructura

El puerto `TotpProvider` vive en `domain/auth/two_factor.py` y su implementación en `infrastructure/auth/pyotp_totp_provider.py` — mismo principio que confina `google-auth` a `google_id_token_verifier.py`, `resend` a `infrastructure/email/` y `psycopg` a `infrastructure/persistence/` (`BACKEND_ARCHITECTURE.md` §17).

**No se implementa TOTP a mano** aunque RFC 6238 sean unas veinte líneas: una implementación propia de un algoritmo de autenticación es exactamente el código que no se debe escribir sin necesidad. `pyotp` ya resuelve la ventana de desfase de reloj y la comparación en tiempo constante.

Ventana de tolerancia: ±1 intervalo (±30 s). Subirla amplía el tiempo en que un código interceptado sigue sirviendo.

### Seguridad

- El token de desafío **no sirve en ningún endpoint protegido** (no tiene fila en `sessions`, `ADR-025`), y un token de sesión **no sirve como desafío** (se comprueba `purpose`). Las dos direcciones están cubiertas por prueba.
- El secreto solo viaja a quien ya está autenticado, en la respuesta de `setup`.
- Desactivar y regenerar exigen contraseña: son operaciones sobre credenciales de acceso.
- Los códigos de recuperación se hashean con scrypt y son de un solo uso, garantizado bajo concurrencia por la condición en el `WHERE`.
- `two_factor_enabled` **no** está en la whitelist de `PATCH /api/users/me/security`: activarlo requiere el flujo de dos pasos con verificación de código, no un booleano (verificado por prueba).

## Impacto en Frontend

- **`TwoFactorChallenge.jsx`** (nuevo, ruta pública `/two-factor`): segundo paso del login. El token de desafío viaja por *router state*, **no por `localStorage`** — no es una sesión. Si se pierde (F5, URL directa), el único camino correcto es volver a iniciar sesión; se dice eso en vez de dejar una pantalla rota. No usa `OtpCodeInput` (el de seis casillas) porque el campo acepta dos formatos de longitud distinta, y uno fijo dejaría fuera el código de recuperación — justo el que se usa cuando alguien perdió el teléfono.
- **`TwoFactorRow.jsx`** (nuevo): alta con QR, confirmación, códigos de recuperación, regenerar y desactivar. El **QR se genera en el navegador** (`qrcode`) a partir del `otpauth://`: el secreto no tiene por qué pasar por un servicio de imágenes externo, y el backend no necesita una dependencia de generación de PNG. Si el QR no se puede dibujar, el secreto en texto siempre está visible debajo.
- **`AuthContext.jsx`**: `login`/`loginWithGoogle` devuelven un objeto discriminado (`{twoFactorRequired}`) en vez de lanzar una excepción — que la cuenta tenga 2FA no es un error, es el camino normal del login para esa persona. Nuevo `verifyTwoFactor`, y un `storeSession` compartido por los tres caminos que producen sesión.
- **`Login.jsx`, `AuthPage.jsx`, `Register.jsx`**: interceptan el desafío y navegan a `/two-factor`.

## Impacto en Backend

- `migrations/versions/a3c9f5b1e648_add_two_factor_totp.py` (nueva).
- `requirements.txt`: `pyotp==2.10.0`.
- `domain/auth/two_factor.py` (puerto + constantes), `two_factor_exceptions.py` (nuevos); `token_generator.py`: `generate_recovery_code`/`normalize_recovery_code`; `repositories.py`: `TwoFactorRecoveryCodeRepository`.
- `infrastructure/auth/pyotp_totp_provider.py`, `infrastructure/persistence/repositories/two_factor_recovery_code_repository.py` (nuevos).
- `application/two_factor/two_factor_use_case.py` (nuevo).
- `interfaces/routes/security_routes.py`: los cinco endpoints de gestión; `auth_routes.py`: desafío en login/Google y `POST /api/2fa/verify`.
- `extensions.py`: el *blocklist loader* rechaza los tokens con `purpose: "2fa_challenge"`.
- Tests en `tests/test_security.py`.

## Riesgos

- **`totp_secret` se guarda sin cifrar.** Una fuga de la tabla `users` permite generar códigos válidos para cualquier cuenta con 2FA. Cifrarlo en reposo movería el problema a dónde guardar la clave de cifrado, que sin gestión de secretos en producción (`CLAUDE.md` §15, DevOps sin documentar) estaría en la misma base o en el mismo `.env`. Se registra como pendiente real, no como resuelto.
- **Códigos de recuperación sin expiración.** Compensado con entropía (~48 bits) y hash lento, pero un código anotado hace dos años sigue valiendo.
- **Sin *rate limiting* en `/2fa/verify`.** Un TOTP de 6 dígitos son 10⁶ combinaciones y la ventana es de 30 s: sin límite de intentos, la fuerza bruta es concebible. **Es el riesgo más serio de este ADR.** El proyecto no tiene *rate limiting* en ningún endpoint (`API_CONTRACT.md` §9, pendiente transversal), así que no se resuelve acá — pero a diferencia del resto, acá la ausencia es explotable, y queda señalado como tal.
- **Una cuenta Google-only no puede desactivar su 2FA** (no tiene contraseña). Puede fijar una primera contraseña con el flujo de recuperación (`ADR-012` lo documenta) y entonces sí. El camino existe pero no es obvio desde la interfaz.
- **El desfase de reloj puede bloquear a alguien.** La ventana de ±30 s cubre lo habitual; un teléfono con la hora muy desajustada no genera códigos válidos. El mensaje de error lo dice explícitamente.
- **Los códigos se muestran una sola vez.** Si alguien cierra la pantalla sin guardarlos, puede regenerarlos (con contraseña), pero hasta entonces no tiene red de seguridad.

## Decisiones pendientes (cada una es su propio ADR futuro)

- ***Rate limiting* de `/2fa/verify`** — el más urgente de esta lista.
- Cifrado de `totp_secret` en reposo (depende de gestión de secretos, DevOps).
- WebAuthn / llaves de seguridad.
- "Recordar este dispositivo" para reducir la fricción.
- Exigir el segundo factor para operaciones sensibles dentro de la sesión.
- 2FA obligatorio por rol (no existe el concepto de rol, `DATABASE_ARCHITECTURE.md` §4.B).
- Ruta clara para que una cuenta Google-only fije contraseña desde la interfaz.

## Consecuencias

- **`DATABASE_ARCHITECTURE.md` cambia** (tabla `two_factor_recovery_codes`, `users.totp_secret`/`two_factor_enabled`) → v0.20.
- `API_CONTRACT.md` → v0.24. **`POST /api/login` y `POST /api/auth/google` ganan una segunda forma de respuesta `200`** — es el cambio de contrato más relevante: un cliente que asuma que un `200` siempre trae `token` se rompe. La forma vieja sigue siendo la de toda cuenta sin 2FA.
- `requirements.txt` gana una dependencia; `Frontend/package.json` gana `qrcode`. Ninguna versión del proyecto está ratificada formalmente como estándar (`CLAUDE.md` §5), así que estas tampoco.
- Depende de `ADR-025`: sin el registro de sesiones, el token de desafío no podría distinguirse de un token de sesión sin código extra.

## Referencias

- `docs/architecture/ADR-025-session-registry.md` — dependencia directa.
- `docs/architecture/ADR-010-password-reset-otp-flow.md`, `ADR-011-mandatory-email-verification.md` — los OTP por correo, y por qué su hashing no aplica al secreto TOTP.
- `docs/architecture/ADR-012-google-sign-in.md` — el camino de Google que también pasa por el desafío, y las cuentas sin contraseña.
- `docs/architecture/BACKEND_ARCHITECTURE.md` §17 — la regla que confina `pyotp` a infraestructura.
- `CLAUDE.md` §15 — gestión de secretos sin documentar, de donde viene el riesgo de `totp_secret`.

---

## Cierre

El tercer control `pending` de la pantalla de Seguridad pasa a funcionar, y con un segundo factor que lo es de verdad: la alternativa por correo habría sido más rápida de construir y habría protegido mucho menos de lo que su propio nombre promete. Queda una ausencia que sí es explotable y está señalada como tal: `/2fa/verify` no tiene límite de intentos.
