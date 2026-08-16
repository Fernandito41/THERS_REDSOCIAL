# BACKEND_ARCHITECTURE

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/BACKEND_ARCHITECTURE.md` |
| Versión | 0.3 (Propuesta) |
| Estado | **Pendiente de ratificación formal del equipo** (proceso de decisiones de alto impacto, `HB-001` §11–12) |
| Depende de | `HB-001` (Manual de Organización), `REPOSITORY_STRUCTURE.md` §6, `CLAUDE.md` §4/§14, código real de `backend/` |
| Autoridad sobre este documento | `/docs` oficial > estructura real observada en el código > este documento (mismo orden que `CLAUDE.md` §3) |

> ⚠️ **Nota de estado.** `HB-001` §0 declara explícitamente que no define arquitectura técnica profunda y que "esos temas se documentarán en manuales técnicos separados" — este documento es esa pieza separada, y hasta ahora no existía ninguna. No hay, previo a este documento, ningún documento oficial ratificado de arquitectura backend: solo estructura *observada* en el código (`REPOSITORY_STRUCTURE.md` §6, marcada allí como "propuesta a confirmar"). Este documento documenta y consolida la estructura observada como propuesta de contrato técnico, pero **no la ratifica por sí mismo** — sigue el proceso de gobernanza de `HB-001` §11–12 antes de tratarse como cerrado. Toda sección que introduce una decisión no respaldada por código ni por documento previo se marca explícitamente como `PENDIENTE DE APROBACIÓN` (ver sección 20).
>
> **v0.2 — actualización tras corrección de seguridad puntual (pedida explícitamente por el equipo, no iniciativa de este documento):** se corrigieron dos hallazgos de la auditoría arquitectónica integral de THERS marcados como `CONFLICTO` de prioridad P0 — `JWT_SECRET_KEY` hardcodeado (ahora vía `os.environ` + `.env.example` + `.gitignore`) y comparación de contraseña en texto plano (ahora `werkzeug.security.check_password_hash`). Ambas correcciones están reflejadas en las secciones 9, 12, 16, 19 y 20.
>
> **v0.3 — actualización tras publicar `backend/requirements.txt`:** se creó el archivo de dependencias, fijando únicamente los paquetes que el código actual importa (Flask, flask-cors, Flask-JWT-Extended), deliberadamente sin `Flask-SQLAlchemy`/`SQLAlchemy` para no adoptar una decisión de persistencia sin ratificar. Reflejado en las secciones 2, 18 y 20. Ninguna otra sección de este documento cambió — sigue siendo, en todo lo demás, la misma propuesta v0.1 pendiente de ratificación.
>
> Fuera de esta actualización puntual, este documento no implementa, refactoriza ni modifica código de `backend/` por iniciativa propia. Documenta lo que existe y propone, donde falta una decisión, el hueco explícito — nunca una arquitectura inventada.

---

## 1. Propósito y alcance

**Propósito.** Establecer el contrato técnico propuesto de la arquitectura Backend de THERS: sus capas, el flujo de una petición, autenticación, persistencia, configuración, seguridad y reglas de dependencia — de modo que la implementación futura siga la documentación y no al revés (mismo principio que `FAS-001` §1 aplica al Frontend: "el código sigue a la documentación, no al revés").

**Alcance.** Cubre exclusivamente `backend/`: su estructura interna, el código Python/Flask ya implementado, sus dependencias, y las decisiones de arquitectura que ese código ya asume implícitamente.

**Fuera de alcance de este documento:**
- Frontend (`Frontend/`) y Handbook (`handbook/`) — arquitecturas propias, ya cubiertas por `FAS-001` y `ARC-001` respectivamente.
- Esquema, normalización, índices, migraciones y backups de PostgreSQL — sin documentar en ningún archivo de `/docs` (`CLAUDE.md` §14); no se inventan aquí.
- DevOps, Docker, CI/CD, despliegue — fuera del alcance declarado de `HB-001` §0 y sin ningún otro documento que los cubra.
- Catálogo completo de endpoints de la API — explícitamente pedido fuera de alcance por el usuario en esta tarea; ver sección 14.

**Fuentes consultadas para este documento:** ver sección "Fuentes consultadas" al final.

---

## 2. Stack Backend

| Tecnología | Estado en `/docs` | Estado en el código | Observación |
|---|---|---|---|
| Python | Confirmado como lenguaje del backend (`HB-001` §2, tabla de roles) | 3.14.3 en `backend/venv/pyvenv.cfg` | Versión de entorno local, **no fijada** en ningún archivo del repositorio (no hay `.python-version` ni versión mínima documentada) |
| Flask | Confirmado (`HB-001` portada y §2) | 3.1.3 (`pip freeze` en `backend/venv`) | Implementado — factory `create_app()` en `backend/app/__init__.py` |
| flask-cors | No mencionado por nombre en `/docs` | 6.0.2 instalado, usado en `create_app()` | Ver sección 13 |
| Flask-JWT-Extended | JWT confirmado como mecanismo de auth (`HB-001` portada; `CLAUDE.md` §4 lo nombra explícitamente como `flask_jwt_extended`) | 4.7.1 instalado y en uso (`app/extensions.py`, `app/interfaces/routes/auth_routes.py`) | Implementado parcialmente — ver sección 9 |
| Flask-SQLAlchemy / SQLAlchemy | No mencionado por nombre en `/docs` | 3.1.1 / 2.0.52 — **en uso**: `db = SQLAlchemy()` en `app/extensions.py`, inicializado en `create_app()`, con el modelo `User` en `app/infrastructure/persistence/models.py` | **v0.4 — implementado.** Indicado por el Tech Lead Backend, quien declara la estrategia de persistencia (SQLAlchemy, UUID, CITEXT) como ya aprobada por el equipo — ver nota de gobernanza al final de esta sección |
| Flask-Migrate / Alembic | No mencionado por nombre en `/docs` | 4.1.0 / 1.19.1 — **en uso**: `migrate = Migrate()` en `app/extensions.py`; scaffolding generado en `backend/migrations/` con una migración inicial (`create_users_table`, escrita a mano — ver sección 8) | Implementado — ver sección 8 y 9 |
| psycopg (v3) | No mencionado por nombre en `/docs` | 3.3.4 — driver de PostgreSQL en `requirements.txt` | Se eligió `psycopg` (v3) en vez de `psycopg2-binary` porque este último no tiene wheel precompilado para la versión de Python en uso (3.14) y falla al compilar sin `pg_config`. Nota: la cadena de conexión debe usar el esquema `postgresql+psycopg://`, no `postgresql://` a secas |
| PostgreSQL | Confirmado como motor elegido (`HB-001` portada; `CLAUDE.md` §4 "Base de Datos") | Driver y ORM ya integrados (ver filas arriba); **verificado contra una instancia PostgreSQL 17 real** (instalada localmente para esta tarea, base `thers_dev`) — la migración se aplicó y se confirmó el esquema resultante con `psql` | Implementado a nivel de desarrollo local. Sigue sin existir una base compartida por el equipo o de producción. Ver sección 8 |
| `requirements.txt` | Ya existía fijando `Flask==3.1.3`, `flask-cors==6.0.2`, `Flask-JWT-Extended==4.7.1` | **v0.4:** se agregaron `Flask-SQLAlchemy==3.1.1`, `Flask-Migrate==4.1.0`, `psycopg[binary]==3.3.4` | Versiones tomadas de la instalación real verificada en esta tarea (`pip freeze`). Sigue sin ratificación formal del equipo como estándar oficial (`pyproject.toml` sigue sin existir, sección 20) |

