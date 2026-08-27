# DATABASE_ARCHITECTURE

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/DATABASE_ARCHITECTURE.md` |
| Identificador propuesto | `DB-001` (sigue el patrón `HB-001`/`ARC-001`/`DS-001`/`WF-001`/`PV-001`/`FAS-001`) — **pendiente de ratificación formal** |
| Versión | 0.5 |
| Estado | **Borrador / Contrato técnico — pendiente de aprobación del equipo** |
| Depende de | `HB-001` (organización, gobernanza, git flow, seguridad), `REPOSITORY_STRUCTURE.md` (ubicación del backend y carpeta futura `database/`) |
| Motivo | El `CLAUDE.md` maestro (§4, §14) identificó que la arquitectura de Base de Datos no estaba formalmente documentada |
| Idioma | Español (documentación oficial), identificadores/código en inglés |

> ⚠️ **Nota de alcance y honestidad de fuentes.** Este documento es un **contrato técnico previo a la implementación**, no una descripción de un esquema ya existente. Al momento de escribirlo (v0.1), el backend **no tenía base de datos, ni ORM, ni driver de PostgreSQL instalado**: la autenticación funcionaba contra credenciales hardcodeadas (ver §4). Todo lo que aquí se define como "decidido" se limita a lo que la documentación oficial ya respalda o a lo que el estado real del código justifica de forma evidente. Todo lo demás está marcado explícitamente como **PENDIENTE DE APROBACIÓN** (§14). No se inventan entidades, columnas, índices ni políticas que el proyecto no necesite hoy.
>
> **v0.3 — cierre de la capa de persistencia (auditoría y validación real de esta tarea).** Se corrigió la referencia a una instalación nativa de PostgreSQL 17.11 (no reproducible por el equipo) por el entorno estandarizado real: **PostgreSQL 16 vía Docker Compose** (`docker-compose.yml`, raíz del repo, imagen `postgres:16-alpine`), verificado end-to-end (`flask db upgrade`/`downgrade` repetidos, INSERT sin `id` confirmando `gen_random_uuid()` en PostgreSQL, UPDATE confirmando el trigger de `updated_at`, unicidad case-insensitive de `email` vía `CITEXT`, y reconstrucción completa desde un volumen Docker vacío). Se marcó como resuelta la herramienta de migraciones (§9) donde el documento aún decía `PENDIENTE`, pese a que Flask-Migrate/Alembic ya estaba implementado. Ningún esquema, entidad ni columna cambió — solo se sincronizó el documento con el código real ya existente.
>
> **v0.4 — integración de autenticación con persistencia real.** `users` pasó de "modelo implementado pero no conectado" a **en uso real**: `POST /api/register` y `POST /api/login` (`BACKEND_ARCHITECTURE.md` §8/§9, v0.6) ya crean/consultan filas reales, y la credencial hardcodeada (`test@test.com`/`123456`) se eliminó del código por completo. Reflejado en §4 y §5. No se agregó ninguna entidad, columna ni índice nuevo — sigue siendo únicamente `users`, sin cambios de esquema.
>
> **v0.5 — columnas de perfil ratificadas por ADR (THERS Backend Fase 2.1).** `username`, `phone`, `country_code` y `birth_date` pasan de **OBJETIVO** (§4.B) a **IMPLEMENTADAS** en `users`, ratificado por `ADR-002-user-profile-fields.md` — el ADR que esta misma sección (v0.2–v0.4) ya pedía antes de tocar el esquema. Migración `a1edcbff74d8_add_profile_fields_to_users.py`, verificada con `flask db upgrade`/`downgrade` contra PostgreSQL 16 real (`thers_dev`, Docker) y con 27 pruebas de integración (`backend/tests/`). `username` es único (`uq_users_username`) pero **no** usa `CITEXT` (a diferencia de `email`) — decisión explícita en `ADR-002` §3, no una omisión. `avatar_url`/`bio` (§4.B) siguen sin ratificar. Reflejado en §4.A, §4.B y §5.

---

## 1. Propósito y alcance

### Propósito
Establecer un contrato técnico claro y verificable para la **futura** implementación de PostgreSQL en THERS, de modo que cuando el equipo de backend implemente la capa de persistencia lo haga sobre decisiones ya acordadas y no improvisadas durante el desarrollo (mismo principio que `FAS-001` §1: "el código sigue a la documentación, no al revés").

### Alcance
Este documento cubre:
- Motor de base de datos y sus principios de diseño.
- El modelo conceptual de THERS en **tres capas explícitas** (nuevo en v0.2):
  1. **Estado actual implementado** — lo que el código de hoy justifica y ratifica (§4.A).
  2. **Arquitectura objetivo del producto** — el alcance funcional confirmado por el equipo, traducido a *estructuras candidatas de persistencia* **sin decidir todavía su modelado** (§4.B).
  3. **Decisiones de persistencia pendientes** — lo que falta ratificar antes de implementar (§4.C y §14).
- Convenciones de nombres, índices, migraciones, seeds, integridad, seguridad y backups.
- La integración con las capas ya observadas del backend.

> 🔑 **Distinción central (mantener siempre).** Un **requisito funcional** confirmado ("el producto tendrá mensajería") **no es** una **decisión de persistencia** ("mensajería se modela con las tablas X, Y con estas PK/FK y estos tipos"). La capa objetivo (§4.B) registra requisitos confirmados como *candidatos*; solo la ratificación por ADR (`HB-001` §11–12) los convierte en modelo implementable. Este documento **no** cruza esa línea por iniciativa propia.

### Fuera de alcance (explícito)
- **No** define el esquema concreto (tablas, columnas, PK/FK, tipos SQL) de las entidades objetivo de la red social: la capa objetivo (§4.B) solo las lista como **candidatas**, sin decidir su modelado.
- **No** implementa nada: no crea tablas, migraciones, seeds ni instala dependencias (regla de la tarea que originó este documento).
- **No** define DevOps de base de datos (aprovisionamiento del servidor, réplicas, alta disponibilidad): territorio no especificado según `CLAUDE.md` §14.

---

## 2. Motor de base de datos

| Aspecto | Valor | Fuente |
|---|---|---|
| Motor | **PostgreSQL** | `HB-001` (portada del stack) y `REPOSITORY_STRUCTURE.md` §4 |
| Versión | **PostgreSQL 16** (imagen `postgres:16-alpine`) — entorno de desarrollo local estandarizado vía Docker Compose (`docker-compose.yml`, raíz del repo), reproducible para los 4 integrantes. Reemplaza la nota de v0.2 sobre una instalación nativa de PostgreSQL 17.11 verificada solo en una máquina — esa instancia no era reproducible por el equipo y ya no es la referencia. Versión oficial para un entorno compartido/producción sigue sin ratificación formal (DevOps, `CLAUDE.md` §5) | `docker-compose.yml`; verificado end-to-end en esta tarea (migración, UUID, CITEXT, trigger, downgrade/upgrade, reconstrucción desde volumen vacío) |
| Driver / adaptador Python | **`psycopg` (v3), `psycopg[binary]==3.3.4`** — agregado a `backend/requirements.txt` junto con `Flask-SQLAlchemy` y `Flask-Migrate` | Implementado en código (`BACKEND_ARCHITECTURE.md` §2). **Ratificación formal por el Comité Técnico pendiente de confirmar** (`HB-001` §11.1) — decisión indicada directamente por el Tech Lead Backend, no consensuada por los 4 integrantes en esta tarea |

> ⚠️ **Hallazgo de entorno local (no un cambio de arquitectura, una nota operativa).** En al menos una máquina del equipo, un servicio nativo de PostgreSQL instalado en Windows ya ocupa el puerto `5432` del host, en conflicto con el mapeo de puertos de `docker-compose.yml`. `docker compose ps`/`healthcheck` reportan el contenedor como saludable igualmente (el healthcheck corre *dentro* del contenedor, no prueba el puerto del host), pero cualquier cliente conectando a `localhost:5432` desde el host puede terminar hablando con el Postgres nativo en vez del de Docker, con errores de autenticación confusos. `docker-compose.yml` ya soporta este caso sin modificarse: `ports: "${POSTGRES_PORT:-5432}:5432"` permite fijar `POSTGRES_PORT` (p. ej. `5433`) para evitar el choque, ajustando `DATABASE_URL`/`TEST_DATABASE_URL` al mismo puerto. Ver el informe de la tarea que agregó esta nota para el procedimiento exacto.

### Razones técnicas
La elección de PostgreSQL **ya está tomada** a nivel de organización (`HB-001` la fija como parte del stack y asigna al Tech Lead Backend "Administrar el esquema de base de datos (PostgreSQL) y migraciones"). Este documento **no re-justifica** esa decisión ni añade razones que la documentación no haya declarado; se limita a heredarla.

> ⚠️ **Contradicción detectada — no resuelta aquí.** El `README.md` raíz describe **MySQL** como base de datos, en conflicto directo con PostgreSQL (`HB-001`, `REPOSITORY_STRUCTURE.md`). Por la jerarquía de fuentes (`CLAUDE.md` §3, §14), gana `/docs`: el motor es **PostgreSQL**. La corrección del `README.md` queda fuera del alcance de este documento y debe hacerse en una tarea propia.

---

## 3. Principios de diseño

Estos principios son la guía de decisión para cualquier tabla, columna o índice futuro. Se enuncian junto al problema que resuelven (mismo estilo que `FAS-001` §2) para que no queden como enunciados decorativos.

- **Normalización.** Objetivo de referencia: **3FN** para datos transaccionales, evitando duplicación y anomalías de actualización. La desnormalización puntual (por rendimiento) es una decisión de impacto medio y debe registrarse como ADR (`HB-001` §11–12), no aplicarse por criterio individual.
- **Integridad referencial.** Toda relación entre tablas se expresa con claves foráneas (`FOREIGN KEY`) reales a nivel de motor, no solo por convención de la aplicación. La política de borrado (`ON DELETE`) se decide por relación y se documenta en la definición de cada entidad.
- **Consistencia.** Las reglas de negocio expresables como restricciones de datos (unicidad, no nulos, rangos, enums) viven en el esquema, no solo en la capa de aplicación, para que la base de datos sea la última línea de defensa de la integridad.
- **Seguridad.** Ningún secreto ni credencial vive en el repositorio (`HB-001` §19.1, §20). Los datos sensibles (p. ej. contraseñas) nunca se almacenan en claro (ver §11). El acceso a la base se hace con credenciales provistas por entorno, no hardcodeadas.
- **Escalabilidad.** El esquema se diseña para admitir nuevas entidades (nuevos dominios funcionales de la red social) **agregando** tablas, sin reorganizar las existentes — el mismo principio de crecimiento por adición que `REPOSITORY_STRUCTURE.md` §2 aplica a las `features/` del Frontend.
- **Rendimiento.** Los índices se crean **solo** para consultas reales y justificadas (ver §8). No se crean índices especulativos: cada índice tiene un costo de escritura y almacenamiento y debe pagar su costo con una consulta concreta.

---

## 4. Modelo conceptual: estado actual, objetivo y pendientes

Esta sección separa deliberadamente **tres capas** para no confundir lo implementado con lo deseado ni con lo decidido.

### Método
Se distingue entre:
- **Evidencia de código** → justifica la capa **4.A** (estado actual).
- **Alcance funcional confirmado por el equipo** → define la capa **4.B** (objetivo del producto); es un conjunto de *requisitos*, no de decisiones de modelado.
- **Decisiones de persistencia** → capa **4.C** (lo que falta ratificar).

### Evidencia disponible (código actual)
- Backend: **autenticación con persistencia real** (`POST /api/register`, `POST /api/login`). `register_use_case.register_user` crea filas reales en `users` (id generado por PostgreSQL); `login_use_case.login_user` consulta `users` por email (vía `SQLAlchemyUserRepository`) y verifica el hash. La credencial hardcodeada (`test@test.com`/`123456`) que existía en `auth_service.validate_user` **se eliminó por completo** (`BACKEND_ARCHITECTURE.md` §9, v0.6). El backend devuelve `{ id, email, name }`, con datos reales, no un objeto fijo.
- Frontend: `Register.jsx` recolecta exactamente tres campos — `name`, `email`, `password`. `Login.jsx` usa `email` (la contraseña está fijada como `"123456" // temporal`). El objeto de usuario que la app espera de vuelta es `{ email, name }` (`useAuth.js`) — el Frontend **todavía no** consume los endpoints reales; esa integración queda fuera de esta actualización (backend-only).
- Frontend `legal/` (`Terms`, `Privacy`, `Cookies`): páginas **estáticas**, sin datos que persistir.

