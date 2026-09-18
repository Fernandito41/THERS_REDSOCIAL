# ADR-012 — Registro e inicio de sesión con Google ("Continuar con Google")

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/ADR-012-google-sign-in.md` |
| Tipo | Architecture Decision Record (`HB-001` §11–12) |
| Fecha | 21/09/2026 |
| Estado | **Aceptada** — implementada en esta tarea. Método **adicional**, no reemplaza el registro/login tradicional |
| Alcance | `backend/` — nuevo endpoint `POST /api/auth/google`, nueva tabla `user_identities`, `users` gana `profile_completed` y relaja `password_hash`/`phone`/`country_code`/`birth_date` a nullable; `Frontend/` — botón real de Google en `Login.jsx`/`Register.jsx`, nueva pantalla `CompleteProfile.jsx`. El registro/login por email+contraseña, JWT, `/api/users/me`, verificación de email por OTP (`ADR-011`) y recuperación de contraseña (`ADR-010`) **no se tocan** en su comportamiento existente |
| Autoridad sobre este documento | `/docs` oficial > estructura real observada en el código > este documento (mismo orden que `CLAUDE.md` §4) |

---

## Contexto

THERS solo tenía un método de autenticación: email + contraseña, con verificación obligatoria por OTP (`ADR-011`) y recuperación por OTP (`ADR-010`). El equipo pidió agregar "Continuar con Google" como método **adicional** para registrarse e iniciar sesión, sin reemplazar el flujo tradicional ni debilitarlo, usando los mecanismos oficiales de Google (OAuth 2.0 + OpenID Connect) y verificando la credencial criptográficamente en el backend — nunca confiando en datos que el Frontend diga que vienen de Google.

## Problema

Integrar Google Identity Services de punta a punta (Frontend → backend → PostgreSQL → JWT de THERS) resolviendo, sin improvisar, los puntos que cualquier integración de "Sign in with Google" tiene que decidir explícitamente:

- Qué identificador de Google usar (nunca solo el email).
- Qué pasa si ya existe una cuenta tradicional con el mismo email (account linking, con riesgo real de account takeover si se hace mal).
- Qué pasa si THERS necesita datos (username elegido, teléfono, fecha de nacimiento) que Google no entrega.
- Qué pasa si una cuenta creada solo por Google intenta usar `Forgot password` o el login tradicional.
- Cómo verificar la credencial sin implementar criptografía a mano.

## Objetivos

- `POST /api/auth/google` (nuevo, público): recibe `{credential}` (el ID Token que Google Identity Services le entrega al Frontend), lo verifica criptográficamente contra las claves públicas reales de Google, y crea/vincula/loguea según corresponda — nunca confía en un email/nombre que el Frontend le pase por su cuenta.
- El registro/login tradicional (email + contraseña) sigue exactamente igual, sin ningún cambio de comportamiento.
- Google nunca sustituye al JWT de THERS: todos los endpoints protegidos (incluido `/api/users/me`) siguen exigiendo el JWT propio de THERS, nunca un token de Google.
- Account linking seguro: una cuenta tradicional y una cuenta de Google con el mismo email correcto terminan siendo la misma cuenta de THERS, nunca dos — con una política determinística que nunca vincula por la sola coincidencia de un email sin garantías.
- Una cuenta Google-only puede completar su perfil (`username`/`phone`/`country_code`/`birth_date`, que Google no entrega) sin que el backend permita saltarse ese paso navegando directo a otra URL.
- Una cuenta Google-only puede fijar su primera contraseña reutilizando el flujo de recuperación existente, sin duplicar esa lógica.
- Reutilización explícita: generador de identificadores/hash ya existentes, `EmailService` (para los correos que ya se envían, ninguno nuevo), `PATCH /api/users/me` (para completar perfil), Repository/puerto-adaptador pattern ya establecido.

## No objetivos (explícitamente fuera de este ADR)

- **No** implementa Apple/Microsoft/otros proveedores — el modelo de datos (`user_identities`) queda preparado para agregarlos después sin migrar `users` de nuevo, pero no se implementan en esta tarea.
- **No** implementa el flujo de código de autorización servidor-a-servidor (`GOOGLE_CLIENT_SECRET`, intercambio de código por token) — THERS usa exclusivamente verificación de ID Token (OpenID Connect), que no requiere el Client Secret en absoluto (§Opciones consideradas).
- **No** usa la foto de perfil que Google entrega (`picture` claim) — prioriza autenticación, queda fuera de alcance (FASE 19 de la tarea origen lo permite explícitamente).
- **No** implementa "Google One Tap" (el aviso automático que aparece sin que la persona haga clic) — solo el botón estándar "Continuar con Google" que la persona activa a propósito.
- **No** cambia el algoritmo de hashing de contraseñas ni introduce un tercer algoritmo — sigue siendo scrypt para `password_hash` (cuando existe).

## Opciones consideradas — mecanismo de verificación

| Opción | Descripción | Trade-off |
|---|---|---|
| **A — Verificación de ID Token (OpenID Connect), librería oficial `google-auth` (elegida)** | El Frontend usa Google Identity Services (`accounts.google.com/gsi/client`), obtiene un ID Token firmado por Google, y lo envía tal cual a `POST /api/auth/google`; el backend lo verifica con `google.oauth2.id_token.verify_oauth2_token()` | Sin intercambio de código, sin `GOOGLE_CLIENT_SECRET`, sin sesión de servidor a mantener durante el flujo — el ID Token ya es la prueba criptográfica completa (firma + claims). Es el mecanismo que Google mismo recomienda para "Sign in with Google" en aplicaciones con un backend propio que no necesita llamar a las APIs de Google en nombre del usuario (no se piden Google Drive, Calendar, etc. — solo identidad) |
| B — Flujo de código de autorización (`response_type=code`), intercambio servidor-a-servidor con `GOOGLE_CLIENT_SECRET` | Necesario si THERS necesitara además un `access_token` para llamar a APIs de Google en nombre del usuario | Descartada: THERS solo necesita **identidad** (quién es esta persona), no acceso a ningún recurso de Google -- agregar el intercambio de código y gestionar un `client_secret` sería complejidad e infraestructura sin ningún beneficio real para este caso de uso |
| C — Decodificar el JWT manualmente (`base64` + parseo) sin verificar firma | Ninguna librería nueva | Descartada explícitamente por la tarea de origen ("nunca implementes manualmente criptografía o validación de tokens si existe una librería oficial") -- decodificar sin verificar la firma permite que cualquiera envíe un JWT fabricado a mano con cualquier email, exactamente el ataque que este ADR existe para prevenir |

**Elegida: A.**

## Opciones consideradas — identificador de Google e integración con `users`

| Opción | Descripción | Trade-off |
|---|---|---|
| **A — Tabla `user_identities` separada (elegida)** | `user_identities(id, user_id, provider, provider_subject, created_at)`, `UNIQUE(provider, provider_subject)` | Agregar Apple/Microsoft más adelante es una fila nueva con otro `provider`, no una migración de `users`. Un usuario puede tener varias identidades vinculadas a la vez (password + Google, FASE 9) sin que `users` necesite una columna por proveedor. Mismo criterio que `notifications.type` (`ADR-008`): discriminador validado en la aplicación, no un `ENUM` de PostgreSQL |
| B — Columnas `google_sub`/`auth_provider` directas en `users` | Más simple de consultar (un solo `JOIN` menos) | Descartada: `auth_provider` como columna de un solo valor no representa bien "password + Google al mismo tiempo" (FASE 9, account linking); agregar Apple después exigiría otra columna (`apple_sub`) y ampliar `auth_provider` a una lista, en vez de una fila nueva en una tabla ya pensada para eso |

**Elegida: A.** `provider_subject` guarda el claim `sub` del ID Token (identificador estable de la cuenta de Google, FASE 6 de la tarea origen) — nunca el email, que en teoría podría cambiar sin que la cuenta de Google deje de ser la misma.

## Opciones consideradas — perfil incompleto (Google no entrega teléfono ni fecha de nacimiento)

| Opción | Descripción | Trade-off |
|---|---|---|
| **A — Crear la cuenta de inmediato, `profile_completed=false`, "Complete your profile" gatea el resto de la app (elegida)** | `phone`/`country_code`/`birth_date` pasan a nullable en `users`; nueva columna `profile_completed`; `ProtectedRoute.jsx` redirige a `/complete-profile` mientras sea `false`; se completa reutilizando `PATCH /api/users/me` (`ADR-003`), sin endpoint nuevo | Mismo criterio que `ADR-011` ya aplicó para "cuenta pendiente de verificar" (Estrategia A, usar una columna existente/nueva sobre `users` en vez de una tabla de "registros pendientes" separada) — la identidad ya está autenticada por Google, así que tiene sentido que la sesión ya exista (JWT válido) mientras se completa el resto |
| B — No crear la fila en `users` hasta que el onboarding esté completo (tabla de "registros pendientes" temporal) | `users` nunca tiene una fila "a medias" | Descartada por el mismo motivo que `ADR-011` §Opciones consideradas ya rechazó una tabla de pendientes separada: reimplementaría la unicidad de `email` que `users` ya garantiza, y todo el resto de THERS referencia `users.id` con FKs -- no hay necesidad real de posponer la creación de la fila |

**Elegida: A.**

## Opciones consideradas — username cuando Google no da uno usable

| Opción | Descripción | Trade-off |
|---|---|---|
| **A — Username provisorio generado con `secrets`, nunca mostrado como definitivo, `profile_completed=false` fuerza a elegir uno real (elegida)** | `domain/auth/placeholder_username.py`, formato `user_<12 hex>` — cumple el mismo regex que ya exige el registro tradicional | `users.username` sigue siendo `NOT NULL UNIQUE` -- hace falta *algún* valor para insertar la fila. La pantalla "Complete your profile" muestra el campo de username **vacío** (nunca prellenado con el placeholder), obligando a elegir uno real antes de terminar el onboarding -- nunca queda un username "raro" permanente sin que la persona lo haya visto y decidido activamente |
| B — Derivar el username de `email`/`name` (p. ej. `nombre.apellido123`) | Más "amigable" a primera vista | Descartada: sigue siendo un valor que la persona no eligió, con el mismo riesgo de colisión (`nombre.apellido`, `nombre.apellido2`...) que la tarea de origen pidió evitar explícitamente -- generar algo "menos feo" no cambia que sigue siendo no elegido |

**Elegida: A.**

## Decisión — account linking (FASE 9 de la tarea origen)

Política **determinística**, sin pedirle a la persona un paso de confirmación interactivo (ver razonamiento abajo):

| Escenario | Qué pasa |
|---|---|
| Ya existe una identidad de Google vinculada (mismo `sub`) | **Login directo** — nunca se vuelve a tocar `users`, ni siquiera si `name` cambió del lado de Google. |
| No existe ninguna cuenta con ese email | **Se crea una cuenta nueva** — `email_verified=true` (la garantía de Google reemplaza al OTP de THERS para este email, FASE 8/§Decisión de abajo), `profile_completed=false`, sin `password_hash`. |
| Ya existe una cuenta de THERS con ese email, **ya verificada** (`email_verified=true`) | **Se vincula automático** — se agrega la identidad de Google; cualquier contraseña que ya tuviera la cuenta **sigue existiendo**, Google se suma como método adicional, no reemplaza nada. |
| Ya existe una cuenta de THERS con ese email, **nunca verificada** (`email_verified=false`) | **Se reclama** — se vincula, se marca `email_verified=true`, y se **anula** cualquier `password_hash` existente. Razonamiento: nadie había probado nunca ser el dueño real de esa cuenta (podría haberla registrado alguien más, sin ser el dueño del correo, exactamente el riesgo que `ADR-011` ya identificó para reintentos de registro) — ahora que Google sí lo prueba, la cuenta pasa a la persona real, y cualquier contraseña que hubiera puesto quien la registró antes deja de servir. |
| Google indica `email_verified=false` en su propio ID Token (caso raro) | **Se rechaza** — no se crea, no se vincula, no se inicia sesión. Sin la garantía explícita de Google, no hay ninguna base para confiar en ese email. |

**Por qué no hace falta un paso de confirmación interactivo:** el riesgo real de account takeover en este escenario es que alguien registre una cuenta tradicional con el email de otra persona (sin ser su dueño) y luego el dueño real llegue con "Continuar con Google" — si se vinculara sin condiciones, el atacante conservaría su contraseña sobre una cuenta que el dueño real ahora también puede usar. La política de arriba ya cierra ese hueco de forma determinística: **solo se vincula sin anular nada cuando la cuenta ya estaba verificada** (alguien ya demostró ser su dueño antes, vía OTP); si nunca se verificó, se reclama y la contraseña existente se anula. No queda ningún escenario ambiguo que requiera pedirle a la persona una contraseña adicional para decidir qué hacer — la decisión ya es segura sin ese paso.

## Decisión — email verificado por Google (FASE 8)

Si el ID Token de Google trae `email_verified=true`, THERS **no** exige además el OTP de `ADR-011` para esa misma dirección de correo — la garantía de Google (una identidad autenticada por Google, con su propio `email_verified`) cumple el mismo propósito que el OTP: demostrar que la persona controla el correo. Exigir un segundo OTP sería redundante. **Nunca** se marca `email_verified=true` porque el Frontend lo diga — siempre proviene de un ID Token ya verificado criptográficamente por el backend (`GoogleIdentityVerifier.verify()`).

## Decisión — cuenta Google-only sin contraseña (FASE 10/12)

`users.password_hash` pasa a **nullable**. `NULL` significa exactamente "esta cuenta no tiene contraseña local" — nunca una contraseña vacía, ni un valor inventado (`"GOOGLE_USER"` u otro). `login_use_case.py` corta antes de llamar a `verify_password()` si `password_hash is None`, con el mismo `InvalidCredentialsError` genérico que cualquier otro login fallido (nunca revela que la cuenta es Google-only).

**"Set password" reutiliza el flujo de recuperación de contraseña existente (`ADR-010`) sin ningún cambio de código**: `forgot_password_use_case.py`/`verify_reset_code_use_case.py`/`reset_password_use_case.py` nunca asumen que `password_hash` ya tenía un valor — un `UPDATE password_hash = ...` funciona exactamente igual si el valor previo era `NULL`. Una cuenta Google-only que quiere "fijar su primera contraseña" simplemente usa `Forgot password` con su email — el resultado es indistinguible, a propósito, de una recuperación real (mismo criterio anti-enumeración: la respuesta nunca revela si la cuenta tenía o no una contraseña antes).

## Decisión — JWT (FASE 15)

Google autentica la identidad; THERS sigue siendo el único emisor de JWT. `POST /api/auth/google`, tras verificar y resolver el usuario, llama a `create_access_token(identity=user["id"])` -- el mismo mecanismo exacto que `POST /api/login`, con la misma `identity` (el UUID de `users.id`, nunca el `sub` de Google). Ningún endpoint protegido (incluido `GET /api/users/me`) sabe ni le importa si la sesión empezó por password o por Google.

## Decisión — modelo de datos

### `users` (columnas modificadas)

| Columna | Cambio | Justificación |
|---|---|---|
| `password_hash` | `NOT NULL` → `NULLABLE` | Cuenta Google-only sin contraseña local (§Decisión de arriba). |
| `phone` | `NOT NULL` → `NULLABLE` | Google no lo entrega. |
| `country_code` | `NOT NULL` → `NULLABLE` | Google no lo entrega. |
| `birth_date` | `NOT NULL` → `NULLABLE` | Google no lo entrega. |
| `profile_completed` | Nueva, `BOOLEAN NOT NULL DEFAULT true` | `true` para toda cuenta existente (siempre creada por el registro tradicional, que exige los tres campos de arriba) y para todo registro tradicional futuro; una cuenta Google nueva nace en `false` hasta completar `phone`/`country_code`/`birth_date` vía `PATCH /api/users/me`. |

El registro tradicional (`register_use_case.py`, vía la route) sigue exigiendo los tres campos relajados arriba a nivel de validación de formato -- nunca quedan en `NULL` en la práctica para una cuenta creada así.

### `user_identities` (tabla nueva)

| Columna | Tipo | Nulo | Justificación |
|---|---|---|---|
| `id` | `UUID`, `DEFAULT gen_random_uuid()` | No (PK) | Mismo patrón que el resto de entidades. |
| `user_id` | `UUID`, FK → `users.id`, `ON DELETE CASCADE` | No | Dueño de la identidad vinculada. |
| `provider` | `VARCHAR(20)` | No | `"google"` hoy -- string libre, no `ENUM` (mismo criterio que `notifications.type`). |
| `provider_subject` | `TEXT` | No | El claim `sub` del ID Token -- identificador estable, nunca el email. |
| `created_at` | `TIMESTAMPTZ`, `DEFAULT now()` | No | Auditoría de cuándo se vinculó. |

**Constraints:**
- `uq_user_identities_provider_subject` — índice único: `UNIQUE (provider, provider_subject)`. Garantiza a nivel de motor que la misma cuenta de Google nunca termine vinculada a dos usuarios de THERS a la vez.
- `ix_user_identities_user_id` — lookup de "identidades de este usuario" (hoy no expuesto por ningún endpoint, preparado para cuando lo esté).

## Decisión — contrato API

- **`POST /api/auth/google`** (público, nuevo) — `{"credential": "<ID Token>"}` → `{"token", "user"}` en éxito (mismo shape que `POST /api/login`). `400` si la credencial es inválida/expiró/audience o issuer incorrectos (todos con el mismo mensaje genérico, `InvalidGoogleCredentialError` unificado) o si Google indica `email_verified=false` (`GoogleEmailNotVerifiedError`, mensaje propio).
- El objeto `user` (compartido con register/login/me, `to_public_user`) gana `profile_completed` (booleano) y `has_password` (booleano, derivado — nunca expone `password_hash` en sí). `birth_date` puede ser `null` ahora (antes siempre una fecha).
- `PATCH /api/users/me` (`ADR-003`, sin cambio de contrato) es, sin ningún endpoint nuevo, la pantalla "Complete your profile" — cuando la actualización deja `phone`/`country_code`/`birth_date` completos, `profile_completed` pasa a `true` en la misma escritura.

## Seguridad

- **Verificación criptográfica real**: firma, `iss`, `aud` (Client ID exacto de THERS), `exp` -- todo vía `google.oauth2.id_token.verify_oauth2_token()` (librería oficial), nunca decodificación manual.
- **`aud` nunca es "cualquier Client ID de Google"** -- se exige exactamente `GOOGLE_CLIENT_ID` (config), así que un ID Token real de Google pero emitido para otra aplicación se rechaza igual.
- **`sub` como identificador estable**, nunca el email, para resolver "¿ya conozco esta cuenta de Google?" (FASE 6).
- **`email_verified` de Google nunca se confía por defecto** -- si Google mismo lo marca `false`, se rechaza (§Decisión "email verificado por Google").
- **Nunca se marca `email_verified=true` porque el Frontend lo diga** -- siempre viene de un ID Token ya verificado en el backend.
- **Account linking sin ambigüedad** (§Decisión de arriba) -- ninguna vinculación depende solo de que el email coincida; siempre se apoya en `email_verified` (de THERS o de Google) como señal de verdad.
- **`user_identities` con índice único** (`provider`, `provider_subject`) -- defensa de última línea contra dos requests concurrentes de `POST /api/auth/google` para una cuenta de Google que todavía no existía en THERS (condición de carrera); `IdentityAlreadyLinkedError` si el `IntegrityError` ocurre.
- **Nunca se guarda el Client Secret** -- este flujo no lo necesita (§Opciones consideradas, Opción A vs. B); no existe una variable `GOOGLE_CLIENT_SECRET` en `backend/.env.example`.
- **Nunca se loguea el `credential` ni ningún claim sensible** -- solo se propaga la excepción de dominio (`InvalidGoogleCredentialError`/`GoogleEmailNotVerifiedError`), nunca el JWT ni sus claims crudos.
- **JWT de THERS sin cambios de política** -- Google no altera la expiración, el algoritmo de firma, ni el `identity` (sigue siendo `users.id`).
- **CORS/CSRF**: el flujo de ID Token de Google Identity Services no usa redirect URI ni `state`/`nonce` propios de THERS (a diferencia del flujo de código de autorización) -- la superficie que esos mecanismos protegerían no existe en esta integración (§Opciones consideradas, Opción A). El único paso sensible del lado de THERS es la propia verificación de firma/`aud`/`iss`, ya cubierta arriba.

## Impacto en Backend

- `domain/auth/google_identity.py` (nuevo): puerto `GoogleIdentityVerifier` + `GoogleIdentity` (dataclass).
- `domain/auth/user_identity_repository.py` (nuevo): puerto `UserIdentityRepository`.
- `domain/auth/placeholder_username.py` (nuevo): generador de username provisorio.
- `domain/auth/exceptions.py`: nuevas `InvalidGoogleCredentialError`, `GoogleEmailNotVerifiedError`, `IdentityAlreadyLinkedError`.
- `domain/auth/repositories.py`: `UserRepository.create()` gana parámetros opcionales (`phone`/`country_code`/`birth_date`/`password_hash`/`email_verified`/`profile_completed`).
- `infrastructure/auth/google_id_token_verifier.py` (nuevo): adaptador sobre `google-auth`.
- `infrastructure/persistence/models.py`: `User` relaja `password_hash`/`phone`/`country_code`/`birth_date` a nullable, gana `profile_completed`; nuevo modelo `UserIdentity`.
- `infrastructure/persistence/repositories/user_identity_repository.py` (nuevo).
- `infrastructure/persistence/repositories/user_repository.py`: `create()` actualizado con los mismos parámetros opcionales.
- `application/auth/google_auth_use_case.py` (nuevo): orquesta los tres caminos (login directo, cuenta nueva, account linking/reclamo).
- `application/auth/login_use_case.py`: guarda contra `password_hash IS NULL`.
- `application/auth/update_profile_use_case.py`: recalcula `profile_completed` cuando corresponde.
- `application/auth/user_presenter.py`: gana `profile_completed`/`has_password`; `birth_date` tolera `None`.
- `interfaces/routes/auth_routes.py`: nueva `google_auth_route` (`POST /api/auth/google`), composición del verificador/repositorio nuevos.
- `config.py`: nueva `GOOGLE_CLIENT_ID`.
- `requirements.txt`: nueva `google-auth==2.58.0`.
- Nueva migración `b1e5d8a4f3c7` (altera `users`, crea `user_identities`; downgrade revierte ambos).
- Tests: `tests/test_google_id_token_verifier.py` (13 pruebas, sin red) + `tests/test_google_auth.py` (17 pruebas de integración, Google mockeado) + `tests/conftest.py` (TRUNCATE incluye `user_identities`).

## Impacto en Frontend

- `features/auth/lib/googleIdentityServices.js` (nuevo): carga del script oficial de Google Identity Services, sin librería npm.
- `features/auth/components/GoogleSignInButton.jsx` (nuevo): botón real de Google (`renderButton`), reutilizado en Login y Register.
- `features/auth/pages/CompleteProfile.jsx` (nueva): "Complete your profile", reutiliza `PATCH /api/users/me` vía `updateProfile()` (ya existente en `AuthContext.jsx`).
- `features/auth/context/AuthContext.jsx`: nueva `loginWithGoogle(credential)`.
- `features/auth/pages/Login.jsx`/`Register.jsx`: reemplazan el botón "Google" simulado (`useOAuthNotice`) por `GoogleSignInButton` real; Apple sigue simulado, sin cambios.
- `features/auth/hooks/useOAuthNotice.js`: comentario actualizado (ya no cubre Google).
- `app/router/ProtectedRoute.jsx`: redirige a `/complete-profile` mientras `user.profile_completed === false`.
- `app/router/router.jsx`: nueva ruta `/complete-profile` (protegida, fuera de `AppShell`).
- `features/auth/index.js`: exporta `CompleteProfile`.
- `.env.example` (Frontend): nueva `VITE_GOOGLE_CLIENT_ID`.

## Riesgos

- **Username provisorio ocupa el espacio de nombres hasta que se elige uno real** — mismo tipo de riesgo aceptado que `ADR-011` ya documentó para cuentas nunca verificadas; la probabilidad de colisión del generador (`secrets.token_hex`, 2^48 combinaciones) es despreciable, sin necesidad de un mecanismo de reintento dedicado.
- **Sin foto de perfil de Google** — decisión explícita (§No objetivos), no un hueco.
- **Sin Apple/Microsoft todavía** — el modelo (`user_identities`) ya está preparado; falta el adaptador y el botón correspondientes cuando se decida agregarlos.
- **Downgrade de la migración pierde datos si alguna fila real usa las columnas nuevas** — aceptable, mismo criterio que toda migración de esta app.

## Decisiones pendientes (quedan fuera, cada una es su propio ADR futuro)

- Apple/Microsoft u otros proveedores adicionales.
- Rate limiting de infraestructura para `POST /api/auth/google` (mismo hueco compartido con el resto de endpoints públicos, `ADR-010`/`ADR-011`).
- Limpieza periódica de cuentas con `profile_completed=false` abandonadas antes de completar el onboarding.
- Usar la foto de perfil de Google (`picture` claim) si el equipo decide que vale la pena.

## Consecuencias

- THERS pasa a tener dos métodos de autenticación reales (email+contraseña, Google), coexistiendo sin que ninguno reemplace al otro.
- `users` deja de exigir `phone`/`country_code`/`birth_date`/`password_hash` a nivel de esquema — la validación de esos campos para el registro tradicional sigue viviendo en la capa de aplicación (route/validators), no en la base de datos.
- El modelo de identidades externas (`user_identities`) queda listo para crecer a otros proveedores sin otra migración de `users`.
- `DATABASE_ARCHITECTURE.md`, `DATABASE_ERD.md` y `API_CONTRACT.md` se actualizan el mismo día que este contrato se implementa (`HB-001` §15.1).

## Referencias

- `CLAUDE.md` — jerarquía de fuentes (§4), regla de alcance (§14), reglas específicas para Claude Code (§8).
- `docs/architecture/ADR-010-password-reset-otp-flow.md` — flujo de recuperación de contraseña reutilizado tal cual para "Set password" en cuentas Google-only.
- `docs/architecture/ADR-011-mandatory-email-verification.md` — mismo criterio de "cuenta pendiente" (Estrategia A) aplicado acá a "perfil incompleto"; mismo criterio de "reclamar una cuenta nunca verificada" aplicado al account linking.
- `docs/architecture/DATABASE_ARCHITECTURE.md` §3 (principios de diseño), §5 (definición de `users`).
- `docs/architecture/organization/01_Manual_Organizacion/Source/HB-001-manual-organizacion.md.md` §11 (clasificación de impacto de decisiones), §15.1 (documentar endpoints el mismo día del PR), §19.1 (nunca loguear secretos).
- [Google Identity Services — Sign in with Google](https://developers.google.com/identity/gsi/web) — documentación oficial del mecanismo de Frontend usado.
- [`google-auth` (Python) — verificar ID Tokens](https://google-auth.readthedocs.io/) — librería oficial usada en el backend.

---

## Cierre
