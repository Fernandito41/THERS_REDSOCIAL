"""add profile fields to users

Revision ID: a1edcbff74d8
Revises: a1b2c3d4e5f6
Create Date: 2026-08-27 00:00:00.000000

Agrega username, phone, country_code, birth_date a `users`, ratificados por
ADR-002 (docs/architecture/ADR-002-user-profile-fields.md) — antes eran
columnas OBJETIVO en DATABASE_ARCHITECTURE.md §4.B, pendientes de ADR.

Escrita a mano (no autogenerada), igual que la migración inicial, para
controlar explícitamente el nombre del índice único de `username` según la
convención de DATABASE_ARCHITECTURE.md §7 (`uq_<tabla>_<columna>`).

Todas las columnas se agregan como NOT NULL directamente: `users` no tiene
todavía ninguna base compartida por el equipo ni de producción (solo
`thers_dev`/`thers_test` locales, DATABASE_ARCHITECTURE.md §2), y ambas se
reconstruyen habitualmente desde un volumen vacío — no hace falta un backfill
de datos existentes.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1edcbff74d8'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('username', sa.String(length=30), nullable=False))
    op.add_column('users', sa.Column('phone', sa.String(length=20), nullable=False))
    op.add_column('users', sa.Column('country_code', sa.String(length=6), nullable=False))
    op.add_column('users', sa.Column('birth_date', sa.Date(), nullable=False))

    op.create_unique_constraint('uq_users_username', 'users', ['username'])


def downgrade():
    op.drop_constraint('uq_users_username', 'users', type_='unique')

    op.drop_column('users', 'birth_date')
    op.drop_column('users', 'country_code')
    op.drop_column('users', 'phone')
    op.drop_column('users', 'username')
