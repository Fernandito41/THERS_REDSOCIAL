# DATABASE_ARCHITECTURE

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/DATABASE_ARCHITECTURE.md` |
| Identificador propuesto | `DB-001` (sigue el patrón `HB-001`/`ARC-001`/`DS-001`/`WF-001`/`PV-001`/`FAS-001`) — **pendiente de ratificación formal** |
| Versión | 0.17 |
| Estado | **Borrador / Contrato técnico — pendiente de aprobación del equipo** |
| Depende de | `HB-001` (organización, gobernanza, git flow, seguridad), `REPOSITORY_STRUCTURE.md` (ubicación del backend y carpeta futura `database/`) |
| Motivo | El `CLAUDE.md` maestro (§4, §14) identificó que la arquitectura de Base de Datos no estaba formalmente documentada |
| Idioma | Español (documentación oficial), identificadores/código en inglés |

> ⚠️ **Nota de alcance y honestidad de fuentes.** Este documento es un **contrato técnico previo a la implementación**, no una descripción de un esquema ya existente. Al momento de escribirlo (v0.1), el backend **no tenía base de datos, ni ORM, ni driver de PostgreSQL instalado**: la autenticación funcionaba contra credenciales hardcodeadas (ver §4). Todo lo que aquí se define como "decidido" se limita a lo que la documentación oficial ya respalda o a lo que el estado real del código justifica de forma evidente. Todo lo demás está marcado explícitamente como **PENDIENTE DE APROBACIÓN** (§14). No se inventan entidades, columnas, índices ni políticas que el proyecto no necesite hoy.
>
> **v0.17 — mensajes directos, `messages` (`ADR-013-messages-minimal-model.md`):** "Conversaciones (privadas y grupales), Participantes" + "Mensajes" (§4.B › Mensajería) se resuelve **solo a medias** — pasa a **implementada** (§4.A, §5.10) únicamente la mitad 1:1: mensaje directo entre dos usuarios reales, sin la tabla puente `conversation_participants` que soportaría grupos (sigue sin ratificar). Nueva tabla `messages`: `sender_id`/`recipient_id` (FKs a `users`, ambas `ON DELETE CASCADE`), `content` (texto, sin límite de esquema — validado en la aplicación, máximo 2000 caracteres), `read_at` (`TIMESTAMPTZ`, nullable, `NULL` = no leído, mismo criterio que `notifications.read_at`), sin `updated_at` (mismo criterio que `likes`/`follows`/`notifications`). **Segunda `CHECK` constraint del esquema** (`ck_messages_no_self_message`: `sender_id <> recipient_id`, mismo criterio que `ck_follows_no_self_follow`). Sin `UNIQUE` — dos mensajes entre las mismas personas son eventos legítimos, no un duplicado a impedir (mismo criterio que `notifications`). Dos índices compuestos nuevos, `ix_messages_sender_recipient_created`/`ix_messages_recipient_sender_created` (§8) — el hilo entre A y B se busca con un `OR` sobre ambos sentidos de la relación, que ninguna `UNIQUE` cubre. Decimocuarta y decimoquinta relación real entre entidades (§6): `messages.sender_id → users.id`, `messages.recipient_id → users.id`. Migración `f7a2c9e4d1b8`. Verificado con `flask db upgrade`/`downgrade` contra PostgreSQL 16 real y la suite completa de pruebas (`backend/tests/`, 263 pruebas).
>
> **v0.3 — cierre de la capa de persistencia (auditoría y validación real de esta tarea).** Se corrigió la referencia a una instalación nativa de PostgreSQL 17.11 (no reproducible por el equipo) por el entorno estandarizado real: **PostgreSQL 16 vía Docker Compose** (`docker-compose.yml`, raíz del repo, imagen `postgres:16-alpine`), verificado end-to-end (`flask db upgrade`/`downgrade` repetidos, INSERT sin `id` confirmando `gen_random_uuid()` en PostgreSQL, UPDATE confirmando el trigger de `updated_at`, unicidad case-insensitive de `email` vía `CITEXT`, y reconstrucción completa desde un volumen Docker vacío). Se marcó como resuelta la herramienta de migraciones (§9) donde el documento aún decía `PENDIENTE`, pese a que Flask-Migrate/Alembic ya estaba implementado. Ningún esquema, entidad ni columna cambió — solo se sincronizó el documento con el código real ya existente.
>
> **v0.4 — integración de autenticación con persistencia real.** `users` pasó de "modelo implementado pero no conectado" a **en uso real**: `POST /api/register` y `POST /api/login` (`BACKEND_ARCHITECTURE.md` §8/§9, v0.6) ya crean/consultan filas reales, y la credencial hardcodeada (`test@test.com`/`123456`) se eliminó del código por completo. Reflejado en §4 y §5. No se agregó ninguna entidad, columna ni índice nuevo — sigue siendo únicamente `users`, sin cambios de esquema.
>
> **v0.5 — columnas de perfil ratificadas por ADR (THERS Backend Fase 2.1).** `username`, `phone`, `country_code` y `birth_date` pasan de **OBJETIVO** (§4.B) a **IMPLEMENTADAS** en `users`, ratificado por `ADR-002-user-profile-fields.md` — el ADR que esta misma sección (v0.2–v0.4) ya pedía antes de tocar el esquema. Migración `a1edcbff74d8_add_profile_fields_to_users.py`, verificada con `flask db upgrade`/`downgrade` contra PostgreSQL 16 real (`thers_dev`, Docker) y con 27 pruebas de integración (`backend/tests/`). `username` es único (`uq_users_username`) pero **no** usa `CITEXT` (a diferencia de `email`) — decisión explícita en `ADR-002` §3, no una omisión. `avatar_url`/`bio` (§4.B) siguen sin ratificar. Reflejado en §4.A, §4.B y §5.
>
> **v0.6 — soporte de cooldown para `PATCH /api/users/me` (THERS Backend, `ADR-003-profile-update-contract.md`).** `users` gana `username_changed_at` (`TIMESTAMPTZ`, nullable), migración aditiva `b2f4a19c3d7e_add_username_changed_at_to_users.py`, verificada con `flask db upgrade`/`downgrade` repetidos contra PostgreSQL 16 real (`thers_dev`, Docker) y con la suite completa de pruebas (`backend/tests/`, 52 pruebas). `NULL` significa "nunca cambió su username" — sin backfill, ningún usuario existente pudo cambiar su username antes de esta tarea. `ADR-003` decidió explícitamente **no** crear ninguna columna nueva más allá de esta (`bio`/`avatar_url` siguen sin ratificar, `email`/`password` quedan fuera del contrato de `PATCH`). Reflejado en §5.
>
> **v0.7 — auditoría documental integral de THERS (corrección de un hallazgo obsoleto, sin cambios de esquema).** §11 y §14 seguían advirtiendo `JWT_SECRET_KEY = "super-secret-key"` **hardcodeado** en `backend/app/config.py` como hallazgo de seguridad abierto — ya corregido desde `BACKEND_ARCHITECTURE.md` v0.2 (lee `os.environ.get("JWT_SECRET_KEY")`, con un fallback de desarrollo explícitamente inseguro advertido por `stderr`, nunca un literal hardcodeado). El propio `ADR-003-profile-update-contract.md` (§Estado actual) ya había señalado esta desincronización entre documentos hermanos sin corregirla, por estar fuera de su alcance. Verificado en esta auditoría releyendo `backend/app/config.py` línea por línea. Ningún esquema, entidad ni columna cambió — solo se sincronizaron §11 y §14 con el código real.
>
> **v0.8 — primera entidad social real, `posts` (`ADR-004-posts-minimal-model.md`):** `posts` pasa de candidata objetivo (§4.B › Contenido) a **implementada** (§4.A, §5.2) — deliberadamente mínima: solo `author_id` (FK a `users`, `ON DELETE CASCADE`) y `content` (texto, máximo 2000 caracteres). Primera relación real entre entidades (§6). Nuevo índice `ix_posts_created_at` (§8), justificado por `GET /api/posts` (§9 se actualiza con la cuarta migración). `visibility`, medios, reacciones, comentarios, hashtags, mood, ubicación, edición/borrado — todo lo demás que §4.B seguía listando junto a "Posts" — sigue sin ratificar, cada uno queda para su propio ADR (`ADR-004` §Decisiones pendientes). Verificado con `flask db upgrade`/`downgrade` contra PostgreSQL 16 real y la suite completa de pruebas (`backend/tests/`, 71 pruebas).
>
> **v0.9 — segunda entidad social real, `likes` (`ADR-005-likes-minimal-model.md`):** `reactions` (§4.B › Interacciones, "Likes / reacciones") pasa de candidata objetivo a **implementada** (§4.A, §5.3), pero solo en su versión mínima binaria (like/no-like) — la forma general "con tipo" que §4.B seguía describiendo sigue sin ratificar. Nueva tabla `likes`: `post_id`/`user_id` (FKs a `posts`/`users`, ambas `ON DELETE CASCADE`), `UNIQUE (post_id, user_id)` (`uq_likes_post_user`), sin `updated_at` (un like no se edita, solo se crea o se borra). Sin índice adicional — la propia `UNIQUE` ya cubre el patrón de acceso real por `post_id` (§8). Segunda relación real entre entidades (§6): `likes.post_id → posts.id`, `likes.user_id → users.id`. Verificado con `flask db upgrade`/`downgrade` contra PostgreSQL 16 real y la suite completa de pruebas (`backend/tests/`, 89 pruebas).
>
> **v0.10 — comentarios planos sobre posts, `comments` (`ADR-006-comments-minimal-model.md`):** la candidata combinada "Comentarios + Respuestas a comentarios" (§4.B › Interacciones) se resuelve **solo a medias** — pasa a **implementada** (§4.A, §5.4) únicamente su mitad plana: comentar un post, sin hilos de respuestas (`parent_comment_id` sigue sin ratificar). Nueva tabla `comments`: `post_id`/`author_id` (FKs a `posts`/`users`, ambas `ON DELETE CASCADE`), `content` (texto, máximo 1000 caracteres), con `updated_at`+trigger (mismo patrón de auditoría que `posts`, aunque sin edición todavía). Nuevo índice compuesto `ix_comments_post_id_created_at` (§8), justificado por `GET /api/posts/<id>/comments`. Tercera y cuarta relación real entre entidades (§6): `comments.post_id → posts.id`, `comments.author_id → users.id`. Verificado con `flask db upgrade`/`downgrade` contra PostgreSQL 16 real y la suite completa de pruebas (`backend/tests/`, 93 pruebas).
>
> **v0.11 — seguir/dejar de seguir, `follows` (`ADR-007-follows-minimal-model.md`):** "Seguir, Dejar de seguir, Seguidores, Seguidos" (§4.B › Relaciones sociales) pasa de candidata objetivo a **implementada** (§4.A, §5.5). Nueva tabla `follows`: `follower_id`/`followed_id` (FKs a `users`, ambas `ON DELETE CASCADE`), `UNIQUE (follower_id, followed_id)` (`uq_follows_follower_followed`), **primera `CHECK` constraint del esquema** (`ck_follows_no_self_follow`: `follower_id <> followed_id`), sin `updated_at` (mismo criterio que `likes`). Primera relación auto-referencial (`users`↔`users`) del modelo. Nuevo índice `ix_follows_followed_id` (§8) — a diferencia de `likes`, sí hace falta un segundo índice porque `followers_count` filtra por la columna no líder de la `UNIQUE`. Quinta y sexta relación real entre entidades (§6): `follows.follower_id → users.id`, `follows.followed_id → users.id`. `users` gana `followers_count`/`following_count` calculados (no columnas propias) expuestos en `GET`/`PATCH /api/users/me`; `posts.author` gana `is_followed_by_me` calculado, expuesto en `GET`/`POST /api/posts`. El feed **sigue sin filtrar por seguidos** — deliberadamente fuera de este ADR (§No objetivos). Verificado con `flask db upgrade`/`downgrade` contra PostgreSQL 16 real y la suite completa de pruebas (`backend/tests/`, 124 pruebas).
>
> **v0.16 — "Continuar con Google" (`ADR-012-google-sign-in.md`):** "Login con Google" (§4.B › Autenticación y cuenta) pasa de `PENDIENTE DE DECISIÓN` a **implementada** (§4.A, §5.9) — nueva tabla `user_identities` (`user_id`, `provider`, `provider_subject`, `UNIQUE (provider, provider_subject)`), separada de `users` para no acoplar el esquema a un proveedor específico. `users` relaja `phone`/`country_code`/`birth_date`/`password_hash` a `NULLABLE` (Google no entrega los primeros tres; una cuenta Google-only no tiene contraseña local) y gana `profile_completed` (`BOOLEAN DEFAULT true`) — el registro tradicional sigue exigiendo esos campos igual que siempre a nivel de aplicación, así que nunca quedan en `NULL` para una cuenta creada así. Decimotercera relación del esquema: `user_identities.user_id → users.id`, `ON DELETE CASCADE`. Nuevos índices `uq_user_identities_provider_subject`/`ix_user_identities_user_id` (§8). Migración `b1e5d8a4f3c7` (altera `users`, crea `user_identities`; downgrade revierte ambos). Verificado con `flask db upgrade`/`downgrade` contra PostgreSQL 16 real y la suite completa de pruebas (`backend/tests/`, 242 pruebas).
>
> **v0.15 — verificación obligatoria de email al registrarse, por código OTP de 6 dígitos (`ADR-011-mandatory-email-verification.md`, reemplaza el modelo de enlace de v0.13 para esta entidad):** `email_verification_tokens` se reconstruye (no se duplica), mismo patrón que `password_reset_tokens` en v0.14 -- pierde `token_hash` (SHA-256), gana `code_hash` (scrypt), `attempts` (§5.8). Nuevo índice único **parcial** `uq_email_verification_tokens_active_user` (`user_id`, `WHERE used_at IS NULL`), reemplaza a `uq_email_verification_tokens_token_hash` de v0.13 — garantiza a nivel de motor que nunca hay más de un código activo por usuario. `password_reset_tokens` **no cambia** — sigue exactamente como en v0.14. Migración `a7d3f6c1e8b9` (recrea la tabla; downgrade restaura la forma de v0.13). Sin columnas de autorización temporal (a diferencia de `password_reset_tokens`) — verificar el código es la acción final, no hay un paso sensible posterior que proteger. Estructuralmente separada de `password_reset_tokens`: un código de una tabla nunca verifica el propósito de la otra (`ADR-011` §Decisión, purpose separation). Verificado con `flask db upgrade`/`downgrade` contra PostgreSQL 16 real y la suite completa de pruebas (`backend/tests/`, 212 pruebas).
>
> **v0.14 — recuperación de contraseña por código OTP de 6 dígitos (`ADR-010-password-reset-otp-flow.md`, reemplaza el modelo de enlace de v0.13 para esta entidad):** `password_reset_tokens` se reconstruye (no se duplica) -- pierde `token_hash` (SHA-256), gana `code_hash` (scrypt, mismo algoritmo que `password_hash`), `attempts`, `verified_at`, `reset_authorization_hash`/`_expires_at` (§5.7). Primer índice único **parcial** del esquema: `uq_password_reset_tokens_active_user` (`user_id`, `WHERE used_at IS NULL`) — garantiza a nivel de motor que nunca hay más de una solicitud activa por usuario, incluso ante dos "Reenviar código" simultáneos. `email_verification_tokens` **no cambia** — sigue exactamente como en v0.13. Migración `f4b8c92a1d67` (recrea la tabla; downgrade restaura la forma de v0.13). Verificado con `flask db upgrade`/`downgrade` contra PostgreSQL 16 real y la suite completa de pruebas (`backend/tests/`, 189 pruebas).
>
> **v0.13 — recuperación de contraseña y verificación de email (`ADR-009-password-reset-and-email-verification.md`):** "Verificación de correo, Recuperación de contraseña" (§4.B › Autenticación y cuenta) pasa de `PENDIENTE DE DECISIÓN` a **implementada** (§4.A, §5.7, §5.8) — se resuelve como tokens de un solo uso respaldados por tabla (la opción que esa misma sección ya anticipaba). `users` gana `email_verified` (`BOOLEAN`, `DEFAULT false`). Dos tablas nuevas: `password_reset_tokens` y `email_verification_tokens`, misma forma (`user_id`, `token_hash` — SHA-256 del token crudo, nunca el valor en claro —, `expires_at`, `used_at`, `created_at`), separadas porque su política (TTL de 30 min vs. 24 h, cooldown, invalidación al usarse) difiere. Novena y décima entidad del alcance objetivo del producto en pasar a ratificadas. Nuevos índices `ix_password_reset_tokens_user_id_created_at`/`ix_email_verification_tokens_user_id_created_at` (§8). Tres migraciones nuevas y consecutivas: `b8d4f2a917c3` (columna), `c1f6a83d2e59`/`d3a9c47b1f68` (tablas). Verificado con `flask db upgrade`/`downgrade` contra PostgreSQL 16 real y la suite completa de pruebas (`backend/tests/`, 175 pruebas).
>
> **v0.12 — notificaciones, `notifications` (`ADR-008-notifications-minimal-model.md`):** "Likes, Comentarios, Respuestas, Nuevos seguidores, Menciones, Mensajes, Actividad relevante" (§4.B › Notificaciones) pasa **parcialmente** de candidata objetivo a **implementada** (§4.A, §5.6) — solo los tres eventos que el backend ya genera hoy (`like`, `comment`, `follow`); respuestas, menciones y mensajes siguen sin ratificar porque las entidades de las que dependen (hilos de comentarios, `mentions`, `conversations`) tampoco existen todavía. Nueva tabla `notifications`: `recipient_id`/`actor_id` (FKs a `users`, ambas `ON DELETE CASCADE`), `type` (`VARCHAR(20)`, discriminador validado en la aplicación, no `ENUM` de PostgreSQL), `post_id` (FK a `posts`, `ON DELETE CASCADE`, nullable — solo aplica a `like`/`comment`), `read_at` (`TIMESTAMPTZ`, nullable, `NULL` = no leída), sin `updated_at` (mismo criterio que `likes`/`follows`: se crea o se marca leída, nunca se edita de otro modo). Sin `UNIQUE` — a diferencia de `likes`/`follows`, dos notificaciones del mismo tipo/actor/post en momentos distintos son eventos legítimos, no un duplicado a impedir. Nuevo índice compuesto `ix_notifications_recipient_id_created_at` (§8). Octava relación real entre entidades (§6): `notifications.recipient_id → users.id`, `notifications.actor_id → users.id`, `notifications.post_id → posts.id`. Verificado con 21 pruebas nuevas + la suite completa (145/145, ejecutada contra PostgreSQL 16 real, incluido un ciclo de `flask db upgrade` sobre `thers_dev` y `thers_test`), más una prueba manual end-to-end contra el backend real.

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
| `users` | **IMPLEMENTADA** (ratificada; definición formal en §5; en uso real por `register`/`login`/`GET /api/users/me`/`PATCH /api/users/me`) | Registro persiste `name`/`username`/`email`/`phone`/`country_code`/`birth_date`/`password_hash` reales (columnas de perfil ratificadas por `ADR-002`, v0.5); login autentica consultando `users` por `email`; `PATCH /api/users/me` (`ADR-003`, v0.6) actualiza `name`/`username`/`phone`/`country_code`/`birth_date`, con `username_changed_at` sosteniendo el cooldown de `username`; el backend devuelve el objeto público completo (§5) con datos reales |
| `posts` | **IMPLEMENTADA — v0.8** (ratificada por `ADR-004-posts-minimal-model.md`; definición formal en §5; en uso real por `POST`/`GET /api/posts`) | Primera entidad de la capa objetivo (§4.B, "Contenido") en pasar a implementada. Modelo deliberadamente mínimo: `author_id` (FK a `users`) y `content` (texto, máximo 2000 caracteres) — sin `visibility`, sin medios, sin ningún otro campo que §4.B seguía listando para "Contenido" |
| `likes` | **IMPLEMENTADA — v0.9** (ratificada por `ADR-005-likes-minimal-model.md`; definición formal en §5; en uso real por `POST`/`DELETE /api/posts/<id>/like`, agregada en `GET`/`POST /api/posts`) | Segunda entidad de la capa objetivo (§4.B, "Interacciones") en pasar a implementada, solo en su versión mínima binaria (like/no-like). Modelo: `post_id`+`user_id` (FKs, `UNIQUE` compuesta) — sin tipos de reacción, sin listar quién dio like |
| `comments` | **IMPLEMENTADA — v0.10** (ratificada por `ADR-006-comments-minimal-model.md`; definición formal en §5; en uso real por `POST`/`GET /api/posts/<id>/comments`, agregada en `GET`/`POST /api/posts`) | Tercera entidad de la capa objetivo (§4.B, "Interacciones") en pasar a implementada, solo en su mitad plana. Modelo: `post_id`+`author_id` (FKs) y `content` (texto, máximo 1000 caracteres) — sin `parent_comment_id`, sin hilos de respuestas |
| `follows` | **IMPLEMENTADA — v0.11** (ratificada por `ADR-007-follows-minimal-model.md`; definición formal en §5; en uso real por `POST`/`DELETE /api/users/<id>/follow`, agregada en `GET`/`PATCH /api/users/me` y en `GET`/`POST /api/posts`) | Cuarta entidad de la capa objetivo (§4.B, "Relaciones sociales") en pasar a implementada. Modelo: `follower_id`+`followed_id` (FKs, `UNIQUE` compuesta, primera `CHECK` del esquema) — sin listar seguidores/seguidos, sin personalizar el feed |
| `notifications` | **IMPLEMENTADA — v0.12** (ratificada por `ADR-008-notifications-minimal-model.md`; definición formal en §5; en uso real por `GET /api/notifications`/`PATCH /api/notifications/<id>/read`, generada como efecto secundario de `POST /api/posts/<id>/like`, `POST /api/posts/<id>/comments` y `POST /api/users/<id>/follow`) | Quinta entidad de la capa objetivo (§4.B, "Notificaciones") en pasar a implementada, solo para los tipos `like`/`comment`/`follow`. Modelo: `recipient_id`+`actor_id` (FKs a `users`), `type` (discriminador), `post_id` (FK a `posts`, nullable), `read_at` (nullable) — sin respuestas/menciones/mensajes, sin push/email, sin preferencias configurables |
| `password_reset_tokens` | **IMPLEMENTADA — v0.14** (reescrita por `ADR-010-password-reset-otp-flow.md`, reemplaza la v0.13 de `ADR-009-password-reset-and-email-verification.md`; definición formal en §5; en uso real por `POST /api/forgot-password`/`POST /api/verify-reset-code`/`POST /api/reset-password`) | Sexta entidad de la capa objetivo (§4.B, "Autenticación y cuenta"). Modelo: `user_id` (FK a `users`), `code_hash` (scrypt del código OTP de 6 dígitos), `attempts`, `expires_at`, `verified_at` (nullable), `reset_authorization_hash`/`_expires_at` (nullable), `used_at` (nullable) — código de un solo uso (10 min), autorización temporal de propósito específico tras verificarlo (10 min), máximo 5 intentos, a lo sumo una solicitud activa por usuario (índice único parcial) |
| `email_verification_tokens` | **IMPLEMENTADA — v0.15** (reescrita por `ADR-011-mandatory-email-verification.md`, reemplaza la v0.13 de `ADR-009-password-reset-and-email-verification.md`; definición formal en §5; en uso real por `POST /api/register`/`POST /api/verify-registration-code`/`POST /api/resend-registration-code`) | Séptima entidad de la capa objetivo (§4.B, "Autenticación y cuenta"). Modelo: `user_id` (FK a `users`), `code_hash` (scrypt del código OTP de 6 dígitos), `attempts`, `expires_at`, `used_at` (nullable) — código de un solo uso (10 min), máximo 5 intentos, a lo sumo un código activo por usuario (índice único parcial); sin columnas de autorización temporal, a diferencia de `password_reset_tokens` — verificar el código ya es la acción final |
| `user_identities` | **IMPLEMENTADA — v0.16** (ratificada por `ADR-012-google-sign-in.md`; definición formal en §5.9; en uso real por `POST /api/auth/google`) | Octava entidad de la capa objetivo (§4.B, "Autenticación y cuenta", candidata `oauth_accounts`). Modelo: `user_id` (FK a `users`), `provider` (string libre, `"google"` hoy), `provider_subject` (el claim `sub`, único junto con `provider`) — un usuario puede tener varias identidades vinculadas a la vez (account linking); preparada para Apple/Microsoft sin otra migración de `users` |
| `messages` | **IMPLEMENTADA — v0.17** (ratificada por `ADR-013-messages-minimal-model.md`; definición formal en §5.10; en uso real por `POST`/`GET /api/users/<id>/messages`, `GET /api/conversations`) | Novena entidad de la capa objetivo (§4.B, "Mensajería") en pasar a implementada, solo su mitad 1:1 — sin `conversation_participants`, sin grupos. Modelo: `sender_id`+`recipient_id` (FKs a `users`), `content` (texto), `read_at` (nullable) — sin fotos/archivos adjuntos, sin tiempo real (polling desde el Frontend) |

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
| Login con Google | ~~Entidad `oauth_accounts` **o** columnas de proveedor en `users`~~ — **resuelto en v0.16** (`ADR-012-google-sign-in.md`, ver §4.A/§5.9): entidad separada, `user_identities` | IMPLEMENTADA | — |
| Verificación de correo, Recuperación de contraseña | ~~Tabla(s) de tokens de un solo uso~~ — **resuelto en v0.13** (`ADR-009-password-reset-and-email-verification.md`, ver §4.A/§5.7/§5.8): dos tablas, `password_reset_tokens`/`email_verification_tokens` | IMPLEMENTADA | — |
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
| Edición del perfil | Comportamiento (UPDATE sobre `users`, `PATCH /api/users/me`) | **IMPLEMENTADA** (v0.6, `ADR-003`) — solo `name`/`username`/`phone`/`country_code`/`birth_date`; `email`/`password` excluidos por decisión explícita del ADR | — |

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
| Posts (solo texto) | Entidad `posts` (`author_id` → `users`, ver §6) | **IMPLEMENTADA — v0.8** (`ADR-004`, §4.A/§5) | — |
| Fotos, Videos, Reels | Entidad `media` ligada a `posts` (con tipo) **o** tablas separadas | PENDIENTE DE DECISIÓN | Tabla de medios con discriminador vs tablas por tipo; "reel" ¿es tipo de video o entidad propia? |
| Editar / Eliminar publicaciones | Comportamientos + columnas (`updated_at`, borrado lógico) sobre `posts` | PENDIENTE DE DECISIÓN | Política de borrado lógico vs físico |
| Compartir publicaciones | Entidad de *repost* **vs** evento **vs** compartir externo | PENDIENTE DE DECISIÓN | La semántica de "compartir" (interno/externo) no está definida |
| Visibilidad de publicaciones | Columna `visibility` (enum) en `posts` | OBJETIVO | Estrategia de enum pendiente (§7) |

#### Interacciones
| Requisito funcional | Forma candidata | Estado | Por qué aún requiere decisión |
|---|---|---|---|
| Likes / reacciones | ~~Entidad `reactions` (N:N usuario↔post, con tipo) — colapsa "like" y "reacción"~~ — **resuelto en v0.9 para el caso binario** (`ADR-005-likes-minimal-model.md`, tabla `likes`, ver §4.A/§5.3); la forma general "con tipo" (❤️/👍/😂/etc.) sigue sin ratificar | OBJETIVO (tipos de reacción) / IMPLEMENTADA (binario) | Modelado de tipos de reacción sin decidir |
| Comentarios + Respuestas a comentarios | ~~Entidad única `comments`~~ — **la mitad plana resuelta en v0.10** (`ADR-006-comments-minimal-model.md`, ver §4.A/§5.4); auto-referencial (respuesta = comentario con `parent_comment_id`) sigue sin ratificar | OBJETIVO (respuestas) / IMPLEMENTADA (comentario plano) | Modelado de `parent_comment_id`/hilos sin decidir |
| Guardar publicaciones | Tabla puente `saves` (usuario↔post) | OBJETIVO | — |
| Menciones | Tabla puente `mentions` **o** parseo en render sin persistir | PENDIENTE DE DECISIÓN | Persistir vs derivar en lectura, no decidido |
| Hashtags | Entidad `hashtags` + puente `post_hashtags` (N:N) | OBJETIVO | Modelado sin decidir |
| Compartir | = ver Contenido › Compartir publicaciones | PENDIENTE DE DECISIÓN | Misma decisión abierta |

#### Relaciones sociales
| Requisito funcional | Forma candidata | Estado | Por qué aún requiere decisión |
|---|---|---|---|
| Seguir, Dejar de seguir, Seguidores, Seguidos | ~~**Una** tabla puente `follows` (auto-referencial `users`↔`users`) — las cuatro funciones son la misma estructura~~ — **resuelto en v0.11** (`ADR-007-follows-minimal-model.md`, ver §4.A/§5.5): seguir/dejar de seguir y los contadores; listar seguidores/seguidos sigue sin ratificar | IMPLEMENTADA (seguir/contar) / PENDIENTE (listar) | Listar seguidores/seguidos sin decidir |
| Bloquear usuarios | Tabla puente `blocks` (auto-referencial) | OBJETIVO | — |
| Restringir usuarios | Tabla puente `restrictions` **o** atributo de la relación social | PENDIENTE DE DECISIÓN | La semántica de "restringir" vs "bloquear" está por definir |

#### Mensajería
| Requisito funcional | Forma candidata | Estado | Por qué aún requiere decisión |
|---|---|---|---|
| Conversaciones grupales, Participantes | `conversations` + puente `conversation_participants` | OBJETIVO | Modelado sin decidir — la mitad 1:1 se resolvió sin esta tabla (ver fila de abajo), grupos siguen pendientes |
| Mensajes (1:1) | ~~Entidad `messages`~~ — **resuelto en v0.17** (`ADR-013-messages-minimal-model.md`, ver §4.A/§5.10): `sender_id`/`recipient_id` directos, sin tabla `conversations` | IMPLEMENTADA | — |
| Fotos/videos en mensajes | `message_media` **o** reutilizar `media` | PENDIENTE DE DECISIÓN | Reutilización vs entidad propia |
| Estado leído/no leído | ~~Columna `last_read_at` en participante **o** tabla `message_reads`~~ — **resuelto en v0.17**: `messages.read_at` por mensaje individual (no por conversación) | IMPLEMENTADA | — |

#### Notificaciones
| Requisito funcional | Forma candidata | Estado | Por qué aún requiere decisión |
|---|---|---|---|
| Likes, Comentarios, Nuevos seguidores | ~~**Una** entidad `notifications` con discriminador de tipo — no una tabla por tipo~~ — **resuelto en v0.12** (`ADR-008-notifications-minimal-model.md`, ver §4.A/§5.6) para estos tres eventos | IMPLEMENTADA | — |
| Respuestas (a comentarios), Menciones, Actividad relevante | Misma entidad `notifications`, tipos adicionales | PENDIENTE DE DECISIÓN | Dependen de que existan primero las entidades de origen (`parent_comment_id`/hilos, `mentions`) — ninguna está ratificada todavía |
| Mensajes nuevos | Misma entidad `notifications`, tipo `'message'` | PENDIENTE DE DECISIÓN | `messages` ya existe (v0.17, `ADR-013`) — lo que falta es una decisión de producto explícita sobre si un mensaje nuevo debe generar notificación además de aparecer en `GET /api/conversations`, no una entidad faltante |

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

## 5. Entidades ratificadas

> **v0.8 — `posts` se suma a `users`** como segunda entidad con definición formal (capa 4.A, `ADR-004-posts-minimal-model.md`). El resto sigue en §4.B (objetivo) y §14 (pendientes).

### 5.1 `users`

**Propósito.** Representar a una persona registrada en THERS y ser la fuente de verdad para autenticación — rol que ya cumple en producción de código desde v0.3 (`register`/`login` reales, `BACKEND_ARCHITECTURE.md` §8/§9).

**Atributos principales**

| Columna | Tipo (conceptual) | Nulo | Justificación / origen |
|---|---|---|---|
| `id` | **UUID** | No | Clave primaria. `id UUID PRIMARY KEY DEFAULT gen_random_uuid()` — el valor se genera **en PostgreSQL** (`gen_random_uuid()`, función nativa desde PostgreSQL 13, no requiere `pgcrypto`/`uuid-ossp`), no en Python. Implementado en `app/infrastructure/persistence/models.py` (`sqlalchemy.dialects.postgresql.UUID(as_uuid=True)`, `server_default=text("gen_random_uuid()")`) y en la migración `a1b2c3d4e5f6_create_users_table.py` |
| `name` | `VARCHAR(120)` | No | Campo `name` recolectado en `Register.jsx`; devuelto por el backend |
| `username` | `VARCHAR(30)`, **UNIQUE** (`uq_users_username`) | No | **v0.5 (`ADR-002`).** Campo `username` recolectado en `Register.jsx`; formato `^[a-zA-Z0-9_]{3,20}$` validado en `domain/auth/validators.py`. A diferencia de `email`, **no** usa `CITEXT` — comparación case-sensitive, decisión explícita (`ADR-002` §3): ningún flujo hoy (login sigue siendo por email) requiere case-insensitivity para username |
| `phone` | `VARCHAR(20)` | **Sí** desde v0.16 | **v0.5 (`ADR-002`).** Campo `phone` recolectado en `Register.jsx` (`PhoneField`); validación laxa de 7–15 dígitos tras limpiar separadores. **v0.16 (`ADR-012-google-sign-in.md`):** pasa a nullable — Google no lo entrega; el registro tradicional sigue exigiéndolo siempre a nivel de route, así que nunca queda en `NULL` para una cuenta creada así |
| `country_code` | `VARCHAR(6)` | **Sí** desde v0.16 | **v0.5 (`ADR-002`).** Campo `countryCode` recolectado en `Register.jsx` (`PhoneField`, p. ej. `+503`); formato `^\+[1-9]\d{0,3}$`. **v0.16:** mismo motivo que `phone` — nullable, Google no lo entrega |
| `birth_date` | `DATE` | **Sí** desde v0.16 | **v0.5 (`ADR-002`).** Campo `birthDate` recolectado en `Register.jsx` (`BirthDateField`, ISO `yyyy-mm-dd`); edad mínima 13 años validada en el backend (mismo placeholder que ya usaba el Frontend, `dateUtils.js` `MIN_AGE_YEARS`). **v0.16:** mismo motivo — nullable, Google no lo entrega |
| `password_hash` | `TEXT` | **Sí** desde v0.16 | Deriva del campo `password` del registro. **Nunca se guarda en claro** — se almacena el hash (necesidad técnica evidente; §11). **v0.16 (`ADR-012`):** pasa a nullable — una cuenta creada exclusivamente vía "Continuar con Google" no tiene contraseña local; `NULL` significa exactamente eso, nunca un valor inventado |
| `username_changed_at` | `TIMESTAMPTZ` | **Sí** | **v0.6 (`ADR-003`).** Marca de tiempo del último cambio de `username` vía `PATCH /api/users/me`; `NULL` significa "nunca cambió su username". Sostiene la regla de cooldown de 30 días (`domain/auth/username_policy.py`) — no se reutiliza `updated_at` porque esa cambia con cualquier campo, no solo con `username`. Nunca se expone en la API pública (`API_CONTRACT.md` §5). **v0.16:** el username provisorio de una cuenta Google nunca toca esta columna (se queda en `NULL`) hasta que la persona elige uno propio en "Complete your profile" — esa primera elección real nunca choca con el cooldown |
| `email_verified` | `BOOLEAN`, `DEFAULT false` | No | **v0.13 (`ADR-009-password-reset-and-email-verification.md`).** `false` en toda cuenta hasta completar la verificación (reescrito a OTP en `ADR-011`, v0.15). **v0.16 (`ADR-012`):** una cuenta creada vía Google nace en `true` directamente (la garantía de Google reemplaza al OTP); también puede pasar de `false` a `true` al vincular Google con una cuenta tradicional nunca verificada (account linking, `ADR-012` §Decisión) |
| `profile_completed` | `BOOLEAN`, `DEFAULT true` | No | **v0.16 (`ADR-012-google-sign-in.md`).** `true` para toda cuenta existente antes de esta migración y para todo registro tradicional (siempre exige `phone`/`country_code`/`birth_date`); una cuenta nueva vía Google nace en `false` hasta completar esos tres campos vía `PATCH /api/users/me`. Nunca vuelve a `false` una vez en `true` |
| `created_at` | `TIMESTAMPTZ`, `DEFAULT now()` | No | Convención de auditoría (§7); estándar para toda entidad |
| `updated_at` | `TIMESTAMPTZ`, `DEFAULT now()`, mantenida por trigger | No | Convención de auditoría (§7). Un trigger de PostgreSQL (`set_updated_at`/`trg_users_updated_at`, ver migración) la actualiza en cada `UPDATE` — funciona igual vía ORM o SQL directo, no depende de que el código de aplicación la toque |

**Clave primaria (PK).** `id`.

**Claves foráneas (FK).** Ninguna en esta versión — `users` no depende de otra entidad todavía.

**Relaciones.** `posts.author_id → users.id` (v0.7, ver §5.2/§6) — `users` es la entidad referenciada, nunca al revés. `user_identities.user_id → users.id` (v0.16, ver §5.9/§6) — mismo patrón. Cuando existan más entidades sociales (`follows`, etc.), seguirán el mismo patrón.

**Constraints relevantes**
- `email` **UNIQUE** (case-insensitive, vía `CITEXT`) y **NOT NULL** — el login identifica al usuario por email; dos cuentas no pueden compartirlo, ni siquiera con distinto casing. (Justifica también el índice de §8.)
- `name` **NOT NULL** — el formulario lo exige (`isValid` requiere `name.trim()`).
- `password_hash` **NOT NULL hasta v0.15, nullable desde v0.16** (`ADR-012-google-sign-in.md`) — ver tabla de arriba.

**`confirm_password`** se valida en la route (`interfaces/routes/auth_routes.py`, debe coincidir con `password`) y **nunca se persiste** — no existe como columna de `users`, ni siquiera transitoriamente.

**Decisiones sobre esta entidad marcadas como PENDIENTES** (§14): algoritmo de hashing definitivo (sigue usándose `werkzeug.security`/scrypt, ya en uso para la credencial de prueba — ver `BACKEND_ARCHITECTURE.md` §9). **Ya resueltos:** tipo de PK (UUID, `gen_random_uuid()`), tipo de `email` (`CITEXT`), longitud de `name` (`VARCHAR(120)`), tipo de `password_hash` (`TEXT`), estrategia de `updated_at` (trigger), desde v0.5 también `username`/`phone`/`country_code`/`birth_date` (`ADR-002`), y desde v0.6 `username_changed_at` (`ADR-003`) — ver tabla arriba.

> **Actualización v0.2 — reconciliación con el alcance objetivo.** El alcance funcional confirmado por el equipo incorporó `username`, `avatar_url` y `bio` como **columnas OBJETIVO** de `users` (§4.B › Perfil), pendientes de ADR. **Actualización v0.5:** `username` (junto con `phone`/`country_code`/`birth_date`, no anticipadas en v0.2) ya se ratificaron e implementaron por `ADR-002-user-profile-fields.md` — ver tabla arriba. **Actualización v0.6:** `username_changed_at` se ratificó e implementó por `ADR-003-profile-update-contract.md`, exclusivamente como soporte de la regla de cooldown de `PATCH /api/users/me` — no era una columna candidata previa en §4.B. `avatar_url`/`bio` siguen como columnas OBJETIVO, sin ADR propio todavía.

---

### 5.2 `posts`

> Segunda entidad con definición formal (capa 4.A), ratificada por `ADR-004-posts-minimal-model.md` — deliberadamente mínima: solo lo indispensable para que el feed deje de ser mock. Reacciones, comentarios, hashtags, medios, mood, ubicación, edición/borrado, visibilidad **no** están en esta entidad — cada uno es su propia candidata en §4.B, a resolver en un ADR futuro y acotado (mismo patrón que este).

**Propósito.** Un post de texto publicado por un usuario autenticado — primera pieza real de contenido del producto, más allá de la cuenta/perfil.

**Atributos principales**

| Columna | Tipo (conceptual) | Nulo | Justificación / origen |
|---|---|---|---|
| `id` | **UUID** | No | Clave primaria, `DEFAULT gen_random_uuid()` en PostgreSQL — mismo patrón que `users.id` |
| `author_id` | **UUID**, FK → `users.id` | No | Autor del post. Siempre resuelto desde `get_jwt_identity()` en el backend, nunca aceptado del body (`ADR-004` §Contrato, mismo principio anti mass-assignment que `PATCH /api/users/me`) |
| `content` | `TEXT` | No | Sin límite de longitud a nivel de esquema — la validación de negocio (máximo 2000 caracteres, placeholder revisable) vive en `domain/posts/validators.py`, no en el tipo de columna |
| `created_at` | `TIMESTAMPTZ`, `DEFAULT now()` | No | Define el orden del feed (`GET /api/posts`, `ORDER BY created_at DESC`) |
| `updated_at` | `TIMESTAMPTZ`, `DEFAULT now()`, mantenida por trigger | No | Convención de auditoría (§7), mismo trigger `set_updated_at()` reutilizado de `users` — sin uso funcional todavía porque no hay edición de posts (`ADR-004` §No objetivos) |

**Clave primaria (PK).** `id`.

**Claves foráneas (FK).** `author_id → users.id`, `ON DELETE CASCADE` — placeholder razonable dado que borrado de cuenta tampoco existe todavía como funcionalidad (§4.B, "Gestión/desactivación/eliminación de cuenta", `PENDIENTE DE DECISIÓN`); revisar esta política cuando esa funcionalidad se ratifique (`ADR-004` §Riesgos).

**Relaciones.** `users (1) ←→ (N) posts` — un usuario puede tener muchos posts; cada post tiene exactamente un autor.

**Constraints relevantes**
- `author_id` **NOT NULL** — todo post tiene autor, sin excepción.
- `content` **NOT NULL** — la validación de "no vacío tras trim()" vive en la capa de aplicación (`domain/posts/validators.py`), no como `CHECK` de PostgreSQL en esta versión.

**Decisiones sobre esta entidad marcadas como PENDIENTES** (§14, `ADR-004` §Decisiones pendientes): índice compuesto por `author_id` (si en el futuro se necesita filtrar por autor — hoy `GET /api/posts` no filtra), `CHECK` de longitud máxima a nivel de esquema (hoy solo aplicación), política `ON DELETE` definitiva (depende de la decisión de borrado de cuenta).

---

### 5.3 `likes`

> Tercera entidad con definición formal (capa 4.A), ratificada por `ADR-005-likes-minimal-model.md` — resuelve únicamente el caso binario like/no-like de la candidata `reactions` (§4.B). Tipos de reacción, notificaciones y listar quién dio like **no** están en esta entidad — quedan para un ADR futuro si el producto los necesita.

**Propósito.** Registra que un usuario le dio "me gusta" a un post — tabla puente N:N entre `users` y `posts`, sin ningún atributo más allá de quién/qué/cuándo.

**Atributos principales**

| Columna | Tipo (conceptual) | Nulo | Justificación / origen |
|---|---|---|---|
| `id` | **UUID** | No | Clave primaria, `DEFAULT gen_random_uuid()` — mismo patrón que `users.id`/`posts.id` |
| `post_id` | **UUID**, FK → `posts.id` | No | Post likeado |
| `user_id` | **UUID**, FK → `users.id` | No | Quién dio el like. Siempre resuelto desde `get_jwt_identity()`, nunca aceptado del body (mismo principio anti mass-assignment que `posts.author_id`) |
| `created_at` | `TIMESTAMPTZ`, `DEFAULT now()` | No | Auditoría — sin uso funcional todavía (no hay orden ni listado de likes en esta versión) |

**Sin `updated_at`.** A diferencia de `users`/`posts`, un like no se edita in place — se crea o se borra, nunca se actualiza (`ADR-005` §Modelo de datos).

**Clave primaria (PK).** `id`.

**Claves foráneas (FK).** `post_id → posts.id` y `user_id → users.id`, ambas `ON DELETE CASCADE` — mismo placeholder que `ADR-004` ya aceptó para `posts.author_id` (borrado de cuenta/post tampoco existe todavía como funcionalidad).

**Relaciones.** `users (1) ←→ (N) likes ←→ (N) 1) posts` — tabla puente N:N entre `users` y `posts`.

**Constraints relevantes**
- `post_id`/`user_id` **NOT NULL** — todo like tiene post y usuario, sin excepción.
- `UNIQUE (post_id, user_id)` (`uq_likes_post_user`) — un usuario no puede likear el mismo post dos veces; también sostiene la idempotencia de `POST /api/posts/<id>/like` (`ADR-005` §Decisión).

**Decisiones sobre esta entidad marcadas como PENDIENTES** (§14, `ADR-005` §Decisiones pendientes): tipos de reacción más allá del binario, tabla/columna de notificaciones asociadas, forma de exponer quién dio like (si el producto lo necesita).

---

### 5.4 `comments`

> Cuarta entidad con definición formal (capa 4.A), ratificada por `ADR-006-comments-minimal-model.md` — resuelve solo la mitad plana de la candidata combinada "Comentarios + Respuestas" (§4.B). `parent_comment_id`/hilos de respuestas **no** están en esta entidad — quedan para un ADR futuro si el producto los necesita.

**Propósito.** Un comentario de texto plano sobre un post, publicado por un usuario autenticado.

**Atributos principales**

| Columna | Tipo (conceptual) | Nulo | Justificación / origen |
|---|---|---|---|
| `id` | **UUID** | No | Clave primaria, `DEFAULT gen_random_uuid()` — mismo patrón que `users.id`/`posts.id` |
| `post_id` | **UUID**, FK → `posts.id` | No | Post comentado |
| `author_id` | **UUID**, FK → `users.id` | No | Autor del comentario. Siempre resuelto desde `get_jwt_identity()`, nunca aceptado del body (mismo principio anti mass-assignment que `posts.author_id`) |
| `content` | `TEXT` | No | Sin límite de longitud a nivel de esquema — la validación de negocio (máximo 1000 caracteres, placeholder revisable, más corto que el de `posts`) vive en `domain/comments/validators.py` |
| `created_at` | `TIMESTAMPTZ`, `DEFAULT now()` | No | Define el orden del hilo (cronológico ascendente, a diferencia del feed) |
| `updated_at` | `TIMESTAMPTZ`, `DEFAULT now()`, mantenida por trigger | No | Convención de auditoría (§7), mismo trigger `set_updated_at()` reutilizado de `users`/`posts` — sin uso funcional todavía porque no hay edición de comentarios (`ADR-006` §No objetivos) |

**Clave primaria (PK).** `id`.

**Claves foráneas (FK).** `post_id → posts.id` y `author_id → users.id`, ambas `ON DELETE CASCADE` — mismo placeholder que `ADR-004`/`ADR-005` ya aceptaron (borrado de cuenta/post no existe todavía como funcionalidad).

**Relaciones.** `posts (1) ←→ (N) comments` y `users (1) ←→ (N) comments` — un post puede tener muchos comentarios, un usuario puede escribir muchos comentarios; cada comentario tiene exactamente un post y un autor.

**Constraints relevantes**
- `post_id`/`author_id` **NOT NULL** — todo comentario tiene post y autor, sin excepción.
- `content` **NOT NULL** — la validación de "no vacío tras trim()" vive en la capa de aplicación, no como `CHECK` de PostgreSQL en esta versión.

**Decisiones sobre esta entidad marcadas como PENDIENTES** (§14, `ADR-006` §Decisiones pendientes): `parent_comment_id` (hilos de respuestas), edición/borrado, `CHECK` de longitud máxima a nivel de esquema, política `ON DELETE` definitiva.

---

### 5.5 `follows`

> Quinta entidad con definición formal (capa 4.A), ratificada por `ADR-007-follows-minimal-model.md` — primera relación auto-referencial (`users`↔`users`) del esquema. Listar seguidores/seguidos, notificaciones y personalizar el feed **no** están en esta entidad — quedan para un ADR futuro si el producto los necesita.

**Propósito.** Registra que un usuario sigue a otro — tabla puente N:N auto-referencial sobre `users`, sin ningún atributo más allá de quién/a quién/cuándo.

**Atributos principales**

| Columna | Tipo (conceptual) | Nulo | Justificación / origen |
|---|---|---|---|
| `id` | **UUID** | No | Clave primaria, `DEFAULT gen_random_uuid()` — mismo patrón que el resto de entidades |
| `follower_id` | **UUID**, FK → `users.id` | No | Quién sigue. Siempre resuelto desde `get_jwt_identity()`, nunca aceptado del body |
| `followed_id` | **UUID**, FK → `users.id` | No | A quién se sigue. Viene de la URL (`user_id`), nunca del body |
| `created_at` | `TIMESTAMPTZ`, `DEFAULT now()` | No | Auditoría — sin uso funcional todavía (no hay orden ni listado de follows en esta versión) |

**Sin `updated_at`.** Igual que `likes` (`ADR-005` §Modelo de datos): una relación de "seguir" se crea o se borra, nunca se edita in place.

**Clave primaria (PK).** `id`.

**Claves foráneas (FK).** `follower_id → users.id` y `followed_id → users.id`, ambas `ON DELETE CASCADE` — mismo placeholder que el resto de entidades (borrado de cuenta no existe todavía como funcionalidad).

**Relaciones.** `users (1) ←→ (N) follows ←→ (N) 1) users` — tabla puente N:N auto-referencial: un usuario puede seguir a muchos, y ser seguido por muchos.

**Constraints relevantes**
- `follower_id`/`followed_id` **NOT NULL** — todo follow tiene ambos lados, sin excepción.
- `UNIQUE (follower_id, followed_id)` (`uq_follows_follower_followed`) — un usuario no puede seguir dos veces al mismo usuario; sostiene la idempotencia de `POST /api/users/<id>/follow`.
- `CHECK (follower_id <> followed_id)` (`ck_follows_no_self_follow`) — **primera `CHECK` constraint del esquema**: un usuario no puede seguirse a sí mismo, impuesto a nivel de motor y no solo en la aplicación (`DATABASE_ARCHITECTURE.md` §3, "la base de datos como última línea de defensa").

**Decisiones sobre esta entidad marcadas como PENDIENTES** (§14, `ADR-007` §Decisiones pendientes): personalizar el feed por seguidos, listar seguidores/seguidos, notificaciones de "nuevo seguidor", perfiles públicos de otros usuarios.

---

### 5.6 `notifications`

> Sexta entidad con definición formal (capa 4.A), ratificada por `ADR-008-notifications-minimal-model.md` — cubre solo los tres eventos que el backend ya genera: `like`, `comment`, `follow`. Respuestas a comentarios, menciones y mensajes **no** están en esta entidad — dependen de que sus propias entidades de origen se ratifiquen primero.

**Propósito.** Registra que un evento social (like, comentario, follow) generó una notificación para el usuario destinatario — discriminada por `type`, no una tabla por tipo de evento (§4.B › Notificaciones).

**Atributos principales**

| Columna | Tipo (conceptual) | Nulo | Justificación / origen |
|---|---|---|---|
| `id` | **UUID** | No | Clave primaria, `DEFAULT gen_random_uuid()` — mismo patrón que el resto de entidades |
| `recipient_id` | **UUID**, FK → `users.id` | No | Quién recibe la notificación — el autor del post (`like`/`comment`) o el usuario seguido (`follow`) |
| `actor_id` | **UUID**, FK → `users.id` | No | Quién generó el evento. Siempre resuelto desde `get_jwt_identity()` de quien hizo la acción original, nunca aceptado del body |
| `type` | `VARCHAR(20)` | No | Discriminador: `'like'` / `'comment'` / `'follow'`. Validado en `domain/`, no como `ENUM` de PostgreSQL — agregar un tipo nuevo el día de mañana no requiere `ALTER TYPE` (`ADR-008` §Opciones consideradas) |
| `post_id` | **UUID**, FK → `posts.id` | **Sí** | Post de origen — solo aplica a `like`/`comment`; `NULL` en `follow` |
| `read_at` | `TIMESTAMPTZ` | **Sí** | `NULL` = no leída. Se expone en la API como booleano (`read`), nunca como el timestamp crudo (`API_CONTRACT.md` §5) |
| `created_at` | `TIMESTAMPTZ`, `DEFAULT now()` | No | Define el orden de la lista (más reciente primero) |

**Sin `updated_at`.** Igual que `likes`/`follows`: una notificación no se edita in place más allá de marcarse como leída (`read_at`), que tiene su propia semántica de "solo se fija una vez" (`ADR-008` §Contrato API).

**Clave primaria (PK).** `id`.

**Claves foráneas (FK).** `recipient_id → users.id` y `actor_id → users.id` (ambas `ON DELETE CASCADE`, mismo placeholder que el resto de entidades); `post_id → posts.id` (`ON DELETE CASCADE` — si el post se borra, no tiene sentido conservar notificaciones sobre un post inexistente).

**Relaciones.** `users (1) ←→ (N) notifications` (dos veces: como destinatario y como actor) y `posts (1) ←→ (N) notifications` — un post puede generar muchas notificaciones (una por cada like/comentario que recibe), una notificación tiene exactamente un destinatario, un actor, y opcionalmente un post de origen.

**Constraints relevantes**
- `recipient_id`/`actor_id`/`type` **NOT NULL** — toda notificación tiene destinatario, actor y tipo, sin excepción.
- **Sin `UNIQUE`.** A diferencia de `likes`/`follows`, dos notificaciones legítimas pueden compartir destinatario/actor/post/tipo (like → unlike → like genera dos notificaciones reales, `ADR-008` §Opciones consideradas) — no hay una repetición a impedir a nivel de esquema.
- **Sin `CHECK` de auto-notificación.** Ningún endpoint acepta datos para esta tabla directamente del usuario — los tres únicos puntos de creación (`like_post_use_case`, `create_comment_use_case`, `follow_user_use_case`) ya comparan `actor_id`/`recipient_id` en la capa de aplicación antes de crear la fila; no hay superficie de ataque que una `CHECK` adicional esté cerrando (a diferencia de `follows`, donde sí hacía falta como segunda línea de defensa).

**Decisiones sobre esta entidad marcadas como PENDIENTES** (§14, `ADR-008` §Decisiones pendientes): notificaciones push/email, preferencias configurables, tipos adicionales (respuestas, menciones, mensajes — dependen de sus propias entidades), endpoint de "marcar todas como leídas", contador de no leídas como endpoint propio, borrado/expiración, actualización en tiempo real (WebSockets/SSE).

---

### 5.7 `password_reset_tokens`

> Séptima entidad con definición formal (capa 4.A). Ratificada originalmente por `ADR-009-password-reset-and-email-verification.md` (v0.13, flujo de enlace); **reconstruida** por `ADR-010-password-reset-otp-flow.md` (v0.14, flujo de código OTP) — la entidad es la misma, su modelo cambió por completo. Una sola fila cubre las tres etapas del ciclo de vida de una solicitud: creada (código emitido) → verificada (código correcto, autorización emitida) → usada (contraseña cambiada) — no hay una tabla por etapa (`ADR-010` §Decisión).

**Propósito.** Una solicitud de recuperación de contraseña: primero un código de 6 dígitos que el usuario recibe por correo y transcribe de vuelta (`POST /api/forgot-password` → `POST /api/verify-reset-code`), después la autorización temporal que esa verificación emite para el paso final (`POST /api/reset-password`).

**Atributos principales**

| Columna | Tipo (conceptual) | Nulo | Justificación / origen |
|---|---|---|---|
| `id` | **UUID** | No | Clave primaria, `DEFAULT gen_random_uuid()` — mismo patrón que el resto de entidades |
| `user_id` | **UUID**, FK → `users.id` | No | Dueño de la solicitud |
| `code_hash` | **TEXT** | No | Hash **scrypt** (`domain/auth/auth_service.hash_password`, el mismo algoritmo que `users.password_hash`) del código de 6 dígitos — nunca SHA-256: con solo `10^6` combinaciones, un hash rápido no protege nada ante una tabla filtrada (`ADR-010` §Opciones consideradas). `TEXT`, no una longitud fija corta: el formato de salida de scrypt no la tiene |
| `attempts` | **INTEGER**, `DEFAULT 0` | No | Intentos de verificación fallidos contra esta solicitud (`ADR-010` §Seguridad) |
| `expires_at` | `TIMESTAMPTZ` | No | Vigencia del código en sí — 10 minutos desde su creación (`domain/auth/token_policy.PASSWORD_RESET_CODE_TTL_MINUTES`) |
| `verified_at` | `TIMESTAMPTZ` | **Sí** | `NULL` = código todavía no verificado correctamente. Se fija una sola vez, junto con la autorización |
| `reset_authorization_hash` | `VARCHAR(64)` | **Sí** | SHA-256 (`domain/auth/token_generator.hash_token`) de la autorización temporal emitida al verificar el código — a diferencia de `code_hash`, esta sí es alta entropía (256 bits), mismo criterio de hash rápido que ya usaba el token de enlace de v0.13 |
| `reset_authorization_expires_at` | `TIMESTAMPTZ` | **Sí** | Vigencia de la autorización — 10 minutos desde la verificación (`PASSWORD_RESET_AUTHORIZATION_TTL_MINUTES`) |
| `used_at` | `TIMESTAMPTZ` | **Sí** | `NULL` = la contraseña todavía no se cambió con esta solicitud. Se fija una sola vez al consumirse (`reset_password_use_case.py`), nunca se revierte |
| `created_at` | `TIMESTAMPTZ`, `DEFAULT now()` | No | Sostiene el cooldown anti-spam de `POST /api/forgot-password`/"Reenviar código" (`has_recent_unused_code`) |

**Sin `updated_at`.** Mismo criterio que `likes`/`follows`/`notifications`: una solicitud avanza de etapa (creada → verificada → usada) mediante columnas propias, nunca se "edita" en el sentido de un `PATCH` genérico.

**Clave primaria (PK).** `id`.

**Claves foráneas (FK).** `user_id → users.id`, `ON DELETE CASCADE` — mismo placeholder que el resto de entidades.

**Relaciones.** `users (1) ←→ (N) password_reset_tokens` — un usuario puede tener varias solicitudes a lo largo del tiempo (nunca más de una **activa** a la vez, ver constraint de abajo).

**Constraints relevantes**
- `user_id`/`code_hash`/`expires_at` **NOT NULL**.
- **`uq_password_reset_tokens_active_user`** — índice único **parcial**: `UNIQUE (user_id) WHERE used_at IS NULL`. **Primer índice parcial del esquema de THERS.** Garantiza a nivel de motor que nunca hay más de una solicitud activa por usuario, incluso ante dos "Reenviar código" simultáneos (`ADR-010` §Opciones consideradas — condición de carrera) — el repositorio (`infrastructure/persistence/repositories/password_reset_repository.py`) invalida la solicitud activa previa e inserta la nueva; si dos requests concurrentes chocan contra este índice, la que pierde la carrera reintenta (hasta 3 veces) en vez de fallar.
- **Sin `UNIQUE` sobre `code_hash`/`reset_authorization_hash`** (a diferencia de `token_hash` en v0.13) — dos solicitudes distintas del mismo o de distintos usuarios pueden, en teoría, terminar con el mismo código de 6 dígitos (espacio de solo `10^6` valores); el hash con salado de scrypt ya produce salidas distintas igual, pero la unicidad no es una invariante de negocio real acá como sí lo era con un token de 256 bits.

**Decisiones sobre esta entidad marcadas como PENDIENTES** (§14, `ADR-010` §Decisiones pendientes): limpieza periódica de solicitudes vencidas.

---

### 5.8 `email_verification_tokens`

> Octava entidad con definición formal (capa 4.A). Ratificada originalmente por `ADR-009-password-reset-and-email-verification.md` (v0.13, flujo de enlace, sin cambios en v0.14 — solo `password_reset_tokens`, §5.7, se reconstruyó entonces); **reconstruida** por `ADR-011-mandatory-email-verification.md` (v0.15, flujo de código OTP de 6 dígitos, mismo patrón que §5.7) — la entidad es la misma, su modelo cambió por completo. A diferencia de `password_reset_tokens`, verificar el código **es** la acción final: no hay columnas de autorización temporal, el propio acierto ya marca `users.email_verified = true`.

**Propósito.** Un código de verificación de 6 dígitos que confirma que quien se registró controla de verdad la dirección de correo indicada, emitido automáticamente por `POST /api/register` (y reenviado por `POST /api/resend-registration-code`) y consumido por `POST /api/verify-registration-code`.

**Atributos principales**

| Columna | Tipo (conceptual) | Nulo | Justificación / origen |
|---|---|---|---|
| `id` | **UUID** | No | Clave primaria, `DEFAULT gen_random_uuid()` — mismo patrón que el resto de entidades |
| `user_id` | **UUID**, FK → `users.id` | No | Dueño del código |
| `code_hash` | **TEXT** | No | Hash **scrypt** (`domain/auth/auth_service.hash_password`, mismo algoritmo que `users.password_hash` y que `password_reset_tokens.code_hash`) del código de 6 dígitos — nunca SHA-256, mismo motivo que §5.7 (`10^6` combinaciones, un hash rápido no protege nada ante una tabla filtrada) |
| `attempts` | **INTEGER**, `DEFAULT 0` | No | Intentos de verificación fallidos contra este código (`ADR-011` §Seguridad) |
| `expires_at` | `TIMESTAMPTZ` | No | Vigencia del código — 10 minutos desde su creación (`domain/auth/token_policy.REGISTRATION_CODE_TTL_MINUTES`) |
| `used_at` | `TIMESTAMPTZ` | **Sí** | `NULL` = el código todavía no se verificó correctamente. Se fija una sola vez al verificarse (`verify_registration_code_use_case.py`), nunca se revierte |
| `created_at` | `TIMESTAMPTZ`, `DEFAULT now()` | No | Sostiene el cooldown anti-spam de `POST /api/register`/`POST /api/resend-registration-code` (`has_recent_unused_code`) |

**Sin `updated_at`.** Mismo criterio que `password_reset_tokens` (§5.7).

**Clave primaria (PK).** `id`.

**Claves foráneas (FK).** `user_id → users.id`, `ON DELETE CASCADE`.

**Relaciones.** `users (1) ←→ (N) email_verification_tokens` — un usuario puede tener varios códigos a lo largo del tiempo (nunca más de uno **activo** a la vez, ver constraint de abajo); incluye los reintentos de registro sobre una cuenta nunca verificada (`ADR-011` §Decisión, Estrategia A).

**Constraints relevantes**
- `user_id`/`code_hash`/`expires_at` **NOT NULL**.
- **`uq_email_verification_tokens_active_user`** — índice único **parcial**: `UNIQUE (user_id) WHERE used_at IS NULL`. Mismo patrón que `uq_password_reset_tokens_active_user` (§5.7, primer índice parcial del esquema) — garantiza a nivel de motor que nunca hay más de un código activo por usuario, incluso ante dos "Reenviar código" simultáneos o un reintento de registro concurrente; el repositorio (`infrastructure/persistence/repositories/email_verification_repository.py`) invalida el código activo previo e inserta el nuevo, con el mismo reintento (hasta 3 veces) ante `IntegrityError` que `password_reset_repository.py`.
- **Sin `UNIQUE` sobre `code_hash`** — mismo motivo que §5.7: espacio de solo `10^6` combinaciones, no es una invariante de negocio real.
- **Tabla estructuralmente separada de `password_reset_tokens`** (`ADR-011` §Decisión, purpose separation) — no es un discriminador de tipo sobre una tabla compartida: un código de esta tabla nunca es una fila que `verify-reset-code` consulte, ni viceversa, así que el propósito de cada código queda separado por esquema, no solo por convención de aplicación.

**Decisiones sobre esta entidad marcadas como PENDIENTES** (§14, `ADR-011` §Decisiones pendientes): limpieza periódica de códigos vencidos/cuentas nunca verificadas.

---

### 5.9 `user_identities`

> Novena entidad con definición formal (capa 4.A), ratificada por `ADR-012-google-sign-in.md`. Tabla separada de `users` (no columnas `google_sub`/`auth_provider` sueltas ahí) para que agregar Apple/Microsoft más adelante sea una fila nueva con otro `provider`, no una migración de esquema de `users`.

**Propósito.** Vincula una identidad externa (hoy solo Google) a un usuario de THERS. Un usuario puede tener cero, una, o varias identidades vinculadas a la vez -- por ejemplo, password + Google al mismo tiempo (account linking, `ADR-012` §Decisión).

**Atributos principales**

| Columna | Tipo (conceptual) | Nulo | Justificación / origen |
|---|---|---|---|
| `id` | **UUID** | No | Clave primaria, `DEFAULT gen_random_uuid()` — mismo patrón que el resto de entidades |
| `user_id` | **UUID**, FK → `users.id` | No | Usuario de THERS al que pertenece esta identidad |
| `provider` | `VARCHAR(20)` | No | `"google"` hoy -- string libre, no `ENUM` de PostgreSQL, mismo criterio que `notifications.type` (`ADR-008`): discriminador validado en la aplicación |
| `provider_subject` | `TEXT` | No | El claim `sub` del ID Token de Google (identificador estable de la cuenta) -- nunca el email, que en teoría podría cambiar sin que la cuenta de Google deje de ser la misma |
| `created_at` | `TIMESTAMPTZ`, `DEFAULT now()` | No | Auditoría de cuándo se vinculó esta identidad |

**Sin `updated_at`.** Una identidad vinculada no se "edita" -- se crea o, en el futuro, se desvincula (funcionalidad todavía no implementada).

**Clave primaria (PK).** `id`.

**Claves foráneas (FK).** `user_id → users.id`, `ON DELETE CASCADE`.

**Relaciones.** `users (1) ←→ (N) user_identities` — un usuario puede tener varias identidades vinculadas; cada identidad pertenece a exactamente un usuario.

**Constraints relevantes**
- `user_id`/`provider`/`provider_subject` **NOT NULL**.
- **`uq_user_identities_provider_subject`** — índice único: `UNIQUE (provider, provider_subject)`. Garantiza a nivel de motor que la misma cuenta de Google nunca termine vinculada a dos usuarios de THERS a la vez -- defensa de última línea contra la condición de carrera de dos requests simultáneas de `POST /api/auth/google` para una cuenta de Google que todavía no existía en THERS.

**Decisiones sobre esta entidad marcadas como PENDIENTES** (§14, `ADR-012` §Decisiones pendientes): endpoint para listar/desvincular identidades propias; soporte para Apple/Microsoft (la tabla ya está preparada, falta el adaptador correspondiente).

---

### 5.10 `messages`

> Décima entidad con definición formal (capa 4.A), ratificada por `ADR-013-messages-minimal-model.md` — cubre solo la mitad 1:1 de la candidata "Conversaciones + Mensajes" (§4.B › Mensajería): mensaje directo entre dos usuarios reales, sin tabla `conversations`/`conversation_participants`. Una "conversación" es una vista derivada de los mensajes entre dos usuarios (`GET /api/conversations`), no una fila propia.

**Propósito.** Un mensaje de texto directo de un usuario a otro, con su estado de lectura.

**Atributos principales**

| Columna | Tipo (conceptual) | Nulo | Justificación / origen |
|---|---|---|---|
| `id` | **UUID** | No | Clave primaria, `DEFAULT gen_random_uuid()` — mismo patrón que el resto de entidades |
| `sender_id` | **UUID**, FK → `users.id` | No | Quién manda — siempre resuelto desde `get_jwt_identity()`, nunca aceptado del body |
| `recipient_id` | **UUID**, FK → `users.id` | No | Quién recibe — viene de la URL, nunca del body |
| `content` | **TEXT** | No | Sin límite de longitud a nivel de esquema — validado en la aplicación (máximo 2000 caracteres, mismo criterio que `posts`) |
| `read_at` | `TIMESTAMPTZ` | **Sí** | `NULL` = no leído. Se expone en la API como booleano (`read`), nunca como el timestamp crudo — mismo criterio que `notifications.read_at` |
| `created_at` | `TIMESTAMPTZ`, `DEFAULT now()` | No | Define el orden cronológico del hilo |

**Sin `updated_at`.** Igual que `likes`/`follows`/`notifications`: un mensaje no se edita in place más allá de marcarse como leído.

**Clave primaria (PK).** `id`.

**Claves foráneas (FK).** `sender_id → users.id` y `recipient_id → users.id` (ambas `ON DELETE CASCADE`, mismo placeholder que el resto de entidades).

**Relaciones.** `users (1) ←→ (N) messages` (dos veces: como remitente y como destinatario) — un usuario puede mandar y recibir muchos mensajes; cada mensaje tiene exactamente un remitente y un destinatario.

**Constraints relevantes**
- `sender_id`/`recipient_id`/`content` **NOT NULL**.
- **`ck_messages_no_self_message`** — segunda `CHECK` del esquema (`sender_id <> recipient_id`), mismo criterio que `ck_follows_no_self_follow` (§5.5): impide mandarse un mensaje a sí mismo incluso con un `INSERT` directo.
- **Sin `UNIQUE`.** Dos mensajes entre las mismas dos personas son eventos legítimos e independientes, no un duplicado a impedir — mismo criterio que `notifications`.

**Índices.** `ix_messages_sender_recipient_created` (`sender_id`, `recipient_id`, `created_at`) e `ix_messages_recipient_sender_created` (`recipient_id`, `sender_id`, `created_at`) — el hilo entre dos usuarios se busca con un `OR` sobre ambos sentidos de la relación, que ninguna columna única cubre; ambos índices permiten que PostgreSQL resuelva ese `OR` sin escanear la tabla completa (`ADR-013` §Índices).

**Decisiones sobre esta entidad marcadas como PENDIENTES** (§14, `ADR-013` §Decisiones pendientes): conversaciones grupales (`conversation_participants`), fotos/archivos adjuntos, actualización en tiempo real (WebSockets/Flask-SocketIO en vez de polling), borrado de mensajes/conversaciones, confirmación de lectura visible para el remitente ("visto").

---

## 6. Relaciones entre entidades

**v0.8 — primera relación implementada:** `posts.author_id → users.id` (`ADR-004-posts-minimal-model.md`, ver §5.2) — `ON DELETE CASCADE`.

**v0.9 — segunda y tercera relación implementadas:** `likes.post_id → posts.id` y `likes.user_id → users.id` (`ADR-005-likes-minimal-model.md`, ver §5.3), ambas `ON DELETE CASCADE` — `likes` es la primera tabla puente N:N real del esquema.

**v0.10 — cuarta y quinta relación implementadas:** `comments.post_id → posts.id` y `comments.author_id → users.id` (`ADR-006-comments-minimal-model.md`, ver §5.4), ambas `ON DELETE CASCADE`.

**v0.11 — sexta y séptima relación implementadas:** `follows.follower_id → users.id` y `follows.followed_id → users.id` (`ADR-007-follows-minimal-model.md`, ver §5.5), ambas `ON DELETE CASCADE` — primera relación auto-referencial (`users`↔`users`) del esquema. Todo lo demás sigue siendo candidato (§4.B).

**v0.12 — octava, novena y décima relación implementadas:** `notifications.recipient_id → users.id`, `notifications.actor_id → users.id` y `notifications.post_id → posts.id` (`ADR-008-notifications-minimal-model.md`, ver §5.6), todas `ON DELETE CASCADE`. Todo lo demás sigue siendo candidato (§4.B).

**v0.13 — decimoprimera y decimosegunda relación implementadas:** `password_reset_tokens.user_id → users.id` (`ADR-009-password-reset-and-email-verification.md`, ver §5.7) y `email_verification_tokens.user_id → users.id` (ver §5.8), ambas `ON DELETE CASCADE`. Todo lo demás sigue siendo candidato (§4.B).

**v0.16 — decimotercera relación implementada:** `user_identities.user_id → users.id` (`ADR-012-google-sign-in.md`, ver §5.9), `ON DELETE CASCADE`.

**v0.17 — decimocuarta y decimoquinta relación implementadas:** `messages.sender_id → users.id` y `messages.recipient_id → users.id` (`ADR-013-messages-minimal-model.md`, ver §5.10), ambas `ON DELETE CASCADE`. Todo lo demás (conversaciones grupales) sigue siendo candidato (§4.B).

Regla de diseño para cuando existan más entidades (para evitar decisiones improvisadas durante la implementación):
- Las entidades dependientes referencian a `users` y/o `posts` (o a otras entidades ratificadas, cuando corresponda) con una FK.
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
| `ix_posts_created_at` | `posts(created_at)` | **v0.8 (`ADR-004`).** `GET /api/posts` ordena por `created_at DESC` en cada consulta del feed — primer índice justificado por una consulta de una entidad distinta de `users`. |
| `uq_likes_post_user` | `likes(post_id, user_id)`, `UNIQUE` | **v0.9 (`ADR-005`).** Impone la regla de negocio (un usuario no likea el mismo post dos veces) y, por ser `post_id` su columna líder, ya cubre `COUNT(*)`/`IN (...)` por post sin necesitar un índice adicional. |
| `ix_comments_post_id_created_at` | `comments(post_id, created_at)`, compuesto | **v0.10 (`ADR-006`).** `GET /api/posts/<id>/comments` filtra por `post_id` y ordena por `created_at ASC` — la columna líder (`post_id`) cubre además el `COUNT(*)` de `comments_count` sin necesitar un índice adicional. |
| `uq_follows_follower_followed` | `follows(follower_id, followed_id)`, `UNIQUE` | **v0.11 (`ADR-007`).** Impone la regla de negocio (no seguir dos veces al mismo usuario) y cubre `following_count`/`POST .../follow` por ser `follower_id` su columna líder. |
| `ix_follows_followed_id` | `follows(followed_id)` | **v0.11 (`ADR-007`).** `followers_count` y "¿me sigue esta persona?" filtran por `followed_id` — a diferencia de `likes`, esta *no* es la columna líder de la `UNIQUE` de arriba, así que necesita su propio índice o escanearía la tabla completa. |
| `ix_notifications_recipient_id_created_at` | `notifications(recipient_id, created_at)`, compuesto | **v0.12 (`ADR-008`).** `GET /api/notifications` filtra por `recipient_id` (siempre el usuario autenticado) y ordena por `created_at DESC` — la columna líder (`recipient_id`) cubre el filtro sin escanear la tabla completa, mismo patrón que `ix_comments_post_id_created_at`. |
| `ix_messages_sender_recipient_created` / `ix_messages_recipient_sender_created` | `messages(sender_id, recipient_id, created_at)` y `messages(recipient_id, sender_id, created_at)`, ambos compuestos | **v0.17 (`ADR-013`).** El hilo entre dos usuarios (`GET /api/users/<id>/messages`) filtra con `(sender_id=A AND recipient_id=B) OR (sender_id=B AND recipient_id=A)` y ordena por `created_at` — ninguna `UNIQUE` cubre ese acceso (a diferencia de `likes`/`follows`), así que hacen falta ambos índices para que PostgreSQL resuelva el `OR` sin escanear la tabla completa. |
| `ix_password_reset_tokens_user_id_created_at` | `password_reset_tokens(user_id, created_at)`, compuesto | **v0.13 (`ADR-009`), sin cambios en v0.14.** `has_recent_unused_code` filtra por `user_id` y compara `created_at` contra el cooldown. |
| `ix_password_reset_tokens_reset_authorization_hash` | `password_reset_tokens(reset_authorization_hash)` | **v0.14 (`ADR-010`).** `find_valid_by_reset_authorization_hash` busca por este hash en cada `POST /api/reset-password` — reemplaza al índice de `token_hash` de v0.13 (ese lookup ahora es sobre `reset_authorization_hash`, no sobre el código en sí, que ya no admite búsqueda directa por hash al estar salado con scrypt). |
| `uq_password_reset_tokens_active_user` | `password_reset_tokens(user_id)`, `UNIQUE` **parcial** (`WHERE used_at IS NULL`) | **v0.14 (`ADR-010`).** Primer índice parcial del esquema — garantiza a lo sumo una solicitud activa por usuario, defensa de última línea contra la condición de carrera de dos "Reenviar código" simultáneos. |
| `ix_email_verification_tokens_user_id_created_at` | `email_verification_tokens(user_id, created_at)`, compuesto | **v0.13 (`ADR-009`), sin cambios en v0.15.** Mismo criterio que `ix_password_reset_tokens_user_id_created_at`, para el cooldown de `POST /api/register`/`POST /api/resend-registration-code`. |
| `uq_email_verification_tokens_active_user` | `email_verification_tokens(user_id)`, `UNIQUE` **parcial** (`WHERE used_at IS NULL`) | **v0.15 (`ADR-011`), reemplaza a `uq_email_verification_tokens_token_hash` de v0.13.** Mismo criterio que `uq_password_reset_tokens_active_user` — garantiza a lo sumo un código activo por usuario, defensa de última línea contra dos "Reenviar código" simultáneos o un reintento de registro concurrente. |
| `uq_user_identities_provider_subject` | `user_identities(provider, provider_subject)`, `UNIQUE` | **v0.16 (`ADR-012`).** `POST /api/auth/google` busca por (`provider`, `provider_subject`) en cada intento -- garantiza además que la misma cuenta de Google nunca quede vinculada a dos usuarios de THERS a la vez. |
| `ix_user_identities_user_id` | `user_identities(user_id)` | **v0.16 (`ADR-012`).** Lookup de "identidades de este usuario" -- no expuesto por ningún endpoint todavía, preparado para cuando lo esté (p. ej. listar/desvincular proveedores conectados). |

**No se añaden más índices en esta versión.** La PK (`id`) de cada entidad ya está indexada por definición. Cualquier índice adicional (p. ej. `posts(author_id)`, si en el futuro se filtra el feed por autor) se justificará **cuando exista la consulta que lo pague**, no antes.

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

> ✅ **Hallazgo de seguridad resuelto — corregido en v0.7 de este documento.** Versiones anteriores de esta sección advertían `backend/app/config.py` con `JWT_SECRET_KEY = "super-secret-key"` **hardcodeado en el repositorio**. Verificado directamente contra el código real en esta auditoría: `config.py` ya no tiene ningún literal hardcodeado — lee `JWT_SECRET_KEY` de `os.environ.get(...)`, con un valor de desarrollo explícitamente marcado como inseguro (`dev-only-insecure-key-CHANGE-ME`) como único fallback si la variable no está definida, y una advertencia impresa en `stderr` cuando eso ocurre (mismo mecanismo que `BACKEND_ARCHITECTURE.md` §12/§16/§19 ya documentaba como resuelto desde su v0.2). Esta sección quedó desincronizada con esa corrección — ya señalado, sin corregirse, en `ADR-003-profile-update-contract.md` §Estado actual. Sigue **pendiente**, sin cambios: la gestión de secretos para un entorno desplegado (vault, CI/CD) — ver §14.

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
La lista completa de estructuras candidatas del producto objetivo (con su **forma candidata, estado y motivo de decisión**) vive ahora en **§4.B**, para no duplicarla ni arriesgar divergencia. Criterio invariable: **ninguna se implementa sin ratificación por ADR** (`HB-001` §11–12), y su **modelado (PK/FK/tipos) permanece PENDIENTE**. ~~`posts`~~ — **resuelto en v0.8** (`ADR-004-posts-minimal-model.md`, ver §4.A/§5.2): solo su versión mínima de texto; sigue pendiente todo lo demás que §4.B › Contenido listaba junto a ella (`visibility`, edición/borrado, compartir). ~~`reactions` (caso binario)~~ — **resuelto en v0.9** (`ADR-005-likes-minimal-model.md`, ver §4.A/§5.3): solo like/no-like; sigue pendiente la forma general con tipos de reacción. ~~`comments` (mitad plana)~~ — **resuelto en v0.10** (`ADR-006-comments-minimal-model.md`, ver §4.A/§5.4): solo comentar un post; sigue pendiente `parent_comment_id`/hilos de respuestas. ~~`follows`~~ — **resuelto en v0.11** (`ADR-007-follows-minimal-model.md`, ver §4.A/§5.5): seguir/dejar de seguir y contadores; sigue pendiente listar seguidores/seguidos. ~~`notifications`~~ — **resuelto en v0.12** (`ADR-008-notifications-minimal-model.md`, ver §4.A/§5.6): solo los tipos `like`/`comment`/`follow`; sigue pendiente todo lo demás (respuestas, menciones, mensajes, push/email, preferencias, "marcar todas como leídas", borrado). ~~`password_reset_tokens`/`email_verification_tokens`~~ — **resuelto en v0.13** (`ADR-009-password-reset-and-email-verification.md`, ver §4.A/§5.7/§5.8); `password_reset_tokens` **reconstruida en v0.14** (`ADR-010-password-reset-otp-flow.md`, mismo §5.7 actualizado) y `email_verification_tokens` **reconstruida en v0.15** (`ADR-011-mandatory-email-verification.md`, mismo §5.8 actualizado), ambas para el mismo flujo de código OTP de 6 dígitos, sin afectar el estado "resuelto" de la candidata en sí. ~~`oauth_accounts`~~ — **resuelto en v0.16** (`ADR-012-google-sign-in.md`, ver §4.A/§5.9): entidad separada `user_identities`, preparada para más proveedores sin otra migración de `users`. ~~`messages` (mitad 1:1)~~ — **resuelto en v0.17** (`ADR-013-messages-minimal-model.md`, ver §4.A/§5.10): mensaje directo `sender_id`/`recipient_id`, sin tabla `conversations`/`conversation_participants`; sigue pendiente todo lo demás que §4.B › Mensajería seguía listando (grupos, fotos/archivos adjuntos). Entre las candidatas que siguen sin ratificar: `sessions`/`devices`, `user_settings`, columnas de perfil (`avatar_url`/`bio`), `media`, `reactions` (forma general con tipos), `saves`, `mentions`, `hashtags` (+`post_hashtags`), `blocks`, `restrictions`, `conversations` (+`conversation_participants`, para grupos), `message_media`, `password_changes`, `security_events`.

### Operación
- ~~Herramienta de migraciones~~ — **resuelto en código: Flask-Migrate/Alembic**, scaffolding en `backend/migrations/` (ver `BACKEND_ARCHITECTURE.md` §8); ratificación formal pendiente de confirmar. **Ubicación de la carpeta `database/`** sigue sin definir — las migraciones quedaron dentro de `backend/`, no en una carpeta `database/` separada.
- **Procedimiento de rollback** en entornos desplegados (DevOps).
- **Estrategia de backups y recuperación** — §12, sección completa pendiente.
- **Lista oficial de variables de entorno** — `DATABASE_URL` ya documentada en `backend/.env.example` (formato `postgresql+psycopg://usuario:password@host:puerto/nombre_bd`); sigue sin existir una lista oficial completa más allá de `JWT_SECRET_KEY` y `DATABASE_URL`.
- **Roles/privilegios de acceso** de PostgreSQL.
- **Ubicación exacta de la capa de repositorios** dentro de la estructura de backend — el modelo ya vive en `backend/app/infrastructure/persistence/models.py`, pero el repositorio que lo conecte con `application/`/`domain/` todavía no existe.

