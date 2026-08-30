# BACKEND_ARCHITECTURE

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/BACKEND_ARCHITECTURE.md` |
| Versión | 0.12 (Propuesta) |
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
>
> **v0.7 — perfil completo de registro + primer endpoint protegido (THERS Backend Fase 2.1, `ADR-002-user-profile-fields.md`):** `users` gana `username`/`phone`/`country_code`/`birth_date` (migración `a1edcbff74d8`); `domain/auth/validators.py` (nuevo) valida su formato; `domain/auth/repositories.py` gana `find_by_id`; `application/auth/user_presenter.py` (nuevo) centraliza la forma pública del `user` para register/login/`me`; `application/auth/get_current_user_use_case.py` (nuevo) orquesta el primer endpoint protegido; `interfaces/routes/user_routes.py` (nuevo blueprint `users_bp`) implementa `GET /api/users/me` con `@jwt_required()`; `app/extensions.py` gana callbacks de error JWT (`unauthorized_loader`/`invalid_token_loader`/`expired_token_loader`) para homogenizar a `401`. Reflejado en §2, §6, §7, §8, §9, §14, §15, §18, §19, §20.
>
> **v0.8 — auditoría documental integral de THERS, parte 1 (sincronización de §4, sin cambios de código):** corregido §4 ("Flujo de una petición"), que seguía describiendo el flujo pre-persistencia (`validate_user()` contra credenciales hardcodeadas, capas de Repository/PostgreSQL marcadas "NO IMPLEMENTADO") — desactualizado respecto al resto del documento desde v0.6. Verificado con ejecución real: `pytest` (52/52 tests) corrido contra PostgreSQL 16 real en el contenedor `thers_postgres_dev` (puerto local mapeado a 5433) — confirma que la suite completa (`test_auth.py`, `test_users_me.py`, `test_update_profile.py`, `test_username_policy.py`) pasa.
>
> **v0.9 — auditoría documental integral de THERS, parte 2 (documentar `PATCH /api/users/me`, hueco real, sin cambios de código):** este documento nunca se actualizó cuando se implementó `PATCH /api/users/me` (`ADR-003-profile-update-contract.md`, commit `ff9c899`) — a diferencia de `API_CONTRACT.md` (v0.5) y `DATABASE_ARCHITECTURE.md` (v0.6/v0.7), que sí lo documentaron el mismo día (`HB-001` §15.1). Se agregan aquí: `domain/auth/username_policy.py` (`can_change_username()`, regla pura de cooldown de 30 días), `domain/auth/repositories.py` gana el método abstracto `update()`, `infrastructure/persistence/repositories/user_repository.py` gana `SQLAlchemyUserRepository.update()` (mismo patrón de traducción de `IntegrityError` que `create()`), `application/auth/update_profile_use_case.py` (nuevo, orquesta la lógica de no-op/cooldown de `username`), `interfaces/routes/user_routes.py` gana `PATCH /users/me` sobre el blueprint `users_bp` existente, migración `b2f4a19c3d7e_add_username_changed_at_to_users.py`. Reflejado en §6, §7, §8, §14, §15, §18, §19.
>
> **v0.12 — primer despliegue real (Render) y fail-fast de `JWT_SECRET_KEY`.** Dos cambios distintos, documentados juntos por tocar la misma sección:
>
> *(a) Sincronización — despliegue a Render, sin ratificación formal, ya en el código desde antes de esta actualización, nunca documentado hasta ahora:* `backend/requirements.txt` gana `gunicorn==23.0.0`; `run.py` ya no fija `host="127.0.0.1"`/`debug=True` como literales de solo-desarrollo — usa `host="0.0.0.0"`, `port` desde `$PORT` (convención de Render) y `debug=False`; `config.py` gana `_normalize_database_url()` porque Render entrega `DATABASE_URL` como `postgres://`/`postgresql://` sin driver explícito, y SQLAlchemy 2.x lo resuelve contra `psycopg2` (no instalado) si no se reescribe a `postgresql+psycopg://`. **No hay todavía ningún ADR ni documento de DevOps que ratifique Render como plataforma** (`CLAUDE.md` §5 "DevOps": sigue siendo territorio no especificado) — se documenta como hecho de código observado, igual que esta sección ya hace con otras decisiones de infraestructura.
>
> *(b) Corrección de seguridad — `JWT_SECRET_KEY` deja de tener un fallback inseguro automático:* con un despliegue real en marcha, que `JWT_SECRET_KEY` faltara y la app arrancara igual con `dev-only-insecure-key-CHANGE-ME` (un valor público, en este mismo archivo) dejó de ser una molestia de desarrollo y pasó a ser una forma de que cualquiera con acceso al repositorio firme JWTs válidos para cualquier usuario contra un backend desplegado. `config.py` ahora **falla al arrancar** (`RuntimeError`) si `JWT_SECRET_KEY` no está definida, salvo que se pida explícitamente el fallback con `ALLOW_INSECURE_JWT_DEV_FALLBACK=1` (nueva variable, solo para desarrollo local — `backend/.env.example` ya la trae en `1` para que `cp .env.example .env` siga funcionando sin pasos extra). 4 pruebas nuevas en subproceso (`test_config_jwt_secret.py`, necesario porque `Config` solo se evalúa una vez por proceso); suite completa 63/63. Reflejado en §12, §16, §19, §20.
>
> **v0.11 — validación de formato de `email` y longitud mínima de `password` en `POST /api/register` (cierra el pendiente de §9/§19 y `API_CONTRACT.md` §9 ítem 2 — no confundir con §20 ítem 4, "DTOs/schemas", que sigue abierto y es un asunto distinto):** `domain/auth/validators.py` gana `is_valid_email()` (regex básica, sin verificar dominio real) e `is_valid_password()` (`MIN_PASSWORD_LENGTH = 8`) — mismo patrón que los validadores ya existentes, sin librería declarativa nueva. Ambos umbrales son placeholders de producto explícitos y revisables (mismo criterio que `MIN_AGE_YEARS`, `ADR-002` §3), decididos como cambio técnico de bajo impacto (`HB-001` §11) — no alteran arquitectura, esquema, ni ningún endpoint más allá de `register`. 3 pruebas nuevas; suite completa 59/59, ejecutada contra PostgreSQL 16 real. Reflejado en §9, §10, §16, §20.
>
> **v0.10 — manejador global de errores (cierra `BACKEND_ARCHITECTURE.md` §20 ítem 6 y `API_CONTRACT.md` §9 ítem 1):** nuevo `app/interfaces/error_handlers.py` (`register_error_handlers(app)`, llamado desde `create_app()`) traduce cualquier `HTTPException` de Flask/Werkzeug (`404`, `405`, y de forma genérica cualquier otra, incluido el `400` que `request.get_json()` sin `silent=True` ya lanzaba en `auth_routes.py` ante un body no-JSON — hallazgo real detectado al implementar esto, no hipotético) y cualquier excepción no controlada (`500`) al mismo formato `{"msg": "..."}` que el resto de la API — **se mantiene deliberadamente ese formato, sin introducir `{"error": {...}}`**, para no forzar una migración de contrato que ningún endpoint necesita hoy. El `500` nunca expone traceback, tipo de excepción, ni datos sensibles — el detalle real va a `app.logger.exception(...)`. No interfiere con los callbacks de `flask_jwt_extended` (`app/extensions.py`), que siguen resolviendo sus propios `401` antes de llegar a este manejador — verificado con la suite completa (56/56 tests, incluidos los 4 nuevos de `test_error_handlers.py`) contra PostgreSQL 16 real. `run.py` (`debug=True` hardcodeado) no se modificó — sigue `PENDIENTE` (§12), pero el riesgo principal que representaba (fuga de traceback en un `500`) ya no depende de esa configuración pendiente: el manejador intercepta la excepción antes de que el modo debug decida mostrarla. Reflejado en §11, §15, §16, §18, §19, §20.

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
| `requirements.txt` | Ya existía fijando `Flask==3.1.3`, `flask-cors==6.0.2`, `Flask-JWT-Extended==4.7.1` | **v0.4:** se agregaron `Flask-SQLAlchemy==3.1.1`, `Flask-Migrate==4.1.0`, `psycopg[binary]==3.3.4`. **v0.12:** se agregó `gunicorn==23.0.0` | Versiones tomadas de la instalación real verificada en esta tarea (`pip freeze`). Sigue sin ratificación formal del equipo como estándar oficial (`pyproject.toml` sigue sin existir, sección 20) |
| gunicorn | No mencionado en `/docs` — DevOps sigue sin documentación oficial (`CLAUDE.md` §5) | 23.0.0 — servidor WSGI de producción, agregado junto con el resto de la preparación para Render (ver nota v0.12 al inicio del documento) | `run.py`/`app.run()` (servidor de desarrollo de Werkzeug) sigue existiendo como punto de entrada local; `gunicorn` es el que se asume en el entorno desplegado, aunque no hay ningún `Procfile`/`render.yaml` en el repositorio que lo confirme — el comando de arranque real vive en la configuración de Render, fuera de este repositorio |

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

