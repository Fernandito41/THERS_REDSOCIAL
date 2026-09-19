"""create messages table

Revision ID: f7a2c9e4d1b8
Revises: b1e5d8a4f3c7
Create Date: 2026-09-19 00:00:00.000000

Décima entidad del alcance objetivo del producto en pasar a ratificada
(ADR-013-messages-minimal-model.md — docs/architecture/ADR-013-messages-minimal-model.md).
Mensaje directo entre dos usuarios reales -- sin tabla `conversations`/
`conversation_participants` (ADR-013 §Opciones consideradas).

Escrita a mano (no autogenerada), mismo criterio que las migraciones
anteriores.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'f7a2c9e4d1b8'
down_revision = 'b1e5d8a4f3c7'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'messages',
        sa.Column(
            'id',
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text('gen_random_uuid()'),
        ),
        sa.Column(
            'sender_id',
            UUID(as_uuid=True),
            sa.ForeignKey('users.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column(
            'recipient_id',
            UUID(as_uuid=True),
            sa.ForeignKey('users.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
        sa.CheckConstraint(
            'sender_id <> recipient_id', name='ck_messages_no_self_message'
        ),
    )

    # Dos índices compuestos, no uno: el hilo entre A y B se busca con
    # (sender_id=A AND recipient_id=B) OR (sender_id=B AND recipient_id=A),
    # ordenado por created_at -- ninguna UNIQUE cubre ese acceso (ADR-013
    # §Índices, a diferencia de `follows` que solo necesitó un índice extra
    # sobre la columna no líder de su UNIQUE).
    op.create_index(
        'ix_messages_sender_recipient_created',
        'messages',
        ['sender_id', 'recipient_id', 'created_at'],
    )
    op.create_index(
        'ix_messages_recipient_sender_created',
        'messages',
        ['recipient_id', 'sender_id', 'created_at'],
    )


def downgrade():
    op.drop_index('ix_messages_recipient_sender_created', table_name='messages')
    op.drop_index('ix_messages_sender_recipient_created', table_name='messages')
    op.drop_table('messages')
