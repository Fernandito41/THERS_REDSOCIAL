"""create user restrictions table

Revision ID: d9a3b7f1c5e2
Revises: c4d8e2a6f913
Create Date: 2026-10-01 00:00:00.000000

Bloqueo y restricción de cuentas (ADR-029-blocked-and-restricted-accounts.md).
Una fila por par (owner, target) con un `kind` ('block' | 'restrict'): una
cuenta está bloqueada o restringida, nunca ambas -- la UNIQUE sobre el par lo
garantiza a nivel de motor.

Escrita a mano (no autogenerada), mismo criterio que las migraciones anteriores.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'd9a3b7f1c5e2'
down_revision = 'c4d8e2a6f913'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'user_restrictions',
        sa.Column(
            'id',
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text('gen_random_uuid()'),
        ),
        sa.Column(
            'owner_id',
            UUID(as_uuid=True),
            sa.ForeignKey('users.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column(
            'target_id',
            UUID(as_uuid=True),
            sa.ForeignKey('users.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column('kind', sa.String(length=10), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
        sa.UniqueConstraint('owner_id', 'target_id', name='uq_user_restrictions_pair'),
        sa.CheckConstraint('owner_id <> target_id', name='ck_user_restrictions_no_self'),
    )
    op.create_index(
        'ix_user_restrictions_target',
        'user_restrictions',
        ['target_id', 'kind'],
    )


def downgrade():
    op.drop_index('ix_user_restrictions_target', table_name='user_restrictions')
    op.drop_table('user_restrictions')
