# ADR-027 — Rate limiting de los endpoints de autenticación

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/ADR-027-rate-limiting.md` |
| Tipo | Architecture Decision Record (`HB-001` §11–12) |
| Fecha | 01/10/2026 |
| Estado | **Aceptada** — implementada en esta tarea (ver §Decisión) |
| Alcance | `backend/` — entidad `rate_limit_buckets`, `domain/rate_limiting/`, guard de aplicación, y el límite aplicado a nueve endpoints de `auth_bp` y `security_bp`; `Frontend/` — manejo del `429` en `getErrorMessage` |
| Autoridad sobre este documento | `/docs` oficial > estructura real observada en el código > este documento (mismo orden que `CLAUDE.md` §4) |

> Cierra el **ítem 8 de `API_CONTRACT.md` §9**, que v0.24 había registrado como pendiente explícito. Primer uso del código **429** en la API.

---

## Contexto

Ningún endpoint de THERS limitaba intentos ni frecuencia. Durante años de versiones de este contrato eso fue una buena práctica ausente sin consecuencias graves: una contraseña tiene entropía suficiente para que la fuerza bruta exhaustiva no sea práctica.

**`ADR-026` rompió esa suposición.** `POST /api/2fa/verify` acepta un código TOTP de **10⁶ combinaciones** dentro de una ventana de 30 segundos. Sin límite de intentos, quien ya tiene la contraseña (y por tanto el token de desafío) puede recorrer el espacio entero en minutos, y el segundo factor no protege nada. Era el agujero que `ADR-026` §Riesgos señaló como "el riesgo más serio de este ADR" y dejó abierto.

Hubo además un hallazgo de proceso: varios ADR (desde `ADR-019`) decían *"`API_CONTRACT.md` §9 ya registra el rate limiting como pendiente transversal"*. **No lo registraba.** La afirmación se propagó de ADR en ADR sin que nadie la verificara contra el documento. v0.24 lo corrigió añadiéndolo como ítem 8; este ADR lo resuelve.

### Qué ya estaba protegido (y no se duplica)

| Mecanismo | Qué cubre | Hueco que deja |
|---|---|---|
| `PASSWORD_RESET_MAX_ATTEMPTS` = 5 (`ADR-010`) | Intentos de verificar **un** código de reset | Es **por código**: pedir uno nuevo daba 5 intentos más |
| `REGISTRATION_MAX_ATTEMPTS` = 5 (`ADR-011`) | Ídem, para el código de registro | Ídem |
| Cooldown de 60 s (`ADR-010`/`ADR-011`) | Reenviar el código a **una** cuenta | No frena a una IP bombardeando **muchas** direcciones |

Este ADR **complementa** esos tres, no los reemplaza.

## Objetivos

- Que `POST /api/2fa/verify` deje de ser atacable por fuerza bruta.
- Acotar el relleno de credenciales en `POST /api/login`.
- Acotar el abuso de los endpoints que mandan correo o crean cuentas.
- Que el límite sea cierto **bajo concurrencia** y **con varios workers** — un ataque de fuerza bruta es concurrente por definición.
- Que alguien legítimo que se equivoca un par de veces y luego acierta no quede bloqueado.

## No objetivos (explícitamente fuera de este ADR)

- **No** limita los endpoints de producto (feed, posts, comentarios, mensajes, likes). Ahí el riesgo es abuso/DoS, no adivinar una credencial, y añadir una escritura en base por cada petición del feed sería un coste desproporcionado. Queda como pendiente aparte.
- **No** implementa un *rate limit* global por IP para toda la API. Eso pertenece a una capa anterior (proxy inverso, WAF, CDN), que es DevOps — sin documentación oficial (`CLAUDE.md` §15).
- **No** bloquea cuentas tras N fallos (*account lockout*). Un bloqueo persistente es un vector de denegación de servicio contra una persona concreta: cualquiera que sepa tu email podría dejarte afuera. La ventana que vence sola es deliberadamente preferible.
- **No** implementa CAPTCHA.
- **No** añade un `Retry-After` a respuestas que no sean `429`.
- **No** usa Flask-Limiter (ver §Opciones consideradas).

## Opciones consideradas — dónde vive el contador

| Opción | Trade-off |
|---|---|
| **A — Tabla en PostgreSQL (elegida)** | Correcto entre *workers* y sobrevive a un reinicio. Es el mismo criterio que el proyecto ya aplicó dos veces: `ADR-025` descartó una lista negra **en memoria** para revocar tokens por perderse al reiniciar, y `ADR-024`/`ADR-025` pusieron sus *throttles* en el propio `WHERE` para que funcionaran con varios *workers*. Cuesta una escritura por intento, pero solo en endpoints de autenticación |
| B — En memoria del proceso | Cero coste, pero con dos *workers* el límite real sería **el doble** del configurado, y un reinicio borraría todos los contadores. `ADR-014` sí se permitió memoria para el indicador de "escribiendo" y lo justificó explícitamente: es efímero y cosmético. Un control de seguridad no lo es |
| C — Flask-Limiter | Es la librería estándar y resuelve esto bien, **pero su almacenamiento recomendado es Redis**, que no está en el stack (agregarlo es una decisión de infraestructura, y DevOps no tiene documentación oficial). Su backend en memoria tiene el defecto de la opción B, y su backend de base de datos no cubre PostgreSQL de forma nativa. La alternativa propia son ~80 líneas y una tabla |
| D — Dejarlo pendiente | Es lo que había. Con `ADR-026` en producción, significa un segundo factor que no protege |

**Elegida: A.**

## Opciones consideradas — algoritmo

**Ventana fija** (una fila con `window_started_at` + `attempts`), no *sliding window log* ni *token bucket*.

El *sliding window* es más justo en el borde (con ventana fija, alguien puede gastar el límite al final de una ventana y otra vez al principio de la siguiente, duplicando el ritmo instantáneo). Pero exige una fila por intento y una consulta agregada por comprobación. Para lo que se está defendiendo —acotar 10⁶ combinaciones a 5 intentos— ese factor 2 en el peor caso no cambia nada: 10 intentos por 30 minutos sigue siendo inviable para un atacante. La simplicidad y el coste constante ganan.

## Opciones consideradas — ¿cuentan los aciertos?

**Las dos semánticas existen y la diferencia importa**, así que la regla lo declara (`clear_on_success`):

| Semántica | Para qué | Endpoints |
|---|---|---|
| **Cuenta fallos; un acierto borra el contador** | Credenciales. Lo que hay que frenar es *adivinar*, no *usar* — contar los aciertos bloquearía a quien entra y sale legítimamente varias veces | `login`, `2fa/verify`, los tres de gestión de 2FA, `verify-*-code` |
| **Cuenta todas las llamadas** | Cuando la llamada **en sí** tiene un coste aunque salga bien: mandar un correo, crear una cuenta. Acá el acierto **es** el abuso | `register`, `forgot-password`, `resend-registration-code` |

## Decisión

### Tabla `rate_limit_buckets`

Una fila por `(scope, identity_hash)`, con `window_started_at` y `attempts`.

- **`identity_hash` es SHA-256 de la identidad**, no la identidad en claro. La tabla solo necesita **contar**, nunca saber de quién: guardar emails e IPs en claro acumularía datos personales en una tabla puramente operativa cuando un hash cumple la misma función. SHA-256 y no scrypt porque acá no se protege un secreto de baja entropía contra fuerza bruta *offline* (como `password_hash`), solo se evita el dato en claro — y corre en el camino caliente de cada intento de login, donde un hash lento sería un coste innecesario.
- **Sin FK a `users`**, a propósito: la identidad puede ser una IP, o el email de una cuenta que no existe. Un intento contra un email inventado **también tiene que contar** (si no, se podría enumerar cuentas sin límite). Atarla a `users` dejaría fuera justo los casos que más interesa limitar.
- Es la única entidad del esquema que no modela un hecho del producto sino una defensa operativa: no aparece en ninguna respuesta de la API.

### El incremento es **una sola sentencia**

```sql
INSERT ... ON CONFLICT (scope, identity_hash) DO UPDATE SET
  attempts = CASE WHEN <ventana vencida> THEN 1 ELSE attempts + 1 END,
  window_started_at = CASE WHEN <ventana vencida> THEN now() ELSE window_started_at END