> ⚠️ **Nota de gobernanza (v0.5, actualizada).** `HB-001` §11 clasifica "cambiar el modelo de datos" como decisión de **alto impacto**, que se lleva al Comité Técnico completo (los 4 integrantes) y se documenta como ADR (§12). Las decisiones reflejadas en esta actualización (SQLAlchemy como ORM; `id` de `users` como **UUID** con `DEFAULT gen_random_uuid()` en PostgreSQL; `email` como **`CITEXT`**; Flask-Migrate/Alembic como herramienta de migraciones) fueron indicadas por el Tech Lead Backend, quien declara esta estrategia de persistencia como ya aprobada por el equipo. Este documento no tiene acceso al ADR/registro de decisiones de Notion (`HB-001` §12) para verificarlo de forma independiente, así que **registra la implementación como un hecho de código confirmado** y la aprobación **como lo reportado por el Tech Lead Backend** — si el ADR correspondiente ya existe en Notion, referenciarlo aquí en la próxima actualización de este documento cierra el punto de forma definitiva.

**Notas de contradicción:**
- El `README.md` raíz declara **MySQL** como base de datos (`README.md`, badge y tabla de stack) — contradice a `HB-001` (PostgreSQL) y a este documento. Ya identificado y no resuelto en `CLAUDE.md` §14; por la jerarquía de fuentes (`CLAUDE.md` §3), `/docs` gana. Este documento asume PostgreSQL por esa razón, no por preferencia propia.
- `backend/app.py` (raíz de `backend/`) define una segunda aplicación Flask mínima e independiente (`Flask(__name__)`, ruta `/`), **no conectada** a la arquitectura por capas de `app/`. Coexiste con `backend/run.py` (el punto de entrada real, que sí usa `create_app()`). Ningún documento oficial explica el propósito de `app.py`. Se reporta como hallazgo, no se elimina ni se modifica (fuera del alcance de esta tarea).

---

## 3. Arquitectura

Capas observadas en `backend/app/` (mismas que `REPOSITORY_STRUCTURE.md` §6 describe como "propuesta a confirmar" según Clean Architecture / Arquitectura Hexagonal):

```
backend/app/
├── interfaces/     # Adaptadores de entrada — HTTP (routes/blueprints)
├── application/    # Casos de uso — orquestación
├── domain/         # Entidades y reglas de negocio puras
├── config.py       # Configuración de la aplicación
├── extensions.py   # Inicialización de extensiones Flask (JWT)
└── __init__.py     # Application factory (create_app)
```

| Capa | Responsabilidad | Implementación actual |
|---|---|---|
| `interfaces/routes/` | Recibir peticiones HTTP, parsear/validar forma básica del request, invocar un caso de uso, traducir su resultado a una respuesta HTTP | `auth_routes.py` — un blueprint (`auth_bp`), un endpoint (`POST /api/login`) |
| `application/` | Casos de uso: orquestan la lógica de negocio del `domain/` sin conocer detalles HTTP ni de infraestructura | `application/auth/login_use_case.py` — `login_user(email, password)` |
| `domain/` | Entidades y reglas de negocio puras, sin dependencia de Flask ni de ningún framework | `domain/auth/auth_service.py` — `validate_user(email, password)` |
| `config.py` | Configuración de la aplicación (claves, futuras variables de entorno) | Una sola clase `Config` con `JWT_SECRET_KEY` hardcodeado (ver sección 12 y 16) |
| `extensions.py` | Inicialización de extensiones Flask compartidas, instanciadas una vez y enlazadas en `create_app()` | Solo `jwt = JWTManager()` |
| `__init__.py` (application factory) | Construir y configurar la instancia de `Flask`, registrar extensiones y blueprints | `create_app()` — instancia Flask, carga `Config`, activa `CORS`, inicializa `jwt`, registra `auth_bp` bajo `/api` |