> **Corregido en v0.8 (auditoría documental).** Esta sección seguía describiendo el flujo pre-persistencia (anterior a v0.6) — quedó desactualizada respecto al resto del propio documento (§6–§9, §19) cuando se integró la persistencia real. Lo que sigue refleja el código actual, verificado en esta auditoría (lectura de `interfaces/routes/`, `application/auth/`, `domain/auth/`, `infrastructure/persistence/`, y ejecución real de la suite de tests contra PostgreSQL 16).

Confirmado por el código actual (`interfaces/routes/` → `application/auth/` → `domain/auth/` + `infrastructure/persistence/`), para los cuatro endpoints implementados (`POST /api/register`, `POST /api/login`, `GET /api/users/me`, `PATCH /api/users/me`):

```
HTTP Request
   ↓
Interface / Route          (backend/app/interfaces/routes/auth_routes.py, user_routes.py)
   ↓
Application / Use Case     (backend/app/application/auth/*_use_case.py)
   ↓
Domain                     (backend/app/domain/auth/auth_service.py, validators.py, username_policy.py — reglas puras)
   ↓
Repository (puerto)        (backend/app/domain/auth/repositories.py — interfaz UserRepository, sin I/O)
   ↓
Repository (adaptador)     (backend/app/infrastructure/persistence/repositories/user_repository.py — SQLAlchemyUserRepository)
   ↓
PostgreSQL                 (tabla `users`, PostgreSQL 16 real — ver sección 8)
```

El flujo real termina en PostgreSQL, no en `domain/`: cada route (composition root, ver §17) instancia `SQLAlchemyUserRepository` y lo inyecta en el caso de uso correspondiente (`login_user`, `register_user`, `get_current_user`, `update_profile`), que a su vez usa `domain/` solo para reglas puras (hashing, validación de formato, política de cooldown de `username`) — nunca para acceder a datos. La credencial hardcodeada (`test@test.com`/`123456`) que este diagrama describía como el comportamiento real **se eliminó por completo en v0.6** (ver §7, §9, §19) y no existe en el código actual.

---

## 5. Interfaces

- **Routes:** un único módulo, `app/interfaces/routes/auth_routes.py`.
- **Blueprints:** un único blueprint, `auth_bp`, registrado en `create_app()` con prefijo `/api` (`app.register_blueprint(auth_bp, url_prefix="/api")`).
- **Request handling:** cada route lee el body con `request.get_json()`, valida presencia de campos manualmente (`if not data`, `if not email or not password`) y responde con `jsonify(...)` + código HTTP explícito. No hay capa de validación declarativa (schemas) — ver sección 10.
- **Responses:** formato observado — `{"msg": "..."}` para errores, `{"token": ..., "user": {...}}` para éxito de login. No hay un formato de respuesta estandarizado ni documentado para todos los endpoints futuros — ver sección 11 y 20.

---

## 6. Application

