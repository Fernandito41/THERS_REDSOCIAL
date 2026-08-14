# AUDITORÍA TÉCNICA READ-ONLY — Backend THERS

**Contrato de referencia:** `docs/architecture/BACKEND_ARCHITECTURE.md`
**Alcance:** `backend/` (código real). Ningún archivo fue modificado, creado ni ejecutado.

---

## Resumen ejecutivo

El backend implementa un único flujo end-to-end (`POST /api/login`) que atraviesa correctamente las tres capas propuestas (interfaces → application → domain), respetando la regla de dependencia (dominio sin imports de framework). Fuera de ese flujo, la arquitectura documentada es en gran parte aspiracional: no hay persistencia, no hay PostgreSQL, no hay usuarios reales, no hay autorización, no hay validación declarativa, no hay manejo de errores global, no hay testing, y no hay archivo de dependencias. El mayor riesgo no es la ausencia de estas piezas (esperable en etapa temprana), sino dos hechos concretos: un secreto JWT hardcodeado y versionado en git, y una segunda aplicación Flask huérfana (`app.py`) sin relación con la arquitectura documentada. El backend está, en esencia, en fase de scaffold funcional, no de producto.

---

## Tabla de estado del Backend

| # | Componente | Estado |
|---|---|---|
| 4 | Flask App Factory (`create_app()`) | IMPLEMENTADO |
| 5 | `config.py` | PARCIAL |
| 6 | `extensions.py` | PARCIAL |
| 7 | Blueprints / routes | PARCIAL |
| 8 | Application / use cases | PARCIAL |
| 9 | Domain | PARCIAL |
| 10 | Repositories / persistence | FALTANTE |
| 11 | PostgreSQL / config de BD | FALTANTE |
| 12 | Autenticación | PARCIAL |
| 13 | JWT | PARCIAL |
| 14 | Autorización | FALTANTE |
| 15 | Validaciones | PARCIAL |
| 16 | Manejo de errores | PARCIAL |
| 17 | CORS | IMPLEMENTADO (sin política por ambiente) |
| 18 | Testing | FALTANTE |
| — | `app.py` (raíz de `backend/`) | CONTRADICTORIO |
| — | Nombrado de paquetes (`__init__.py`) | CONTRADICTORIO |
| — | Flask-SQLAlchemy / SQLAlchemy (venv) | PREPARADO |
| — | `requirements.txt` / `pyproject.toml` | FALTANTE |

---

## 1–3. Implementado / Parcial / Faltante — detalle por punto

### 1. Implementado

- Application factory (`create_app()`) con registro de `Config`, `CORS`, `JWTManager` y `auth_bp`.
- Flujo `interfaces/routes` → `application` → `domain` para login, con dirección de dependencia correcta.
- Emisión de JWT (`create_access_token`) tras validación exitosa.
- CORS habilitado globalmente.

### 2. Parcial

- **`config.py`**: existe y se carga correctamente, pero solo define `JWT_SECRET_KEY` (hardcodeado); no hay config por ambiente ni variables de entorno.
- **`extensions.py`**: patrón correcto (instancia desacoplada + `init_app`), pero solo contiene `jwt`; no hay `db`, `migrate`, ni otras extensiones.
- **Blueprints/routes**: un blueprint, un endpoint, patrón replicable pero sin ejemplo de endpoint protegido.
- **Application/use cases**: un único caso de uso (`login_user`), correctamente desacoplado de Flask, pero retorna datos parcialmente hardcodeados (`"name": "Fernando"`).
- **Domain**: `auth_service.py` es puro (sin dependencias de framework — cumple la regla de capas), pero no tiene entidades, solo una función de comparación fija.
- **Autenticación**: el mecanismo (JWT vía `flask_jwt_extended`) funciona, pero no valida contra usuarios reales.
- **JWT**: se emite correctamente, pero sin política de expiración explícita, sin refresh, y sin ningún endpoint que lo exija (`@jwt_required()` no aparece en el código).
- **Validaciones**: hay validación manual de presencia de campos en el único endpoint; no hay validación de formato ni librería declarativa.
- **Manejo de errores**: hay manejo ad-hoc por endpoint (400/401 con JSON); no hay manejador global (`@app.errorhandler`) ni formato de error unificado.

### 3. Faltante

- Repositories/persistence: ningún módulo de acceso a datos.
- PostgreSQL: sin driver (`psycopg2`/`psycopg`), sin cadena de conexión, sin modelos, sin `SQLALCHEMY_DATABASE_URI`.
- Autorización: sin roles, permisos ni scopes.
- Testing: sin carpeta `tests/`, sin framework instalado (no hay `pytest` en el venv), sin ninguna prueba.
- `requirements.txt`/`pyproject.toml`: no existen en el repo.
- Registro de usuario (`/register`), logout, refresh token.

---

## 4–18. Estado por componente específico

