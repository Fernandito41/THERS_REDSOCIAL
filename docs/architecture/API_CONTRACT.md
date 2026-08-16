# API_CONTRACT

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/API_CONTRACT.md` |
| Versión | 0.1 (Propuesta) |
| Estado | **Pendiente de ratificación formal del equipo** (proceso de decisiones de alto impacto, `HB-001` §11–12) |
| Depende de | `BACKEND_ARCHITECTURE.md` (fuente directa del estado real del backend), `DATABASE_ARCHITECTURE.md` (modelo de datos disponible), `FRONTEND_ARCHITECTURE.md` (consumidor del contrato), `HB-001` §15.1 (exige documentar cada endpoint el mismo día del PR) |
| Autoridad sobre este documento | `/docs` oficial > estructura real observada en el código > este documento (mismo orden que `CLAUDE.md` §3) |

> ⚠️ **Nota de estado.** Este documento nace de un hueco identificado en la auditoría arquitectónica integral de THERS: no existía ninguna fuente única de verdad para el contrato entre Frontend y Backend, pese a que `HB-001` §15.1 ya exige documentar cada endpoint el mismo día de su PR. `BACKEND_ARCHITECTURE.md` §14 declara explícitamente fuera de su propio alcance "el catálogo completo de endpoints" — este documento es esa pieza separada, y hasta ahora no existía ninguna.
>
> Sigue el mismo método que `BACKEND_ARCHITECTURE.md`, `DATABASE_ARCHITECTURE.md` y `FRONTEND_ARCHITECTURE.md` ya validaron: separa explícitamente **lo implementado** (un único endpoint real, con limitaciones conocidas) de **lo pendiente de definición** (formato de error estándar, convención de paginación, versionado de API, etc.). No se inventa aquí ningún endpoint, contrato o convención que el código o la documentación oficial no respalden todavía.
>
> Este documento no implementa, refactoriza ni modifica ningún código de `backend/` ni de `Frontend/`. Documenta el contrato tal como existe hoy y, donde falta una decisión, señala el hueco explícito — nunca un contrato inventado.

---

## 1. Propósito y alcance

**Propósito.** Ser la única fuente de verdad del contrato HTTP entre `Frontend/` y `backend/`: qué endpoints existen, qué reciben, qué devuelven, cómo se autentican y cómo se comunican los errores — de modo que Backend y Frontend puedan implementar en paralelo contra el mismo contrato acordado, en vez de negociarlo ad-hoc en cada feature (que es lo que ha ocurrido hasta ahora: `Register.jsx` ya asume un endpoint `/register` que el backend no expone).

**Alcance.** Cubre exclusivamente el contrato HTTP expuesto por `backend/` bajo el prefijo `/api` y consumido por `Frontend/` a través de `shared/lib/api.js`. Incluye: catálogo de endpoints, formato de request/response, autenticación, formato de error, códigos HTTP y convenciones para endpoints futuros.

**Fuera de alcance de este documento:**
- Implementación interna del backend (capas `domain/`, `application/`, `interfaces/`) — cubierta por `BACKEND_ARCHITECTURE.md`.
- Modelo de datos y persistencia — cubierto por `DATABASE_ARCHITECTURE.md`.
- Cómo el Frontend consume el contrato internamente (hooks, componentes, estado) — cubierto por `FRONTEND_ARCHITECTURE.md`.
- Especificación formal OpenAPI/Swagger — se evalúa como evolución futura (§10), no se adopta en esta versión por ser desproporcionado frente a un único endpoint real (principio de simplicidad, mismo criterio que `FAS-001` §2 aplica por analogía en los otros documentos de THERS).
- Autorización por roles/permisos — no existe ningún concepto de rol en el sistema hoy (`BACKEND_ARCHITECTURE.md` §9); no se inventa aquí.

---

## 2. Convenciones generales

| Aspecto | Estado |
|---|---|
| Prefijo base | `/api` — todos los blueprints se registran bajo este prefijo (`create_app()`, `url_prefix="/api"`) |
| Formato de body | JSON exclusivamente, en request y response (`request.get_json()` / `jsonify(...)`) — sin excepción observada en el código actual |
| Autenticación | `Bearer <jwt>` en el header `Authorization` — **convención estándar de `flask_jwt_extended`, no verificada contra ningún endpoint protegido real porque ninguno existe todavía** (`BACKEND_ARCHITECTURE.md` §9: "Ningún endpoint protegido todavía") |
| Verbos HTTP | Declarados explícitamente por ruta (`methods=["POST"]`); **no hay convención documentada** todavía para operaciones futuras (GET de colección, PUT/PATCH de actualización, DELETE) — `PENDIENTE DE APROBACIÓN` (§9) |
| Versionado de API | **No existe.** No hay prefijo de versión (`/api/v1`) ni ningún mecanismo de versionado — `PENDIENTE DE APROBACIÓN` (§9) |
| Paginación | **No existe.** Ningún endpoint actual devuelve una colección — `PENDIENTE DE APROBACIÓN` (§9) |
| CORS | Habilitado globalmente sin restricción de origen (`CORS(app)`, `BACKEND_ARCHITECTURE.md` §13) — responsabilidad del backend, el Frontend no la controla |

---

## 3. Formato de error

**Estado actual observado (no un estándar diseñado, es lo que el único endpoint existente ya produce):**

```json
{ "msg": "<texto del error>" }
```

- Usado para validación fallida (`400`) y credenciales inválidas (`401`).
- No hay campo de código de error machine-readable, ni estructura anidada (`{"error": {"code": ..., "message": ...}}`).
- No hay manejador global de excepciones (`@app.errorhandler`) registrado en `create_app()` — un `500` o `404` no manejado hoy cae en el comportamiento HTML por defecto de Flask, no en JSON (`BACKEND_ARCHITECTURE.md` §11).

**`PENDIENTE DE APROBACIÓN`** (§9): definir un formato de error único para toda la API antes de que existan más endpoints que cada uno improvise el suyo. Este documento no fija ese estándar por iniciativa propia — depende de una decisión de backend (`BACKEND_ARCHITECTURE.md` §20, ítem 5) que este contrato debe reflejar cuando se ratifique, no anticipar.

---

## 4. Catálogo de endpoints

### 4.1 Implementados

#### `POST /api/login`

| Campo | Valor |
|---|---|
| Estado | **IMPLEMENTADO** |
| Blueprint | `auth_bp` (`backend/app/interfaces/routes/auth_routes.py`) |
| Auth requerida | No (endpoint público — emite el token) |

**Request body**
```json
{
  "email": "string",
  "password": "string"
}
```

**Response — éxito (200)**
```json
{
  "token": "string (JWT)",
  "user": {
    "email": "string",
    "name": "string"
  }
}
```

**Response — error**

| Código | Causa | Body |
|---|---|---|
| `400` | Body vacío, o `email`/`password` ausentes | `{"msg": "..."}` |
| `401` | Credenciales inválidas | `{"msg": "..."}` |

**Limitaciones conocidas (heredadas literalmente de `BACKEND_ARCHITECTURE.md` §9/§19 — no se repiten como novedad, se citan porque afectan directamente lo que el Frontend puede asumir de este endpoint):**
- La validación compara contra una única credencial hardcodeada en código (`test@test.com` / `123456`) — no hay usuarios reales ni base de datos detrás.
- El objeto `user` devuelto es siempre `{"email": email, "name": "Fernando"}` — el campo `name` está hardcodeado, no proviene de ningún dato real asociado al `email` recibido.
- **Corregido:** la contraseña ya no se compara en texto plano — `domain/auth/auth_service.py` usa `werkzeug.security.check_password_hash` contra un hash `scrypt` de la credencial de prueba. Sigue siendo una única credencial hardcodeada (sin tabla `users` real); el algoritmo definitivo para el modelo de datos persistido sigue sin ratificar (`BACKEND_ARCHITECTURE.md` §20, ítem 3).
- El token no tiene política de expiración explícita configurada.

### 4.2 Esperados por el Frontend pero NO implementados

#### `POST /api/register` — **NO EXISTE EN EL BACKEND**

| Campo | Valor |
|---|---|
| Estado | **NO IMPLEMENTADO** |
| Evidencia de que se espera | `Frontend/src/features/auth/pages/Register.jsx` ya recolecta `name`/`email`/`password` en un formulario completo, pero `handleRegister` no llama a ningún endpoint — hace `console.log(form)` y navega a `/login` (comentario `// temporal` en el propio código) |
| Confirmación del hueco | `BACKEND_ARCHITECTURE.md` §9: "Sin registro (`register`): el Frontend ya tiene una página `Register.jsx`... pero el backend no expone ningún endpoint de registro" |

