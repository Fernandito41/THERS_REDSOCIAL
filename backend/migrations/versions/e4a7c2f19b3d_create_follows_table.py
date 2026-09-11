"""create follows table

Revision ID: e4a7c2f19b3d
Revises: d8f3b6a2c1e9
Create Date: 2026-09-10 00:00:00.000000

Cuarta entidad del alcance objetivo del producto en pasar a ratificada
(ADR-007-follows-minimal-model.md — docs/architecture/ADR-007-follows-minimal-model.md).
Primera relación auto-referencial (users<->users) del esquema. Primera
`CHECK` constraint del esquema: impide que un usuario se siga a sí mismo a
nivel de motor, no solo en la capa de aplicación (ADR-007 §Opciones
consideradas).

Escrita a mano (no autogenerada), mismo criterio que las migraciones
anteriores.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'e4a7c2f19b3d'
down_revision = 'd8f3b6a2c1e9'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'follows',
        sa.Column(
            'id',
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text('gen_random_uuid()'),
        ),
        sa.Column(
            'follower_id',
            UUID(as_uuid=True),
            sa.ForeignKey('users.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column(
            'followed_id',
            UUID(as_uuid=True),
            sa.ForeignKey('users.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
        sa.UniqueConstraint(
            'follower_id', 'followed_id', name='uq_follows_follower_followed'
        ),
        sa.CheckConstraint(
            'follower_id <> followed_id', name='ck_follows_no_self_follow'
        ),
    )

    # A diferencia de `likes` (ADR-005), acá sí hace falta un segundo índice:
    # followers_count/"me sigue?" filtran por followed_id, la columna NO
    # líder de la UNIQUE (follower_id, followed_id) -- sin este índice esas
    # consultas escanean la tabla completa (ADR-007 §Índices).
    op.create_index('ix_follows_followed_id', 'follows', ['followed_id'])


def downgrade():
    op.drop_index('ix_follows_followed_id', table_name='follows')
    op.drop_table('follows')