---

### 4.A ESTADO ACTUAL IMPLEMENTADO

> Actualización (v0.3): la persistencia de `users` ya está implementada y en uso real por `register`/`login` (`BACKEND_ARCHITECTURE.md` §8/§9, v0.6) — verificada con pruebas de integración contra PostgreSQL 16 real (`backend/tests/test_auth.py`). "Implementada" en la tabla de abajo ya no es solo una ratificación de modelo: es el estado real y verificado del backend.

| Entidad | Estado | Justificación |
|---|---|---|
| `users` | **IMPLEMENTADA** (ratificada; definición formal en §5; en uso real por `register`/`login`/`GET /api/users/me`) | Registro persiste `name`/`username`/`email`/`phone`/`country_code`/`birth_date`/`password_hash` reales (columnas de perfil ratificadas por `ADR-002`, v0.5); login autentica consultando `users` por `email`; el backend devuelve el objeto público completo (§5) con datos reales |

**Ninguna otra entidad está en esta capa.** Todo lo demás pertenece a la capa objetivo (§4.B) o a pendientes (§4.C).

---

### 4.B ARQUITECTURA OBJETIVO DEL PRODUCTO

El equipo confirmó el alcance funcional de THERS. Aquí se traduce cada grupo funcional a su **forma candidata de persistencia**, bajo dos reglas estrictas:

