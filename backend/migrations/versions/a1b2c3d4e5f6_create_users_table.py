"""create users table

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2026-08-16 17:00:00.000000

Escrita a mano (no autogenerada) porque Alembic no puede detectar extensiones
de PostgreSQL ni triggers a partir del modelo de SQLAlchemy. Contrato de
`users` alineado a docs/architecture/DATABASE_ARCHITECTURE.md §5:
- id UUID PRIMARY KEY DEFAULT gen_random_uuid()
- email CITEXT NOT NULL UNIQUE (requiere extensión citext)
- password_hash TEXT NOT NULL
- created_at / updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
- trigger que mantiene updated_at actualizado en cada UPDATE
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import CITEXT, UUID


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # CITEXT: tipo case-insensitive para `email`, evita normalizar
    # manualmente mayusculas/minusculas en la capa de aplicacion.
    op.execute('CREATE EXTENSION IF NOT EXISTS citext')

    op.create_table(
        'users',
        sa.Column(
            'id',
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text('gen_random_uuid()'),
        ),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('email', CITEXT(), nullable=False),
        sa.Column('password_hash', sa.Text(), nullable=False),
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
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Trigger: mantiene updated_at correcto sin depender de que el codigo de
    # aplicacion lo actualice (funciona igual via ORM o SQL directo).
    op.execute(
        """
        CREATE OR REPLACE FUNCTION set_updated_at()
        RETURNS trigger AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_users_updated_at
        BEFORE UPDATE ON users
        FOR EACH ROW
        EXECUTE FUNCTION set_updated_at();
        """
    )


def downgrade():
    op.execute('DROP TRIGGER IF EXISTS trg_users_updated_at ON users')
    op.execute('DROP FUNCTION IF EXISTS set_updated_at()')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    # La extension citext no se elimina en el downgrade: podria ser usada por
    # otras tablas mas adelante y DROP EXTENSION no es parte del contrato de
    # esta migracion especifica.
