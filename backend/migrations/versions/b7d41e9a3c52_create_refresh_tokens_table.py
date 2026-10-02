"""create refresh_tokens table

Revision ID: b7d41e9a3c52
Revises: a5c8e2d71f34
Create Date: 2026-10-02 00:00:00.000000

Tabla de refresh tokens rotativos (ADR-017-jwt-session-policy.md,
docs/architecture/ADR-017-jwt-session-policy.md). Cada login abre una
"familia" (`family_id`); cada renovación consume la fila vigente y crea la
siguiente. Se guarda el SHA-256 del `jti`, nunca el token (ADR-017 §4.1).

Encadena con `a5c8e2d71f34` (perfil y media, ADR-015), que a esta fecha aún
no está en `origin/develop`: este PR no puede mergearse antes que ese
trabajo.

Escrita a mano (no autogenerada), mismo criterio que las migraciones
anteriores.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'b7d41e9a3c52'
down_revision = 'a5c8e2d71f34'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'refresh_tokens',
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
        sa.Column('family_id', UUID(as_uuid=True), nullable=False),
        sa.Column('token_hash', sa.String(length=64), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('replaced_by_id', UUID(as_uuid=True), nullable=True),
    )

    op.create_index(
        'uq_refresh_tokens_token_hash', 'refresh_tokens', ['token_hash'], unique=True
    )
    op.create_index('ix_refresh_tokens_user_id', 'refresh_tokens', ['user_id'])
    op.create_index('ix_refresh_tokens_family_id', 'refresh_tokens', ['family_id'])

    # A lo sumo un token activo (sin usar y sin revocar) por familia
    # (ADR-017 §4.3): defensa de última línea contra dos rotaciones
    # simultáneas del mismo token.
    op.create_index(
        'uq_refresh_tokens_active_family',
        'refresh_tokens',
        ['family_id'],
        unique=True,
        postgresql_where=sa.text('used_at IS NULL AND revoked_at IS NULL'),
    )


def downgrade():
    op.drop_index('uq_refresh_tokens_active_family', table_name='refresh_tokens')
    op.drop_index('ix_refresh_tokens_family_id', table_name='refresh_tokens')
    op.drop_index('ix_refresh_tokens_user_id', table_name='refresh_tokens')
    op.drop_index('uq_refresh_tokens_token_hash', table_name='refresh_tokens')
    op.drop_table('refresh_tokens')
