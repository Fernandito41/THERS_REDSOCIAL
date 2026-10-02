"""merge heads; link sessions to refresh token family

Une las dos ramas de migraciones (refresh tokens de ADR-017 y preferencias de
contenido de ADR-030) y agrega `sessions.refresh_family_id`, que enlaza cada fila
del registro de sesiones (ADR-025) con la familia de refresh tokens de su login.

Revision ID: f8c2d6a4b190
Revises: b7d41e9a3c52, e1b5c9d3a7f4
Create Date: 2026-10-02
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "f8c2d6a4b190"
down_revision = ("b7d41e9a3c52", "e1b5c9d3a7f4")
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "sessions",
        sa.Column("refresh_family_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index(
        "ix_sessions_refresh_family_id", "sessions", ["refresh_family_id"]
    )


def downgrade():
    op.drop_index("ix_sessions_refresh_family_id", table_name="sessions")
    op.drop_column("sessions", "refresh_family_id")