**Hallazgo de nomenclatura (no es una contradicción documental, es un hallazgo de código):** los archivos marcador de paquete dentro de `application/`, `application/auth/`, `domain/`, `domain/auth/` e `interfaces/routes/` se llaman `_init_.py` (un solo guion bajo a cada lado), no `__init__.py`. Solo `backend/app/__init__.py` (la raíz del paquete `app`) tiene el nombre correcto. Además, `interfaces/` no tiene ningún archivo marcador, ni siquiera mal nombrado. Esto no rompe las importaciones porque Python 3 soporta *namespace packages* implícitos, pero significa que esos archivos **no cumplen la función que su nombre sugiere** (ninguno puede contener código de inicialización de paquete que realmente se ejecute como tal). Se reporta como hallazgo técnico; no se corrige en este documento por estar fuera de alcance.

---

## 4. Flujo de una petición

Confirmado por el código actual (`auth_routes.py` → `login_use_case.py` → `auth_service.py`), sin contradicción con la documentación (que no define un flujo alternativo):

```
HTTP Request
   ↓
Interface / Route          (backend/app/interfaces/routes/auth_routes.py)
   ↓
Application / Use Case     (backend/app/application/auth/login_use_case.py)
   ↓
Domain                     (backend/app/domain/auth/auth_service.py)
   ↓
Repository / Persistence   ⚠️ NO IMPLEMENTADO — ver sección 8
   ↓
PostgreSQL                 ⚠️ NO IMPLEMENTADO — ver sección 2 y 8
```

El flujo real hoy termina en `domain/` — `validate_user()` compara contra credenciales hardcodeadas en el propio código (`email == "test@test.com" and password == "123456"`), no contra un repositorio ni una base de datos. Las dos últimas capas del diagrama (`Repository/Persistence` y `PostgreSQL`) están **definidas como destino arquitectónico** por el stack confirmado (sección 2), pero no tienen ninguna implementación en el código actual.

---

## 5. Interfaces

- **Routes:** un único módulo, `app/interfaces/routes/auth_routes.py`.
- **Blueprints:** un único blueprint, `auth_bp`, registrado en `create_app()` con prefijo `/api` (`app.register_blueprint(auth_bp, url_prefix="/api")`).
- **Request handling:** cada route lee el body con `request.get_json()`, valida presencia de campos manualmente (`if not data`, `if not email or not password`) y responde con `jsonify(...)` + código HTTP explícito. No hay capa de validación declarativa (schemas) — ver sección 10.
- **Responses:** formato observado — `{"msg": "..."}` para errores, `{"token": ..., "user": {...}}` para éxito de login. No hay un formato de respuesta estandarizado ni documentado para todos los endpoints futuros — ver sección 11 y 20.

---

## 6. Application

- **Casos de uso:** un único caso de uso implementado, `login_user(email, password)` en `application/auth/login_use_case.py`. Orquesta: llama a `validate_user()` del dominio y, si es válido, devuelve un diccionario de usuario.
- **Orquestación:** el caso de uso no conoce Flask ni HTTP — recibe primitivos (`email`, `password`) y devuelve un `dict` o `None`. Esto es coherente con el principio de que `application/` no debería depender del framework de entrada.
- **DTOs / Schemas:** **no están definidos.** No existe ninguna librería de serialización/validación (p. ej. Marshmallow, Pydantic) instalada ni referenciada en el código. El caso de uso retorna un `dict` construido a mano (`{"email": email, "name": "Fernando"}`) — el `"name": "Fernando"` está hardcodeado, no proviene de ningún dato real de usuario. Definir una estrategia de DTOs queda como `PENDIENTE DE APROBACIÓN`.

---

## 7. Domain

- **Entidades:** **no existen entidades formales** (clases de dominio). `domain/auth/auth_service.py` expone una única función, `validate_user(email, password)`, sin una clase `User` ni ningún objeto de dominio.
- **Reglas de negocio:** la única regla implementada es la comparación literal contra credenciales fijas en código (`test@test.com` / `123456`). No hay reglas de negocio reales (hashing de contraseñas, expiración, roles, permisos).
- **Lógica actualmente ubicada en domain:** `auth_service.py` contiene actualmente la única lógica ubicada bajo `domain/`, pero su clasificación formal como servicio de dominio queda sujeta a la ratificación de la arquitectura. No depende de nada externo (ni de Flask, ni de una base de datos).
- **Qué NO debe depender del framework:** por diseño de Clean Architecture (la misma que `REPOSITORY_STRUCTURE.md` §6 propone), `domain/` no debe importar Flask, `flask_jwt_extended`, ni ningún detalle de infraestructura (ORM, HTTP, PostgreSQL). El código actual **cumple** esto — `auth_service.py` no importa nada fuera de la librería estándar. Mantener esta regla hacia adelante es un requisito de este documento, no una preferencia personal.

---

## 8. Persistencia

