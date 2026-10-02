# ADR-017 — Política de expiración y refresh de tokens JWT

- **Estado:** **`ACEPTADO`** el 2026-10-01 (decisión tomada junto a `ADR-016`).
  **Backend implementado el 2026-10-02** en la rama `feature/refresh-tokens` (sin commit
  ni merge todavía; 316 pruebas verdes). **Pendientes:** cliente móvil (§7, PR 2), adopción en la
  web (opcional) y mergear después de `ADR-015` (la migración encadena con `a5c8e2d71f34`).
- **Fecha:** 2026-10-01
- **Cierra:** `BACKEND_ARCHITECTURE.md` §20 ítem 9 («Política de expiración y refresh de tokens
  JWT»), registrado como `PENDIENTE DE APROBACIÓN` desde v0.7, y la nota equivalente de
  `API_CONTRACT.md` §4.2 («el token sigue sin política de expiración explícita configurada»).

---

## 1. Contexto — qué hay hoy, verificado

Verificado el 2026-10-01 instanciando la app real (`create_app()`), no leyendo documentación:

```
JWT_ACCESS_TOKEN_EXPIRES  = 0:15:00     <- default de flask-jwt-extended, nunca configurado
JWT_REFRESH_TOKEN_EXPIRES = 30 days     <- default de la librería, pero sin usar
```

- `app/config.py` **no fija ninguna** de las dos: el valor viene del default de la librería, no de
  una decisión del equipo.
- `create_refresh_token` **no aparece en ninguna parte del backend** — no hay refresh real.
- No hay logout de servidor ni blacklist: un token robado es válido hasta expirar.
- El Frontend web guarda el token en `localStorage` (`AuthContext.jsx`) y, ante un `401` de
  `GET /api/users/me`, limpia la sesión local.

**Efecto actual:** la sesión muere a los 15 minutos y la única salida es volver a introducir la
contraseña. En el web se tolera. En una app móvil es inaceptable, y además rompe cualquier registro
de dispositivo para push que dependa de una sesión viva.

## 2. Decisión

**Access token corto + refresh token de larga vida, con rotación y revocación.**

| Parámetro | Valor propuesto | Motivo |
|---|---|---|
| `JWT_ACCESS_TOKEN_EXPIRES` | **15 minutos, fijado explícitamente** | mismo valor que hoy, pero como decisión registrada y no como default accidental |
| `JWT_REFRESH_TOKEN_EXPIRES` | **30 días** | sesión móvil razonable sin volverse indefinida |
| Rotación | **cada uso del refresh emite un refresh nuevo y marca el anterior como usado** | un refresh robado sirve una sola vez |
| Detección de reuso | **reusar un refresh ya consumido revoca toda la familia de tokens de ese usuario** | convierte el robo en una sesión cortada y detectable, en vez de un acceso silencioso |
| Persistencia | tabla propia, guardando **hash** del token (nunca el valor crudo) | mismo criterio que `ADR-010`/`ADR-011` ya aplican a los códigos OTP |
| Logout | endpoint que revoca el refresh presentado | hoy no existe logout de servidor |

Los dos valores de tiempo son **placeholders de producto explícitos y revisables**, mismo criterio
que `MIN_AGE_YEARS` (`ADR-002` §3) y `MIN_PASSWORD_LENGTH` (`API_CONTRACT.md` v0.7).

### 2.1 Qué NO cambia

- `POST /api/login` y `POST /api/auth/google` siguen devolviendo `{token, user}`. El refresh se
  **agrega** al cuerpo; ningún campo existente cambia de nombre ni de significado.
- Ningún endpoint protegido cambia: siguen esperando `Authorization: Bearer <access>`.
- El formato de error `{"msg": "..."}` se mantiene (`API_CONTRACT.md` §3).
- El `401` homogeneizado de `app/extensions.py` sigue siendo la señal de «access token vencido».

Es decir: **cambio aditivo**, el Frontend web sigue funcionando sin tocarlo, y puede adoptar el
refresh cuando el equipo quiera.

## 3. Opciones consideradas

| Opción | A favor | En contra | Decisión |
|---|---|---|---|
| **A — Refresh token rotativo con revocación (elegida)** | Estándar para móvil; `flask-jwt-extended` ya lo soporta nativamente (`create_refresh_token`, `@jwt_required(refresh=True)`); habilita logout real y corta un token robado | Endpoint nuevo + tabla nueva + migración; el cliente debe evitar renovaciones paralelas | **Elegida** |
| B — Solo alargar el access token (7–30 días) | Cambio de una línea en `config.py`, sin migración | Un token robado vive semanas **sin ninguna forma de revocarlo**: no hay blacklist ni logout. Empeora la postura de seguridad justo cuando se amplía la superficie a una app instalada en teléfonos | Descartada |
| C — Dejarlo como está | Nada que implementar | La app móvil pediría contraseña cada 15 minutos; el registro de dispositivo para push no tendría sesión estable donde apoyarse | Descartada |
| D — Sesiones con cookies | Revocación del lado del servidor «gratis» | Cambiaría el contrato de toda la API y el modelo CORS que el web ya tiene afinado, para resolver un problema que A resuelve sin romper nada | Descartada |

## 4. Reglas de implementación (vinculantes cuando se implemente)

1. **El refresh token nunca se guarda en claro**, ni en la base de datos ni en logs — hash, igual
   que los códigos OTP de `ADR-010`/`ADR-011`.
2. **Un refresh token no sirve como access token.** `flask-jwt-extended` ya distingue ambos tipos;
   ningún endpoint protegido debe aceptar uno de refresh.
