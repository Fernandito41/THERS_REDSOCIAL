"""rebuild password_reset_tokens for OTP flow

Revision ID: f4b8c92a1d67
Revises: d3a9c47b1f68
Create Date: 2026-09-16 00:00:00.000000

Reemplaza el modelo de `password_reset_tokens` (ADR-010-password-reset-otp-flow.md,
docs/architecture/ADR-010-password-reset-otp-flow.md) -- pasa de un token de
enlace con hash SHA-256 (ADR-009-password-reset-and-email-verification.md) a
un código OTP de 6 dígitos con hash scrypt, más las columnas de la
autorización temporal emitida al verificarlo. Se recrea la tabla en vez de
alterarla columna por columna: el significado de casi todas las columnas
cambia (token_hash -> code_hash es un cambio de algoritmo de hash, no solo
de nombre) y no hay datos de producción reales que preservar todavía
(THERS no está desplegado con usuarios reales, DATABASE_ARCHITECTURE.md
§14) -- cualquier fila existente representa un enlace de recuperación bajo
el esquema anterior, ya sin sentido bajo el nuevo.

Escrita a mano (no autogenerada), mismo criterio que las migraciones
anteriores.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'f4b8c92a1d67'
down_revision = 'd3a9c47b1f68'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('password_reset_tokens')

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
        # TEXT, no VARCHAR(64): el formato de salida de scrypt
        # (algoritmo$parámetros$salt$hash) no tiene una longitud fija corta
        # como el SHA-256 hexadecimal que usaba la columna anterior.
        sa.Column('code_hash', sa.Text(), nullable=False),
        sa.Column('attempts', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reset_authorization_hash', sa.String(length=64), nullable=True),
        sa.Column('reset_authorization_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
    )

    op.create_index(
        'ix_password_reset_tokens_user_id_created_at',
        'password_reset_tokens',
        ['user_id', 'created_at'],
    )

    # Lookup de POST /api/reset-password por la autorización temporal
    # (fast SHA-256, alta entropía -- ADR-010 §Seguridad).
    op.create_index(
        'ix_password_reset_tokens_reset_authorization_hash',
        'password_reset_tokens',
        ['reset_authorization_hash'],
    )

    # Único índice parcial del esquema: a lo sumo una solicitud sin usar por
    # usuario en todo momento -- también es la defensa de última línea
    # contra la condición de carrera de dos "Reenviar código" simultáneos
    # (ADR-010 §Riesgos; el manejo de la excepción que esto puede producir
    # vive en infrastructure/persistence/repositories/password_reset_repository.py).
    op.create_index(
        'uq_password_reset_tokens_active_user',
        'password_reset_tokens',
        ['user_id'],
        unique=True,
        postgresql_where=sa.text('used_at IS NULL'),
    )


def downgrade():
    op.drop_index('uq_password_reset_tokens_active_user', table_name='password_reset_tokens')
    op.drop_index(
        'ix_password_reset_tokens_reset_authorization_hash', table_name='password_reset_tokens'
    )
    op.drop_index(
        'ix_password_reset_tokens_user_id_created_at', table_name='password_reset_tokens'
    )
    op.drop_table('password_reset_tokens')

    # Restaura la forma anterior (ADR-009), para que el downgrade deje el
    # esquema exactamente como lo dejaba
    # c1f6a83d2e59_create_password_reset_tokens_table.py.
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
    op.create_index(
        'ix_password_reset_tokens_user_id_created_at',
        'password_reset_tokens',
        ['user_id', 'created_at'],
    )
