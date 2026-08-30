# ADR-002 — Columnas de perfil en `users`: `username`, `phone`, `country_code`, `birth_date`

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/ADR-002-user-profile-fields.md` |
| Tipo | Architecture Decision Record (`HB-001` §11–12) |
| Fecha | 27/08/2026 |
| Estado | **Aceptada** — implementada en esta tarea (ver §3) |
| Alcance | `backend/` — modelo `users`, `POST /api/register`, `POST /api/login`, `GET /api/users/me` (nuevo) |
| Autor | Diego (decisión confirmada explícitamente en sesión de trabajo con IA, ver §6) |
| Autoridad sobre este documento | `/docs` oficial > estructura real observada en el código > este documento (mismo orden que `CLAUDE.md` §4) |

> ⚠️ **Nota de proceso, igual que `ADR-001`.** `HB-001` §12 especifica que los ADR se registran en Notion. Este documento sigue la misma excepción pragmática ya aceptada por el equipo en `ADR-001-language-switcher-i18n.md`: un ADR versionado junto al código. Numeración `ADR-002` es local a este repositorio, continuando `ADR-001`.

---

## 1. Contexto

`DATABASE_ARCHITECTURE.md` §4.B (Perfil) y §5 registraban explícitamente `username` (y, por extensión del mismo principio, `phone`/`country_code`/`birth_date`, que ni siquiera aparecían todavía como candidatas) como **OBJETIVO** — requisito funcional confirmado, pero sin modelado ratificado — con la nota expresa: *"se añadirán cuando el modelo de `users` se actualice por ADR, no ahora"*. `API_CONTRACT.md` §9 ítem 2 mantiene además la validación de formato de email y la política de contraseña como `PENDIENTE DE APROBACIÓN` — este ADR no las resuelve, las deja igual de pendientes.

El Frontend (`Register.jsx`, mergeado a `develop` antes de esta tarea) ya recolecta `username`, `phone` (`countryCode` + `phone`) y `birthDate`, pero explícitamente **no los envía todavía** al backend (comentario `TODO BACKEND` en el propio archivo) porque el contrato no los aceptaba. Esta tarea (THERS Backend Fase 2.1) pide dejar el flujo completo de Register/Login/`GET /api/users/me` funcionando de punta a punta contra PostgreSQL real, lo que requiere persistir esos cuatro campos.

Se marcó como bloqueo explícito ante el usuario antes de escribir código (contradicción con `DATABASE_ARCHITECTURE.md` §4.B/§14, regla de `CLAUDE.md` §14) y el usuario confirmó continuar escribiendo este ADR como parte de la misma tarea, en vez de detener el trabajo o implementar solo lo ya ratificado.

## 2. Opciones consideradas

| Opción | Descripción | Trade-off |
|---|---|---|
| **Columnas nuevas en `users` (elegida)** | Igual que `DATABASE_ARCHITECTURE.md` §4.B ya anticipaba para `username` ("Columna `users.username` (única)") | Sin nueva entidad ni FK; consistente con que hoy `users` es la única tabla y no hay todavía ningún otro perfil/entidad social que justifique separarlo |
| Tabla `profiles` separada (1:1 con `users`) | Aislaría datos de perfil de los datos de autenticación | Introduce una entidad y una relación nuevas sin ninguna necesidad funcional hoy (nadie consulta perfil sin autenticación); sobre-ingeniería para 4 columnas simples — contradice el principio de simplicidad ya aplicado en el resto de `/docs` (`FAS-001` §2, citado también por `DATABASE_ARCHITECTURE.md` §1) |

## 3. Decisión

Se agregan cuatro columnas a `users` (migración nueva, no se edita la migración `a1b2c3d4e5f6_create_users_table.py` ya fusionada):

| Columna | Tipo | Nulo | Único | Justificación |
|---|---|---|---|---|
| `username` | `VARCHAR(30)` | No | Sí (`uq_users_username`, siguiendo la convención de nombres de índice único de `DATABASE_ARCHITECTURE.md` §7) | Recolectado por `Register.jsx`; formato `^[a-zA-Z0-9_]{3,20}$` ya validado como UX en `Frontend/src/features/auth/lib/validators.js` — el backend replica el mismo formato como regla de negocio real (§4) |
| `phone` | `VARCHAR(20)` | No | No | Recolectado por `Register.jsx` (`PhoneField`); solo dígitos tras limpiar separadores, 7–15 dígitos (misma validación laxa que el Frontend, `isValidPhone`) |
| `country_code` | `VARCHAR(6)` | No | No | Recolectado por `Register.jsx` (`PhoneField` → `countryCode`, p. ej. `+503`); formato `^\+[1-9]\d{0,3}$` |
| `birth_date` | `DATE` | No | No | Recolectado por `Register.jsx` (`BirthDateField`, ISO `yyyy-mm-dd`) |

**No se usa `CITEXT`** para `username` (a diferencia de `email`): no hay ningún flujo hoy (login sigue siendo por email, no por username) que requiera comparación case-insensitive de `username`; se documenta como decisión explícita, no como omisión.

**Edad mínima.** Se replica en el backend el mismo valor placeholder que ya usa el Frontend (`MIN_AGE_YEARS = 13`, `Frontend/src/features/auth/lib/dateUtils.js`, comentado ahí mismo como "placeholder de UX... Backend deberá aplicar la misma regla... del lado del servidor"). Este ADR ratifica ese valor como la regla real del servidor — sigue siendo un placeholder de producto, no una política legal investigada; si el equipo decide otro valor, es un cambio a este mismo ADR, no una reinterpretación silenciosa.

**`confirm_password`** se valida en `interfaces/routes/auth_routes.py` (coincide con `password`) y **nunca** se pasa al caso de uso ni se persiste — no existe como columna.

**Validación de formato en el backend** (nuevo, `domain/auth/validators.py`, funciones puras sin Flask/SQLAlchemy): `username`, `phone`, `country_code`, `birth_date`/edad mínima. **No** se valida formato de `email` ni longitud mínima de `password` — siguen exactamente como estaban, `PENDIENTE DE APROBACIÓN` según `API_CONTRACT.md` §9 ítem 2, sin tocar en este ADR.

**`GET /api/users/me`** (nuevo): `@jwt_required()`, identidad exclusivamente desde `get_jwt_identity()`. Devuelve `{ "user": { id, username, email, name, phone, country_code, birth_date } }` — mismo objeto público que `register`/`login`, ahora también expuesto vía lectura. Nunca expone `password_hash`.

## 4. Consecuencias

- `POST /api/register` deja de aceptar solo `{name, email, password}` y pasa a requerir también `username`, `phone`, `country_code`, `birth_date`, `confirm_password` — cambio de contrato documentado el mismo día en `API_CONTRACT.md` (`HB-001` §15.1), no aditivo-compatible puro (los cuatro campos nuevos son obligatorios, no opcionales), porque un usuario sin ellos no tiene forma de iniciar sesión por username ni de cumplir el formulario ya mergeado a `develop`.
- El Frontend (`Register.jsx`) puede ahora enviar los campos que ya recolecta — esa integración (quitar el comentario `TODO BACKEND`, actualizar `useAuth`/`AuthContext`) queda **fuera de alcance** de esta tarea (backend-only, igual que `ADR` anterior de auth), y es el primer paso sugerido para el equipo (ver informe final).
- Cualquier entidad futura de perfil extendido (avatar, bio — `DATABASE_ARCHITECTURE.md` §4.B) sigue siendo su propia decisión objetivo, no heredada automáticamente de este ADR.
- `DATABASE_ARCHITECTURE.md` y `API_CONTRACT.md` se actualizan en la misma tarea para reflejar esta decisión (§5/§4.A/§4.B del primero; §4.1/§5 del segundo) — no queda pendiente de sincronización.

## 5. Verificación

Migración aplicada y revertida contra PostgreSQL 16 real (`thers_dev`, Docker Compose); 13 pruebas de integración existentes de `register`/`login` actualizadas para los campos nuevos + pruebas nuevas de validación y de `GET /api/users/me` corridas contra `thers_test` real (ver informe final de la tarea para el conteo exacto y el resultado de `pytest`).

## 6. Fuentes consultadas

- `CLAUDE.md` (raíz) — jerarquía de fuentes (§4) y regla de alcance (§14): esta decisión se marcó como bloqueo y se confirmó explícitamente con el usuario antes de escribir código.
- `docs/architecture/DATABASE_ARCHITECTURE.md` §4.B, §5, §14 — registro explícito de `username`/`phone`/`country_code`/`birth_date` como objetivo pendiente de ADR.
- `docs/architecture/API_CONTRACT.md` §9 — pendientes de validación de email/password, no tocados por este ADR.
- `docs/architecture/ADR-001-language-switcher-i18n.md` — precedente de formato y de la excepción de proceso (ADR en `docs/architecture/` en vez de Notion).
- Código real: `Frontend/src/features/auth/pages/Register.jsx`, `Frontend/src/features/auth/lib/validators.js`, `Frontend/src/features/auth/lib/dateUtils.js`, `Frontend/src/features/auth/components/PhoneField.jsx`.
- Confirmación explícita del usuario (Diego) sobre proceder con este ADR en la misma sesión que produjo este documento.

---

## Cierre

Este documento ratifica la incorporación de `username`, `phone`, `country_code` y `birth_date` a `users`, cerrando la contradicción registrada en `DATABASE_ARCHITECTURE.md` §4.B/§14 mediante el proceso de ADR que esos mismos documentos exigían antes de implementar. No resuelve ni reinterpreta ningún otro pendiente de `API_CONTRACT.md` §9 (formato de email, longitud de password) — esos siguen abiertos.