RETURNING attempts, extract(epoch FROM now() - window_started_at)
```

Crear la fila, reiniciar la ventana vencida y sumar el intento son **atómicos**. Si fueran tres pasos (leer, decidir, escribir), dos peticiones simultáneas leerían el mismo valor y escribirían el mismo incremento, perdiendo uno — y **la concurrencia es precisamente el escenario de un ataque de fuerza bruta**, no un caso raro.

**Bug real encontrado al implementar esto, y por qué el `RETURNING` calcula el tiempo transcurrido:** la primera versión obtenía `elapsed` con un `SELECT now() - window_started_at` **después** del `commit()`. Ese `SELECT` abría una transacción nueva que quedaba abierta, y en PostgreSQL `now()` es el instante de **inicio de transacción** — así que la llamada siguiente reutilizaba un `now()` rancio y **nunca veía la ventana como vencida**: el límite se volvía permanente. Se detectó con una prueba de reinicio de ventana. Calcularlo dentro del mismo `RETURNING` lo resuelve y además ahorra una consulta.

### Límites (`domain/rate_limiting/policy.py`)

| Endpoint(s) | Límite | Ventana | Identidad | Acierto |
|---|---|---|---|---|
| `POST /api/2fa/verify` | **5** | 15 min | cuenta **y** IP | borra |
| `POST /api/login` | 10 | 15 min | email **y** IP | borra |
| `POST /api/2fa/confirm`/`disable`/`recovery-codes` | 10 | 15 min | cuenta | borra |
| `POST /api/forgot-password`, `/resend-registration-code` | 5 | 15 min | IP | cuenta |
| `POST /api/register` | 5 | 1 hora | IP | cuenta |
| `POST /api/verify-reset-code`, `/verify-registration-code` | 15 | 15 min | IP | borra |

Son placeholders de producto explícitos y revisables, igual que `PASSWORD_RESET_MAX_ATTEMPTS` o `MAX_CONTENT_LENGTH`: reglas de negocio, no parámetros de despliegue, así que **no** se configuran por variable de entorno.

**5 intentos por 15 minutos en `2fa/verify`** deja la probabilidad de acierto por fuerza bruta en 5/10⁶ por ventana (0.0005%) — mismo orden de magnitud que `PASSWORD_RESET_MAX_ATTEMPTS` (`ADR-010`), deliberadamente, porque el problema es el mismo: un código corto que hay que proteger con intentos, no con entropía.

**Dos identidades donde se protege una cuenta concreta** (`login`, `2fa/verify`): por cuenta **y** por IP. La IP sola no alcanza porque `X-Forwarded-For` se falsifica y rotarla es trivial; la cuenta sola no alcanza porque no vería un ataque contra muchas cuentas desde un mismo origen.

### El guard se llama explícitamente, no desde un hook global

A diferencia del registro de actividad (`ADR-024`/`ADR-025`, que **sí** es un `after_request`), el límite es una línea visible al principio de cada route.

Un hook global tendría que saber qué *scope* y qué identidad corresponden a cada ruta, y esa correspondencia es justamente la decisión de producto de cada endpoint (¿por IP o por cuenta? ¿cuenta los aciertos?). Un mapa de rutas a reglas escondido en un hook sería más difícil de auditar que una línea en cada route — y **en un control de seguridad, poder auditarlo de un vistazo vale más que ahorrar la línea**.

### Orden de las comprobaciones

- **Antes** de verificar la credencial, nunca después: si se contara solo al fallar, el scrypt (lento a propósito) ya se habría ejecutado, y eso es por sí mismo un vector de agotamiento de CPU.
- En `2fa/verify`, **después** de validar el token de desafío: así un token basura no consume el presupuesto de intentos de una cuenta real (verificado por prueba).

### `429` + `Retry-After`

Primer uso de `429` en la API. No `403`: el pedido no está prohibido, está **de más** — y `429` es lo que cualquier cliente HTTP sabe interpretar como "frená y reintentá".

`retry_after_seconds` viaja **en el header `Retry-After` y en el body**. El header es el estándar; el body existe porque es lo que los llamadores del Frontend ya tienen a mano. Decir "demasiados intentos" sin decir cuánto esperar deja al cliente reintentando a ciegas: peor para la persona (no sabe cuándo volver) y peor para el servidor (sigue recibiendo peticiones).

### Purga

Las filas cuya ventana venció se borran de forma **oportunista**: una de cada 200 llamadas a `hit()` dispara un `DELETE` de lo vencido hace más de 24 h. No es un proceso programado porque el proyecto no tiene tareas periódicas (DevOps sin documentación oficial, `CLAUDE.md` §15). Un fallo de la purga nunca afecta al límite que se acaba de aplicar.

## Impacto en Frontend

- **`getErrorMessage`**: rama nueva para `429` que compone el mensaje con la espera formateada (segundos o minutos). Antes caía en `errors.unexpected` ("Ocurrió un error inesperado"), que es engañoso — no pasó nada inesperado.
- **`es.json`/`en.json`**: `errors.tooManyAttemptsSeconds` y `errors.tooManyAttemptsMinutes`, con interpolación (`translate.js` ya la soportaba).
- No hay cambios de componentes: todos los caminos afectados (login, 2FA, recuperación) ya mostraban el resultado de `getErrorMessage` por Toast.

## Impacto en Backend

- `migrations/versions/b6e3a9d4f270_create_rate_limit_buckets.py` (nueva).
- `domain/rate_limiting/`: `policy.py`, `repositories.py`, `exceptions.py` (nuevos).
- `infrastructure/persistence/models.py`: modelo `RateLimitBucket`.
- `infrastructure/persistence/repositories/rate_limit_repository.py` (nuevo).
- `application/rate_limiting/rate_limit_guard.py` (nuevo).
- `interfaces/routes/auth_routes.py`: seis endpoints limitados + helpers `_client_ip`/`_rate_limited_response`.
- `interfaces/routes/security_routes.py`: tres endpoints limitados.
- `tests/test_rate_limiting.py` (nuevo); `tests/conftest.py`: `rate_limit_buckets` en el `TRUNCATE` y el helper `reset_rate_limits()`.

**Nota sobre los tests:** los límites **no se relajaron** para que la suite pasara. Un test que legítimamente necesita más peticiones de las que un límite permite (uno de menciones registra doce cuentas) llama a `reset_rate_limits()` explícitamente. Un límite ajustado para que los tests pasen deja de ser el que protege producción, y esa diferencia es justo la que nadie recuerda después.

## Riesgos

- **Una escritura en base por intento de autenticación.** Solo en endpoints de auth, por índice único, pero es una escritura donde antes no había ninguna. No se midió con carga real (el proyecto no tiene entorno de carga, `CLAUDE.md` §15).
- **`X-Forwarded-For` se puede falsificar**, así que el límite por IP es evadible rotándolo. Mitigado donde importa (login y 2FA limitan **además** por cuenta, que no se puede falsear) pero **no** en los endpoints que solo limitan por IP: `register`, `forgot-password` y `verify-*-code` siguen siendo abusables por alguien dispuesto a rotar ese header. Cerrarlo de verdad exige confiar solo en la IP que inyecta un proxy conocido, que es configuración de despliegue — DevOps.
- **Ventana fija: ritmo instantáneo hasta 2× el configurado** en el borde entre ventanas. Aceptado conscientemente (§Opciones consideradas).
- **La tabla crece con cada identidad que haya intentado entrar.** La purga oportunista la acota, pero depende de que haya tráfico: en un sistema parado, las filas vencidas se quedan. No es un problema de volumen en este proyecto.
- **Un `429` puede alcanzar a alguien legítimo** detrás de un NAT compartido (una oficina, una universidad) donde muchas personas comparten IP. Los límites por IP son holgados justamente por eso, y los endpoints críticos limitan por cuenta en paralelo — pero el caso existe.
- **Los endpoints de producto siguen sin límite** (§No objetivos). No es un riesgo de credenciales, pero es una puerta abierta a abuso.

## Decisiones pendientes (cada una es su propio ADR futuro)

- *Rate limiting* de los endpoints de producto (feed, posts, comentarios, mensajes), con un mecanismo más barato que una escritura por petición.
- *Rate limit* en la capa anterior (proxy/WAF/CDN) — depende de DevOps.
- Confiar en `X-Forwarded-For` solo cuando lo inyecta un proxy conocido — depende de DevOps.
- Purga programada en vez de oportunista — depende de que exista un proceso periódico.
- CAPTCHA tras N fallos, como alternativa menos frustrante que esperar.
- *Sliding window* si el borde entre ventanas llega a importar.

## Consecuencias

- **`DATABASE_ARCHITECTURE.md` cambia** (tabla `rate_limit_buckets`) → v0.21.
- `API_CONTRACT.md` → v0.25. **`429` se incorpora al formato de error (§3)** y nueve endpoints pueden devolverlo. Ninguno cambia de forma en su camino de éxito. **El ítem 8 de §9 queda resuelto** para los endpoints de autenticación, y se reescribe para reflejar qué parte sigue pendiente (los de producto).
- `ADR-026` §Riesgos deja de tener su riesgo más serio abierto: el apartado se mantiene como registro histórico, con la referencia a este ADR.
- Un cliente que reintente en bucle ante un error empezará a ver `429`. Es el comportamiento deseado, pero es un cambio observable.

## Referencias

- `docs/architecture/ADR-026-two-factor-authentication.md` — el riesgo que este ADR cierra.
- `docs/architecture/ADR-010-password-reset-otp-flow.md`, `ADR-011-mandatory-email-verification.md` — los límites por código y cooldowns que ya existían, y el hueco que dejaban.
- `docs/architecture/ADR-025-session-registry.md` — precedente de descartar memoria del proceso para un control de seguridad.
- `docs/architecture/ADR-014-messages-ux-improvements.md` — el caso en que la memoria del proceso **sí** era aceptable, y por qué acá no.
- `docs/architecture/ADR-024-content-filters-and-privacy-preferences.md` — precedente del *throttle* impuesto en el propio `WHERE`.
- `CLAUDE.md` §15 — DevOps sin documentar, de donde viene el límite de varias mitigaciones de §Riesgos.

---

## Cierre

El agujero que `ADR-026` dejó señalado como el más serio queda cerrado: adivinar un código TOTP pasa de ser cuestión de minutos a ser inviable. Y de paso se corrige un defecto de proceso — una afirmación sobre el contrato que seis ADR repitieron sin que fuera cierta. Lo que sigue abierto está acotado y dicho: los endpoints de producto no tienen límite, y el límite por IP es evadible donde no hay una cuenta que anclar.