| # | Componente | Estado | Evidencia |
|---|---|---|---|
| 4 | App Factory | IMPLEMENTADO | `app/__init__.py`: crea `Flask(__name__)`, carga `Config`, activa `CORS`, `jwt.init_app(app)`, registra `auth_bp` bajo `/api`. Coincide con lo descrito en el contrato §3. |
| 5 | `config.py` | PARCIAL | Solo `JWT_SECRET_KEY = "super-secret-key"` como literal. Sin `os.environ`, sin clases por ambiente, sin `.env`. Coincide con contrato §12 (ya marcado allí como hueco). |
| 6 | `extensions.py` | PARCIAL | Solo `jwt = JWTManager()`. Sin `db`, sin `migrate`, sin ninguna otra extensión — pese a que Flask-SQLAlchemy está instalada en el venv. |
| 7 | Blueprints/routes | PARCIAL | Un blueprint (`auth_bp`), un endpoint (`POST /api/login`). Manejo de request/response correcto para ese único caso; patrón no probado aún con más de un endpoint. |
| 8 | Application/use cases | PARCIAL | `login_use_case.py`: orquesta correctamente `domain.validate_user`, pero el dict de usuario que retorna tiene `"name": "Fernando"` hardcodeado — no proviene de ningún dato real. Sin DTOs/schemas. |
| 9 | Domain | PARCIAL | `auth_service.py`: función pura, sin dependencias de framework (cumple regla de capas del contrato §7/§17). Sin entidades, sin reglas de negocio reales más allá de la comparación fija. |
| 10 | Repositories/persistence | FALTANTE | No existe ningún archivo ni carpeta relacionada en `backend/app/`. |
| 11 | PostgreSQL/config BD | FALTANTE | Sin driver, sin URI, sin modelos. Flask-SQLAlchemy/SQLAlchemy están en el venv pero sin ninguna instancia ni import en el código (ver PREPARADO más abajo). |
| 12 | Autenticación | PARCIAL | Login funcional, pero contra credenciales hardcodeadas (`test@test.com`/`123456`), sin hashing, sin backing store. |
| 13 | JWT | PARCIAL | `flask_jwt_extended` correctamente inicializado y usado para emitir tokens; sin configuración de expiración/refresh explícita; ningún endpoint lo exige todavía. |
| 14 | Autorización | FALTANTE | Ningún concepto de rol/permiso en el código. |
| 15 | Validaciones | PARCIAL | Validación manual de presencia (`if not data`, `if not email or not password`); sin validación de formato ni librería declarativa (Marshmallow/Pydantic no instaladas). |
| 16 | Manejo de errores | PARCIAL | Manejo local por endpoint (400/401); sin `@app.errorhandler` global; un 500 no controlado caería en el comportamiento por defecto de Flask (agravado por `debug=True` en `run.py`, ver Riesgos). |
| 17 | CORS | IMPLEMENTADO | `CORS(app)` activo sin restricciones; funcional pero sin política diferenciada por ambiente (ver Riesgos). |
| 18 | Testing | FALTANTE | Sin carpeta `tests/`, sin `pytest` (ni ningún framework) en el venv, sin configuración de testing en ningún archivo. |

---

## 19. Dependencias instaladas y su propósito

Observado en `backend/venv` vía `pip freeze` (snapshot local, no fijado en ningún `requirements.txt`/`pyproject.toml` — no existe ninguno en el repo):

| Paquete | Versión | Propósito | ¿En uso en el código? |
|---|---|---|---|
| Flask | 3.1.3 | Framework web | Sí |
| flask-cors | 6.0.2 | Middleware CORS | Sí (`create_app()`) |
| Flask-JWT-Extended | 4.7.1 | Emisión/gestión de JWT | Sí (`extensions.py`, `auth_routes.py`) |
| PyJWT | 2.12.1 | Dependencia transitiva de Flask-JWT-Extended | Indirecto |
| Flask-SQLAlchemy | 3.1.1 | ORM (integración Flask) | No — ningún import en el código |
| SQLAlchemy | 2.0.49 | ORM core | No — ningún import en el código |

No se encontró driver de PostgreSQL (`psycopg2`/`psycopg`) en el entorno. No hay `pytest`, `marshmallow`, `pydantic`, `python-dotenv`, `bcrypt`, ni `werkzeug.security` en uso explícito para hashing.

---

## Archivos relevantes encontrados

```
backend/
├── app.py                                  ⚠️ huérfano — ver Contradicciones
├── run.py                                  entry point real
├── app/
│   ├── __init__.py                         app factory
│   ├── config.py
│   ├── extensions.py
│   ├── application/
│   │   ├── __init__.py                     ⚠️ mal nombrado
│   │   └── auth/
│   │       ├── __init__.py                 ⚠️ mal nombrado
│   │       └── login_use_case.py
│   ├── domain/
│   │   ├── __init__.py                     ⚠️ mal nombrado
│   │   └── auth/
│   │       ├── __init__.py                 ⚠️ mal nombrado
│   │       └── auth_service.py
│   └── interfaces/
│       └── routes/
│           ├── __init__.py                 ⚠️ mal nombrado
│           └── auth_routes.py
└── venv/                                    entorno local, versionado en git (ver Riesgos)
```

