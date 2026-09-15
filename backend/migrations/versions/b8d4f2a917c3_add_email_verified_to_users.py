"""add email_verified to users

Revision ID: b8d4f2a917c3
Revises: f9c3a71b4d2e
Create Date: 2026-09-15 00:00:00.000000

Séptima entidad del alcance objetivo del producto en pasar a ratificada
(ADR-009-password-reset-and-email-verification.md —
docs/architecture/ADR-009-password-reset-and-email-verification.md).
`users` gana `email_verified` (BOOLEAN, DEFAULT false) -- toda cuenta
existente antes de esta migración queda sin verificar (sin backfill posible:
no hay forma de saber si un email histórico es válido).

Escrita a mano (no autogenerada), mismo criterio que las migraciones
anteriores.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b8d4f2a917c3'
down_revision = 'f9c3a71b4d2e'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'users',
        sa.Column(
            'email_verified',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
        ),
    )


def downgrade():
    op.drop_column('users', 'email_verified')