3. **La rotación es atómica**: consumir el viejo y emitir el nuevo en la misma transacción, con un
   índice único que impida dos tokens activos de la misma cadena (mismo patrón de índice único
   parcial que `ADR-010` usa para los códigos de recuperación).
4. **El cliente nunca hace renovaciones en paralelo.** Una sola renovación en vuelo, el resto de las
   peticiones esperan; ante `401` en la renovación, se cierra sesión limpiamente (sin bucles de
   reintento, `THERS_PROMPT_CLAUDE_ANDROID.md` §7).
5. **En móvil el refresh vive en SecureStore**, nunca en AsyncStorage, archivos planos, logs ni URLs.
   El access token puede quedar en memoria.
6. **Logout limpia los dos lados**: revoca en el servidor y borra el almacenamiento local,
   incluida la asociación de push cuando exista.
7. **Se documenta en `API_CONTRACT.md` el mismo día del PR** (`HB-001` §15.1), con su propia versión
   del changelog.
8. **Pruebas obligatorias** antes de cerrar: refresh válido renueva; refresh rotado y reusado revoca
   la familia; refresh expirado rechaza; un access token no sirve para renovar; logout invalida.

## 5. Riesgos aceptados

- Un refresh de 30 días en un teléfono perdido mantiene acceso hasta que alguien revoque. Mitigación
  mínima aceptada: revocación por reuso (§2) + logout real. Una pantalla de «dispositivos activos»
  queda **fuera** de alcance, como ADR futuro.
- La rotación mal implementada puede expulsar a usuarios legítimos en condiciones de carrera (dos
  peticiones renovando a la vez). La regla 4 existe precisamente para eso y debe probarse.
- Mientras esto no se implemente, **cualquier app móvil que se construya tendrá sesiones de 15
  minutos**. Es una limitación conocida de la primera entrega, no un defecto a descubrir después.

## 7. Decisiones de implementación y plan (2026-10-02)

Estas cinco decisiones las tomó el propietario del proyecto el 2026-10-02 al revisar el plan; **son
una enmienda de implementación, pendiente de revisión del equipo**. No cambian la decisión de §2.

| # | Decisión | Resultado |
|---|---|---|
| 1 | Al resetear la contraseña (`reset-password`) se **revocan todas las familias** de refresh del usuario | Adoptada. No estaba en §2 |
| 2 | En móvil se guardan **ambos** tokens en SecureStore (§4.5 permitía el access solo en memoria) | Adoptada: se intenta `GET /users/me` primero, así un arranque en frío sin red no equivale a sesión cerrada |
| 3 | Hash del refresh: **SHA-256 del `jti`**, no scrypt | Adoptada: el token es de alta entropía; scrypt es para los códigos OTP de 6 dígitos |
| 4 | Respuesta de refresh perdida por la red → el cliente reintenta con un token ya consumido y se revoca la familia | **Riesgo aceptado en la v1**, igual que §5 |
| 5 | Varias sesiones simultáneas por usuario | Adoptada: una familia por login, sin límite |

**Variables de entorno:** `JWT_ACCESS_TOKEN_EXPIRES` y `JWT_REFRESH_TOKEN_EXPIRES` deben poder
sobreescribirse por entorno, para probar la renovación en un dispositivo con un access de segundos.

**Plan por PR** (rama `feature/*` → `develop`, `HB-001` §7–9):

1. **Backend.** `config.py` (valores explícitos); tabla `refresh_tokens` (`id`, `user_id` con cascada,
   `family_id`, `token_hash`, `created_at`, `expires_at`, `used_at`, `revoked_at`, `replaced_by_id`)
   con índice único parcial «un token activo por familia»; puerto `RefreshTokenRepository` + casos
   de uso emitir/rotar/cerrar sesión (rotación atómica con `SELECT … FOR UPDATE`);
   `POST /api/refresh` y `POST /api/logout`; `refresh_token` añadido a login y Google; comprobar que
   un refresh usado como access da `401` y no `422`; pruebas de §4.8 más carrera de dos renovaciones;
   `API_CONTRACT.md` v0.21 el mismo día (`HB-001` §15.1).
2. **Móvil.** Refresh en SecureStore; una sola renovación en vuelo; ante `401`, renovar y reintentar
   **una vez**; un fallo de red no cierra sesión; logout con llamada al servidor (si falla, limpia
   igual). Se aprovecha para enviar `Cache-Control: no-store` en respuestas autenticadas.
3. **Web (opcional).** Adoptar el refresh; el cambio es aditivo, el web actual sigue funcionando.

**Dependencia bloqueante:** la nueva migración encadenaría con `a5c8e2d71f34` (perfil y media,
`ADR-015`), que a 2026-10-02 **no está commiteada ni en `origin/develop`**. El PR de backend no
puede mergearse antes que ese trabajo.

## 6. Documentos relacionados

- `docs/architecture/ADR-016-mobile-stack.md` §5 — este ADR es el bloqueo que ahí se señala.
- `docs/architecture/BACKEND_ARCHITECTURE.md` §20 ítem 9 — el hueco que este ADR cierra.
- `docs/architecture/API_CONTRACT.md` §4.2 — deberá reflejar los endpoints nuevos al implementarse.
- `docs/architecture/ADR-010-password-reset-otp-flow.md` — criterio de hash + índice único parcial
  reutilizado aquí.
- `docs/mobile/READINESS.md` §4.1 — evidencia de verificación del estado actual.
