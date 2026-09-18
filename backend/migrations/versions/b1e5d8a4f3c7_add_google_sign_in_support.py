"""add Google Sign-In support

Revision ID: b1e5d8a4f3c7
Revises: a7d3f6c1e8b9
Create Date: 2026-09-18 00:00:00.000000

Soporte para "Continuar con Google" (ADR-012-google-sign-in.md), sin tocar
el registro/login tradicional:

- `users.password_hash` pasa a NULLABLE -- una cuenta creada exclusivamente
  vía Google no tiene contraseña local.
- `users.phone`/`country_code`/`birth_date` pasan a NULLABLE -- Google no
  entrega ninguno de los tres.
- `users.profile_completed` (BOOLEAN NOT NULL DEFAULT true) -- todas las
  cuentas existentes (siempre creadas por el registro tradicional, que exige
  los tres campos de arriba) quedan con el perfil ya completo por defecto;
  una cuenta nueva vía Google nace explícitamente en `false`
  (application/auth/google_auth_use_case.py).
- Tabla nueva `user_identities` -- vincula una identidad externa
  (`provider`, `provider_subject`) a un usuario de THERS. `UNIQUE (provider,
  provider_subject)` a nivel de motor: la misma cuenta de Google nunca
  puede terminar vinculada a dos usuarios distintos.

Se altera `users` en vez de recrearla (a diferencia de las migraciones de
`password_reset_tokens`/`email_verification_tokens`) porque esta vez no
cambia el *significado* de ninguna columna existente, solo se relaja su
nulabilidad y se agrega una nueva -- ningún dato existente se pierde ni
cambia de forma.

Escrita a mano (no autogenerada), mismo criterio que las migraciones
anteriores.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'b1e5d8a4f3c7'
down_revision = 'a7d3f6c1e8b9'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('users', 'password_hash', existing_type=sa.Text(), nullable=True)
    op.alter_column('users', 'phone', existing_type=sa.String(length=20), nullable=True)
    op.alter_column('users', 'country_code', existing_type=sa.String(length=6), nullable=True)
    op.alter_column('users', 'birth_date', existing_type=sa.Date(), nullable=True)

    op.add_column(
        'users',
        sa.Column(
            'profile_completed',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('true'),
        ),
    )

    op.create_table(
        'user_identities',
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
        sa.Column('provider', sa.String(length=20), nullable=False),
        sa.Column('provider_subject', sa.Text(), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
    )

    op.create_index(
        'uq_user_identities_provider_subject',
        'user_identities',
        ['provider', 'provider_subject'],
        unique=True,
    )
    op.create_index('ix_user_identities_user_id', 'user_identities', ['user_id'])


def downgrade():
    op.drop_index('ix_user_identities_user_id', table_name='user_identities')
    op.drop_index('uq_user_identities_provider_subject', table_name='user_identities')
    op.drop_table('user_identities')

    op.drop_column('users', 'profile_completed')

    op.alter_column('users', 'birth_date', existing_type=sa.Date(), nullable=False)
    op.alter_column('users', 'country_code', existing_type=sa.String(length=6), nullable=False)
    op.alter_column('users', 'phone', existing_type=sa.String(length=20), nullable=False)
    op.alter_column('users', 'password_hash', existing_type=sa.Text(), nullable=False)
