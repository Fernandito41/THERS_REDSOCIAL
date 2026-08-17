# BACKEND_ARCHITECTURE

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/BACKEND_ARCHITECTURE.md` |
| Versión | 0.6 (Propuesta) |
| Estado | **Pendiente de ratificación formal del equipo** (proceso de decisiones de alto impacto, `HB-001` §11–12) |
| Depende de | `HB-001` (Manual de Organización), `REPOSITORY_STRUCTURE.md` §6, `CLAUDE.md` §4/§14, código real de `backend/` |
| Autoridad sobre este documento | `/docs` oficial > estructura real observada en el código > este documento (mismo orden que `CLAUDE.md` §3) |

> ⚠️ **Nota de estado.** `HB-001` §0 declara explícitamente que no define arquitectura técnica profunda y que "esos temas se documentarán en manuales técnicos separados" — este documento es esa pieza separada, y hasta ahora no existía ninguna. No hay, previo a este documento, ningún documento oficial ratificado de arquitectura backend: solo estructura *observada* en el código (`REPOSITORY_STRUCTURE.md` §6, marcada allí como "propuesta a confirmar"). Este documento documenta y consolida la estructura observada como propuesta de contrato técnico, pero **no la ratifica por sí mismo** — sigue el proceso de gobernanza de `HB-001` §11–12 antes de tratarse como cerrado. Toda sección que introduce una decisión no respaldada por código ni por documento previo se marca explícitamente como `PENDIENTE DE APROBACIÓN` (ver sección 20).
>
> **v0.2 — actualización tras corrección de seguridad puntual (pedida explícitamente por el equipo, no iniciativa de este documento):** se corrigieron dos hallazgos de la auditoría arquitectónica integral de THERS marcados como `CONFLICTO` de prioridad P0 — `JWT_SECRET_KEY` hardcodeado (ahora vía `os.environ` + `.env.example` + `.gitignore`) y comparación de contraseña en texto plano (ahora `werkzeug.security.check_password_hash`). Ambas correcciones están reflejadas en las secciones 9, 12, 16, 19 y 20.
>
> **v0.3 — actualización tras publicar `backend/requirements.txt`:** se creó el archivo de dependencias, fijando únicamente los paquetes que el código actual importa (Flask, flask-cors, Flask-JWT-Extended), deliberadamente sin `Flask-SQLAlchemy`/`SQLAlchemy` para no adoptar una decisión de persistencia sin ratificar. Reflejado en las secciones 2, 18 y 20. Ninguna otra sección de este documento cambió — sigue siendo, en todo lo demás, la misma propuesta v0.1 pendiente de ratificación.
>
> **v0.6 — cierre y validación real de la capa de persistencia:** se reemplazó la referencia a una instalación nativa de PostgreSQL 17.11 (verificada en una sola máquina, no reproducible por el equipo) por el entorno estandarizado real, **PostgreSQL 16 vía Docker Compose** (`docker-compose.yml`, raíz del repo, imagen `postgres:16-alpine`). Se verificó de punta a punta contra esa base: `flask db upgrade`/`downgrade` repetidos, generación de `id` por `gen_random_uuid()` en PostgreSQL (no en Python), trigger de `updated_at`, unicidad case-insensitive de `email` vía `CITEXT`, y reconstrucción completa desde un volumen Docker vacío. Reflejado en las secciones 2, 8 y 19. Ninguna decisión de esquema ni de capas cambió — solo se sincronizó el documento con el código real y se corrigió el entorno de referencia.
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
| PostgreSQL | Confirmado como motor elegido (`HB-001` portada; `CLAUDE.md` §4 "Base de Datos") | Driver y ORM ya integrados (ver filas arriba); **verificado contra PostgreSQL 16 real vía Docker Compose** (`docker-compose.yml`, raíz del repo, imagen `postgres:16-alpine`, base `thers_dev`) — reemplaza la instalación nativa 17.11 usada en la verificación anterior (no reproducible por el equipo). La migración se aplicó y se confirmó el esquema resultante con `psql`, incluyendo downgrade/upgrade y reconstrucción desde un volumen vacío | Implementado a nivel de desarrollo local, ahora reproducible por cualquier integrante (`docker compose up -d`). Sigue sin existir una base compartida por el equipo o de producción. Ver sección 8 |
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

- **Casos de uso — v0.6, migrados a persistencia real:** `login_user(email, password, user_repository)` (`application/auth/login_use_case.py`) y `register_user(name, email, password, user_repository)` (`application/auth/register_use_case.py`, nuevo). Ambos reciben el repositorio como parámetro (inyectado por `interfaces/routes/auth_routes.py`, ver §8) en vez de importar SQLAlchemy — `login_user` ya no llama a `validate_user()`, sino a `user_repository.find_by_email()` + `verify_password()` del dominio; `register_user` llama a `hash_password()` del dominio y `user_repository.create()`.
- **Orquestación:** los casos de uso no conocen Flask ni HTTP — reciben primitivos (`email`, `password`, `name`) y un objeto `UserRepository` (interfaz de dominio, no la implementación concreta), y devuelven un `dict` o lanzan una excepción de dominio (`EmailAlreadyExistsError`, `InvalidCredentialsError` — ver §7). Esto es coherente con el principio de que `application/` no debería depender del framework de entrada ni de infraestructura concreta.
- **DTOs / Schemas:** **siguen sin estar definidos** como estrategia general. El `dict` de respuesta (`{"id": ..., "email": ..., "name": ...}`) ahora proviene de datos reales persistidos, no de un valor hardcodeado — pero sigue siendo un `dict` construido a mano, no un DTO/schema formal. Definir una estrategia general de DTOs queda como `PENDIENTE DE APROBACIÓN`.

---

## 7. Domain

- **Entidades:** sigue sin existir una clase de entidad `User` de dominio (el `User` con el que trabaja el resto del código es el modelo SQLAlchemy de `infrastructure/persistence/models.py` — ver §8; formalizar una entidad de dominio separada sigue `PENDIENTE`, no se justificó como necesaria para esta tarea).
- **Reglas de negocio — v0.6:** la credencial hardcodeada (`test@test.com`/`123456`) **se eliminó por completo**. `domain/auth/auth_service.py` expone únicamente `hash_password(password)` y `verify_password(password, password_hash)` (ambas envoltorios directos de `werkzeug.security`). Las demás reglas de negocio de auth (unicidad de email, "usuario no encontrado") viven como excepciones de dominio en `domain/auth/exceptions.py` (`EmailAlreadyExistsError`, `InvalidCredentialsError`) — deliberadamente sin distinguir "email inexistente" de "password incorrecta" en el mensaje/código HTTP, para no permitir enumerar emails registrados.
- **Repository (puerto) — nuevo, v0.6:** `domain/auth/repositories.py` define `UserRepository` (`abc.ABC`) con `create(name, email, password_hash)` y `find_by_email(email)`. Vive en `domain/` porque es un contrato de negocio puro (sin I/O real, solo `abc`) — la implementación concreta con SQLAlchemy vive en `infrastructure/` (ver §8) y depende de este puerto, nunca al revés.
- **Lógica actualmente ubicada en domain:** `auth_service.py`, `exceptions.py` y `repositories.py`. Ninguno depende de nada externo (ni Flask, ni SQLAlchemy, ni una base de datos real) — `repositories.py` solo usa `abc` de la librería estándar.
- **Qué NO debe depender del framework:** por diseño de Clean Architecture (la misma que `REPOSITORY_STRUCTURE.md` §6 propone), `domain/` no debe importar Flask, `flask_jwt_extended`, ni ningún detalle de infraestructura (ORM, HTTP, PostgreSQL). El código actual **cumple** esto, incluso tras la integración de persistencia — verificado explícitamente en esta tarea (ningún archivo de `domain/` importa `sqlalchemy` ni `flask`). Mantener esta regla hacia adelante es un requisito de este documento, no una preferencia personal.

---

## 8. Persistencia

- **Repositories — v0.6, implementado:** `app/infrastructure/persistence/repositories/user_repository.py` define `SQLAlchemyUserRepository`, que implementa el puerto `UserRepository` (`domain/auth/repositories.py`, ver §7): `create()` inserta un `User` y traduce `sqlalchemy.exc.IntegrityError` (violación de `UNIQUE` en `email`) a `EmailAlreadyExistsError` de dominio; `find_by_email()` hace `SELECT` por `email` (case-insensitive, vía `CITEXT`). Es el único módulo del backend que importa `sqlalchemy` para acceso a datos de `users`. La instancia concreta se crea una única vez en `interfaces/routes/auth_routes.py` (composition root — ver §14) e inyecta en los casos de uso; `domain/`/`application/` solo conocen el puerto abstracto.
- **Acceso a PostgreSQL — v0.5, implementado y verificado localmente:** driver instalado (`psycopg[binary]==3.3.4`), `SQLALCHEMY_DATABASE_URI` leída desde `DATABASE_URL` en `config.py`, modelo `User` definido (`app/infrastructure/persistence/models.py`: `id` **UUID** con `DEFAULT gen_random_uuid()` generado **en PostgreSQL** (no en Python), `name` `VARCHAR(120)`, `email` **`CITEXT`** único+indexado (case-insensitive, extensión `citext`), `password_hash` **`TEXT`**, `created_at`/`updated_at` `TIMESTAMPTZ` con `DEFAULT now()` — `updated_at` mantenida por un trigger de PostgreSQL, no por SQLAlchemy). La migración (`a1b2c3d4e5f6_create_users_table.py`, escrita a mano, no autogenerada) crea la extensión `citext`, la tabla y el trigger `trg_users_updated_at`. El flujo modelo→migración→`flask db upgrade` se verificó contra PostgreSQL 16 real vía Docker Compose (`docker-compose.yml`, imagen `postgres:16-alpine`, base `thers_dev`), confirmando el esquema resultante, el comportamiento del trigger y la unicidad case-insensitive de `email` con `psql` — incluyendo un downgrade + upgrade completo y una reconstrucción desde un volumen Docker vacío (`docker compose down -v && docker compose up -d && flask db upgrade`). **Sigue sin haber una base compartida por el equipo o de producción** — esto es una base de desarrollo local reproducible, no un despliegue real.
- **Migraciones — v0.4, implementado:** `backend/migrations/` (Flask-Migrate/Alembic), con una migración inicial (`create_users_table`) que crea la tabla `users` con índice único en `email`.
- **Separación negocio/persistencia:** `domain/`/`application/` siguen sin conocer SQLAlchemy (regla de dependencia respetada y verificada — ver §7, §17). El repositorio que conecta ambos lados ya está implementado (arriba) siguiendo el patrón Repository con puerto en `domain/` e implementación en `infrastructure/`.
- **Estado real de los datos hoy — v0.6:** `POST /api/register` y `POST /api/login` ya operan contra `users` real en PostgreSQL — la credencial hardcodeada se eliminó por completo (§7, §9). Verificado con una suite de pruebas de integración contra PostgreSQL 16 real (`backend/tests/test_auth.py`, ver §15) y manualmente vía `psql`.

Pendiente (no decidido en esta actualización, `PENDIENTE DE APROBACIÓN`): patrón exacto de repositorio más allá de lo ya implementado (p. ej. Unit of Work si se necesitara transaccionalidad entre múltiples entidades — no hace falta con una sola tabla), pool de conexiones para producción, y — como señala la nota de gobernanza de la sección 2 — la **ratificación formal** por el Comité Técnico de las decisiones ya codificadas (SQLAlchemy, UUID, Flask-Migrate, y ahora el patrón Repository con puerto en `domain/`).

---

## 9. Authentication & Authorization

**Estado actual (IMPLEMENTADO):**
- Registro: `POST /api/register` (**nuevo, v0.6**), recibe `name`/`email`/`password` en JSON, hashea la contraseña (`werkzeug.security`, scrypt) y crea el usuario vía `SQLAlchemyUserRepository` — `id` lo genera PostgreSQL.
- Login: `POST /api/login`, recibe `email`/`password` en JSON, busca el usuario real por email (`find_by_email`, case-insensitive vía `CITEXT`) y verifica la contraseña contra `password_hash` con `verify_password()`.
- Si las credenciales son válidas, se genera un token con `create_access_token(identity=user["id"])` de `flask_jwt_extended` — **`identity` es el `id` (UUID) del usuario, ya no el email** (cambio v0.6, ver nota de impacto más abajo).
- La respuesta de ambos endpoints incluye un objeto `user` (`id`, `email`, `name`); `login` además incluye `token`.
- `JWTManager` está inicializado globalmente (`extensions.py`) y enlazado a la app en `create_app()`.

**Resuelto en esta actualización (v0.6):**
- **Credenciales hardcodeadas — `RESUELTO`, eliminadas por completo.** Ya no existe ningún usuario fijo en código; `login`/`register` operan contra `users` real en PostgreSQL 16 (Docker). Verificado con `backend/tests/test_auth.py` (13 pruebas, ver §15) contra una base de datos real, no mockeada.
- **Sin registro (`register`) — `RESUELTO`.** `POST /api/register` ya existe, documentado en `API_CONTRACT.md` §4.1 el mismo día de esta actualización (`HB-001` §15.1).
- **`identity` del JWT — cambiado de `email` a `user.id` (UUID).** Nota de impacto: cualquier código futuro que use `get_jwt_identity()` recibirá un string UUID de `users.id`, no un email — si se necesita el email en un endpoint protegido, debe resolverse consultando `users` por `id`, no asumiendo que la identity ya es el email.

**Sigue pendiente (sin cambios en esta actualización):**
- **Hashing de contraseñas:** algoritmo (`werkzeug.security`, scrypt) mantenido tal cual estaba aprobado para la credencial de prueba, ahora aplicado a `users` real. El algoritmo **definitivo** ratificado formalmente sigue `PENDIENTE DE APROBACIÓN` (sección 20) — esta tarea no lo cambia, solo lo reutiliza.
- **`JWT_SECRET_KEY`:** sin cambios respecto a la corrección anterior (`os.environ` + `.env.example` + `.gitignore`).
- **Ningún endpoint protegido todavía:** no hay ningún uso de `@jwt_required()` en el código — `/register` y `/login` son públicos por definición. No hay ejemplo real de "protección de endpoint" en el código actual para documentar como patrón ya validado.
- **Sin logout, refresh token, ni expiración configurada explícitamente:** `flask_jwt_extended` trae valores por defecto de expiración de access token, pero no hay ninguna configuración explícita en `config.py` que los fije o los documente.
- **Sin manejo de roles/autorización:** no hay ningún concepto de rol, permiso o scope en el código.
- **Validaciones de `register` más allá de presencia y unicidad:** longitud mínima de contraseña, formato de email — no implementadas, no se inventaron por no estar respaldadas (`API_CONTRACT.md` §9, ítem 2).

Todo lo anterior son observaciones del estado actual, no una lista de tareas asumidas como aprobadas — la estrategia concreta para resolver cada limitación restante (cómo se protege un endpoint, política de expiración/refresh, reglas de validación adicionales) queda `PENDIENTE DE APROBACIÓN` (sección 20).

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
| Errores de dominio | **v0.6 — resuelto para auth.** `domain/auth/exceptions.py` define `InvalidCredentialsError` y `EmailAlreadyExistsError`. Siguen sin existir excepciones de dominio para otros flujos (no hay otros flujos todavía). |
| Errores de aplicación | `login_user()`/`register_user()` **lanzan** las excepciones de dominio de arriba en vez de retornar `None` — la route las captura con `try/except` y las traduce a HTTP (`401`, `409`). |
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
  - `flask_sqlalchemy.SQLAlchemy` (`db`) y `flask_migrate.Migrate` (`migrate`) — instanciadas en `extensions.py` desde v0.4, enlazadas con `db.init_app(app)`/`migrate.init_app(app, db)` en `create_app()` (nota corregida en esta actualización: esta sección seguía sin reflejarlo desde v0.4).

---

## 14. API

Principios generales de diseño de endpoints, basados en lo que los dos endpoints existentes (`POST /api/login`, `POST /api/register`) ya establecen como patrón de facto — **no se define aquí el catálogo completo de endpoints ni su contrato detallado** (eso es `API_CONTRACT.md`), según el alcance explícito de esta tarea:

- **Patrón actualmente observado:** ambos endpoints están registrados en el mismo blueprint (`auth_bp`) en `interfaces/routes/` y montados con prefijo `/api` desde `create_app()` (`url_prefix="/api"`).
- **Organización futura:** el uso de blueprints organizados por dominio funcional (p. ej. `auth_bp` para autenticación) se observa actualmente en `auth`, pero convertir esta organización en una regla general para futuros endpoints queda `PENDIENTE DE APROBACIÓN`.
- Los métodos HTTP se declaran explícitamente por ruta (`methods=["POST"]`), no hay convención documentada todavía sobre verbos para operaciones futuras (GET de colección, PUT/PATCH de actualización, DELETE).
- Los cuerpos de petición y respuesta son JSON (`request.get_json()` / `jsonify(...)`), sin excepción observada.
- No existe especificación formal de API (OpenAPI/Swagger) en `/docs` — `CLAUDE.md` §9 y §14 ya lo confirman. `HB-001` §15.1 exige documentar cada endpoint nuevo el mismo día del PR — esa documentación de endpoints, cuando exista, es un artefacto distinto de este documento de arquitectura.

---

## 15. Testing

- **Estructura — v0.6, implementada para auth:** `backend/tests/` (`conftest.py`, `test_auth.py`). 13 pruebas de integración para `POST /api/register` y `POST /api/login`, corridas contra PostgreSQL 16 real en Docker (base `thers_test`, separada de `thers_dev` — creada por `docker/postgres-init/01-create-test-db.sql`), no contra mocks. Cubren: creación con UUID generado por PostgreSQL, unicidad de email (incluida case-insensitive), presencia de campos, no exposición de `password_hash`, login correcto/incorrecto, usuario inexistente, mismo mensaje de error para "no existe" y "password incorrecta" (anti-enumeración), e identity del JWT (`sub`) igual al `id` del usuario.
- **Framework — elegido pragmáticamente en esta tarea, sin ratificación formal:** `pytest==8.3.4`, en `backend/requirements-dev.txt` (separado de `requirements.txt`, que sigue listando solo dependencias de producción). **`PENDIENTE DE APROBACIÓN`** (sección 20): esta elección resuelve la necesidad inmediata de probar `register`/`login`, pero el Comité Técnico no la ratificó formalmente como el framework oficial del proyecto — es el estándar de facto para Flask, no una decisión inventada, pero tampoco un ADR.
- **Unit tests / Integration tests / API tests:** las 13 pruebas actuales son de integración (HTTP + base de datos real vía `Flask.test_client()`), no hay pruebas unitarias puras de `domain/` todavía (serían triviales dado que `hash_password`/`verify_password` son envoltorios directos de `werkzeug.security`). Ampliar la estrategia a otras capas/flujos sigue `PENDIENTE DE APROBACIÓN`.

---

## 16. Seguridad

Estado actual observado, sin proponer remediaciones (fuera de alcance de esta tarea):

| Área | Estado |
|---|---|
| Secretos | **Corregido (parcial):** `JWT_SECRET_KEY` ya se lee de `os.environ`, con `backend/.env.example` documentando la variable y `backend/.gitignore` protegiendo un futuro `.env` real. Sigue sin existir gestión de secretos para un entorno desplegado (vault, CI/CD) — `PENDIENTE` (sección 20). |
| JWT | Emitido con `flask_jwt_extended` sobre una clave ahora externalizable por entorno; sin política de expiración explícita; sin endpoints protegidos actualmente (`@jwt_required()` no se usa en ningún lugar del código); sin refresh tokens. |
| Validación | Solo presencia de campos (sección 10); sin sanitización, sin límites de longitud, sin validación de formato de email — sin cambios en esta tarea (`API_CONTRACT.md` §9, ítem 2). |
| Autorización | No existe ningún concepto de roles/permisos en el código. |
| Exposición de errores | Los mensajes de error (`{"msg": "..."}`) no exponen detalles internos (stack traces, nombres de excepciones) en ninguno de los dos endpoints — pero no hay un manejador global de errores no capturados, por lo que un error inesperado (`500`) hoy caería en el comportamiento por defecto de Flask, cuyo contenido depende del modo `debug` (activo en `run.py`). |
| Datos sensibles | **v0.6 — corregido para datos reales.** `password_hash` (`werkzeug.security`, scrypt) se aplica ahora a la contraseña real de cada usuario registrado, persistida en `users` — ya no es solo la credencial de prueba. Nunca se expone `password_hash` en ninguna respuesta (verificado por prueba, `test_register_response_never_exposes_password_hash`). |
| Enumeración de usuarios | **Nuevo en esta tarea.** `POST /api/login` devuelve el mismo `401`/mensaje tanto si el email no existe como si la contraseña es incorrecta, para no permitir inferir qué emails están registrados (verificado por prueba). `POST /api/register` sí distingue con `409` cuando el email ya existe — es el comportamiento esperado de un registro, no una enumeración: el usuario ya sabe qué email está intentando registrar. |

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
- `domain/` es la capa más interna: no importa Flask, `flask_jwt_extended`, ni ningún driver de base de datos. El código actual lo cumple, incluyendo los archivos nuevos de esta tarea — `auth_service.py` no tiene imports externos; `repositories.py` (el puerto `UserRepository`) solo usa `abc` de la librería estándar; `exceptions.py` no tiene imports.
- `application/` puede importar de `domain/`, pero no debe importar Flask ni nada de `interfaces/` ni de `infrastructure/`. El código actual lo cumple: `login_use_case.py`/`register_use_case.py` importan de `domain/auth/auth_service.py` y `domain/auth/exceptions.py`, y reciben el repositorio como **parámetro** (tipado implícitamente como el puerto `UserRepository`) en vez de importar la implementación concreta.
- `interfaces/` puede importar de `application/` (y transitivamente de `domain/` a través de application). El código actual lo cumple para la lógica de negocio: `auth_routes.py` importa `login_user`/`register_user`, no `auth_service`/repositorio directamente para esa lógica.
- **Resuelto en esta tarea (era `PENDIENTE DE APROBACIÓN`): relación entre `application/`, persistencia e infraestructura.** Se adoptó el patrón *composition root*: `interfaces/routes/auth_routes.py` es el único punto del backend que importa tanto los casos de uso (`application/`) como la implementación concreta de infraestructura (`SQLAlchemyUserRepository`, `infrastructure/persistence/repositories/`) y las excepciones de dominio (`domain/auth/exceptions.py`, para el `try/except` que las traduce a HTTP). Instancia el repositorio una vez a nivel de módulo y lo inyecta en cada caso de uso como argumento. Esto es una excepción **deliberada y acotada** a la regla "interfaces/ no debería importar domain/ directamente" enunciada arriba — se limita a excepciones de dominio para manejo de errores HTTP, no a lógica de negocio. `domain/`/`application/` nunca importan SQLAlchemy ni `infrastructure/` (verificado explícitamente en esta tarea). Sin DI container: se consideró innecesario para el tamaño actual del proyecto (regla de simplicidad, mismo criterio que `FAS-001` §2).
- `config.py` pertenece a la configuración de la aplicación y `extensions.py` a la integración con Flask. **No son dependencias permitidas para `domain/`.** El acceso de `application/` o `interfaces/` a configuración deberá respetar la estrategia de configuración que sea aprobada.

Esta tabla formaliza como regla de arquitectura lo que el código ya hace hoy. La única adición de esta tarea es el patrón de composition root descrito arriba, ya justificado — no introduce ninguna capa nueva.

---

## 18. Estructura de archivos recomendada

Estructura para la evolución futura del backend, extendiendo la ya observada (sección 3) sin reorganizar lo existente — coherente con el principio de escalabilidad ya usado en el resto del repositorio ("cada dominio nuevo es una carpeta adicional", `REPOSITORY_STRUCTURE.md` §2):

```
backend/
├── app/
│   ├── interfaces/
│   │   └── routes/
│   │       ├── __init__.py          # (corregido — ver hallazgo sección 3)
│   │       └── auth_routes.py        # register + login, composition root (ver sección 17)
│   ├── application/
│   │   └── auth/
│   │       ├── __init__.py
│   │       ├── login_use_case.py
│   │       ├── register_use_case.py  # IMPLEMENTADO — v0.6
│   │       └── dtos.py               # PROPUESTA — no existe hoy
│   ├── domain/
│   │   └── auth/
│   │       ├── __init__.py
│   │       ├── auth_service.py       # hash_password / verify_password — v0.6
│   │       ├── exceptions.py         # IMPLEMENTADO — v0.6
│   │       ├── repositories.py       # IMPLEMENTADO — v0.6 (puerto UserRepository)
│   │       └── entities.py           # PROPUESTA — no existe hoy
│   ├── infrastructure/
│   │   └── persistence/
│   │       ├── __init__.py
│   │       ├── models.py             # IMPLEMENTADO — v0.5
│   │       └── repositories/
│   │           ├── __init__.py       # IMPLEMENTADO — v0.6
│   │           └── user_repository.py  # IMPLEMENTADO — v0.6 (SQLAlchemyUserRepository)
│   ├── config.py
│   ├── extensions.py
│   └── __init__.py
├── tests/                             # IMPLEMENTADO — v0.6 (ver sección 15)
│   ├── __init__.py
│   ├── conftest.py
│   └── test_auth.py
├── migrations/                        # IMPLEMENTADO — v0.4 (ver sección 8)
├── run.py
├── requirements.txt                   # IMPLEMENTADO — ver sección 2 y 19
├── requirements-dev.txt               # IMPLEMENTADO — v0.6 (pytest, ver sección 15)
└── .env.example                       # IMPLEMENTADO — ver sección 12 y 19
```

Todo lo marcado `PROPUESTA` (`dtos.py`, `entities.py`) es una sugerencia de evolución consistente con las capas ya existentes, **no una decisión tomada** — cada una queda listada también en la sección 20. No se necesitaron para register/login (el `dict` de respuesta ya construido a mano cumple, y no hay una entidad de dominio `User` separada del modelo de persistencia — ver sección 7).

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
- **v0.5:** modelo `User` alineado a la estrategia de persistencia aprobada por el equipo (`app/infrastructure/persistence/models.py`): `id` **UUID** con `DEFAULT gen_random_uuid()` en PostgreSQL, `email` **`CITEXT`** (case-insensitive), `password_hash` `TEXT`, `created_at`/`updated_at` `TIMESTAMPTZ` con `DEFAULT now()` y `updated_at` mantenida por trigger (`set_updated_at`/`trg_users_updated_at`). Migración escrita a mano (`a1b2c3d4e5f6_create_users_table.py`) que crea la extensión `citext`, la tabla y el trigger — verificada contra PostgreSQL 16 real vía Docker Compose (`docker-compose.yml`, base `thers_dev`), incluyendo el funcionamiento del trigger, la unicidad case-insensitive de `email`, downgrade/upgrade repetido y reconstrucción completa desde un volumen Docker vacío.
- **v0.6 — integración de autenticación con persistencia real (esta tarea):** `POST /api/register` (nuevo) y `POST /api/login` (migrado) operan contra `users` real, no contra una credencial hardcodeada. Patrón Repository implementado: puerto `UserRepository` en `domain/auth/repositories.py`, adaptador `SQLAlchemyUserRepository` en `infrastructure/persistence/repositories/user_repository.py`, inyectado desde `interfaces/routes/auth_routes.py` (composition root, ver sección 17). Excepciones de dominio (`EmailAlreadyExistsError` → `409`, `InvalidCredentialsError` → `401`, mismo mensaje para "no existe" y "password incorrecta"). `identity` del JWT cambiado de `email` a `user.id` (UUID). `id` sigue generándose exclusivamente en PostgreSQL (`gen_random_uuid()`) — ningún `uuid.uuid4()` en el código Python. 13 pruebas de integración (`backend/tests/`) contra PostgreSQL 16 real (base `thers_test`, separada de `thers_dev`). Documentado el mismo día en `API_CONTRACT.md` §4.1 (`HB-001` §15.1).

### PENDIENTE
- **Conexión a una base PostgreSQL compartida por el equipo o de producción** — el modelo y la migración ya se verificaron end-to-end contra PostgreSQL 16 real en Docker (desarrollo local reproducible, `docker-compose.yml`), pero no existe todavía ninguna base compartida por el equipo ni de producción.
- **Ratificación formal por el Comité Técnico** de las decisiones ya codificadas en v0.4/v0.5/v0.6 (SQLAlchemy, UUID, CITEXT, Flask-Migrate, patrón Repository con puerto en `domain/`, pytest como framework de testing) — ver nota de gobernanza, sección 2.
- Estrategia de hashing **definitiva** para `users` (la v0.6 reutiliza `werkzeug.security`/scrypt ya usado para la credencial de prueba, no ratifica un algoritmo distinto — sección 20).
- Endpoints protegidos con `@jwt_required()` (ninguno existe hoy — el primer caso real definirá el patrón de uso de `get_jwt_identity()` sobre el UUID, ver sección 9).
- Política de expiración/refresh de JWT.
- Roles y autorización.
- Validación declarativa (schemas/DTOs) — y validaciones adicionales de `register` (longitud mínima de contraseña, formato de email).
- Manejo global de errores (`@app.errorhandler`) y formato de error unificado.
- Configuración por ambiente (`Development`/`Production`/`Testing`).
- Ratificación formal de `requirements.txt`/`requirements-dev.txt` y `pyproject.toml` (sección 20, ítem 14).
- Integración del Frontend (`Register.jsx`, `Login.jsx`, `useAuth.js`) con los endpoints reales — fuera de alcance de esta tarea, que fue exclusivamente de backend.
- Entidad de dominio `User` separada del modelo de persistencia (`domain/auth/entities.py`, marcada `PROPUESTA` — no se justificó como necesaria para register/login).
- Especificación formal de API (OpenAPI/Swagger).
- Política de CORS por ambiente.

---

## 20. PENDIENTES DE APROBACIÓN

Toda decisión arquitectónica no respaldada hoy por código ni por documento oficial ratificado:

1. **Estrategia de persistencia:** ORM vs. SQL directo — **ya implementado como SQLAlchemy + Flask-Migrate/Alembic (v0.4)** por indicación directa del Tech Lead Backend; **ratificación formal por el Comité Técnico pendiente de confirmar** (`HB-001` §11.1). ~~Patrón de repository exacto~~ y ~~mecanismo de dependencia entre `application/` y la implementación de persistencia~~ — **resueltos en v0.6** (patrón Repository con puerto en `domain/`, composition root en `interfaces/routes/`, ver sección 17); ratificación formal igualmente pendiente. Pool de conexiones para producción sigue sin definir.
2. **Modelo de datos de usuario y esquema de PostgreSQL** — normalización, índices, migraciones (ya señalado como hueco general en `CLAUDE.md` §14).
3. **Estrategia de hashing de contraseñas para el modelo de datos real** (algoritmo, librería) — se aplicó `werkzeug.security`/`scrypt` como corrección puntual sobre la credencial de prueba hardcodeada, y **v0.6 la reutiliza tal cual para `users` real** (sección 9, 16, 19), pero **sigue sin quedar ratificado como el algoritmo definitivo**; esa decisión sigue abierta.
4. **Estructura de DTOs/schemas** y si se adopta una librería de validación declarativa (Marshmallow, Pydantic, u otra).
5. **Formato estándar de respuesta de error** para toda la API.
6. **Manejador global de excepciones** (`@app.errorhandler`) y taxonomía de excepciones de dominio/aplicación.
7. **Configuración por ambiente** (Development/Production/Testing) y lista oficial de variables de entorno requeridas.
8. **Gestión de secretos en un entorno desplegado** (vault, variables de CI/CD, rotación) — el mecanismo local ya se resolvió (`JWT_SECRET_KEY` vía `os.environ` + `.env.example` + `.gitignore`, sección 12, 16, 19); la estrategia para producción/CI sigue sin definir.
9. **Política de expiración y refresh de tokens JWT.**
10. **Modelo de roles y autorización.**
11. **Política de CORS por ambiente** (orígenes permitidos en producción vs. desarrollo).
12. **Framework y estrategia de testing** (unit/integration/API) — **`pytest` elegido pragmáticamente en v0.6** (13 pruebas de integración para auth, sección 15), sin ratificación formal por el Comité Técnico todavía. Ampliar a otras capas/flujos sigue sin definir.
13. **Especificación formal de API** (OpenAPI/Swagger) y su ubicación (`/docs` vs. Notion, según `HB-001` §15.1 que menciona ambas opciones sin decidir).
14. **Ratificación formal de las versiones fijadas en `requirements.txt`** — el archivo ya existe (Flask 3.1.3, flask-cors 6.0.2, Flask-JWT-Extended 4.7.1, tomadas del entorno local observado), pero el equipo no lo ha ratificado formalmente como el estándar oficial de versiones; `pyproject.toml` sigue sin existir.
15. **Propósito de `backend/app.py`** — si se conserva, se elimina o se integra a la arquitectura por capas (fuera de alcance de esta tarea decidirlo).
16. **Corrección del nombrado `_init_.py` → `__init__.py`** en `application/`, `domain/` e `interfaces/routes/`, y si `interfaces/` debe tener su propio marcador de paquete (hallazgo de código, sección 3) — fuera de alcance implementarlo aquí.
17. ~~Definición formal de las reglas de dependencia entre `application/`, persistencia e infraestructura~~ — **resuelto en v0.6** (patrón Repository + composition root, sección 17); ratificación formal por el Comité Técnico pendiente de confirmar.
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