- **Casos de uso — v0.9:** `login_user(email, password, user_repository)`, `register_user(name, username, email, phone, country_code, birth_date, password, user_repository)` (firma ampliada v0.7, `ADR-002`), `get_current_user(user_id, user_repository)` (v0.7, `application/auth/get_current_user_use_case.py`, usado por `GET /api/users/me`) y `update_profile(user_id, fields, user_repository)` (nuevo, v0.9, `application/auth/update_profile_use_case.py`, `ADR-003` — usado por `PATCH /api/users/me`). Todos reciben el repositorio como parámetro (inyectado desde `interfaces/routes/`, ver §8) en vez de importar SQLAlchemy.
- **`update_profile` — v0.9:** orquesta dos reglas de `ADR-003` que no son solo formato: (1) un `username` igual al actual se elimina de `fields` antes de persistir — no actualiza `username_changed_at` ni consume el cooldown; (2) si el único campo enviado era ese `username` sin cambio real, no hay `commit` (`fields` queda vacío) y se devuelve el usuario tal como está, sin tratarlo como error. Si `fields` queda vacío tras esa depuración de `username`, delega en `user_repository.update()`.
- **Orquestación:** los casos de uso no conocen Flask ni HTTP — reciben primitivos y un objeto `UserRepository` (interfaz de dominio, no la implementación concreta), y devuelven un `dict` o lanzan una excepción de dominio (`EmailAlreadyExistsError`, `UsernameAlreadyExistsError`, `InvalidCredentialsError`, `UserNotFoundError` — ver §7). Esto es coherente con el principio de que `application/` no debería depender del framework de entrada ni de infraestructura concreta.
- **`user_presenter.py` — nuevo, v0.7:** `application/auth/user_presenter.py` centraliza `to_public_user(user)`, la forma pública compartida del objeto `user` (`id`, `username`, `email`, `name`, `phone`, `country_code`, `birth_date`) que devuelven `register`/`login`/`me` — evita duplicar esa construcción en los tres casos de uso.
- **DTOs / Schemas:** **siguen sin estar definidos** como estrategia general — `user_presenter.py` (arriba) resuelve la duplicación puntual del objeto `user`, no es un framework de DTOs/schemas. Definir una estrategia general (Marshmallow/Pydantic) queda como `PENDIENTE DE APROBACIÓN`.

---

## 7. Domain

- **Entidades:** sigue sin existir una clase de entidad `User` de dominio (el `User` con el que trabaja el resto del código es el modelo SQLAlchemy de `infrastructure/persistence/models.py` — ver §8; formalizar una entidad de dominio separada sigue `PENDIENTE`, no se justificó como necesaria para esta tarea).
- **Reglas de negocio — v0.6:** la credencial hardcodeada (`test@test.com`/`123456`) **se eliminó por completo**. `domain/auth/auth_service.py` expone únicamente `hash_password(password)` y `verify_password(password, password_hash)` (ambas envoltorios directos de `werkzeug.security`). Las demás reglas de negocio de auth (unicidad de email, "usuario no encontrado") viven como excepciones de dominio en `domain/auth/exceptions.py` (`EmailAlreadyExistsError`, `InvalidCredentialsError`) — deliberadamente sin distinguir "email inexistente" de "password incorrecta" en el mensaje/código HTTP, para no permitir enumerar emails registrados.
- **Repository (puerto) — v0.9:** `domain/auth/repositories.py` define `UserRepository` (`abc.ABC`) con `create(name, username, email, phone, country_code, birth_date, password_hash)`, `find_by_email(email)`, `find_by_id(user_id)` (v0.7, usado por `GET /api/users/me`) y `update(user_id, fields)` (nuevo, v0.9, usado por `PATCH /api/users/me`) — actualiza únicamente las columnas presentes en `fields`, un único commit, `None` si el usuario no existe. Vive en `domain/` porque es un contrato de negocio puro (sin I/O real, solo `abc`) — la implementación concreta con SQLAlchemy vive en `infrastructure/` (ver §8) y depende de este puerto, nunca al revés.
- **Validators — v0.7:** `domain/auth/validators.py` (funciones puras, solo `re`/`datetime` de la librería estándar) valida formato de `username`, `phone`, `country_code` y edad mínima de `birth_date` (`ADR-002-user-profile-fields.md` §3) — reutilizado sin cambios por `PATCH /api/users/me` (v0.9, `ADR-003`). Deliberadamente no valida `email` ni longitud de `password` (siguen `PENDIENTE DE APROBACIÓN`, `API_CONTRACT.md` §9 ítem 2).
- **Username policy — nuevo, v0.9:** `domain/auth/username_policy.py` (`can_change_username(last_changed_at, today=None)`, funciones puras, solo `datetime` de la librería estándar) implementa el cooldown de 30 días entre cambios de `username` ratificado por `ADR-003-profile-update-contract.md` §Evolución futura. `today` es inyectable para tests deterministas sin depender del reloj del sistema.
- **Lógica actualmente ubicada en domain:** `auth_service.py`, `exceptions.py`, `repositories.py`, `validators.py` y `username_policy.py` (v0.9). Ninguno depende de nada externo (ni Flask, ni SQLAlchemy, ni una base de datos real) — verificado explícitamente en esta auditoría (ningún archivo de `domain/` importa `sqlalchemy` ni `flask`).
- **Qué NO debe depender del framework:** por diseño de Clean Architecture (la misma que `REPOSITORY_STRUCTURE.md` §6 propone), `domain/` no debe importar Flask, `flask_jwt_extended`, ni ningún detalle de infraestructura (ORM, HTTP, PostgreSQL). El código actual **cumple** esto, incluso tras la integración de persistencia — verificado explícitamente en esta tarea (ningún archivo de `domain/` importa `sqlalchemy` ni `flask`). Mantener esta regla hacia adelante es un requisito de este documento, no una preferencia personal.

---

## 8. Persistencia