1. **Una funcionalidad no equivale a una tabla.** Varias funciones colapsan en una sola estructura (p. ej. *seguidores + seguidos + seguir + dejar de seguir* = una única tabla puente `follows`; *todos los tipos de notificación* = una sola entidad `notifications` con discriminador de tipo).
2. **No se decide el modelado.** No se fijan PK/FK, tipos SQL ni cardinalidades definitivas (reglas 6–7 de esta tarea). La "forma candidata" es una **hipótesis a ratificar por ADR**, no una decisión.

Estados usados en esta capa:
- **OBJETIVO** — confirmado como parte del producto; forma candidata identificable; modelado a ratificar.
- **PENDIENTE DE DECISIÓN** — incluso la *forma* de persistencia (tabla vs columna vs configuración vs evento) está genuinamente abierta.

#### Autenticación y cuenta
| Requisito funcional | Forma candidata de persistencia | Estado | Por qué aún requiere decisión |
|---|---|---|---|
| Registro, Login, Cerrar sesión | Operan sobre `users` (ya ratificada) — son **comportamientos**, no tablas nuevas | OBJETIVO | El registro persistente reemplaza la validación hardcodeada; depende de implementar `users` |
| Login con Google | Entidad `oauth_accounts` **o** columnas de proveedor en `users` | PENDIENTE DE DECISIÓN | La forma (entidad separada vs columnas) no está decidida |
| Verificación de correo, Recuperación de contraseña | Tabla(s) de tokens de un solo uso **o** columnas + servicio externo | PENDIENTE DE DECISIÓN | Depende de si se persisten tokens o se delega en un servicio |
| Cambio de contraseña | Comportamiento sobre `users`; historial opcional (ver Seguridad) | PENDIENTE DE DECISIÓN | Persistir historial es opcional y depende de requisitos de auditoría |
| Gestión / desactivación / eliminación de cuenta | Columna de estado (`status`/`deleted_at`, borrado lógico) **vs** borrado físico | PENDIENTE DE DECISIÓN | La política de borrado (lógico vs físico) no está decidida |
| Sesiones y dispositivos | Entidades `sessions`, `devices` | OBJETIVO | Hoy el JWT es stateless; pasar a sesiones/dispositivos persistidos es un cambio a ratificar |

#### Perfil
| Requisito funcional | Forma candidata | Estado | Por qué aún requiere decisión |
|---|---|---|---|
| Nombre | Columna `users.name` (ya existe) | **IMPLEMENTADA** | — |
| Username | Columna `users.username` (única) | **IMPLEMENTADA** (v0.5, `ADR-002`) | — |
| Teléfono | Columnas `users.phone` + `users.country_code` | **IMPLEMENTADA** (v0.5, `ADR-002`) | — |
| Fecha de nacimiento | Columna `users.birth_date` | **IMPLEMENTADA** (v0.5, `ADR-002`) | — |
| Foto de perfil | Columna `avatar_url` en `users` **o** referencia a entidad `media` | PENDIENTE DE DECISIÓN | URL simple vs entidad de medios, no decidido |
| Biografía | Columna `bio` en `users` | OBJETIVO | Longitud/tipo a decidir; no añade PK/FK |
| Edición del perfil | Comportamiento (UPDATE sobre `users`) | OBJETIVO | No añade estructura |

