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
