"""add is_moderator and account suspension to users (ADR-032 phase 2)

Revision ID: e5b8c3a7d912
Revises: d4a9b6c1e275
Create Date: 2026-10-02

Moderación de la plataforma (ADR-032-content-reports-and-moderation.md, fase 2):

- `is_moderator`: quién puede ver la cola de reportes y resolverlos. Se asigna SOLO
  por línea de comandos, nunca por la API.
- `suspended_at` / `suspension_reason`: una cuenta suspendida no puede iniciar sesión
  y la persona ve el motivo.

Migración ADITIVA y no destructiva: las cuentas existentes quedan como no moderadoras
y no suspendidas (el valor por defecto), no se borra ni se recrea nada.
"""
from alembic import op
import sqlalchemy as sa

revision = "e5b8c3a7d912"
down_revision = "d4a9b6c1e275"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users",
        sa.Column("is_moderator", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.add_column("users", sa.Column("suspended_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("suspension_reason", sa.String(length=500), nullable=True))


def downgrade():
    op.drop_column("users", "suspension_reason")
    op.drop_column("users", "suspended_at")
    op.drop_column("users", "is_moderator")