- **Repositories:** **todavía no existen.** Existe `app/infrastructure/persistence/` (nuevo, v0.4) con el modelo `User`, pero ningún módulo de acceso a datos (repositorio) que lo consuma — `domain/auth/auth_service.py` sigue comparando contra la credencial hardcodeada, sin consultar el modelo. Esa migración de `login`/`validate_user` a persistencia real queda para una tarea siguiente.
- **Acceso a PostgreSQL — v0.5, implementado y verificado localmente:** driver instalado (`psycopg[binary]==3.3.4`), `SQLALCHEMY_DATABASE_URI` leída desde `DATABASE_URL` en `config.py`, modelo `User` definido (`app/infrastructure/persistence/models.py`: `id` **UUID** con `DEFAULT gen_random_uuid()` generado **en PostgreSQL** (no en Python), `name` `VARCHAR(120)`, `email` **`CITEXT`** único+indexado (case-insensitive, extensión `citext`), `password_hash` **`TEXT`**, `created_at`/`updated_at` `TIMESTAMPTZ` con `DEFAULT now()` — `updated_at` mantenida por un trigger de PostgreSQL, no por SQLAlchemy). La migración (`a1b2c3d4e5f6_create_users_table.py`, escrita a mano, no autogenerada) crea la extensión `citext`, la tabla y el trigger `trg_users_updated_at`. El flujo modelo→migración→`flask db upgrade` se verificó contra una instancia PostgreSQL 17 real instalada localmente (base `thers_dev`), confirmando el esquema resultante y el comportamiento del trigger con `psql`. **Sigue sin haber una base compartida por el equipo o de producción** — esto es una base de desarrollo local, no un despliegue real.
- **Migraciones — v0.4, implementado:** `backend/migrations/` (Flask-Migrate/Alembic), con una migración inicial (`create_users_table`) que crea la tabla `users` con índice único en `email`.
- **Separación negocio/persistencia:** `domain/`/`application/` siguen sin conocer SQLAlchemy (regla de dependencia respetada — el modelo vive en `infrastructure/`, no en `domain/`). La forma exacta del repositorio que conectará ambos lados sigue sin implementarse.
- **Estado real de los datos hoy:** el único "dato" de usuario que el flujo de login usa en producción de código sigue siendo el valor hardcodeado en `domain/auth/auth_service.py` — el modelo `User` nuevo todavía no está conectado a ningún endpoint.

Pendiente (no decidido en esta actualización, `PENDIENTE DE APROBACIÓN`): patrón exacto de repositorio (Repository simple vs. Unit of Work), pool de conexiones para producción, y — como señala la nota de gobernanza de la sección 2 — la **ratificación formal** por el Comité Técnico de las decisiones ya codificadas (SQLAlchemy, UUID, Flask-Migrate).

---

## 9. Authentication & Authorization

**Estado actual (IMPLEMENTADO):**
- Login: `POST /api/login`, recibe `email`/`password` en JSON.
- Si las credenciales son válidas (comparación hardcodeada, sección 7), se genera un token con `create_access_token(identity=user["email"])` de `flask_jwt_extended`.
- La respuesta incluye `token` y un objeto `user`.
- `JWTManager` está inicializado globalmente (`extensions.py`) y enlazado a la app en `create_app()`.

**Limitaciones conocidas (estado actual, no propuestas de solución):**
- **Credenciales hardcodeadas:** no hay usuarios reales, no hay tabla/modelo de usuario, no hay verificación contra una base de datos. Un único usuario fijo (`test@test.com` / `123456`) es "válido". **Actualización (corrección de seguridad aplicada):** la comparación de contraseña ya no es texto plano — ver siguiente punto. La ausencia de persistencia real sigue `PENDIENTE` (sección 20).
- **Hashing de contraseñas — `RESUELTO` para la credencial de prueba actual:** `domain/auth/auth_service.py` compara ahora contra un hash (`werkzeug.security.check_password_hash`, algoritmo `scrypt`) en vez de texto plano. Sigue siendo una única credencial hardcodeada en código (no hay tabla `users` real todavía), pero ya no se compara la contraseña en claro. El algoritmo de hashing para el futuro modelo de datos real sigue `PENDIENTE DE APROBACIÓN` (sección 20) — esta corrección no lo ratifica como decisión definitiva, solo elimina la comparación en texto plano del código actual.
- **`JWT_SECRET_KEY` — `RESUELTO` (mecanismo de sustitución por entorno):** `config.py` ahora lee `JWT_SECRET_KEY` de `os.environ`; si no está definida, usa un valor de desarrollo explícitamente marcado como inseguro (`dev-only-insecure-key-CHANGE-ME`) y advierte por `stderr` al arrancar. Se agregó `backend/.env.example` documentando la variable y `backend/.gitignore` (antes inexistente) para que un futuro `.env` real nunca se versione. La **gestión de secretos en un entorno desplegado** (vault, variables de CI/CD) sigue `PENDIENTE DE APROBACIÓN` (sección 20) — esta corrección resuelve el mecanismo de sustitución local, no la estrategia de producción.
- **Ningún endpoint protegido todavía:** no hay ningún uso de `@jwt_required()` en el código — el único endpoint existente (`/login`) es público por definición (emite el token, no lo exige). No hay ejemplo real de "protección de endpoint" en el código actual para documentar como patrón ya validado.
- **Sin registro (`register`):** el Frontend ya tiene una página `Register.jsx` (`REPOSITORY_STRUCTURE.md` §3), pero el backend no expone ningún endpoint de registro. `CLAUDE.md` §9 ya confirma: "El backend actual solo expone `auth` (`/login`)".
- **Sin logout, refresh token, ni expiración configurada explícitamente:** `flask_jwt_extended` trae valores por defecto de expiración de access token, pero no hay ninguna configuración explícita en `config.py` que los fije o los documente.
- **Sin manejo de roles/autorización:** no hay ningún concepto de rol, permiso o scope en el código.