### Contradicciones / hallazgos reportados (no resueltos aquí)
- **README raíz dice MySQL** vs. PostgreSQL oficial (§2). Gana `/docs`; corregir el README en tarea aparte. *(Nota v0.7: `CLAUDE.md` §15 ya registra el `README.md` raíz como corregido en una tarea posterior — este documento no verificó esa corrección directamente, se deja la entrada por si el README volviera a divergir.)*
- ~~`JWT_SECRET_KEY` hardcodeado en `config.py`~~ — **corregido en v0.7 de este documento** (era un hallazgo obsoleto: el código ya lee `JWT_SECRET_KEY` de `os.environ` desde `BACKEND_ARCHITECTURE.md` v0.2; ver §11).
- ~~`username`/`phone`/`country_code`/`birth_date` en `users`~~ — **resuelto en v0.5** por `ADR-002-user-profile-fields.md` (ver §5). `avatar_url`/`bio` (§4.B › Perfil) **siguen** pendientes de ADR — no cubiertas por `ADR-002`.

---

## 15. Cierre

Este documento **no modifica** el backend, el Frontend, el Handbook ni instala dependencias: define el contrato de base de datos que la implementación futura deberá respetar, separando explícitamente **lo implementado (§4.A)**, **lo objetivo (§4.B)** y **lo pendiente (§4.C, §14)**. Cualquier cambio a este contrato sigue el proceso de decisiones de impacto medio/alto de `HB-001` §11–12 (ADR), no el criterio individual de quien implementa.