> ⚠️ **Contradicción registrada en v0.1–v0.4, cerrada en v0.5.** La v0.1 (§5) excluía `username` por no recolectarse en el registro; v0.2–v0.4 la registraron como **columna objetivo**, pendiente de ADR. `ADR-002-user-profile-fields.md` (THERS Backend Fase 2.1) resuelve esa pendiente: `username`, `phone`, `country_code` y `birth_date` pasan a **IMPLEMENTADA** (ver §5). `avatar_url`/`bio` **siguen** como objetivo/pendiente — este ADR no las toca.

#### Configuración
| Requisito funcional | Forma candidata | Estado | Por qué aún requiere decisión |
|---|---|---|---|
| Cuenta, Privacidad, Seguridad, Notificaciones, Preferencias | Entidad `user_settings` (1:1) **o** columnas en `users` **o** documento JSON | PENDIENTE DE DECISIÓN | La forma (tabla 1:1 vs columnas vs JSON) es una decisión de modelado abierta |
| Sesiones / dispositivos | = entidades `sessions`/`devices` (ver Autenticación/Seguridad) | OBJETIVO | Misma estructura, no se duplica |
| Usuarios bloqueados | Tabla puente `blocks` (ver Relaciones sociales) | OBJETIVO | Misma estructura que el bloqueo social |
| Gestión de datos (export/borrado) | Comportamiento/proceso; no necesariamente una tabla | PENDIENTE DE DECISIÓN | Puede no requerir persistencia propia |

#### Contenido
| Requisito funcional | Forma candidata | Estado | Por qué aún requiere decisión |
|---|---|---|---|
| Posts | Entidad `posts` (referenciará a `users` como autor, ver §6) | OBJETIVO | Modelado (PK/FK/tipos) sin decidir |
| Fotos, Videos, Reels | Entidad `media` ligada a `posts` (con tipo) **o** tablas separadas | PENDIENTE DE DECISIÓN | Tabla de medios con discriminador vs tablas por tipo; "reel" ¿es tipo de video o entidad propia? |
| Editar / Eliminar publicaciones | Comportamientos + columnas (`updated_at`, borrado lógico) sobre `posts` | PENDIENTE DE DECISIÓN | Política de borrado lógico vs físico |
| Compartir publicaciones | Entidad de *repost* **vs** evento **vs** compartir externo | PENDIENTE DE DECISIÓN | La semántica de "compartir" (interno/externo) no está definida |
| Visibilidad de publicaciones | Columna `visibility` (enum) en `posts` | OBJETIVO | Estrategia de enum pendiente (§7) |

#### Interacciones
| Requisito funcional | Forma candidata | Estado | Por qué aún requiere decisión |
|---|---|---|---|
| Likes / reacciones | Entidad `reactions` (N:N usuario↔post, con tipo) — colapsa "like" y "reacción" | OBJETIVO | Modelado sin decidir |
| Comentarios + Respuestas a comentarios | Entidad única `comments` **auto-referencial** (respuesta = comentario con padre) | OBJETIVO | Colapsa dos funciones en una entidad; PK/FK sin decidir |
| Guardar publicaciones | Tabla puente `saves` (usuario↔post) | OBJETIVO | — |
| Menciones | Tabla puente `mentions` **o** parseo en render sin persistir | PENDIENTE DE DECISIÓN | Persistir vs derivar en lectura, no decidido |
| Hashtags | Entidad `hashtags` + puente `post_hashtags` (N:N) | OBJETIVO | Modelado sin decidir |
| Compartir | = ver Contenido › Compartir publicaciones | PENDIENTE DE DECISIÓN | Misma decisión abierta |

#### Relaciones sociales
| Requisito funcional | Forma candidata | Estado | Por qué aún requiere decisión |
|---|---|---|---|
| Seguir, Dejar de seguir, Seguidores, Seguidos | **Una** tabla puente `follows` (auto-referencial `users`↔`users`) — las cuatro funciones son la misma estructura | OBJETIVO | Cardinalidad y política `ON DELETE` sin decidir |
| Bloquear usuarios | Tabla puente `blocks` (auto-referencial) | OBJETIVO | — |
| Restringir usuarios | Tabla puente `restrictions` **o** atributo de la relación social | PENDIENTE DE DECISIÓN | La semántica de "restringir" vs "bloquear" está por definir |

#### Mensajería
| Requisito funcional | Forma candidata | Estado | Por qué aún requiere decisión |
|---|---|---|---|
| Conversaciones (privadas y grupales), Participantes | `conversations` + puente `conversation_participants` (1:1 y grupo con la misma estructura) | OBJETIVO | Modelado sin decidir |
| Mensajes | Entidad `messages` | OBJETIVO | — |
| Fotos/videos en mensajes | `message_media` **o** reutilizar `media` | PENDIENTE DE DECISIÓN | Reutilización vs entidad propia |
| Estado leído/no leído | Columna `last_read_at` en participante **o** tabla `message_reads` | PENDIENTE DE DECISIÓN | Granularidad (por conversación vs por mensaje) no decidida |

#### Notificaciones
| Requisito funcional | Forma candidata | Estado | Por qué aún requiere decisión |
|---|---|---|---|
| Likes, Comentarios, Respuestas, Nuevos seguidores, Menciones, Mensajes, Actividad relevante | **Una** entidad `notifications` con discriminador de tipo — no una tabla por tipo | OBJETIVO | Estructura del tipo/payload sin decidir |