Todo lo anterior son observaciones del estado actual, no una lista de tareas asumidas como aprobadas — la estrategia concreta para resolver cada limitación (dónde vive el modelo de usuario, cómo se hashean contraseñas, cómo se protege un endpoint, política de expiración/refresh) queda `PENDIENTE DE APROBACIÓN` (sección 20).

---

## 10. Validación

- **Request validation:** manual, dentro de cada route. `auth_routes.py` valida: que el body no sea `None`/vacío, y que `email` y `password` estén presentes. No hay validación de formato (formato de email, longitud mínima de password, tipos de datos).
- **Reglas:** no hay reglas de validación centralizadas ni reutilizables — cada route tendría que repetir su propia lógica de validación si se agregan más endpoints, siguiendo el patrón actual.
- **Errores de validación:** responden `400` con `{"msg": "..."}` cuando falta el body o los campos obligatorios.
- **Librería de validación declarativa:** no hay ninguna instalada (ni Marshmallow, ni Pydantic, ni `flask-inputs`, ni WTForms). Adoptar una queda `PENDIENTE DE APROBACIÓN` — no se asume ninguna en este documento.

---

## 11. Error handling

Estado actual, capa por capa:

| Tipo de error | Estado actual |
|---|---|
| Errores de dominio | No existen excepciones de dominio propias (p. ej. `InvalidCredentialsError`). `validate_user()` simplemente retorna `False`/`True`. |
| Errores de aplicación | `login_user()` retorna `None` cuando el login falla — no lanza excepciones, la route interpreta el `None`. |
| Errores HTTP | Manejados manualmente en cada route con `jsonify(...)`, código explícito (`400`, `401`). No hay manejadores de error globales (`@app.errorhandler`) registrados en `create_app()` — un `404` o `500` no manejado usa las páginas de error por defecto de Flask (HTML, no JSON). |
| Formato de respuesta de error | Observado: `{"msg": "<texto>"}`. No está documentado como estándar oficial en ningún lugar de `/docs` — es simplemente el patrón que el único endpoint existente usa hoy. |

No existe todavía un formato de error unificado para toda la API (p. ej. `{"error": {"code": ..., "message": ...}}`), ni un manejador global de excepciones no capturadas. Definir ese estándar queda `PENDIENTE DE APROBACIÓN`.

---

## 12. Configuration

- **`config.py`:** una única clase `Config`. **Actualización (corrección de seguridad aplicada):** `JWT_SECRET_KEY` ya no es un literal de texto — se lee de `os.environ.get("JWT_SECRET_KEY")`, con un valor de desarrollo explícitamente marcado como inseguro (`dev-only-insecure-key-CHANGE-ME`) como único fallback si la variable no está definida, y una advertencia impresa en `stderr` cuando eso ocurre.
- **Variables de entorno:** ya se lee una (`JWT_SECRET_KEY`, vía `os.environ`, sin `python-dotenv` — no se instaló ninguna dependencia nueva). Se agregó `backend/.env.example` documentando la variable. `run.py` sigue fijando `host="127.0.0.1"`, `port=5000` y `debug=True` como literales, no como configuración externa — **`PENDIENTE`**.
- **Secretos:** el `JWT_SECRET_KEY` real ya no vive hardcodeado en el código — se agregó `backend/.env.example` (documentación, sin secreto real) y `backend/.gitignore` (antes inexistente en `backend/`) para que un futuro `.env` real nunca se versione, cumpliendo la regla innegociable de `HB-001` §20. La gestión de secretos en un entorno desplegado (vault, variables de CI/CD) sigue **`PENDIENTE DE APROBACIÓN`** (sección 20) — esto resuelve el mecanismo local, no la estrategia de producción.
- **Configuración por ambiente:** **sigue sin existir.** Una sola clase `Config`, sin `DevelopmentConfig`/`ProductionConfig`/`TestingConfig`, sin selección de configuración según una variable de entorno (p. ej. `FLASK_ENV`). No se introduce en esta corrección — fuera del alcance de un fix puntual de seguridad.

`CLAUDE.md` §14 ya confirmaba este hueco como "solo la regla de no subir `.env`, sin lista oficial" — con esta corrección existe ya una primera variable documentada (`JWT_SECRET_KEY`), pero sigue sin haber una lista oficial completa ni una política de configuración por ambiente.

---

## 13. CORS y extensiones Flask

- **CORS:** habilitado globalmente con `CORS(app)` (sin restricción de orígenes, métodos ni headers) en `create_app()`. No hay ninguna política de CORS por ambiente documentada — en desarrollo esto permite cualquier origen, lo cual no está evaluado como aceptable o no para un entorno de producción futuro, porque no existe documentación de despliegue/DevOps (`CLAUDE.md` §4 "DevOps": sin documentación oficial).
- **Extensiones Flask activas:**
  - `flask_cors.CORS` — inicializado directamente sobre `app` en `create_app()`.
  - `flask_jwt_extended.JWTManager` — instanciado una vez en `extensions.py` (`jwt = JWTManager()`) y enlazado con `jwt.init_app(app)` en `create_app()`, siguiendo el patrón estándar de Flask de extensiones desacopladas de la instancia de la app.
- **Extensiones instaladas pero no inicializadas:** `Flask-SQLAlchemy` está en el venv pero no hay ninguna instancia `db = SQLAlchemy()` en `extensions.py` ni en ningún otro archivo.

---

## 14. API

Principios generales de diseño de endpoints, basados en lo que el único endpoint existente (`POST /api/login`) ya establece como patrón de facto — **no se define aquí el catálogo completo de endpoints**, según el alcance explícito de esta tarea:

