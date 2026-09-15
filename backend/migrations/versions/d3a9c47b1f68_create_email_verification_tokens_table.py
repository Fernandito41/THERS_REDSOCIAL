"""create email_verification_tokens table

Revision ID: d3a9c47b1f68
Revises: c1f6a83d2e59
Create Date: 2026-09-15 00:10:00.000000

Novena entidad del alcance objetivo del producto en pasar a ratificada
(ADR-009-password-reset-and-email-verification.md). Misma forma que
`password_reset_tokens` (migración anterior) -- tabla separada porque su
política (TTL de 24h vs. 30min, cooldown de reenvío) es propia
(ADR-009 §Opciones consideradas).

Escrita a mano (no autogenerada), mismo criterio que las migraciones
anteriores.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'd3a9c47b1f68'
down_revision = 'c1f6a83d2e59'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'email_verification_tokens',
        sa.Column(
            'id',
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text('gen_random_uuid()'),
        ),
        sa.Column(
            'user_id',
            UUID(as_uuid=True),
            sa.ForeignKey('users.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column('token_hash', sa.String(length=64), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
        sa.UniqueConstraint('token_hash', name='uq_email_verification_tokens_token_hash'),
    )

    op.create_index(
        'ix_email_verification_tokens_user_id_created_at',
        'email_verification_tokens',
        ['user_id', 'created_at'],
    )


def downgrade():
    op.drop_index(
        'ix_email_verification_tokens_user_id_created_at',
        table_name='email_verification_tokens',
    )
    op.drop_table('email_verification_tokens')