- **Repositories — v0.9:** `app/infrastructure/persistence/repositories/user_repository.py` define `SQLAlchemyUserRepository`, que implementa el puerto `UserRepository` (`domain/auth/repositories.py`, ver §7): `create()` inserta un `User` (con los campos de perfil, `ADR-002`) y traduce `sqlalchemy.exc.IntegrityError` a `EmailAlreadyExistsError` o `UsernameAlreadyExistsError` de dominio, distinguiendo por `constraint_name` del error de PostgreSQL (`ix_users_email` vs `uq_users_username`) en vez de adivinar por texto; `find_by_email()` hace `SELECT` por `email` (case-insensitive, vía `CITEXT`); `find_by_id()` (v0.7) hace `db.session.get(User, user_id)`, usado por `GET /api/users/me`; `update()` (nuevo, v0.9, usado por `PATCH /api/users/me`) hace `setattr` columna por columna solo sobre las claves de `fields` (nunca `**data`/mass assignment — la whitelist ya llega filtrada desde la route), un único `commit()`, mismo patrón de traducción de `IntegrityError` → `UsernameAlreadyExistsError` que `create()`, y `db.session.refresh(user)` antes de devolver el registro actualizado. Es el único módulo del backend que importa `sqlalchemy` para acceso a datos de `users`. Instanciado en `interfaces/routes/auth_routes.py` **y** en `interfaces/routes/user_routes.py` (cada blueprint compone su propio repositorio, ver §14) e inyectado en los casos de uso; `domain/`/`application/` solo conocen el puerto abstracto.
- **Acceso a PostgreSQL — v0.5, implementado y verificado localmente:** driver instalado (`psycopg[binary]==3.3.4`), `SQLALCHEMY_DATABASE_URI` leída desde `DATABASE_URL` en `config.py`, modelo `User` definido (`app/infrastructure/persistence/models.py`: `id` **UUID** con `DEFAULT gen_random_uuid()` generado **en PostgreSQL** (no en Python), `name` `VARCHAR(120)`, `email` **`CITEXT`** único+indexado (case-insensitive, extensión `citext`), `password_hash` **`TEXT`**, `created_at`/`updated_at` `TIMESTAMPTZ` con `DEFAULT now()` — `updated_at` mantenida por un trigger de PostgreSQL, no por SQLAlchemy). La migración (`a1b2c3d4e5f6_create_users_table.py`, escrita a mano, no autogenerada) crea la extensión `citext`, la tabla y el trigger `trg_users_updated_at`. El flujo modelo→migración→`flask db upgrade` se verificó contra PostgreSQL 16 real vía Docker Compose (`docker-compose.yml`, imagen `postgres:16-alpine`, base `thers_dev`), confirmando el esquema resultante, el comportamiento del trigger y la unicidad case-insensitive de `email` con `psql` — incluyendo un downgrade + upgrade completo y una reconstrucción desde un volumen Docker vacío (`docker compose down -v && docker compose up -d && flask db upgrade`). **Sigue sin haber una base compartida por el equipo o de producción** — esto es una base de desarrollo local reproducible, no un despliegue real.
- **Migraciones — v0.9:** `backend/migrations/` (Flask-Migrate/Alembic), con tres migraciones: `a1b2c3d4e5f6_create_users_table` (inicial, `email` único), `a1edcbff74d8_add_profile_fields_to_users` (v0.7, `ADR-002`) que agrega `username`/`phone`/`country_code`/`birth_date` con `uq_users_username`, y `b2f4a19c3d7e_add_username_changed_at_to_users` (nuevo, v0.9, `ADR-003`) que agrega `username_changed_at` (`TIMESTAMPTZ`, nullable) — migración aditiva sin backfill, soporta el cooldown de `PATCH /api/users/me`. Las tres verificadas con `flask db upgrade`/`downgrade` — la última, con ejecución real en esta auditoría (`alembic_version` en `thers_test` confirmado en `b2f4a19c3d7e`, cabeza de la cadena).
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
- ~~Ningún endpoint protegido todavía~~ — **resuelto en v0.7:** `GET /api/users/me` (`interfaces/routes/user_routes.py`, blueprint `users_bp`) es el primer endpoint con `@jwt_required()`, identidad resuelta exclusivamente con `get_jwt_identity()`. Fija el patrón: nuevo blueprint por recurso (no reutiliza `auth_bp`), composition root propio (instancia su propio `SQLAlchemyUserRepository()`), y errores JWT homogenizados a `401` vía callbacks en `app/extensions.py` (por defecto `flask_jwt_extended` responde `422` para token malformado — se sobrescribió para que todo caso de token ausente/inválido/expirado responda `401` con `{"msg": "..."}`, mismo formato que el resto de la API).
- **Sin logout, refresh token, ni expiración configurada explícitamente:** `flask_jwt_extended` trae valores por defecto de expiración de access token, pero no hay ninguna configuración explícita en `config.py` que los fije o los documente.
- **Sin manejo de roles/autorización:** no hay ningún concepto de rol, permiso o scope en el código.
- **Validaciones de `register` más allá de presencia y unicidad — v0.11: resuelto.** `domain/auth/validators.py` ya valida formato de `email` e `password` (`is_valid_email`/`is_valid_password`, `API_CONTRACT.md` §9 ítem 2), además de los campos de perfil ya cubiertos desde v0.7 (`username`/`phone`/`country_code`/`birth_date`, incluida edad mínima, ratificados por `ADR-002`).

Todo lo anterior son observaciones del estado actual, no una lista de tareas asumidas como aprobadas — la estrategia concreta para resolver cada limitación restante (cómo se protege un endpoint, política de expiración/refresh, reglas de validación adicionales) queda `PENDIENTE DE APROBACIÓN` (sección 20).

---

## 10. Validación

- **Request validation:** manual, dentro de cada route. `auth_routes.py` valida presencia de todos los campos obligatorios y, desde v0.11, también formato de `email` (`is_valid_email`) y longitud mínima de `password` (`is_valid_password`, 8 caracteres) — mismo nivel de rigor que el resto de `domain/auth/validators.py`. Sigue sin haber validación general de tipos de datos más allá de los campos ya cubiertos.
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
| Errores HTTP explícitos | Manejados manualmente en cada route con `jsonify(...)`, código explícito (`400`, `401`, `404`, `409`) — sin cambios, este manejo local sigue siendo la primera línea para los errores que cada endpoint ya conoce de antemano. |
| Errores HTTP no anticipados y excepciones no controladas | **v0.10 — resuelto.** `app/interfaces/error_handlers.py` (`register_error_handlers(app)`, registrado en `create_app()`) captura: `404` (URL sin ruta), `405` (verbo no permitido), cualquier otro `HTTPException` de Werkzeug (p. ej. `400` por `request.get_json()` con body no-JSON) y `Exception` genérica (`500`) — todas responden `{"msg": "..."}`, nunca la página HTML por defecto de Flask. El `500` nunca expone traceback ni el tipo/mensaje real de la excepción (verificado por prueba, `test_error_handlers.py`); el detalle completo va a `app.logger.exception(...)`. |
| Formato de respuesta de error | `{"msg": "<texto>"}`, aplicado ahora de forma **uniforme a toda la API** (v0.10) — antes era el patrón que cada endpoint reproducía manualmente, ahora también es el formato de cualquier error no anticipado por ninguna route. Sigue sin existir un código de error machine-readable (`{"msg": ..., "code": ...}`) — no se introdujo por no estar respaldado por ninguna decisión ni necesidad actual (§20). |