No hay `requirements.txt`, `pyproject.toml`, `.env`, `.env.example`, ni carpeta `tests/`.

---

## Problemas encontrados

1. Comparación de credenciales en texto plano en `domain/auth/auth_service.py` (sin hashing).
2. Dato de usuario parcialmente hardcodeado (`"name": "Fernando"`) en `login_use_case.py`, independiente del email recibido.
3. Sin manejador global de errores — cualquier excepción no capturada expone el comportamiento por defecto de Flask.
4. Sin ningún endpoint protegido — no hay evidencia en código de que `@jwt_required()` funcione en este proyecto todavía (nunca se usa).
5. Ausencia total de capa de persistencia pese a que PostgreSQL está confirmado como motor elegido en la documentación oficial.

---

## Contradicciones (entre BACKEND_ARCHITECTURE.md y la implementación, o internas al código)

| # | Contradicción | Detalle |
|---|---|---|
| 1 | `backend/app.py` vs. arquitectura por capas | Segunda app Flask independiente (`Flask(__name__)`, ruta `/`) que no pasa por `create_app()` ni por ninguna capa documentada. Ya señalada en el contrato (§2, §20.15) como hallazgo sin resolver. |
| 2 | Nombrado de paquetes | `__init_.py` (guion simple, mal nombrado) en vez de `__init__.py` en `application/`, `application/auth/`, `domain/`, `domain/auth/`, `interfaces/routes/`; `interfaces/` no tiene ninguno. Ya señalado en el contrato (§3, §20.16) como hallazgo de código, no de documentación. |
| 3 | Dependencia fantasma | Flask-SQLAlchemy/SQLAlchemy instaladas pero sin ninguna integración — el contrato ya advierte no leer esto como "persistencia lista" (§2, §19 PREPARADO). Confirmado: sigue sin uso. |
| 4 | README.md raíz vs. /docs/contrato | MySQL (README) vs. PostgreSQL (HB-001, contrato). Ya documentada, no resuelta; no afecta al código porque el código no tiene ninguna base de datos conectada todavía. |

No se encontraron contradicciones nuevas entre el contrato y el código — el contrato ya había registrado correctamente el estado actual al momento de redactarse, y el código no cambió desde entonces.

---

## Riesgos técnicos encontrados

| Riesgo | Severidad | Nota |
|---|---|---|
| `JWT_SECRET_KEY` hardcodeado y versionado en git | Alto (higiene/seguridad) | `config.py`, valor `"super-secret-key"` — sin variable de entorno ni mecanismo de rotación. |
| `debug=True` fijo en `run.py` | Medio | Sin condicionarlo a un ambiente; si se ejecutara así en un despliegue real, expondría el debugger interactivo de Werkzeug. |
| `venv/` versionado en git (`git ls-files backend` lo confirma) | Medio (higiene de repo) | Un entorno virtual completo trackeado infla el repositorio y puede filtrar rutas/versiones locales; no es un riesgo de seguridad de datos, pero sí de higiene. |
| Sin manejador de errores global | Medio | Un 500 no controlado depende del comportamiento por defecto de Flask, agravado por `debug=True`. |
| CORS abierto sin política por ambiente | Bajo–Medio (hoy) | Aceptable en desarrollo temprano, pero no hay ninguna decisión documentada sobre producción. |
| Ausencia de `requirements.txt`/`pyproject.toml` | Medio | Las versiones observadas (sección 19) no son reproducibles ni garantizadas para otro entorno. |
| Doble entry point (`app.py` vs. `run.py`) | Bajo–Medio | Riesgo de confusión operativa (¿cuál se ejecuta en cada contexto?), no de seguridad. |

---

## Próximos pasos recomendados (sin implementar nada)

Estos son puntos a decidir con el equipo — no acciones tomadas ni propuestas de código:

1. Resolver los pendientes de aprobación ya listados en `BACKEND_ARCHITECTURE.md` §20 (persistencia, hashing, DTOs, formato de error, config por ambiente, gestión de secretos, expiración JWT, roles, CORS por ambiente, testing, OpenAPI, `requirements.txt`).
2. Decidir el destino de `backend/app.py` (conservar/eliminar/integrar) — requiere autorización explícita antes de tocarlo.
3. Decidir si se corrige el nombrado `__init_.py` → `__init__.py` — requiere autorización explícita, es un cambio de código aunque sea trivial.
4. Evaluar si `venv/` debería salir del control de versiones (decisión de higiene de repo, no de arquitectura — fuera del alcance de este documento).
5. Priorizar, antes de cualquier otra pieza, la definición del modelo de usuario y la conexión a PostgreSQL, dado que es el bloqueador de facto para autenticación real, autorización y testing de integración.
