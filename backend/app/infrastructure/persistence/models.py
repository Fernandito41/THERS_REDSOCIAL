# Modelos de persistencia (SQLAlchemy). Ver docs/architecture/DATABASE_ARCHITECTURE.md
# §5 para el contrato de `users` y ADR-001 (persistencia de usuarios) para las
# decisiones de driver/ORM, tipo de PK y hashing que este módulo implementa.
#
# Nota de capas (BACKEND_ARCHITECTURE.md §17): este módulo pertenece a
# infraestructura/persistencia, no a `domain/`. `domain/auth/auth_service.py`
# no debe importar SQLAlchemy ni este módulo directamente.

import uuid
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.extensions import db


def _utcnow():
    return datetime.now(timezone.utc)


class User(db.Model):
    __tablename__ = "users"

    # UUID (decisión aplicada sobre DATABASE_ARCHITECTURE.md §14, "tipo de PK" —
    # antes BIGINT autoincremental, cambiado a UUID por indicación del Tech Lead
    # Backend). Se genera en Python (uuid.uuid4) al crear el objeto, no en la base
    # de datos, para no depender de la extensión pgcrypto/uuid-ossp de PostgreSQL.
    id = db.Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = db.Column(db.String(120), nullable=False)

    # Longitud de columnas: valor por defecto razonable, no ratificado formalmente
    # por el equipo (DATABASE_ARCHITECTURE.md §14, "longitudes máximas de columnas"
    # sigue listado como pendiente). Ajustar si el equipo decide otro límite.
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)

    # Hash generado con werkzeug.security.generate_password_hash (scrypt) — nunca
    # se guarda la contraseña en claro (DATABASE_ARCHITECTURE.md §11).
    password_hash = db.Column(db.String(255), nullable=False)

    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_utcnow)
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=_utcnow,
        onupdate=_utcnow,
    )

    def __repr__(self):
        return f"<User id={self.id} email={self.email!r}>"
