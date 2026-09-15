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
    phone = db.Column(db.String(20), nullable=False)
    country_code = db.Column(db.String(6), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)

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

    # CITEXT (case-insensitive text, extensión de PostgreSQL) en vez de VARCHAR:
    # el UNIQUE sobre email ignora mayúsculas/minúsculas a nivel de motor, sin
    # normalizar manualmente en la capa de aplicación. Requiere
    # `CREATE EXTENSION IF NOT EXISTS citext` (ver migración).
    email = db.Column(CITEXT, unique=True, nullable=False, index=True)

    # TEXT en vez de VARCHAR(255): el hash (scrypt vía werkzeug.security) no
    # tiene una longitud máxima fija que valga la pena restringir a nivel de
    # esquema.
    password_hash = db.Column(db.Text, nullable=False)

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


class PasswordResetToken(db.Model):
    __tablename__ = "password_reset_tokens"

    # Séptima entidad del alcance objetivo del producto en pasar a
    # ratificada (ADR-009-password-reset-and-email-verification.md) -- token
    # de un solo uso para POST /api/reset-password. Solo se persiste el hash
    # SHA-256 del token (domain/auth/token_generator.py), nunca el valor
    # crudo que viaja en el enlace del correo.

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

    # UNIQUE además de índice: colisión con 256 bits de entropía es
    # estadísticamente imposible, pero la constraint es defensa en
    # profundidad gratuita, mismo criterio que uq_likes_post_user (ADR-005).
    token_hash = db.Column(db.String(64), unique=True, nullable=False)

    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)

    # NULL = no usado todavía. Se fija una sola vez al consumir el token
    # (mark_used) -- nunca se revierte a NULL.
    used_at = db.Column(db.DateTime(timezone=True), nullable=True)

    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    __table_args__ = (
        db.Index("ix_password_reset_tokens_user_id_created_at", "user_id", "created_at"),
    )

    def __repr__(self):
        return f"<PasswordResetToken user_id={self.user_id}>"


class EmailVerificationToken(db.Model):
    __tablename__ = "email_verification_tokens"

    # Octava entidad del alcance objetivo del producto en pasar a ratificada
    # (ADR-009-password-reset-and-email-verification.md) -- misma forma que
    # PasswordResetToken, tabla separada porque su política (TTL, cooldown de
    # reenvío) es propia (ADR-009 §Opciones consideradas).

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

    token_hash = db.Column(db.String(64), unique=True, nullable=False)

    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)

    used_at = db.Column(db.DateTime(timezone=True), nullable=True)

    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    __table_args__ = (
        db.Index("ix_email_verification_tokens_user_id_created_at", "user_id", "created_at"),
    )

    def __repr__(self):
        return f"<EmailVerificationToken user_id={self.user_id}>"