**No se define aquí un contrato hipotético para este endpoint** (request/response, validaciones) — hacerlo sería inventar una decisión de backend/base de datos que no está ratificada (`DATABASE_ARCHITECTURE.md` §5 solo ratifica `users` con `name`/`email`/`password_hash`, sin definir reglas de negocio de registro como duplicados de email, longitud mínima de contraseña, etc.). Se lista en §9 como decisión pendiente de mayor prioridad del roadmap (Fase 1 de la hoja de ruta técnica de THERS).

### 4.3 Endpoints protegidos — ninguno existe

No hay ningún endpoint que use `@jwt_required()` en el código actual (`BACKEND_ARCHITECTURE.md` §9). Esto significa que este documento **no tiene todavía ningún caso real de "endpoint protegido"** que documentar como patrón validado — cuando exista el primero, deberá añadirse aquí con su convención exacta de envío del header `Authorization`.

---

## 5. Modelo de datos expuesto por la API

Este documento no define el modelo de datos (eso es `DATABASE_ARCHITECTURE.md`) pero sí documenta **qué forma tiene el dato tal como cruza la frontera HTTP**, que puede no coincidir 1:1 con el modelo de persistencia:

| Objeto | Campos expuestos hoy | Fuente |
|---|---|---|
| `user` (en response de login) | `email`, `name` | `BACKEND_ARCHITECTURE.md` §6; coincide con la única entidad ratificada `users` en `DATABASE_ARCHITECTURE.md` §4.A, sin exponer `password_hash` (correcto — nunca debe exponerse) |