**v0.10 — resuelto:** ya existe un manejador global de excepciones no capturadas (`app/interfaces/error_handlers.py`). Sigue `PENDIENTE DE APROBACIÓN` únicamente si el equipo quiere evolucionar el formato `{"msg": "..."}` hacia una estructura con código machine-readable — no hay ninguna necesidad actual que lo justifique, así que este documento no lo propone.

---

## 12. Configuration

- **`config.py`:** una única clase `Config`. `JWT_SECRET_KEY` se lee de `os.environ.get("JWT_SECRET_KEY")`. **v0.12 — ya no cae en un fallback inseguro automático**: si falta, `Config` lanza `RuntimeError` al importarse (la app no llega a arrancar) salvo que se defina explícitamente `ALLOW_INSECURE_JWT_DEV_FALLBACK=1` — variable pensada exclusivamente para desarrollo local, nunca para un entorno desplegado. Antes de v0.12, la ausencia de `JWT_SECRET_KEY` producía solo una advertencia por `stderr` y la app arrancaba igual con un valor público (`dev-only-insecure-key-CHANGE-ME`) — aceptable mientras no hubiera ningún despliegue real, dejó de serlo en cuanto lo hubo (ver nota v0.12 al inicio del documento).
- **Variables de entorno:** `JWT_SECRET_KEY`, `DATABASE_URL` y, desde v0.12, `ALLOW_INSECURE_JWT_DEV_FALLBACK` (leídas vía `os.environ`, sin `python-dotenv` — no se instaló ninguna dependencia nueva). `backend/.env.example` las documenta las tres. **v0.12 — resuelto:** `run.py` ya no fija `host`/`port`/`debug` como literales de solo-desarrollo — `host="0.0.0.0"`, `port` desde `$PORT` (default `5000` si no está definida), `debug=False` siempre (ver nota v0.12).
- **`_normalize_database_url()` — nuevo, v0.12:** Render (y otros proveedores de PostgreSQL gestionado) entregan `DATABASE_URL` como `postgres://`/`postgresql://`, sin driver explícito — SQLAlchemy 2.x lo resolvería contra `psycopg2` (no instalado, solo `psycopg[binary]` v3, ver §2) y fallaría recién al conectar, no al arrancar. `config.py` reescribe cualquiera de esos dos prefijos a `postgresql+psycopg://` antes de asignarlo a `SQLALCHEMY_DATABASE_URI`.
- **Secretos:** el `JWT_SECRET_KEY` real no vive hardcodeado en el código — `backend/.env.example` (documentación, sin secreto real) y `backend/.gitignore` evitan que un `.env` real se versione (`HB-001` §20, regla innegociable). La gestión de secretos en el entorno desplegado real (confirmar que Render tiene `JWT_SECRET_KEY`/`DATABASE_URL` configuradas con valores reales, rotación, etc.) sigue **`PENDIENTE`** — es una verificación operativa que corresponde al equipo, no algo que este documento pueda confirmar por sí mismo.
- **Configuración por ambiente:** **sigue sin existir como arquitectura formal.** Una sola clase `Config`, sin `DevelopmentConfig`/`ProductionConfig`/`TestingConfig` ni un mecanismo general de selección por ambiente (p. ej. `FLASK_ENV`). v0.12 resuelve **puntualmente** el caso de mayor riesgo (`JWT_SECRET_KEY`) con una variable de opt-in explícita, sin adoptar una arquitectura de configuración por ambiente completa — esa decisión más amplia sigue `PENDIENTE DE APROBACIÓN` (sección 20).

`CLAUDE.md` §14 ya confirmaba este hueco como "solo la regla de no subir `.env`, sin lista oficial" — sigue sin haber una lista oficial completa más allá de las tres variables ya documentadas, ni una política de configuración por ambiente ratificada.

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

- **Patrón actualmente observado:** `register`/`login` están en el blueprint `auth_bp` (`interfaces/routes/auth_routes.py`); `GET /api/users/me` (v0.7) y `PATCH /api/users/me` (nuevo, v0.9, `ADR-003`) comparten un blueprint separado, `users_bp` (`interfaces/routes/user_routes.py`) — ambos blueprints montados con prefijo `/api` desde `create_app()`. La separación se hizo porque `/me` no es un endpoint de autenticación en sí (no emite ni valida credenciales, es el primer endpoint protegido) — es el primer caso real de "más de un blueprint", y sugiere organizar por recurso/dominio (`auth` vs `users`), no todo bajo un único blueprint. `PATCH /users/me` confirma el patrón: mismo blueprint que el `GET` del mismo recurso, whitelist explícita de campos extraídos uno por uno con `data.get(...)` (nunca `**data`), reutilizando `domain/auth/validators.py` sin reglas de formato nuevas.
- **Organización futura:** con dos blueprints ya observados (`auth_bp`, `users_bp`), convertir "un blueprint por dominio funcional" en regla general para futuros endpoints sigue `PENDIENTE DE APROBACIÓN` formal, aunque el patrón de facto ya apunta en esa dirección.
- Los métodos HTTP se declaran explícitamente por ruta (`methods=["POST"]`), no hay convención documentada todavía sobre verbos para operaciones futuras (GET de colección, PUT/PATCH de actualización, DELETE).
- Los cuerpos de petición y respuesta son JSON (`request.get_json()` / `jsonify(...)`), sin excepción observada.
- No existe especificación formal de API (OpenAPI/Swagger) en `/docs` — `CLAUDE.md` §9 y §14 ya lo confirman. `HB-001` §15.1 exige documentar cada endpoint nuevo el mismo día del PR — esa documentación de endpoints, cuando exista, es un artefacto distinto de este documento de arquitectura.

---

## 15. Testing