- **Patrón actualmente observado:** el endpoint existente está registrado mediante un blueprint en `interfaces/routes/` y montado con prefijo `/api` desde `create_app()` (`url_prefix="/api"`).
- **Organización futura:** el uso de blueprints organizados por dominio funcional (p. ej. `auth_bp` para autenticación) se observa actualmente en `auth`, pero convertir esta organización en una regla general para futuros endpoints queda `PENDIENTE DE APROBACIÓN`.
- Los métodos HTTP se declaran explícitamente por ruta (`methods=["POST"]`), no hay convención documentada todavía sobre verbos para operaciones futuras (GET de colección, PUT/PATCH de actualización, DELETE).
- Los cuerpos de petición y respuesta son JSON (`request.get_json()` / `jsonify(...)`), sin excepción observada.
- No existe especificación formal de API (OpenAPI/Swagger) en `/docs` — `CLAUDE.md` §9 y §14 ya lo confirman. `HB-001` §15.1 exige documentar cada endpoint nuevo el mismo día del PR — esa documentación de endpoints, cuando exista, es un artefacto distinto de este documento de arquitectura.

---

## 15. Testing

- **Estructura prevista:** **ninguna.** No hay carpeta `tests/` en `backend/`, ni en el resto del repositorio para backend.
- **Framework:** no hay ningún framework de testing instalado en el venv (`pytest` no aparece en `pip freeze`), ni configurado en ningún archivo del proyecto. `CLAUDE.md` §9 ya lo confirma explícitamente: "no hay framework de testing configurado... ni estrategia documentada en `/docs`."
- **Unit tests / Integration tests / API tests:** no implementados, no propuestos en ningún documento oficial. No se propone aquí una estructura de testing como si fuera decisión ya tomada — queda como `PENDIENTE DE APROBACIÓN` (sección 20), a decidir junto con el equipo antes de asumir `pytest` u otra herramienta.

---

## 16. Seguridad

Estado actual observado, sin proponer remediaciones (fuera de alcance de esta tarea):

| Área | Estado |
|---|---|
| Secretos | **Corregido (parcial):** `JWT_SECRET_KEY` ya se lee de `os.environ`, con `backend/.env.example` documentando la variable y `backend/.gitignore` protegiendo un futuro `.env` real. Sigue sin existir gestión de secretos para un entorno desplegado (vault, CI/CD) — `PENDIENTE` (sección 20). |
| JWT | Emitido con `flask_jwt_extended` sobre una clave ahora externalizable por entorno; sin política de expiración explícita; sin endpoints protegidos actualmente (`@jwt_required()` no se usa en ningún lugar del código); sin refresh tokens. |
| Validación | Solo presencia de campos (sección 10); sin sanitización, sin límites de longitud, sin validación de formato de email. |
| Autorización | No existe ningún concepto de roles/permisos en el código. |
| Exposición de errores | Los mensajes de error (`{"msg": "..."}`) no exponen detalles internos (stack traces, nombres de excepciones) en el único endpoint existente — pero no hay un manejador global de errores no capturados, por lo que un error inesperado (`500`) hoy caería en el comportamiento por defecto de Flask, cuyo contenido depende del modo `debug` (activo en `run.py`). |
| Datos sensibles | **Corregido:** la contraseña de la credencial de prueba ya se compara mediante `werkzeug.security.check_password_hash` (`scrypt`), no en texto plano. Sigue siendo una única credencial hardcodeada en código — no hay tabla `users` real ni hashing aplicado a un modelo de datos persistido (`PENDIENTE`, sección 20). |

`CLAUDE.md` §8 (fila Backend) ya anticipaba este hueco: "Seguridad: sin documento oficial; aplicar buenas prácticas estándar... y señalar huecos, no llenarlos por inferencia silenciosa." Las dos correcciones de esta revisión (secreto por entorno, hashing de la credencial de prueba) son exactamente ese tipo de buena práctica estándar aplicada sin inventar nada — el resto de huecos de esta tabla sigue señalado, no resuelto.

---

## 17. Reglas de dependencia

Basadas en el principio de Clean Architecture que la propia estructura de carpetas ya sugiere (`REPOSITORY_STRUCTURE.md` §6) y que el código actual **respeta** en su forma mínima actual:

```
interfaces/  →  puede depender de  →  application/
application/ →  puede depender de  →  domain/
domain/      →  NO depende de nada externo (ni Flask, ni application/, ni interfaces/, ni infraestructura)
```

Reglas explícitas:
- `domain/` es la capa más interna: no importa Flask, `flask_jwt_extended`, ni ningún driver de base de datos. El código actual lo cumple (`auth_service.py` no tiene imports externos).
- `application/` puede importar de `domain/`, pero no debe importar Flask ni nada de `interfaces/`. El código actual lo cumple (`login_use_case.py` solo importa de `domain`).
- `interfaces/` puede importar de `application/` (y transitivamente de `domain/` a través de application, aunque no debería importar `domain/` directamente). El código actual lo cumple (`auth_routes.py` importa `login_use_case`, no `auth_service` directamente).
- La forma exacta en que una futura capa de persistencia (`repository`/`infrastructure`) se relacionará con `application/` queda `PENDIENTE DE APROBACIÓN`. En cualquier caso, `domain/` no debe depender de PostgreSQL ni de una implementación concreta de persistencia.
- `config.py` pertenece a la configuración de la aplicación y `extensions.py` a la integración con Flask. **No son dependencias permitidas para `domain/`.** El acceso de `application/` o `interfaces/` a configuración deberá respetar la estrategia de configuración que sea aprobada.

Esta tabla formaliza como regla de arquitectura lo que el código ya hace hoy — no introduce ninguna capa ni dependencia nueva.

---