#### Seguridad
| Requisito funcional | Forma candidata | Estado | Por qué aún requiere decisión |
|---|---|---|---|
| Sesiones, Dispositivos | Entidades `sessions`, `devices` (mismas que Autenticación) | OBJETIVO | Requiere pasar de JWT stateless a estado persistido |
| Cambios de contraseña (historial) | Entidad `password_changes` | PENDIENTE DE DECISIÓN | Solo si se requiere historial/auditoría |
| Eventos de seguridad / Auditoría | Entidad `security_events` / log de auditoría | PENDIENTE DE DECISIÓN | El propio alcance dice "auditoría cuando sea necesaria" — es condicional |

---

### 4.C DECISIONES DE PERSISTENCIA TODAVÍA PENDIENTES

Lo que impide pasar de la capa objetivo (§4.B) a un esquema real:
- **Forma de cada candidato** marcado *PENDIENTE DE DECISIÓN* arriba (tabla vs columna vs configuración vs evento).
- **Modelado transversal** de todas las entidades objetivo: tipo de PK, FK y políticas `ON DELETE`, tipos SQL, enums, índices. **No** se fijan aquí (reglas 6–7 de esta tarea).
- **Decisiones de motor y operación** ya listadas en §14 (versión, driver/ORM, migraciones, backups, variables de entorno, roles de acceso).

Ninguna entidad de la capa objetivo se implementa hasta que su modelado se ratifique por ADR (`HB-001` §11–12) y se incorpore a este documento. El `DATABASE_ERD.md` seguirá representando **solo** la capa 4.A (`users`) hasta entonces.

---

## 5. Entidad propuesta: `users`

> Única entidad con definición formal en esta versión (capa 4.A). El resto está en §4.B (objetivo) y §14 (pendientes).

**Propósito.** Representar a una persona registrada en THERS y ser la fuente de verdad para autenticación — rol que ya cumple en producción de código desde v0.3 (`register`/`login` reales, `BACKEND_ARCHITECTURE.md` §8/§9).

**Atributos principales**

| Columna | Tipo (conceptual) | Nulo | Justificación / origen |
|---|---|---|---|
| `id` | **UUID** | No | Clave primaria. `id UUID PRIMARY KEY DEFAULT gen_random_uuid()` — el valor se genera **en PostgreSQL** (`gen_random_uuid()`, función nativa desde PostgreSQL 13, no requiere `pgcrypto`/`uuid-ossp`), no en Python. Implementado en `app/infrastructure/persistence/models.py` (`sqlalchemy.dialects.postgresql.UUID(as_uuid=True)`, `server_default=text("gen_random_uuid()")`) y en la migración `a1b2c3d4e5f6_create_users_table.py` |
| `name` | `VARCHAR(120)` | No | Campo `name` recolectado en `Register.jsx`; devuelto por el backend |
| `username` | `VARCHAR(30)`, **UNIQUE** (`uq_users_username`) | No | **v0.5 (`ADR-002`).** Campo `username` recolectado en `Register.jsx`; formato `^[a-zA-Z0-9_]{3,20}$` validado en `domain/auth/validators.py`. A diferencia de `email`, **no** usa `CITEXT` — comparación case-sensitive, decisión explícita (`ADR-002` §3): ningún flujo hoy (login sigue siendo por email) requiere case-insensitivity para username |
| `phone` | `VARCHAR(20)` | No | **v0.5 (`ADR-002`).** Campo `phone` recolectado en `Register.jsx` (`PhoneField`); validación laxa de 7–15 dígitos tras limpiar separadores |
| `country_code` | `VARCHAR(6)` | No | **v0.5 (`ADR-002`).** Campo `countryCode` recolectado en `Register.jsx` (`PhoneField`, p. ej. `+503`); formato `^\+[1-9]\d{0,3}$` |
| `birth_date` | `DATE` | No | **v0.5 (`ADR-002`).** Campo `birthDate` recolectado en `Register.jsx` (`BirthDateField`, ISO `yyyy-mm-dd`); edad mínima 13 años validada en el backend (mismo placeholder que ya usaba el Frontend, `dateUtils.js` `MIN_AGE_YEARS`) |
| `password_hash` | `TEXT` | No | Deriva del campo `password` del registro. **Nunca se guarda en claro** — se almacena el hash (necesidad técnica evidente; §11) |
| `created_at` | `TIMESTAMPTZ`, `DEFAULT now()` | No | Convención de auditoría (§7); estándar para toda entidad |
| `updated_at` | `TIMESTAMPTZ`, `DEFAULT now()`, mantenida por trigger | No | Convención de auditoría (§7). Un trigger de PostgreSQL (`set_updated_at`/`trg_users_updated_at`, ver migración) la actualiza en cada `UPDATE` — funciona igual vía ORM o SQL directo, no depende de que el código de aplicación la toque |

**Clave primaria (PK).** `id`.

**Claves foráneas (FK).** Ninguna en esta versión — `users` no depende de otra entidad todavía.

**Relaciones.** Ninguna definida hoy. Cuando existan entidades sociales (posts, follows), serán ellas quienes referencien a `users` mediante FK, no al revés (ver §6 y §4.B).

**Constraints relevantes**
- `email` **UNIQUE** (case-insensitive, vía `CITEXT`) y **NOT NULL** — el login identifica al usuario por email; dos cuentas no pueden compartirlo, ni siquiera con distinto casing. (Justifica también el índice de §8.)
- `name` **NOT NULL** — el formulario lo exige (`isValid` requiere `name.trim()`).
- `password_hash` **NOT NULL**.

