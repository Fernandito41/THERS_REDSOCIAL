"""add two-factor authentication (TOTP)

Revision ID: a3c9f5b1e648
Revises: f1a4c8e2d573
Create Date: 2026-10-01 00:00:00.000000

Autenticación en dos pasos con TOTP (ADR-026-two-factor-authentication.md).
Resuelve "Activar 2FA" de la pantalla de Seguridad (REF-SET-03), que estaba
`pending` con el motivo "No está implementado. Mostrarlo como activo sería
afirmar una protección inexistente".

1. `users.totp_secret` — `TEXT`, nullable. El secreto compartido en base32.
   **Se guarda recuperable, no hasheado**, y es inevitable: verificar un código
   TOTP exige recalcularlo a partir del secreto, así que un hash lo haría
   inservible (a diferencia de los OTP de ADR-010/ADR-011, que se comparan
   contra un `code_hash` scrypt porque el código viaja y se descarta). La
   consecuencia -- una fuga de esta columna permite generar códigos válidos --
   queda registrada en ADR-026 §Riesgos.

2. `users.two_factor_enabled` — `BOOLEAN NOT NULL DEFAULT false`. Separada de
   `totp_secret` a propósito: durante el alta existe un secreto **todavía no
   confirmado** (la persona lo escaneó pero no probó aún que su app genera
   códigos correctos). Sin esa separación, escanear el QR y abandonar dejaría
   la cuenta exigiendo un código que nadie puede producir.

3. Tabla `two_factor_recovery_codes` — códigos de un solo uso para entrar
   cuando se pierde el dispositivo. Se guardan con hash scrypt (igual que los
   OTP de ADR-010/ADR-011) porque sí se pueden hashear: el código viaja una vez
   y se compara, no hace falta reconstruirlo. `used_at` en vez de borrar la
   fila: así se puede decir cuántos quedan sin perder el rastro de cuántos se
   usaron.

Escrita a mano (no autogenerada), mismo criterio que las migraciones anteriores.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'a3c9f5b1e648'
down_revision = 'f1a4c8e2d573'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('totp_secret', sa.Text(), nullable=True))
    op.add_column(
        'users',
        sa.Column(
            'two_factor_enabled',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
        ),
    )

    op.create_table(
        'two_factor_recovery_codes',
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
        # Hash scrypt del código (domain/auth/auth_service.hash_password),
        # nunca el valor crudo -- mismo criterio que PasswordResetToken.code_hash
        # (ADR-010) y EmailVerificationToken.code_hash (ADR-011).
        sa.Column('code_hash', sa.Text(), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
        # NULL = sin usar. Un código de recuperación es de un solo uso.
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
    )

    # Buscar los códigos sin usar de una persona al intentar entrar con uno.
    # Sin UNIQUE sobre `code_hash`: scrypt usa sal, así que dos códigos iguales
    # (improbable, pero posible entre usuarios distintos) producen hashes
    # distintos -- una UNIQUE no garantizaría nada y además no hay motivo para
    # impedirlo.
    op.create_index(
        'ix_two_factor_recovery_codes_user_id',
        'two_factor_recovery_codes',
        ['user_id'],
    )


def downgrade():
    op.drop_index(
        'ix_two_factor_recovery_codes_user_id',
        table_name='two_factor_recovery_codes',
    )
    op.drop_table('two_factor_recovery_codes')
    op.drop_column('users', 'two_factor_enabled')
    op.drop_column('users', 'totp_secret')
