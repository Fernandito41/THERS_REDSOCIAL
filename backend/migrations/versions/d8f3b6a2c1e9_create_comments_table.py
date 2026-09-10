"""create comments table

Revision ID: d8f3b6a2c1e9
Revises: f3a8c1d9e274
Create Date: 2026-09-10 00:00:00.000000

Tercera entidad del alcance objetivo del producto en pasar a ratificada
(ADR-006-comments-minimal-model.md — docs/architecture/ADR-006-comments-minimal-model.md).
Modelo deliberadamente mínimo: comentario plano sobre un post, sin hilos de
respuestas (`parent_comment_id` queda fuera -- ver ADR-006 §No objetivos).

Escrita a mano (no autogenerada), mismo criterio que las migraciones
anteriores: reutiliza la función `set_updated_at()` ya creada por la
migración inicial (a1b2c3d4e5f6_create_users_table.py) en vez de duplicarla.

Nota de ramas: parte de f3a8c1d9e274 (posts), no de la migración de `likes`
(ADR-005, en su propia rama sin mergear todavía) -- ambas entidades son
independientes entre sí, cada una referencia solo a `posts`/`users`.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'd8f3b6a2c1e9'
down_revision = 'f3a8c1d9e274'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'comments',
        sa.Column(
            'id',
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text('gen_random_uuid()'),
        ),
        sa.Column(
            'post_id',
            UUID(as_uuid=True),
            sa.ForeignKey('posts.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column(
            'author_id',
            UUID(as_uuid=True),
            sa.ForeignKey('users.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
    )

    # Justificado por GET /api/posts/<post_id>/comments
    # (WHERE post_id = ... ORDER BY created_at ASC) -- mismo criterio de
    # "sin índices especulativos" que ADR-004/ADR-005.
    op.create_index(
        'ix_comments_post_id_created_at', 'comments', ['post_id', 'created_at']
    )

    # Reutiliza set_updated_at(), ya creada por la migración inicial -- no se
    # vuelve a definir la función, solo se agrega el trigger para esta tabla.
    op.execute(
        """
        CREATE TRIGGER trg_comments_updated_at
        BEFORE UPDATE ON comments
        FOR EACH ROW
        EXECUTE FUNCTION set_updated_at();
        """
    )


def downgrade():
    op.execute('DROP TRIGGER IF EXISTS trg_comments_updated_at ON comments')
    op.drop_index('ix_comments_post_id_created_at', table_name='comments')
    op.drop_table('comments')