## 18. Estructura de archivos recomendada

Estructura para la evolución futura del backend, extendiendo la ya observada (sección 3) sin reorganizar lo existente — coherente con el principio de escalabilidad ya usado en el resto del repositorio ("cada dominio nuevo es una carpeta adicional", `REPOSITORY_STRUCTURE.md` §2):

```
backend/
├── app/
│   ├── interfaces/
│   │   └── routes/
│   │       ├── __init__.py          # (corregido — ver hallazgo sección 3)
│   │       └── auth_routes.py
│   ├── application/
│   │   └── auth/
│   │       ├── __init__.py
│   │       ├── login_use_case.py
│   │       └── dtos.py               # PROPUESTA — no existe hoy
│   ├── domain/
│   │   └── auth/
│   │       ├── __init__.py
│   │       ├── auth_service.py
│   │       └── entities.py           # PROPUESTA — no existe hoy
│   ├── infrastructure/               # PROPUESTA — no existe hoy
│   │   └── persistence/
│   │       ├── __init__.py
│   │       ├── db.py                  # PROPUESTA — implementación pendiente de aprobación
│   │       └── repositories/
│   │           └── user_repository.py
│   ├── config.py
│   ├── extensions.py
│   └── __init__.py
├── tests/                             # PROPUESTA — no existe hoy
│   ├── unit/
│   ├── integration/
│   └── api/
├── run.py
├── requirements.txt                   # IMPLEMENTADO — ver sección 2 y 19
└── .env.example                       # IMPLEMENTADO — ver sección 12 y 19
```

Todo lo marcado `PROPUESTA` es una sugerencia de evolución consistente con las capas ya existentes, **no una decisión tomada** — cada una queda listada también en la sección 20. La ubicación exacta de persistencia, DTOs, entidades y testing no debe considerarse establecida hasta su aprobación formal.

---

## 19. Estado actual

### IMPLEMENTADO
- Application factory (`create_app()`) con Flask 3.1.3.
- Arquitectura por capas mínima: `interfaces/routes/` → `application/` → `domain/`, con un único flujo end-to-end (`login`).
- CORS habilitado globalmente.
- Emisión de JWT en login exitoso (`flask_jwt_extended`).
- Validación manual de presencia de campos en el único endpoint existente.
- Manejo de errores básico por endpoint (`400`/`401` con JSON).
- `JWT_SECRET_KEY` leída desde variable de entorno (`os.environ`), con `.env.example` documentando la variable y `.gitignore` protegiendo un futuro `.env` real (corrección de seguridad — ver sección 12, 16).
- Hashing de la credencial de prueba con `werkzeug.security` (`scrypt`) — la comparación de contraseña ya no es en texto plano (corrección de seguridad — ver sección 9, 16).
- `backend/requirements.txt` con las versiones en uso real fijadas (Flask, flask-cors, Flask-JWT-Extended, Flask-SQLAlchemy, Flask-Migrate, psycopg) — ver sección 2.
- **v0.4:** `db = SQLAlchemy()` / `migrate = Migrate()` inicializados en `create_app()` (`app/extensions.py`, `app/__init__.py`); `SQLALCHEMY_DATABASE_URI` leída desde `DATABASE_URL` (`config.py`, `.env.example`); scaffolding de migraciones (`backend/migrations/`).
- **v0.5:** modelo `User` alineado a la estrategia de persistencia aprobada por el equipo (`app/infrastructure/persistence/models.py`): `id` **UUID** con `DEFAULT gen_random_uuid()` en PostgreSQL, `email` **`CITEXT`** (case-insensitive), `password_hash` `TEXT`, `created_at`/`updated_at` `TIMESTAMPTZ` con `DEFAULT now()` y `updated_at` mantenida por trigger (`set_updated_at`/`trg_users_updated_at`). Migración escrita a mano (`a1b2c3d4e5f6_create_users_table.py`) que crea la extensión `citext`, la tabla y el trigger — verificada contra una instancia PostgreSQL 17 real instalada localmente (base `thers_dev`), incluyendo el funcionamiento del trigger y la unicidad case-insensitive de `email`.

### PENDIENTE
- **Conexión a una base PostgreSQL real** (desarrollo compartido y/o producción) — el modelo y la migración existen y se verificaron localmente, pero nadie ha aplicado la migración contra un Postgres real todavía.
- Capa de persistencia (`repositories/`) que conecte el modelo `User` con `application/`/`domain/` — el modelo existe pero ningún caso de uso lo consulta todavía.
- Migrar `login`/`validate_user` de la credencial hardcodeada al modelo `User` real (siguiente tarea planeada).
- Registro de usuario (`/register`) contra el modelo real.
- **Ratificación formal por el Comité Técnico** de las decisiones ya codificadas en v0.4/v0.5 (SQLAlchemy, UUID, CITEXT, Flask-Migrate) — ver nota de gobernanza, sección 2.
- Estrategia de hashing para el futuro modelo de datos real (la corrección aplicada resuelve el mecanismo, no ratifica el algoritmo definitivo — sección 20).
- Endpoints protegidos con `@jwt_required()` (ninguno existe hoy).
- Política de expiración/refresh de JWT.
- Roles y autorización.
- Validación declarativa (schemas/DTOs).
- Manejo global de errores (`@app.errorhandler`) y formato de error unificado.
- Configuración por ambiente (`Development`/`Production`/`Testing`).
- Ratificación formal de `requirements.txt` y `pyproject.toml` (el primero ya existe, sin ratificar formalmente por el equipo — sección 20, ítem 14).
- Estrategia y framework de testing.
- Especificación formal de API (OpenAPI/Swagger).
- Política de CORS por ambiente.

