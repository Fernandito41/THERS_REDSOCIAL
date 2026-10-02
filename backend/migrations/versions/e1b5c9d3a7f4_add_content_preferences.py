"""add content preferences (sensitive content and muted topics)

Revision ID: e1b5c9d3a7f4
Revises: d9a3b7f1c5e2
Create Date: 2026-10-01 00:00:00.000000

Preferencias de contenido y feed (ADR-030-content-preferences.md):

  · `posts.is_sensitive` — lo que el AUTOR declara al publicar.
  · `users.hide_sensitive_content` — si el feed de esa persona omite lo marcado.
  · `muted_topics` — temas (hashtags) que una persona prefiere no ver.

Las dos columnas nuevas son NOT NULL con DEFAULT false: ninguna publicación
existente pasa a ser sensible y a nadie se le oculta nada por efecto de la
migración.

Escrita a mano (no autogenerada), mismo criterio que las migraciones anteriores.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'e1b5c9d3a7f4'
down_revision = 'd9a3b7f1c5e2'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'posts',
        sa.Column(
            'is_sensitive',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
        ),
    )
    op.add_column(
        'users',
        sa.Column(
            'hide_sensitive_content',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
        ),
    )

    op.create_table(
        'muted_topics',
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
        sa.Column('topic', sa.String(length=50), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
        sa.UniqueConstraint('user_id', 'topic', name='uq_muted_topics_user_topic'),
    )


def downgrade():
    op.drop_table('muted_topics')
    op.drop_column('users', 'hide_sensitive_content')
    op.drop_column('posts', 'is_sensitive')