Cuando `DATABASE_ARCHITECTURE.md` incorpore columnas objetivo de `users` (`username`, `avatar_url`, `bio` — §4.B de ese documento), este catálogo deberá actualizarse el mismo día en que el endpoint correspondiente las exponga (`HB-001` §15.1) — no antes, no por anticipación.

---

## 6. Autenticación y autorización

- **Mecanismo:** JWT emitido por `flask_jwt_extended`, `create_access_token(identity=user["email"])` (`BACKEND_ARCHITECTURE.md` §9).
- **Convención de envío (para cuando exista el primer endpoint protegido):** header `Authorization: Bearer <token>` — convención estándar de la librería usada, no verificada contra código real todavía.
- **Almacenamiento en el Frontend:** `localStorage` (`useAuth.js`) — decisión ya registrada como `PENDIENTE DE APROBACIÓN` en `FRONTEND_ARCHITECTURE.md` §16, no se repite la discusión aquí.
- **Autorización (roles/permisos):** no existe ningún concepto en el sistema — no se documenta lo que no existe.

---

## 7. Errores de red y disponibilidad (responsabilidad del Frontend)

- El Frontend hoy maneja fallos de la llamada de login con `try/catch` + `alert()` (`Login.jsx`) — sin distinguir error de red, timeout, o error de servidor. Documentado en `FRONTEND_ARCHITECTURE.md` §12, no se repite aquí como contrato porque no es parte del contrato HTTP en sí, sino de cómo el Frontend reacciona a él.
- Este documento no impone un estándar de manejo de errores en el cliente — esa es responsabilidad de `FRONTEND_ARCHITECTURE.md`.

---

## 8. Qué NO cambia con este documento

