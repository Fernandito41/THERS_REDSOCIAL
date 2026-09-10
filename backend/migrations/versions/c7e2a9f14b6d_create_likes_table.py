"""create likes table

Revision ID: c7e2a9f14b6d
Revises: f3a8c1d9e274
Create Date: 2026-09-10 00:00:00.000000

Segunda entidad del alcance objetivo del producto en pasar a ratificada
(ADR-005-likes-minimal-model.md — docs/architecture/ADR-005-likes-minimal-model.md).
Modelo deliberadamente mínimo: caso binario like/no-like, sin tipos de
reacción -- la candidata general `reactions` (DATABASE_ARCHITECTURE.md §4.B)
sigue sin ratificar en esa forma.

Sin `updated_at`/trigger: a diferencia de `users`/`posts`, un like no se
edita in place, solo se crea o se borra (ADR-005 §Modelo de datos).

Escrita a mano (no autogenerada), mismo criterio que las migraciones
anteriores.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'c7e2a9f14b6d'
down_revision = 'f3a8c1d9e274'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'likes',
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
            'user_id',
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
        sa.UniqueConstraint('post_id', 'user_id', name='uq_likes_post_user'),
    )
    # Sin índice adicional: la propia UNIQUE (post_id, user_id) ya cubre
    # COUNT(*)/IN (...) por post_id como columna líder (ADR-005 §Índices,
    # DATABASE_ARCHITECTURE.md §8 -- sin índices especulativos).


def downgrade():
    op.drop_table('likes')
