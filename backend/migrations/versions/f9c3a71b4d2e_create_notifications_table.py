"""create notifications table

Revision ID: f9c3a71b4d2e
Revises: e4a7c2f19b3d
Create Date: 2026-09-14 00:00:00.000000

Sexta entidad del alcance objetivo del producto en pasar a ratificada
(ADR-008-notifications-minimal-model.md — docs/architecture/ADR-008-notifications-minimal-model.md).
Discriminador de tipo único (`type`: 'like'/'comment'/'follow'), no una
tabla por tipo de evento (DATABASE_ARCHITECTURE.md §4.B › Notificaciones).

Sin `updated_at`/trigger: una notificación no se edita in place más allá de
marcarse como leída (`read_at`), mismo criterio que `likes`/`follows`
(ADR-005/ADR-007 §Modelo de datos).

Escrita a mano (no autogenerada), mismo criterio que las migraciones
anteriores.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'f9c3a71b4d2e'
down_revision = 'e4a7c2f19b3d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'notifications',
        sa.Column(
            'id',
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text('gen_random_uuid()'),
        ),
        sa.Column(
            'recipient_id',
            UUID(as_uuid=True),
            sa.ForeignKey('users.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column(
            'actor_id',
            UUID(as_uuid=True),
            sa.ForeignKey('users.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column('type', sa.String(length=20), nullable=False),
        sa.Column(
            'post_id',
            UUID(as_uuid=True),
            sa.ForeignKey('posts.id', ondelete='CASCADE'),
            nullable=True,
        ),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
    )

    # GET /api/notifications filtra por recipient_id y ordena por
    # created_at DESC -- índice compuesto con recipient_id como columna
    # líder, mismo patrón que ix_comments_post_id_created_at (ADR-006).
    op.create_index(
        'ix_notifications_recipient_id_created_at',
        'notifications',
        ['recipient_id', 'created_at'],
    )


def downgrade():
    op.drop_index('ix_notifications_recipient_id_created_at', table_name='notifications')
    op.drop_table('notifications')