- **Estructura — v0.12:** `backend/tests/` (`conftest.py`, `test_auth.py`, `test_users_me.py`, `test_update_profile.py`, `test_username_policy.py`, `test_error_handlers.py` y `test_config_jwt_secret.py` — este último nuevo, v0.12). **63 pruebas** (59 de v0.11 + 4 nuevas de v0.12, `test_config_jwt_secret.py` — corren `Config` en subprocesos aislados con `subprocess.run`, porque el cuerpo de la clase solo se evalúa una vez por proceso: sin `JWT_SECRET_KEY` ni opt-in falla al importar; con el opt-in usa el fallback; el opt-in con un valor distinto de `"1"` sigue fallando; un `JWT_SECRET_KEY` real nunca necesita el opt-in). Suite completa **ejecutada y verificada en esta auditoría** (63/63 passed). (52 de v0.9 + 4 nuevas de v0.10) para `POST /api/register`, `POST /api/login`, `GET /api/users/me`, `PATCH /api/users/me` y el manejador global de errores, corridas contra PostgreSQL 16 real en Docker (base `thers_test`, separada de `thers_dev`), no contra mocks — **ejecutadas y verificadas en esta auditoría** (`pytest -v`, 56 passed, 0 failed, 0 skipped, 0 warnings). `test_error_handlers.py` (v0.10) cubre: `404` en una URL sin ruta, `405` en un verbo no permitido, `400` ante un body no-JSON (hallazgo real: `request.get_json()` sin `silent=True` en `auth_routes.py`), y `500` ante una excepción forzada con `monkeypatch` sobre `SQLAlchemyUserRepository.find_by_id` en un flujo real (`GET /api/users/me` con JWT válido, sin agregar ninguna ruta insegura solo para el test) — verificando que la respuesta nunca exponga traceback, el tipo/mensaje real de la excepción, ni datos sensibles. `test_auth.py` cubre además (v0.7): duplicidad de `username`, validación de formato de `username`/`phone`/`country_code`/`birth_date`, edad mínima, y `confirm_password` no coincidente. `test_users_me.py` cubre: token válido (200), sin token (401), token inválido (401), token expirado (401), usuario inexistente (404), forma de la respuesta pública, y no exposición de campos sensibles. `test_update_profile.py` (v0.9) cubre: actualización parcial de cada campo editable, whitelist (campos no reconocidos ignorados), `phone`/`country_code` como par atómico, `404`/`409`/cooldown de `username` (`400`), body vacío (`400`), sin token (`401`), no exposición de campos sensibles. `test_username_policy.py` (v0.9) cubre `can_change_username()` de forma puramente unitaria (sin base de datos): `None` permite el cambio, dentro/fuera de la ventana de 30 días.
- **Framework — elegido pragmáticamente en esta tarea, sin ratificación formal:** `pytest==8.3.4`, en `backend/requirements-dev.txt` (separado de `requirements.txt`, que sigue listando solo dependencias de producción). **`PENDIENTE DE APROBACIÓN`** (sección 20): esta elección resuelve la necesidad inmediata de probar `register`/`login`, pero el Comité Técnico no la ratificó formalmente como el framework oficial del proyecto — es el estándar de facto para Flask, no una decisión inventada, pero tampoco un ADR.
- **Unit tests / Integration tests / API tests:** la mayoría de las 63 pruebas son de integración (HTTP + base de datos real vía `Flask.test_client()`). Ya existen pruebas unitarias puras, sin base de datos: `test_username_policy.py` (`domain/auth/username_policy.py`) y `test_config_jwt_secret.py` (`config.py`, en subprocesos aislados — ver arriba). `hash_password`/`verify_password` siguen sin prueba unitaria dedicada (serían triviales, envoltorios directos de `werkzeug.security`). Ampliar la estrategia de forma más sistemática a otras capas/flujos sigue `PENDIENTE DE APROBACIÓN`.

---

## 16. Seguridad

Estado actual observado, sin proponer remediaciones (fuera de alcance de esta tarea):