**`confirm_password`** se valida en la route (`interfaces/routes/auth_routes.py`, debe coincidir con `password`) y **nunca se persiste** — no existe como columna de `users`, ni siquiera transitoriamente.

**Decisiones sobre esta entidad marcadas como PENDIENTES** (§14): algoritmo de hashing definitivo (sigue usándose `werkzeug.security`/scrypt, ya en uso para la credencial de prueba — ver `BACKEND_ARCHITECTURE.md` §9). **Ya resueltos:** tipo de PK (UUID, `gen_random_uuid()`), tipo de `email` (`CITEXT`), longitud de `name` (`VARCHAR(120)`), tipo de `password_hash` (`TEXT`), estrategia de `updated_at` (trigger), y desde v0.5 también `username`/`phone`/`country_code`/`birth_date` (`ADR-002`) — ver tabla arriba.

> **Actualización v0.2 — reconciliación con el alcance objetivo.** El alcance funcional confirmado por el equipo incorporó `username`, `avatar_url` y `bio` como **columnas OBJETIVO** de `users` (§4.B › Perfil), pendientes de ADR. **Actualización v0.5:** `username` (junto con `phone`/`country_code`/`birth_date`, no anticipadas en v0.2) ya se ratificaron e implementaron por `ADR-002-user-profile-fields.md` — ver tabla arriba. `avatar_url`/`bio` siguen como columnas OBJETIVO, sin ADR propio todavía.

---

## 6. Relaciones entre entidades

En esta versión **no existen relaciones implementadas**, porque solo hay una entidad ratificada (`users`, capa 4.A).

Regla de diseño para cuando existan más entidades (para evitar decisiones improvisadas durante la implementación):
- Las entidades dependientes referencian a `users` con una FK (p. ej. un futuro `posts.author_id → users.id`).
- La cardinalidad, la política `ON DELETE` y las tablas puente (p. ej. relaciones N:N de "follows") se definirán **cuando esas entidades se ratifiquen**, cada una como ADR (`HB-001` §12). Las relaciones candidatas del producto objetivo se listan en §4.B, pero **no** se dibujan ni modelan aquí.

---

## 7. Convenciones

> ⚠️ Ninguna convención de base de datos está ratificada en `/docs` (`CLAUDE.md` §14). Las siguientes son **propuestas** alineadas con lo que el repo ya hace en otras capas (código en inglés, Python en `snake_case`). **Requieren ratificación del equipo (ADR, `HB-001` §12)** antes de tratarse como contrato cerrado.

| Elemento | Convención propuesta | Ejemplo |
|---|---|---|
| Nombres de tabla | inglés, `snake_case`, **plural** | `users`, `posts` |
| Nombres de columna | inglés, `snake_case`, singular | `email`, `created_at` |
| Clave primaria | columna `id` | `users.id` |
| Clave foránea | `<entidad_singular>_id` | `author_id`, `user_id` |
| Timestamps | `created_at`, `updated_at` (timestamp **con** zona horaria) | — |
| Booleanos | prefijo `is_`/`has_` | `is_active` |
| Enums / status | valores en `snake_case`; preferir columna de texto con `CHECK` o tipo `ENUM` de PostgreSQL — **la elección entre ambos queda PENDIENTE** (§14) | `status IN ('active','suspended')` |
| Nombres de índice | `ix_<tabla>_<columna(s)>`; únicos: `uq_<tabla>_<columna(s)>` | `uq_users_email` |

---

## 8. Índices

**Principio (repetido por su importancia):** no se crean índices especulativos. Cada índice listado justifica su existencia con una consulta real ya presente en el código.

| Índice propuesto | Tabla / columna | Consulta que lo justifica |
|---|---|---|
| Índice único de email | `users(email)` — `UNIQUE` | El login busca al usuario **por email** en cada intento de autenticación (`Login.jsx` envía `email`; el backend deberá hacer `SELECT ... WHERE email = ?`). La restricción `UNIQUE` de §5 crea este índice automáticamente y sirve tanto para integridad como para el lookup de login. |
| Índice único de username (`uq_users_username`) | `users(username)` — `UNIQUE` | **v0.5 (`ADR-002`).** `POST /api/register` valida unicidad de `username` en cada registro; la constraint `UNIQUE` de §5 crea este índice automáticamente. Ningún flujo consulta hoy por `username` fuera de esa validación de unicidad (login sigue siendo por email) — no se justifica un índice adicional de búsqueda. |

**No se añaden más índices en esta versión.** La PK (`id`) ya está indexada por definición. Cualquier índice adicional (p. ej. sobre columnas de futuras tablas de feed) se justificará **cuando exista la consulta que lo pague**, no antes.

---

## 9. Migraciones

| Aspecto | Estado |
|---|---|
| Estrategia | **Migraciones versionadas e incrementales**, cada cambio de esquema como un archivo de migración revisado por PR (coherente con el git flow de `HB-001` §7–9: nada al esquema sin PR + aprobación). |
| Herramienta | ~~PENDIENTE DE APROBACIÓN~~ — **resuelto: Flask-Migrate/Alembic** (`backend/migrations/`), implementado y verificado en esta tarea: `flask db upgrade`/`downgrade` probados dos veces cada uno contra PostgreSQL 16 real (Docker), incluida la reconstrucción completa desde un volumen vacío. Ratificación formal por el Comité Técnico pendiente de confirmar (`HB-001` §11.1). |
| Versionado | Cada migración es inmutable una vez fusionada a `develop`/`main`; los cambios posteriores son migraciones nuevas, no ediciones de una anterior. |
| Rollback | Cada migración debe declarar su reverso (downgrade). El **procedimiento operativo** de rollback en un entorno desplegado depende de DevOps, que es territorio no especificado (`CLAUDE.md` §14) → **PENDIENTE**. |
| Ubicación de artefactos | `REPOSITORY_STRUCTURE.md` §10 anticipa una carpeta futura `database/` para "scripts de migración, semillas y esquema versionado", hoy "presumiblemente dentro de `backend/`". La ubicación definitiva queda **PENDIENTE** hasta que el equipo la confirme. |

