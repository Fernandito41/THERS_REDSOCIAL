"""add bio, location, website, avatar_path and cover_path to users

Revision ID: a5c8e2d71f34
Revises: f7a2c9e4d1b8
Create Date: 2026-09-26 00:00:00.000000

Columnas ratificadas por ADR-015 (docs/architecture/ADR-015-profile-media.md).
Migración aditiva y reversible: todas nullable, sin backfill (`NULL` = la
persona todavía no definió ese dato).
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a5c8e2d71f34'
down_revision = 'f7a2c9e4d1b8'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('bio', sa.String(length=160), nullable=True))
    op.add_column('users', sa.Column('location', sa.String(length=60), nullable=True))
    op.add_column('users', sa.Column('website', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('avatar_path', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('cover_path', sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column('users', 'cover_path')
    op.drop_column('users', 'avatar_path')
    op.drop_column('users', 'website')
    op.drop_column('users', 'location')
    op.drop_column('users', 'bio')