| Área | Estado |
|---|---|
| Secretos | **v0.12 — reforzado.** `JWT_SECRET_KEY` se lee de `os.environ`, `backend/.env.example`/`backend/.gitignore` protegen un futuro `.env` real, y la app ya **no arranca** si la variable falta salvo opt-in explícito de desarrollo local (`ALLOW_INSECURE_JWT_DEV_FALLBACK=1`, ver sección 12) — antes de v0.12, faltarla en un entorno desplegado dejaba el backend firmando JWTs con una clave pública. Sigue sin existir gestión de secretos con vault/rotación para el entorno desplegado real — `PENDIENTE` (sección 20); y sigue pendiente confirmar operativamente que Render tiene los valores reales configurados (no verificable desde este documento). |
| JWT | Emitido con `flask_jwt_extended` sobre una clave ahora externalizable por entorno; sin política de expiración explícita configurada (aplica el default de la librería, no una decisión ratificada); **dos endpoints protegidos reales desde v0.7/v0.9** (`GET`/`PATCH /api/users/me`, `@jwt_required()`); sin refresh tokens ni logout/blacklist (un token robado sigue válido hasta su expiración natural). |
| Validación | **v0.11 — resuelto para `register`.** Presencia de campos + formato de `email` + longitud mínima de `password` (8 caracteres) — ambos placeholders de producto explícitos, revisables (`API_CONTRACT.md` §9, ítem 2). Sigue sin sanitización de HTML/inyección (no hay todavía ningún campo de texto libre expuesto a otros usuarios — `bio` sigue sin ratificar, `DATABASE_ARCHITECTURE.md` §4.B). |
| Autorización | No existe ningún concepto de roles/permisos en el código. |
| Exposición de errores | **v0.10 — resuelto.** Los mensajes de error (`{"msg": "..."}`) nunca exponen detalles internos (stack traces, nombres de excepciones, `DATABASE_URL`, `JWT_SECRET_KEY`) en ningún endpoint — verificado por prueba (`test_error_handlers.py`). Un error inesperado (`500`) ya no cae en el comportamiento HTML por defecto de Flask: `app/interfaces/error_handlers.py` lo intercepta antes de que el modo `debug` de `run.py` (sigue activo, ver sección 12) tenga oportunidad de mostrarlo — el registro del detalle real ocurre solo en el log del servidor (`app.logger.exception`). |
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
│   │   ├── error_handlers.py         # IMPLEMENTADO — v0.10 (register_error_handlers, ver sección 11)
│   │   └── routes/
│   │       ├── __init__.py          # (corregido — ver hallazgo sección 3)
│   │       ├── auth_routes.py        # register + login, composition root (ver sección 17)
│   │       └── user_routes.py        # IMPLEMENTADO — v0.7/v0.9: GET/PATCH /api/users/me, blueprint users_bp
│   ├── application/
│   │   └── auth/
│   │       ├── __init__.py
│   │       ├── login_use_case.py
│   │       ├── register_use_case.py  # IMPLEMENTADO — v0.7 (firma ampliada, ADR-002)
│   │       ├── get_current_user_use_case.py  # IMPLEMENTADO — v0.7
│   │       ├── update_profile_use_case.py    # IMPLEMENTADO — v0.9 (ADR-003)
│   │       ├── user_presenter.py     # IMPLEMENTADO — v0.7 (to_public_user, compartido)
│   │       └── dtos.py               # PROPUESTA — no existe hoy
│   ├── domain/
│   │   └── auth/
│   │       ├── __init__.py
│   │       ├── auth_service.py       # hash_password / verify_password — v0.6
│   │       ├── exceptions.py         # IMPLEMENTADO — v0.9 (+ UsernameChangeNotAllowedError)
│   │       ├── repositories.py       # IMPLEMENTADO — v0.9 (puerto UserRepository, + update())
│   │       ├── validators.py         # IMPLEMENTADO — v0.7 (ADR-002)
│   │       ├── username_policy.py    # IMPLEMENTADO — v0.9 (can_change_username, ADR-003)
│   │       └── entities.py           # PROPUESTA — no existe hoy
│   ├── infrastructure/
│   │   └── persistence/
│   │       ├── __init__.py
│   │       ├── models.py             # IMPLEMENTADO — v0.9 (+ username_changed_at, ADR-003)
│   │       └── repositories/
│   │           ├── __init__.py       # IMPLEMENTADO — v0.6
│   │           └── user_repository.py  # IMPLEMENTADO — v0.9 (SQLAlchemyUserRepository, + update())
│   ├── config.py
│   ├── extensions.py                  # v0.7: + callbacks de error JWT (ver sección 9)
│   └── __init__.py
├── tests/                             # IMPLEMENTADO — v0.9 (ver sección 15)
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_users_me.py               # IMPLEMENTADO — v0.7
│   ├── test_update_profile.py         # IMPLEMENTADO — v0.9
│   ├── test_username_policy.py        # IMPLEMENTADO — v0.9
│   ├── test_error_handlers.py         # IMPLEMENTADO — v0.10
│   └── test_config_jwt_secret.py      # IMPLEMENTADO — v0.12
├── migrations/                        # IMPLEMENTADO — v0.9 (ver sección 8, 3 migraciones)
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
- **v0.6 — integración de autenticación con persistencia real:** `POST /api/register` y `POST /api/login` operan contra `users` real, no contra una credencial hardcodeada. Patrón Repository implementado: puerto `UserRepository` en `domain/auth/repositories.py`, adaptador `SQLAlchemyUserRepository` en `infrastructure/persistence/repositories/user_repository.py`, inyectado desde `interfaces/routes/auth_routes.py` (composition root, ver sección 17). Excepciones de dominio (`EmailAlreadyExistsError` → `409`, `InvalidCredentialsError` → `401`, mismo mensaje para "no existe" y "password incorrecta"). `identity` del JWT cambiado de `email` a `user.id` (UUID). `id` sigue generándose exclusivamente en PostgreSQL (`gen_random_uuid()`) — ningún `uuid.uuid4()` en el código Python. Documentado el mismo día en `API_CONTRACT.md` §4.1 (`HB-001` §15.1).
- **v0.7 — perfil completo de registro + primer endpoint protegido (THERS Backend Fase 2.1, `ADR-002-user-profile-fields.md`):** `users` gana `username`/`phone`/`country_code`/`birth_date` (migración `a1edcbff74d8`, verificada `flask db upgrade`/`downgrade` contra PostgreSQL 16 real, `thers_dev`). `POST /api/register` valida y persiste los campos nuevos (`domain/auth/validators.py`); `confirm_password` se valida y nunca se persiste. `GET /api/users/me` (nuevo, `@jwt_required()`, `get_jwt_identity()`) es el primer endpoint protegido del backend — identidad exclusivamente del JWT, nunca de query/body/headers. Errores JWT (ausente/inválido/expirado) homogenizados a `401` (`app/extensions.py`). `application/auth/user_presenter.py` centraliza la forma pública del `user`. 27 pruebas de integración (13 + 14 nuevas, `backend/tests/`) contra PostgreSQL 16 real. Flujo completo verificado manualmente (`curl`): register → login → `GET /api/users/me` con fila real en `thers_dev`. Documentado el mismo día en `API_CONTRACT.md` §4.1/§4.2 (`HB-001` §15.1).
- **v0.12 — primer despliegue real (Render) documentado + fail-fast de `JWT_SECRET_KEY`:** `gunicorn` en `requirements.txt`; `run.py` sirve en `0.0.0.0`/`$PORT`/`debug=False`; `config.py` normaliza `DATABASE_URL` para el formato de Render y ya no arranca con un `JWT_SECRET_KEY` inseguro por defecto — requiere `ALLOW_INSECURE_JWT_DEV_FALLBACK=1` explícito, solo para desarrollo local. 4 pruebas nuevas en subprocesos aislados (`test_config_jwt_secret.py`); suite completa 63/63, **ejecutada y verificada en esta auditoría**. Documentado el mismo día en este documento — el despliegue en sí (commits `ce5cc9f`/`ce71e19`) no se había documentado hasta ahora.
- **v0.10 — manejador global de errores:** `app/interfaces/error_handlers.py` (`register_error_handlers(app)`) traduce `404`/`405`/cualquier otro `HTTPException`/`Exception` genérica al formato `{"msg": "..."}` ya usado por el resto de la API, sin introducir un formato nuevo. No interfiere con los callbacks de `flask_jwt_extended` ni con los `4xx` que cada route ya construye a mano. 4 pruebas nuevas (`test_error_handlers.py`); suite completa 56/56, **ejecutada y verificada en esta auditoría**. Documentado el mismo día en `API_CONTRACT.md` §3/§9 (`HB-001` §15.1).
- **v0.9 — actualización de perfil, primer endpoint de escritura protegido (THERS Backend, `ADR-003-profile-update-contract.md`):** `PATCH /api/users/me` (`interfaces/routes/user_routes.py`, mismo blueprint `users_bp` que `GET /me`) permite actualizar parcialmente `name`/`username`/`phone`+`country_code`/`birth_date` — `email`/`password` quedan fuera por decisión explícita del ADR. Whitelist explícita en la route (sin `**data`, sin mass assignment). `users` gana `username_changed_at` (migración `b2f4a19c3d7e`, nullable, sin backfill) para sostener un cooldown de 30 días entre cambios de `username` (`domain/auth/username_policy.py`); un `username` igual al actual no consume ese cooldown (`application/auth/update_profile_use_case.py`). `domain/auth/repositories.py` gana el puerto `update()`; `SQLAlchemyUserRepository.update()` replica el patrón de traducción de `IntegrityError` → `UsernameAlreadyExistsError` (`409`) ya usado en `create()`. Reutiliza `domain/auth/validators.py` y `to_public_user()` sin reglas nuevas — la respuesta coincide con `GET /api/users/me`/`register`/`login`. 25 pruebas nuevas (20 de integración + 5 unitarias puras de la política de cooldown); suite completa 52/52, **ejecutada y verificada en esta auditoría** contra PostgreSQL 16 real. Documentado el mismo día en `API_CONTRACT.md` §4.2 v0.5 y `DATABASE_ARCHITECTURE.md` §5 v0.6 (`HB-001` §15.1) — este documento (`BACKEND_ARCHITECTURE.md`) fue el que quedó sin actualizar hasta esta auditoría (ver nota de v0.9 al inicio).

