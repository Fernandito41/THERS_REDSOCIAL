"""create password_reset_tokens table

Revision ID: c1f6a83d2e59
Revises: b8d4f2a917c3
Create Date: 2026-09-15 00:05:00.000000

Octava entidad del alcance objetivo del producto en pasar a ratificada
(ADR-009-password-reset-and-email-verification.md). Token de un solo uso
para POST /api/reset-password -- solo se persiste `token_hash` (SHA-256 del
token crudo, domain/auth/token_generator.py), nunca el valor que viaja en el
enlace del correo.

Sin `updated_at`/trigger: un token de recuperación no se edita in place más
allá de marcarse usado (`used_at`), mismo criterio que `likes`/`follows`/
`notifications`.

Escrita a mano (no autogenerada), mismo criterio que las migraciones
anteriores.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'c1f6a83d2e59'
down_revision = 'b8d4f2a917c3'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'password_reset_tokens',
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
        sa.UniqueConstraint('token_hash', name='uq_password_reset_tokens_token_hash'),
    )

    # POST /api/forgot-password consulta "¿ya hay un token reciente sin usar
    # de este usuario?" (cooldown anti-spam, ADR-009 §Seguridad) -- filtra
    # por user_id y ordena/compara por created_at, columna líder cubre ambos.
    op.create_index(
        'ix_password_reset_tokens_user_id_created_at',
        'password_reset_tokens',
        ['user_id', 'created_at'],
    )


def downgrade():
    op.drop_index(
        'ix_password_reset_tokens_user_id_created_at', table_name='password_reset_tokens'
    )
    op.drop_table('password_reset_tokens')
