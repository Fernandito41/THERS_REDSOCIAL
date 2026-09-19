# Modelos de persistencia (SQLAlchemy). Ver docs/architecture/DATABASE_ARCHITECTURE.md
# §5 para el contrato de `users` — tipo de PK, tipo de `email` y timestamps
# alineados a la decisión de UUID + CITEXT + DEFAULT en PostgreSQL indicada
# por el Tech Lead Backend.
#
# Nota de capas (BACKEND_ARCHITECTURE.md §17): este módulo pertenece a
# infraestructura/persistencia, no a `domain/`. `domain/auth/auth_service.py`
# no debe importar SQLAlchemy ni este módulo directamente.

from sqlalchemy import text
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    # UUID generado por PostgreSQL (DEFAULT gen_random_uuid(), función nativa
    # desde PostgreSQL 13 — no requiere la extensión pgcrypto/uuid-ossp). El
    # valor por defecto vive en la base de datos (server_default), no en Python,
    # para que cualquier INSERT (vía ORM o SQL directo) reciba un id válido.
    id = db.Column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    name = db.Column(db.String(120), nullable=False)

    # Columnas de perfil (ADR-002 — docs/architecture/ADR-002-user-profile-fields.md),
    # recolectadas por Register.jsx pero no persistidas hasta esta tarea.
    # `username` es case-sensitive a propósito (a diferencia de `email`): hoy
    # ningún flujo (login sigue siendo por email) requiere comparación
    # case-insensitive de username -- ver ADR-002 §3.
    username = db.Column(db.String(30), unique=True, nullable=False)

    # Nullable desde ADR-012-google-sign-in.md: Google no entrega teléfono ni
    # fecha de nacimiento -- una cuenta creada por "Continuar con Google" nace
    # sin estos tres (ver `profile_completed` más abajo). El registro
    # tradicional (`register_use_case.py`) sigue exigiéndolos siempre, a
    # nivel de route (`is_valid_phone`/`parse_birth_date`), así que para esas
    # cuentas nunca quedan en `NULL` en la práctica.
    phone = db.Column(db.String(20), nullable=True)
    country_code = db.Column(db.String(6), nullable=True)
    birth_date = db.Column(db.Date, nullable=True)

    # Soporta la regla de cooldown de cambio de username (ADR-003 —
    # docs/architecture/ADR-003-profile-update-contract.md §Evolución
    # futura, "Cambios de username": máx. 1 cambio cada 30 días). `NULL`
    # significa "nunca cambió su username" -- domain/auth/username_policy.py
    # trata ese caso como "cambio permitido". No se reutiliza `updated_at`
    # porque esa cambia con cualquier campo, no solo con `username`.
    username_changed_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # Verificación de email (ADR-009-password-reset-and-email-verification.md).
    # DEFAULT false en el servidor -- toda cuenta existente antes de esta
    # migración queda sin verificar (no hay backfill que pueda "adivinar" que
    # un email histórico es válido). `email_verified` es la única columna que
    # POST /api/verify-email puede escribir; nunca se acepta desde ningún
    # body (mismo principio anti mass-assignment que el resto de `users`).
    email_verified = db.Column(
        db.Boolean, nullable=False, server_default=text("false")
    )

    # Onboarding con Google (ADR-012-google-sign-in.md §Decisión): una cuenta
    # nueva creada por "Continuar con Google" recibe un JWT válido de
    # inmediato (la identidad ya está autenticada), pero nace con
    # `phone`/`country_code`/`birth_date` en `NULL` y un `username`
    # provisorio -- `profile_completed=false` hasta que la persona los
    # complete vía `PATCH /api/users/me` (reutilizado, ADR-003, sin endpoint
    # nuevo). El registro tradicional los exige todos desde el inicio, así
    # que siempre nace en `true` (`DEFAULT true` a nivel de columna). Nunca
    # se vuelve a `false` una vez en `true`.
    profile_completed = db.Column(
        db.Boolean, nullable=False, server_default=text("true")
    )

    # CITEXT (case-insensitive text, extensión de PostgreSQL) en vez de VARCHAR:
    # el UNIQUE sobre email ignora mayúsculas/minúsculas a nivel de motor, sin
    # normalizar manualmente en la capa de aplicación. Requiere
    # `CREATE EXTENSION IF NOT EXISTS citext` (ver migración).
    email = db.Column(CITEXT, unique=True, nullable=False, index=True)

    # TEXT en vez de VARCHAR(255): el hash (scrypt vía werkzeug.security) no
    # tiene una longitud máxima fija que valga la pena restringir a nivel de
    # esquema.
    #
    # Nullable desde ADR-012-google-sign-in.md: una cuenta creada
    # exclusivamente vía "Continuar con Google" no tiene contraseña local --
    # `NULL` significa exactamente eso, nunca una contraseña vacía/falsa ni
    # un valor inventado (`"GOOGLE_USER"` u otro). `login_use_case.py` trata
    # `password_hash IS NULL` como credenciales inválidas (mismo mensaje
    # genérico que cualquier otro fallo de login, sin revelar que la cuenta
    # es Google-only). El flujo de recuperación de contraseña
    # (`forgot-password`/`verify-reset-code`/`reset-password`, ADR-010) deja
    # de ser solo "recuperación" para esta cuenta -- se reutiliza tal cual
    # para fijar la primera contraseña ("Set password"), sin cambios de
    # código: un `UPDATE password_hash` funciona igual si el valor previo
    # era `NULL`.
    password_hash = db.Column(db.Text, nullable=True)

    # DEFAULT now() en la base de datos. `updated_at` se mantiene actualizado
    # por un trigger de PostgreSQL (set_updated_at, ver migración), no por
    # SQLAlchemy — así funciona igual para updates hechos vía ORM o SQL directo.
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    def __repr__(self):
        return f"<User id={self.id} email={self.email!r}>"