### PENDIENTE
- **Conexión a una base PostgreSQL compartida por el equipo o de producción** — el modelo y la migración ya se verificaron end-to-end contra PostgreSQL 16 real en Docker (desarrollo local reproducible, `docker-compose.yml`), pero no existe todavía ninguna base compartida por el equipo ni de producción.
- **Ratificación formal por el Comité Técnico** de las decisiones ya codificadas en v0.4/v0.5/v0.6 (SQLAlchemy, UUID, CITEXT, Flask-Migrate, patrón Repository con puerto en `domain/`, pytest como framework de testing) — ver nota de gobernanza, sección 2.
- Estrategia de hashing **definitiva** para `users` (la v0.6 reutiliza `werkzeug.security`/scrypt ya usado para la credencial de prueba, no ratifica un algoritmo distinto — sección 20).
- ~~Endpoints protegidos con `@jwt_required()`~~ — **resuelto en v0.7/v0.9** (`GET /api/users/me`, `PATCH /api/users/me`, ver sección 9). Dos casos reales, ambos sobre el mismo blueprint (`users_bp`); el patrón (`get_jwt_identity()` sobre el UUID, blueprint por recurso) queda sentado pero no "ratificado" como norma para docenas de endpoints futuros.
- Política de expiración/refresh de JWT.
- Roles y autorización.
- Validación declarativa (schemas/DTOs, p. ej. Marshmallow/Pydantic) — sigue sin adoptarse, las funciones puras de `domain/auth/validators.py` bastan para el alcance actual. ~~Validaciones adicionales de `register` (longitud mínima de contraseña, formato de email)~~ — **resuelto en v0.11** (ver sección 9, 10, 16).
- ~~Manejo global de errores (`@app.errorhandler`)~~ — **resuelto en v0.10** (`app/interfaces/error_handlers.py`, ver sección 11). El formato `{"msg": "..."}` ya es uniforme para toda la API; sigue sin decidirse si evolucionar a una estructura con código machine-readable (nadie lo necesita hoy).
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
5. **Formato estándar de respuesta de error** para toda la API — **avanzado en v0.10**: `{"msg": "..."}` ya se aplica de forma uniforme (incluidos los casos antes no cubiertos: `404`/`405`/`500`, ver sección 11). Sigue sin decidirse si evolucionar hacia un código de error machine-readable — no hay necesidad actual que lo justifique.
6. ~~Manejador global de excepciones (`@app.errorhandler`)~~ — **resuelto en v0.10** (`app/interfaces/error_handlers.py`, ver sección 11 y 19). Sigue sin ratificar formalmente una taxonomía de excepciones de dominio/aplicación más allá de las ya existentes en `domain/auth/exceptions.py` — no se justificó como necesaria para el alcance actual (solo `auth`).
7. **Configuración por ambiente** (Development/Production/Testing) y lista oficial de variables de entorno requeridas.
8. **Gestión de secretos en un entorno desplegado** (vault, variables de CI/CD, rotación) — el mecanismo local ya se resolvió (`JWT_SECRET_KEY` vía `os.environ` + `.env.example` + `.gitignore`, sección 12, 16, 19); **v0.12** además cerró el caso de mayor riesgo (arranque inseguro por defecto — ver sección 12, 16, 19). La estrategia completa de secretos para producción/CI (vault, rotación) sigue sin definir.
9. **Política de expiración y refresh de tokens JWT.**
10. **Modelo de roles y autorización.**
11. **Política de CORS por ambiente** (orígenes permitidos en producción vs. desarrollo).
12. **Framework y estrategia de testing** (unit/integration/API) — **`pytest` elegido pragmáticamente en v0.6** (27 pruebas de integración a partir de v0.7 — auth + `GET /api/users/me`, sección 15), sin ratificación formal por el Comité Técnico todavía. Ampliar a otras capas/flujos sigue sin definir.
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
- `docs/architecture/ADR-002-user-profile-fields.md` — ratifica las columnas de perfil y `GET /api/users/me` (v0.7).
- Código fuente completo de `backend/`: `app.py`, `run.py`, `app/__init__.py`, `app/config.py`, `app/extensions.py`, `app/application/auth/*.py`, `app/domain/auth/*.py`, `app/interfaces/routes/*.py`, `app/infrastructure/persistence/**`, `backend/tests/*.py`, y todos los archivos `_init_.py`.
- `backend/venv` (entorno local) — `pyvenv.cfg` (versión de Python) y `pip freeze` (versiones de paquetes instalados), usados únicamente como observación de estado, no como fuente de decisión.
- `git ls-files backend` — confirma qué archivos del backend están versionados.

Documentos oficiales **no consultados por no ser procesables en este entorno** (ya señalados como hueco en `CLAUDE.md` §14): `Manual_Operativo/THERS_Manual_Operativo_v1.0.docx`/`.pdf`, `Plan_Estrategico/Plan_Estrategico_IA_THERS.docx`/`.pdf`. Si contienen decisiones de arquitectura backend, este documento no puede confirmarlo ni descartarlo.