- No se crea, modifica ni elimina ningún endpoint real.
- No se ratifica un formato de error nuevo — se documenta el actual y se señala como pendiente de estandarizar.
- No se adopta OpenAPI/Swagger en esta versión.
- No se define el contrato de `/register` ni de ningún endpoint futuro — se señala su ausencia, no se inventa su forma.

---

## 9. PENDIENTES DE APROBACIÓN

Decisiones que este documento **no toma** porque no están respaldadas por código ni por documentación oficial ratificada. Cada una debe resolverse como ADR (`HB-001` §11–12) antes de implementarse:

1. **Formato estándar de error** para toda la API (heredado de `BACKEND_ARCHITECTURE.md` §20, ítem 5 — este documento debe reflejarlo, no decidirlo).
2. **Contrato de `POST /api/register`** — campos, validaciones (unicidad de email, longitud mínima de contraseña), respuesta.
3. **Convención de verbos HTTP** para operaciones futuras (colecciones, actualización parcial, borrado).
4. **Versionado de API** (`/api/v1` u otro mecanismo) — o la decisión explícita de no versionar todavía.
5. **Paginación** — formato (offset/limit, cursor) para cuando exista el primer endpoint de colección (p. ej. feed).
6. **Convención de endpoints protegidos** — primer caso real que fije el patrón (dónde se coloca `@jwt_required()`, cómo se documenta aquí).
7. **Especificación formal (OpenAPI/Swagger)** y su ubicación — evaluar cuando el catálogo de endpoints crezca lo suficiente para justificar el costo de mantenerla (`HB-001` §15.1 menciona esta opción sin decidirla, igual que `BACKEND_ARCHITECTURE.md` §14).

---

## 10. Evolución de este documento

Cada endpoint nuevo se documenta aquí **el mismo día de su PR** (`HB-001` §15.1, regla ya vigente, sin excepción). Este documento crece por adición de secciones en §4, sin reestructurarse — mismo principio de escalabilidad por adición que `REPOSITORY_STRUCTURE.md` §2 y `DATABASE_ARCHITECTURE.md` §3 ya aplican en sus respectivos dominios.

Si el catálogo de endpoints crece lo suficiente para que un Markdown plano deje de ser manejable, migrar a OpenAPI/Swagger es una decisión de impacto medio (§9, ítem 7) — no una consecuencia automática de este documento.

---

## Fuentes consultadas

- `CLAUDE.md` (raíz) — índice de reglas operativas y jerarquía de fuentes.
- `docs/architecture/BACKEND_ARCHITECTURE.md` — fuente directa del estado real del único endpoint implementado (§5, §6, §9, §11, §14).
- `docs/architecture/DATABASE_ARCHITECTURE.md` — modelo de datos disponible para exponer (§4.A, §5).
- `docs/architecture/FRONTEND_ARCHITECTURE.md` — consumidor del contrato (§9, §10, §12, §16).
- `docs/architecture/organization/01_Manual_Organizacion/Source/HB-001-manual-organizacion.md.md` — §15.1 (documentar endpoints el mismo día del PR), §11–12 (proceso de ADR).
- Código fuente: `backend/app/interfaces/routes/auth_routes.py`, `backend/app/application/auth/login_use_case.py`, `backend/app/domain/auth/auth_service.py`, `backend/app/__init__.py`; `Frontend/src/features/auth/hooks/useAuth.js`, `Frontend/src/features/auth/pages/Login.jsx`, `Frontend/src/features/auth/pages/Register.jsx`.

---

## Cierre

Este documento **no modifica** el backend ni el Frontend: define el contrato de API que ambos deben respetar hacia adelante, separando explícitamente **lo implementado** (§4.1), **lo esperado pero ausente** (§4.2) y **lo pendiente de aprobación** (§9). Cualquier cambio a este contrato sigue el proceso de decisiones de impacto medio/alto de `HB-001` §11–12 (ADR), no el criterio individual de quien implementa. A partir de su ratificación, Backend y Frontend deben implementar contra este documento — no negociar el contrato de forma ad-hoc en cada feature.