class Post(db.Model):
    __tablename__ = "posts"

    # Primera entidad del alcance objetivo del producto en pasar a
    # ratificada (ADR-004-posts-minimal-model.md) -- modelo deliberadamente
    # mínimo: solo texto, sin mood/imagen/hashtags/ubicación/likes/comentarios
    # (cada uno queda para su propio ADR, ver DATABASE_ARCHITECTURE.md §4.B).

    id = db.Column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    # ON DELETE CASCADE: placeholder razonable dado que borrado de cuenta
    # tampoco existe todavía como funcionalidad (ADR-004 §Riesgos) -- revisar
    # cuando esa funcionalidad se ratifique.
    author_id = db.Column(
        PG_UUID(as_uuid=True),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Sin límite de longitud a nivel de esquema -- la validación de negocio
    # (MAX_CONTENT_LENGTH) vive en domain/posts/validators.py, no aquí.
    content = db.Column(db.Text, nullable=False)

    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    # lazy="joined": listar posts siempre necesita el autor (to_public_post),
    # un JOIN evita el N+1 que tendría cada post resolviendo su autor por
    # separado.
    author = db.relationship("User", lazy="joined")

    def __repr__(self):
        return f"<Post id={self.id} author_id={self.author_id}>"


class Like(db.Model):
    __tablename__ = "likes"

    # Segunda entidad del alcance objetivo del producto en pasar a
    # ratificada (ADR-005-likes-minimal-model.md) -- caso binario like/no-like,
    # sin tipos de reacción (esa forma general sigue como candidata
    # `reactions` sin ratificar, DATABASE_ARCHITECTURE.md §4.B).

    id = db.Column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    # ON DELETE CASCADE en ambas FKs: si se borra el post o el usuario, sus
    # likes se borran con él (mismo placeholder que ADR-004 ya aceptó para
    # posts.author_id -- borrado de cuenta/post no existe todavía).
    post_id = db.Column(
        PG_UUID(as_uuid=True),
        db.ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id = db.Column(
        PG_UUID(as_uuid=True),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    # Sin `updated_at`: un like no se edita in place, solo se crea o se
    # borra (ADR-005 §Modelo de datos).

    __table_args__ = (
        db.UniqueConstraint("post_id", "user_id", name="uq_likes_post_user"),
    )

    def __repr__(self):
        return f"<Like post_id={self.post_id} user_id={self.user_id}>"


class Comment(db.Model):
    __tablename__ = "comments"

    # Tercera entidad del alcance objetivo del producto en pasar a
    # ratificada (ADR-006-comments-minimal-model.md) -- comentario plano
    # sobre un post, sin hilos de respuestas (`parent_comment_id` queda
    # fuera, ver ADR-006 §No objetivos).

    id = db.Column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    # ON DELETE CASCADE en ambas FKs: si se borra el post o el usuario, sus
    # comentarios se borran con él (mismo placeholder que ADR-004/ADR-005 ya
    # aceptaron -- borrado de cuenta/post no existe todavía).
    post_id = db.Column(
        PG_UUID(as_uuid=True),
        db.ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
    )
    author_id = db.Column(
        PG_UUID(as_uuid=True),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Sin límite de longitud a nivel de esquema -- la validación de negocio
    # (MAX_CONTENT_LENGTH) vive en domain/comments/validators.py, no aquí.
    content = db.Column(db.Text, nullable=False)

    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    # lazy="joined": listar comentarios siempre necesita el autor (mismo
    # motivo que Post.author) -- evita el N+1 de resolverlo por separado.
    author = db.relationship("User", lazy="joined")

    def __repr__(self):
        return f"<Comment id={self.id} post_id={self.post_id} author_id={self.author_id}>"


class Follow(db.Model):
    __tablename__ = "follows"

    # Cuarta entidad del alcance objetivo del producto en pasar a ratificada
    # (ADR-007-follows-minimal-model.md) -- primera relación auto-referencial
    # (users<->users) del esquema.

    id = db.Column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    # ON DELETE CASCADE en ambas FKs: mismo placeholder que el resto de
    # entidades (borrado de cuenta no existe todavía como funcionalidad).
    follower_id = db.Column(
        PG_UUID(as_uuid=True),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    followed_id = db.Column(
        PG_UUID(as_uuid=True),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    # Sin `updated_at`: seguir a alguien no se edita in place, solo se crea
    # o se borra (mismo criterio que Like, ADR-005 §Modelo de datos).

    __table_args__ = (
        db.UniqueConstraint(
            "follower_id", "followed_id", name="uq_follows_follower_followed"
        ),
        db.CheckConstraint(
            "follower_id <> followed_id", name="ck_follows_no_self_follow"
        ),
    )

    def __repr__(self):
        return f"<Follow follower_id={self.follower_id} followed_id={self.followed_id}>"


class Notification(db.Model):
    __tablename__ = "notifications"

    # Sexta entidad del alcance objetivo del producto en pasar a ratificada
    # (ADR-008-notifications-minimal-model.md) -- discriminador de tipo
    # único (`type`), no una tabla por tipo de evento (DATABASE_ARCHITECTURE.md
    # §4.B › Notificaciones: "una entidad `notifications` con discriminador
    # de tipo -- no una tabla por tipo"). Cubre los tres eventos que el
    # backend ya sabe generar: 'like', 'comment', 'follow'.

    id = db.Column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    # ON DELETE CASCADE en ambas FKs a `users`: mismo placeholder que el
    # resto de entidades (borrado de cuenta no existe todavía como
    # funcionalidad).
    recipient_id = db.Column(
        PG_UUID(as_uuid=True),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    actor_id = db.Column(
        PG_UUID(as_uuid=True),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # VARCHAR corto en vez de un ENUM de PostgreSQL -- agregar un tipo nuevo
    # (p. ej. 'mention' el día que exista) no debe requerir un ALTER TYPE;
    # el conjunto válido ('like'/'comment'/'follow') se valida en la capa de
    # aplicación, no en el esquema (mismo criterio ya aceptado para
    # `content` de posts/comments: la forma se valida en domain/, no con un
    # CHECK).
    type = db.Column(db.String(20), nullable=False)

    # Nullable: solo 'like'/'comment' tienen un post de origen -- 'follow'
    # no tiene ningún post asociado, viaja como NULL (ADR-008 §Modelo de
    # datos). ON DELETE CASCADE: si el post se borra, sus notificaciones
    # asociadas se borran con él (no tendría sentido notificar sobre un post
    # que ya no existe).
    post_id = db.Column(
        PG_UUID(as_uuid=True),
        db.ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=True,
    )

    # NULL significa "no leída" -- se usa como el propio booleano en vez de
    # una columna `read` separada, para poder ordenar/filtrar por "hace
    # cuánto se leyó" en el futuro sin migrar de nuevo (mismo espíritu que
    # `username_changed_at`, aunque ese caso es de otra entidad). Nunca
    # cruza la frontera HTTP como timestamp -- la API expone `read` como
    # booleano (`API_CONTRACT.md` §5, mismo criterio que
    # `username_changed_at` nunca se expone tal cual).
    read_at = db.Column(db.DateTime(timezone=True), nullable=True)

    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    # Sin `updated_at`: una notificación no se edita in place más allá de
    # marcarse como leída (`read_at`), mismo criterio que Like/Follow no
    # llevan `updated_at` (ADR-005/ADR-007 §Modelo de datos).

    # lazy="joined": listar notificaciones siempre necesita el actor (mismo
    # motivo que Post.author/Comment.author) -- evita el N+1 de resolverlo
    # por separado. `recipient` no se declara como relationship -- ningún
    # caso de uso necesita navegar de la notificación a su destinatario
    # completo, solo compara su id (siempre ya conocido: es quien pregunta).
    actor = db.relationship("User", foreign_keys=[actor_id], lazy="joined")

    __table_args__ = (
        db.Index("ix_notifications_recipient_id_created_at", "recipient_id", "created_at"),
    )

    def __repr__(self):
        return f"<Notification recipient_id={self.recipient_id} type={self.type!r}>"


class Message(db.Model):
    __tablename__ = "messages"

    # Décima entidad del alcance objetivo del producto en pasar a
    # ratificada (ADR-013-messages-minimal-model.md) -- mensaje directo
    # entre dos usuarios reales, sin tabla `conversations`/`conversation_
    # participants`: una "conversación" es una vista derivada de todos los
    # mensajes entre dos usuarios, no una fila propia (ADR-013 §Opciones
    # consideradas).

    id = db.Column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    # ON DELETE CASCADE en ambas FKs: mismo placeholder que el resto de
    # entidades (borrado de cuenta no existe todavía como funcionalidad).
    sender_id = db.Column(
        PG_UUID(as_uuid=True),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    recipient_id = db.Column(
        PG_UUID(as_uuid=True),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Sin límite de longitud a nivel de esquema -- la validación de negocio
    # (MAX_CONTENT_LENGTH) vive en domain/messages/validators.py, mismo
    # criterio que posts/comments.
    content = db.Column(db.Text, nullable=False)

    # NULL = no leído. Mismo criterio que Notification.read_at (ADR-008):
    # nunca cruza la frontera HTTP como timestamp crudo, la API expone
    # "read" como booleano.
    read_at = db.Column(db.DateTime(timezone=True), nullable=True)

    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    # Sin `updated_at`: un mensaje no se edita in place más allá de
    # marcarse como leído, mismo criterio que Like/Follow/Notification.

    # lazy="joined" en ambos extremos: listar conversaciones siempre
    # necesita identificar "la otra persona" -- evita el N+1 de resolverla
    # por separado (mismo motivo que Post.author/Comment.author).
    sender = db.relationship("User", foreign_keys=[sender_id], lazy="joined")
    recipient = db.relationship("User", foreign_keys=[recipient_id], lazy="joined")

    __table_args__ = (
        # Sin UNIQUE: dos mensajes entre las mismas dos personas son eventos
        # legítimos e independientes, no un duplicado a impedir (mismo
        # criterio que `notifications`, ADR-008 §Modelo de datos).
        db.CheckConstraint(
            "sender_id <> recipient_id", name="ck_messages_no_self_message"
        ),
        # El hilo entre A y B se busca con
        # (sender_id=A AND recipient_id=B) OR (sender_id=B AND recipient_id=A),
        # ordenado por created_at -- ninguna columna única cubre ese acceso,
        # así que hacen falta ambos índices compuestos para que PostgreSQL
        # resuelva el OR sin escanear la tabla completa (ADR-013 §Índices).
        db.Index(
            "ix_messages_sender_recipient_created",
            "sender_id", "recipient_id", "created_at",
        ),
        db.Index(
            "ix_messages_recipient_sender_created",
            "recipient_id", "sender_id", "created_at",
        ),
    )

    def __repr__(self):
        return f"<Message sender_id={self.sender_id} recipient_id={self.recipient_id}>"


class PasswordResetToken(db.Model):
    __tablename__ = "password_reset_tokens"

    # Séptima entidad del alcance objetivo del producto en pasar a
    # ratificada (ADR-009-password-reset-and-email-verification.md),
    # rediseñada en ADR-010-password-reset-otp-flow.md: pasa de un enlace
    # con token en la URL a un código OTP de 6 dígitos. Una sola fila cubre
    # las tres etapas del ciclo de vida (creada -> verificada -> usada) --
    # no hay una tabla separada por etapa (ADR-010 §Decisión).

    id = db.Column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    user_id = db.Column(
        PG_UUID(as_uuid=True),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Hash del código OTP de 6 dígitos -- con `werkzeug.security.generate_password_hash`
    # (scrypt, domain/auth/auth_service.hash_password), NO con el SHA-256
    # rápido de `token_generator.hash_token()`: un código de solo 10^6
    # combinaciones necesita un hash lento para que una fuga de esta tabla
    # no permita fuerza bruta offline instantánea (ADR-010 §Seguridad). TEXT
    # porque el formato de salida de scrypt (algoritmo$parámetros$salt$hash)
    # no tiene una longitud fija corta como el SHA-256 hexadecimal anterior.
    code_hash = db.Column(db.Text, nullable=False)

    # Cuántas veces se probó un código incorrecto contra esta solicitud
    # (ADR-010 §Seguridad) -- alcanzar PASSWORD_RESET_MAX_ATTEMPTS
    # (domain/auth/token_policy.py) vuelve la solicitud inutilizable sin
    # borrarla ni revelarlo distinto de un código simplemente incorrecto.
    attempts = db.Column(db.Integer, nullable=False, server_default=text("0"))

    # Vigencia del código OTP en sí (10 minutos desde su creación).
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)

    # NULL = el código todavía no se verificó correctamente. Se fija una
    # sola vez, junto con la autorización temporal de abajo (mark_verified).
    verified_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # Autorización temporal emitida tras verificar el código -- el token
    # opaco que el Frontend usa en POST /api/reset-password sin tener que
    # reintroducir el OTP. SHA-256 (token_generator.hash_token()): a
    # diferencia del OTP, este token sí tiene 256 bits de entropía propios,
    # el mismo criterio que ya usaba el token de enlace de ADR-009.
    reset_authorization_hash = db.Column(db.String(64), nullable=True)
    reset_authorization_expires_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # NULL = la contraseña todavía no se cambió con esta solicitud. Se fija
    # una sola vez, al completar POST /api/reset-password -- nunca se
    # revierte a NULL.
    used_at = db.Column(db.DateTime(timezone=True), nullable=True)

    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    __table_args__ = (
        db.Index("ix_password_reset_tokens_user_id_created_at", "user_id", "created_at"),
        db.Index(
            "ix_password_reset_tokens_reset_authorization_hash", "reset_authorization_hash"
        ),
        # Único índice parcial del esquema: a lo sumo una solicitud sin usar
        # por usuario en todo momento (ADR-010 §Opciones consideradas) --
        # última línea de defensa contra la condición de carrera de dos
        # "Reenviar código" simultáneos (ver
        # infrastructure/persistence/repositories/password_reset_repository.py
        # para el manejo de la excepción que esto puede producir).
        db.Index(
            "uq_password_reset_tokens_active_user",
            "user_id",
            unique=True,
            postgresql_where=text("used_at IS NULL"),
        ),
    )

    def __repr__(self):
        return f"<PasswordResetToken user_id={self.user_id}>"


class EmailVerificationToken(db.Model):
    __tablename__ = "email_verification_tokens"

    # Octava entidad del alcance objetivo del producto en pasar a ratificada
    # (ADR-009-password-reset-and-email-verification.md), reconstruida por
    # ADR-011-mandatory-email-verification.md: pasa de un enlace con token
    # de 256 bits a un código OTP de 6 dígitos, mismo patrón que
    # PasswordResetToken (ADR-010-password-reset-otp-flow.md) -- sin las
    # columnas de autorización temporal, que ahí no hacen falta: verificar
    # el email es de una sola etapa (el propio acierto ya marca
    # `email_verified = true`, no hay una acción sensible posterior que
    # proteger con un paso extra).

    id = db.Column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    user_id = db.Column(
        PG_UUID(as_uuid=True),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Hash scrypt del código de 6 dígitos (domain/auth/auth_service.hash_password)
    # -- no SHA-256: mismo motivo que PasswordResetToken.code_hash (ADR-010
    # §Opciones consideradas), un código de solo 10^6 combinaciones necesita
    # un hash lento para que una fuga de esta tabla no permita fuerza bruta
    # offline instantánea.
    code_hash = db.Column(db.Text, nullable=False)

    # Intentos de verificación fallidos contra este código (ADR-011 §Seguridad).
    attempts = db.Column(db.Integer, nullable=False, server_default=text("0"))

    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)

    used_at = db.Column(db.DateTime(timezone=True), nullable=True)

    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    __table_args__ = (
        db.Index("ix_email_verification_tokens_user_id_created_at", "user_id", "created_at"),
        # Único índice parcial de esta entidad (mismo patrón que
        # PasswordResetToken, ADR-010 §Opciones consideradas): a lo sumo un
        # código activo por usuario, defensa de última línea contra dos
        # "Reenviar código" simultáneos.
        db.Index(
            "uq_email_verification_tokens_active_user",
            "user_id",
            unique=True,
            postgresql_where=text("used_at IS NULL"),
        ),
    )

    def __repr__(self):
        return f"<EmailVerificationToken user_id={self.user_id}>"


class UserIdentity(db.Model):
    __tablename__ = "user_identities"

    # Novena entidad del alcance objetivo del producto en pasar a ratificada
    # (ADR-012-google-sign-in.md). Vincula una identidad de un proveedor
    # externo (hoy solo "google") a un usuario de THERS -- tabla separada
    # de `users`, no columnas `google_sub`/`auth_provider` sueltas ahí, para
    # que agregar Apple/Microsoft más adelante sea una fila nueva con otro
    # `provider`, no una migración de esquema de `users` (§Opciones
    # consideradas del ADR). Un usuario puede tener cero, una, o varias
    # identidades vinculadas (p. ej. password + Google al mismo tiempo,
    # FASE 9 de la tarea origen -- account linking).

    id = db.Column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    user_id = db.Column(
        PG_UUID(as_uuid=True),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # String libre, no ENUM de PostgreSQL -- mismo criterio que
    # `notifications.type` (ADR-008-notifications-minimal-model.md):
    # discriminador validado en la aplicación (domain/auth/google_identity.py
    # y quien lo llame), no a nivel de motor.
    provider = db.Column(db.String(20), nullable=False)

    # El claim `sub` del ID Token de Google (identificador estable de la
    # cuenta, FASE 6 de la tarea origen) -- nunca el email, que en teoría
    # podría cambiar sin que la cuenta de Google deje de ser la misma.
    provider_subject = db.Column(db.Text, nullable=False)

    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    __table_args__ = (
        # Garantiza a nivel de motor que la misma identidad externa
        # (`provider`, `provider_subject`) nunca termine vinculada a dos
        # usuarios de THERS a la vez -- defensa de última línea contra la
        # condición de carrera de dos requests simultáneas de
        # `POST /api/auth/google` para una cuenta de Google que todavía no
        # existía en THERS (ADR-012 §Seguridad).
        db.Index(
            "uq_user_identities_provider_subject",
            "provider",
            "provider_subject",
            unique=True,
        ),
        db.Index("ix_user_identities_user_id", "user_id"),
    )

    def __repr__(self):
        return f"<UserIdentity provider={self.provider!r} user_id={self.user_id}>"