---

## 10. Seeds

| Aspecto | Definición |
|---|---|
| Propósito | Poblar la base con datos mínimos para desarrollo local y pruebas manuales. |
| Datos de desarrollo | Un conjunto pequeño de usuarios de prueba con contraseñas **de prueba** documentadas como tales. Nunca contraseñas reales de personas. |
| Separación desarrollo / producción | Los seeds de desarrollo **nunca** se ejecutan contra producción. Producción no lleva usuarios de ejemplo. La forma concreta de separar entornos (variable de entorno, comando distinto) depende de la configuración de entornos, hoy **PENDIENTE** (§14). |

> Actualización (v0.3): el usuario hardcodeado (`test@test.com` / `123456`) que vivía en `auth_service.py` **se eliminó del código** al integrar `register`/`login` con `users` real (`BACKEND_ARCHITECTURE.md` §9, v0.6) — no migró a un seed, simplemente se retiró. Sigue sin existir ninguna estrategia de seeds implementada (script, comando, datos de ejemplo); esta sección sigue describiendo el diseño esperado, no algo ya construido.

---

## 11. Integridad y seguridad

- **Constraints como defensa de datos.** Las reglas de integridad (unicidad de `email`, `NOT NULL`, futuros `CHECK`/enums) se declaran en el esquema, no solo en la aplicación (§3, §5).
- **Extensión `citext`.** El tipo `CITEXT` de `email` (§5) requiere `CREATE EXTENSION IF NOT EXISTS citext`, creada por la propia migración (`a1b2c3d4e5f6_create_users_table.py`) antes de crear la tabla — no requiere instalación manual adicional en la base.
- **Contraseñas.** Se almacena `password_hash`, **nunca** la contraseña en claro (§5). El algoritmo de hashing concreto queda **PENDIENTE** (§14) — es una decisión de seguridad que debe confirmar el equipo, no inferirse.
- **Secretos y credenciales.** La cadena de conexión y credenciales de la base **nunca** se suben al repositorio (`HB-001` §20, regla innegociable) y se proveen por variables de entorno. No hay lista oficial de variables de entorno (`CLAUDE.md` §9, §14) → definirla es **PENDIENTE**.
- **Acceso.** El backend accede a la base con un usuario de base de datos de privilegios acotados. La política concreta de roles/privilegios de PostgreSQL es **PENDIENTE** (depende de DevOps, no especificado).
- **Datos sensibles.** Hoy el único dato sensible identificado es la credencial de acceso del usuario (`password` → `password_hash`). Cualquier dato personal adicional que introduzcan futuras features (y su relación con las políticas de `Privacy`/`Cookies` del Frontend) deberá evaluarse cuando esas features existan → **PENDIENTE**.

> ⚠️ **Hallazgo de seguridad en el código actual (fuera del esquema, pero relevante a esta sección).** `backend/app/config.py` define `JWT_SECRET_KEY = "super-secret-key"` **hardcodeado en el repositorio**, lo que contradice `HB-001` §19.1/§20 (no subir secretos). No es un asunto de base de datos y **no se corrige en este documento**, pero se reporta porque toca directamente el principio de seguridad de secretos que este documento hereda. Corrección recomendada en una tarea de backend propia.

---

## 12. Backups y recuperación

**No existe ninguna estrategia de backups o recuperación documentada** en `/docs` (`CLAUDE.md` §14 lo confirma explícitamente).

Estado: **PENDIENTE DE APROBACIÓN — sección completa.**

Preguntas abiertas que el equipo debe responder antes de considerar esta sección cerrada: frecuencia de respaldo, retención, ubicación de los backups, procedimiento y objetivo de recuperación (RPO/RTO), y responsable. Todo esto depende de DevOps, que es territorio no especificado — **no se inventa aquí**.

---

## 13. Integración con el Backend

Se describe la responsabilidad de cada capa **usando la estructura ya observada** en `backend/` (`domain/`, `application/`, `interfaces/routes/`), sin inventar una arquitectura distinta. `CLAUDE.md` §4 y `REPOSITORY_STRUCTURE.md` §6 advierten que estas capas están **observadas, no ratificadas**; este documento las respeta pero no las eleva a contrato cerrado.

| Capa observada | Responsabilidad respecto a la base de datos |
|---|---|
| **`domain/`** | Entidades y reglas de negocio puras (p. ej. qué es un usuario válido). **No** conoce SQL, ni el ORM, ni PostgreSQL. Hoy contiene `auth_service.py` (validación). |
| **`application/`** (use cases / services) | Orquesta el caso de uso (p. ej. "iniciar sesión") pidiendo datos a un repositorio, sin saber **cómo** se persisten. Hoy contiene `login_use_case.py`. |
| **Repositories** (capa a introducir) | Punto único donde vive el acceso a datos: traduce entre las entidades del dominio y las tablas de PostgreSQL. Es la frontera que aísla al resto del backend de los detalles del motor (coherente con el principio de "bajo acoplamiento", `FAS-001` §2). **Su ubicación exacta dentro de la estructura de capas queda PENDIENTE** (§14) porque no hay un documento de arquitectura de backend ratificado. |
| **Database layer / infraestructura** | Conexión, configuración del pool, inicialización del ORM/driver y ejecución de migraciones. Hoy `config.py` y `extensions.py` son los puntos donde esta responsabilidad encajaría, pero **no hay nada de base de datos cableado todavía**. |
| **`interfaces/routes/`** | Adaptadores HTTP; no tocan la base directamente — delegan en `application/`. Hoy contiene `auth_routes.py`. |