---

## 20. PENDIENTES DE APROBACIÓN

Toda decisión arquitectónica no respaldada hoy por código ni por documento oficial ratificado:

1. **Estrategia de persistencia:** ORM vs. SQL directo — **ya implementado como SQLAlchemy + Flask-Migrate/Alembic (v0.4)** por indicación directa del Tech Lead Backend; **ratificación formal por el Comité Técnico pendiente de confirmar** (`HB-001` §11.1). Patrón de repository exacto, pool de conexiones y mecanismo de dependencia entre `application/` y la implementación de persistencia siguen sin definir.
2. **Modelo de datos de usuario y esquema de PostgreSQL** — normalización, índices, migraciones (ya señalado como hueco general en `CLAUDE.md` §14).
3. **Estrategia de hashing de contraseñas para el modelo de datos real** (algoritmo, librería) — se aplicó `werkzeug.security`/`scrypt` como corrección puntual sobre la credencial de prueba hardcodeada (sección 9, 16, 19), pero **no queda ratificado como el algoritmo definitivo** del futuro modelo `users` persistido; esa decisión sigue abierta.
4. **Estructura de DTOs/schemas** y si se adopta una librería de validación declarativa (Marshmallow, Pydantic, u otra).
5. **Formato estándar de respuesta de error** para toda la API.
6. **Manejador global de excepciones** (`@app.errorhandler`) y taxonomía de excepciones de dominio/aplicación.
7. **Configuración por ambiente** (Development/Production/Testing) y lista oficial de variables de entorno requeridas.
8. **Gestión de secretos en un entorno desplegado** (vault, variables de CI/CD, rotación) — el mecanismo local ya se resolvió (`JWT_SECRET_KEY` vía `os.environ` + `.env.example` + `.gitignore`, sección 12, 16, 19); la estrategia para producción/CI sigue sin definir.
9. **Política de expiración y refresh de tokens JWT.**
10. **Modelo de roles y autorización.**
11. **Política de CORS por ambiente** (orígenes permitidos en producción vs. desarrollo).
12. **Framework y estrategia de testing** (unit/integration/API) — sin ninguna herramienta configurada hoy.
13. **Especificación formal de API** (OpenAPI/Swagger) y su ubicación (`/docs` vs. Notion, según `HB-001` §15.1 que menciona ambas opciones sin decidir).
14. **Ratificación formal de las versiones fijadas en `requirements.txt`** — el archivo ya existe (Flask 3.1.3, flask-cors 6.0.2, Flask-JWT-Extended 4.7.1, tomadas del entorno local observado), pero el equipo no lo ha ratificado formalmente como el estándar oficial de versiones; `pyproject.toml` sigue sin existir.
15. **Propósito de `backend/app.py`** — si se conserva, se elimina o se integra a la arquitectura por capas (fuera de alcance de esta tarea decidirlo).
16. **Corrección del nombrado `_init_.py` → `__init__.py`** en `application/`, `domain/` e `interfaces/routes/`, y si `interfaces/` debe tener su propio marcador de paquete (hallazgo de código, sección 3) — fuera de alcance implementarlo aquí.
17. **Definición formal de las reglas de dependencia entre `application/`, persistencia e infraestructura**, incluyendo el mecanismo concreto de inversión de dependencias si se adopta — no definido actualmente en código ni documentación oficial.
18. **Ratificación formal de este mismo documento** como contrato de arquitectura backend, siguiendo el proceso de `HB-001` §11–12.

---

## Fuentes consultadas

- `CLAUDE.md` (raíz del repositorio) — índice de reglas operativas y jerarquía de fuentes.
- `docs/architecture/REPOSITORY_STRUCTURE.md` — estructura del monorepo, incluida la propuesta de capas de `backend/` (§6).
- `docs/architecture/organization/01_Manual_Organizacion/Source/HB-001-manual-organizacion.md.md` — Manual de Organización (roles, stack confirmado, gobernanza, reglas de seguridad de datos con IA).
- `docs/architecture/Frontend/FAS-001-Frontend-Architecture-Specification.md` — confirma que el backend queda explícitamente fuera de su alcance (§ "Alcance"), y el principio "el código sigue a la documentación, no al revés" (§1), reutilizado aquí.
- `docs/architecture/ARC-001-handbook-architecture.md.md` — menciones de Backend/JWT/PostgreSQL como temas de contenido del Handbook, sin definir arquitectura técnica.
- `README.md` (raíz) — fuente no oficial; usado solo para documentar la contradicción MySQL/PostgreSQL ya identificada en `CLAUDE.md` §14.
- Código fuente completo de `backend/`: `app.py`, `run.py`, `app/__init__.py`, `app/config.py`, `app/extensions.py`, `app/application/auth/login_use_case.py`, `app/domain/auth/auth_service.py`, `app/interfaces/routes/auth_routes.py`, y todos los archivos `_init_.py`.
- `backend/venv` (entorno local) — `pyvenv.cfg` (versión de Python) y `pip freeze` (versiones de paquetes instalados), usados únicamente como observación de estado, no como fuente de decisión.
- `git ls-files backend` — confirma qué archivos del backend están versionados.

Documentos oficiales **no consultados por no ser procesables en este entorno** (ya señalados como hueco en `CLAUDE.md` §14): `Manual_Operativo/THERS_Manual_Operativo_v1.0.docx`/`.pdf`, `Plan_Estrategico/Plan_Estrategico_IA_THERS.docx`/`.pdf`. Si contienen decisiones de arquitectura backend, este documento no puede confirmarlo ni descartarlo.
