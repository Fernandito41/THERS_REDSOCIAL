"""create posts table

Revision ID: f3a8c1d9e274
Revises: b2f4a19c3d7e
Create Date: 2026-08-29 00:00:00.000000

Primera entidad del alcance objetivo del producto en pasar a ratificada
(ADR-004-posts-minimal-model.md — docs/architecture/ADR-004-posts-minimal-model.md).
Modelo deliberadamente mínimo: solo `content` de texto, `author_id` (FK a
`users`), timestamps -- sin mood/imagen/hashtags/ubicación/likes/comentarios,
cada uno queda para su propio ADR (DATABASE_ARCHITECTURE.md §4.B).

Escrita a mano (no autogenerada), mismo criterio que las migraciones
anteriores: reutiliza la función `set_updated_at()` ya creada por la
migración inicial (a1b2c3d4e5f6_create_users_table.py) en vez de duplicarla.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'f3a8c1d9e274'
down_revision = 'b2f4a19c3d7e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'posts',
        sa.Column(
            'id',
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text('gen_random_uuid()'),
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

    # Justificado por GET /api/posts (ORDER BY created_at DESC) -- mismo
    # criterio de "sin índices especulativos" que DATABASE_ARCHITECTURE.md §8
    # ya aplica a users.
    op.create_index('ix_posts_created_at', 'posts', ['created_at'])

    # Reutiliza set_updated_at(), ya creada por la migración inicial -- no se
    # vuelve a definir la función, solo se agrega el trigger para esta tabla.
    op.execute(
        """
        CREATE TRIGGER trg_posts_updated_at
        BEFORE UPDATE ON posts
        FOR EACH ROW
        EXECUTE FUNCTION set_updated_at();
        """
    )


def downgrade():
    op.execute('DROP TRIGGER IF EXISTS trg_posts_updated_at ON posts')
    op.drop_index('ix_posts_created_at', table_name='posts')
    op.drop_table('posts')