**Regla de dependencia:** las rutas dependen de los casos de uso, los casos de uso de los repositorios (abstractos), y solo la capa de infraestructura conoce PostgreSQL. Nunca al revés. Esto es una **descripción** del patrón ya insinuado por la estructura existente, no una decisión nueva.

---

## 14. PENDIENTES DE APROBACIÓN

Decisiones que este documento **no toma** porque no están respaldadas por la documentación oficial ni por una necesidad técnica evidente. Cada una debe resolverse como ADR (`HB-001` §11–12) antes de implementarse.

### Motor y dependencias
- ~~Versión de PostgreSQL para desarrollo local~~ — **resuelto: PostgreSQL 16** (`postgres:16-alpine` vía `docker-compose.yml`, raíz del repo), reproducible por cualquier integrante con `docker compose up -d`. No hay todavía una base compartida por el equipo o de producción; la versión oficial para esos entornos sigue sin ratificación formal.
- **Driver/adaptador Python** y **ORM** — **implementado en código** (`psycopg` v3 + SQLAlchemy + Flask-Migrate/Alembic, ver §2); ratificación formal por el Comité Técnico pendiente de confirmar.

### Esquema
- ~~Tipo de PK de `users`~~ — **resuelto: UUID**, `DEFAULT gen_random_uuid()` a nivel de PostgreSQL (implementado, ver §5; ratificación formal pendiente de confirmar).
- ~~Longitudes máximas de columnas de texto~~ — **resuelto:** `name VARCHAR(120)`; `email` (`CITEXT`) y `password_hash` (`TEXT`) sin límite fijo de longitud (ver §5).
- ~~Normalización de `email`~~ — **resuelto: `CITEXT`** (extensión de PostgreSQL, comparación e índice único case-insensitive a nivel de motor — ver §5, §11).
- **Algoritmo de hashing** de contraseñas — sigue pendiente (se usa `werkzeug.security`/scrypt como corrección puntual, no ratificado como definitivo).
- **Estrategia de enums** (columna de texto con `CHECK` vs tipo `ENUM` nativo) — no aplica a `users` todavía, sigue pendiente para entidades futuras.

### Entidades candidatas del modelo objetivo
La lista completa de estructuras candidatas del producto objetivo (con su **forma candidata, estado y motivo de decisión**) vive ahora en **§4.B**, para no duplicarla ni arriesgar divergencia. Criterio invariable: **ninguna se implementa sin ratificación por ADR** (`HB-001` §11–12), y su **modelado (PK/FK/tipos) permanece PENDIENTE**. Entre las candidatas confirmadas por el alcance funcional: `oauth_accounts`, `sessions`/`devices`, `user_settings`, columnas de perfil (`username`/`avatar_url`/`bio`), `posts`, `media`, `reactions`, `comments`, `saves`, `mentions`, `hashtags` (+`post_hashtags`), `follows`, `blocks`, `restrictions`, `conversations` (+`conversation_participants`, `messages`, `message_media`), `notifications`, `password_changes`, `security_events`.

### Operación
- ~~Herramienta de migraciones~~ — **resuelto en código: Flask-Migrate/Alembic**, scaffolding en `backend/migrations/` (ver `BACKEND_ARCHITECTURE.md` §8); ratificación formal pendiente de confirmar. **Ubicación de la carpeta `database/`** sigue sin definir — las migraciones quedaron dentro de `backend/`, no en una carpeta `database/` separada.
- **Procedimiento de rollback** en entornos desplegados (DevOps).
- **Estrategia de backups y recuperación** — §12, sección completa pendiente.
- **Lista oficial de variables de entorno** — `DATABASE_URL` ya documentada en `backend/.env.example` (formato `postgresql+psycopg://usuario:password@host:puerto/nombre_bd`); sigue sin existir una lista oficial completa más allá de `JWT_SECRET_KEY` y `DATABASE_URL`.
- **Roles/privilegios de acceso** de PostgreSQL.
- **Ubicación exacta de la capa de repositorios** dentro de la estructura de backend — el modelo ya vive en `backend/app/infrastructure/persistence/models.py`, pero el repositorio que lo conecte con `application/`/`domain/` todavía no existe.

### Contradicciones / hallazgos reportados (no resueltos aquí)
- **README raíz dice MySQL** vs. PostgreSQL oficial (§2). Gana `/docs`; corregir el README en tarea aparte.
- **`JWT_SECRET_KEY` hardcodeado** en `config.py` (§11), contra `HB-001` §19.1/§20. Corregir en tarea de backend aparte.
- ~~`username`/`phone`/`country_code`/`birth_date` en `users`~~ — **resuelto en v0.5** por `ADR-002-user-profile-fields.md` (ver §5). `avatar_url`/`bio` (§4.B › Perfil) **siguen** pendientes de ADR — no cubiertas por `ADR-002`.

---

## 15. Cierre

Este documento **no modifica** el backend, el Frontend, el Handbook ni instala dependencias: define el contrato de base de datos que la implementación futura deberá respetar, separando explícitamente **lo implementado (§4.A)**, **lo objetivo (§4.B)** y **lo pendiente (§4.C, §14)**. Cualquier cambio a este contrato sigue el proceso de decisiones de impacto medio/alto de `HB-001` §11–12 (ADR), no el criterio individual de quien implementa.
