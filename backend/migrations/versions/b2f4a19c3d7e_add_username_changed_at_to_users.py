"""add username_changed_at to users

Revision ID: b2f4a19c3d7e
Revises: a1edcbff74d8
Create Date: 2026-08-28 00:00:00.000000

Agrega `username_changed_at` (TIMESTAMPTZ, nullable) a `users`, ratificada
por ADR-003 (docs/architecture/ADR-003-profile-update-contract.md
§Evolución futura — "Cambios de username": máximo 1 cambio cada 30 días).
Soporta la regla de cooldown que aplica PATCH /api/users/me
(domain/auth/username_policy.py, ver también app/interfaces/routes/user_routes.py).

Migración aditiva, reversible y sin backfill: `NULL` significa "nunca
cambió su username" (mismo criterio que `can_change_username()` ya trata
`None` como "cambio permitido"). No requiere valor por defecto porque
ningún usuario existente pudo cambiar su username todavía -- el endpoint
que lo permite no existía hasta esta tarea.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2f4a19c3d7e'
down_revision = 'a1edcbff74d8'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'users',
        sa.Column('username_changed_at', sa.DateTime(timezone=True), nullable=True),
    )


def downgrade():
    op.drop_column('users', 'username_changed_at')
