"""rebuild email_verification_tokens for OTP flow

Revision ID: a7d3f6c1e8b9
Revises: f4b8c92a1d67
Create Date: 2026-09-17 00:00:00.000000

Reemplaza el modelo de `email_verification_tokens`
(ADR-011-mandatory-email-verification.md) -- pasa de un token de enlace con
hash SHA-256 (ADR-009-password-reset-and-email-verification.md) a un código
OTP de 6 dígitos con hash scrypt + límite de intentos, mismo patrón que
`password_reset_tokens` (ADR-010-password-reset-otp-flow.md). Se recrea la
tabla en vez de alterarla columna por columna -- mismo criterio que
f4b8c92a1d67: el significado de la columna principal cambia (token_hash ->
code_hash es un cambio de algoritmo de hash, no solo de nombre) y no hay
datos de producción reales que preservar todavía.

Escrita a mano (no autogenerada), mismo criterio que las migraciones
anteriores.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'a7d3f6c1e8b9'
down_revision = 'f4b8c92a1d67'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('email_verification_tokens')

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
        # TEXT, no VARCHAR(64): el formato de salida de scrypt no tiene una
        # longitud fija corta, mismo criterio que password_reset_tokens.code_hash.
        sa.Column('code_hash', sa.Text(), nullable=False),
        sa.Column('attempts', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
    )

    op.create_index(
        'ix_email_verification_tokens_user_id_created_at',
        'email_verification_tokens',
        ['user_id', 'created_at'],
    )

    # Único índice parcial de esta entidad (mismo patrón que
    # password_reset_tokens, ADR-010 §Opciones consideradas): a lo sumo un
    # código activo por usuario, defensa de última línea contra dos
    # "Reenviar código" simultáneos.
    op.create_index(
        'uq_email_verification_tokens_active_user',
        'email_verification_tokens',
        ['user_id'],
        unique=True,
        postgresql_where=sa.text('used_at IS NULL'),
    )


def downgrade():
    op.drop_index(
        'uq_email_verification_tokens_active_user', table_name='email_verification_tokens'
    )
    op.drop_index(
        'ix_email_verification_tokens_user_id_created_at', table_name='email_verification_tokens'
    )
    op.drop_table('email_verification_tokens')

    # Restaura la forma anterior (ADR-009), para que el downgrade deje el
    # esquema exactamente como lo dejaba la migración anterior a esta.
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
