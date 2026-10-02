"""create rate limit buckets

Revision ID: b6e3a9d4f270
Revises: a3c9f5b1e648
Create Date: 2026-10-01 00:00:00.000000

Rate limiting de los endpoints de autenticación (ADR-027-rate-limiting.md —
docs/architecture/ADR-027-rate-limiting.md). Cierra el ítem 8 de
`API_CONTRACT.md` §9, que v0.24 registró como pendiente explícito tras
descubrir que en `POST /api/2fa/verify` esa ausencia era explotable: un código
TOTP son 10^6 combinaciones dentro de una ventana de 30 segundos.

Contador de ventana fija, una fila por (scope, identidad):

  · `scope` — qué se está limitando ('login', '2fa_verify', ...). Los valores
    viven en domain/rate_limiting/policy.py, no en el esquema.

  · `identity_hash` — SHA-256 de la identidad (una IP, un email, un user_id).
    **Se hashea a propósito:** esta tabla solo necesita *contar*, nunca saber
    de quién. Guardar emails o IPs en claro acumularía datos personales en una
    tabla puramente operativa, cuando un hash cumple la misma función
    (ADR-027 §Seguridad). Mismo criterio que `password_reset_tokens.code_hash`:
    si no hace falta el valor original, no se guarda.

  · `window_started_at` + `attempts` — el contador. Reiniciar la ventana y
    sumar un intento ocurren en **una sola sentencia** (INSERT ... ON CONFLICT
    DO UPDATE ... RETURNING), así que dos peticiones simultáneas no pueden
    ninguna de las dos "perder" su incremento. Es lo que hace que el límite sea
    cierto bajo concurrencia, que es justamente el escenario de un ataque de
    fuerza bruta (ADR-027 §Decisión).

Por qué PostgreSQL y no memoria del proceso: un contador en memoria se pierde
al reiniciar y no se comparte entre workers, así que con dos workers el límite
real sería el doble del configurado. Es el mismo razonamiento por el que
ADR-025 descartó una lista negra en memoria para revocar tokens, y la razón por
la que el indicador de "escribiendo" de ADR-014 sí podía permitírselo (es
efímero y cosmético; esto es un control de seguridad).

Escrita a mano (no autogenerada), mismo criterio que las migraciones anteriores.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'b6e3a9d4f270'
down_revision = 'a3c9f5b1e648'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'rate_limit_buckets',
        sa.Column(
            'id',
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text('gen_random_uuid()'),
        ),
        sa.Column('scope', sa.String(length=40), nullable=False),
        # SHA-256 en hexadecimal: siempre 64 caracteres, de ahí el CHAR fijo.
        sa.Column('identity_hash', sa.CHAR(length=64), nullable=False),
        sa.Column(
            'window_started_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
        sa.Column(
            'attempts',
            sa.Integer(),
            nullable=False,
            server_default=sa.text('0'),
        ),
        # Sin FK a `users`: la identidad puede ser una IP o un email de una
        # cuenta que no existe (un intento de login contra un email inventado
        # también tiene que contar). Atarla a `users` dejaría fuera justo los
        # casos que más interesa limitar.
        sa.UniqueConstraint('scope', 'identity_hash', name='uq_rate_limit_scope_identity'),
    )

    # La UNIQUE (scope, identity_hash) es el índice que sostiene el UPSERT, que
    # es el único acceso real a esta tabla. No hace falta ninguno más para
    # operar.
    #
    # Este sí hace falta, pero para otra cosa: purgar las filas cuya ventana ya
    # venció. Sin purga la tabla crece con cada IP que haya intentado entrar
    # alguna vez (ADR-027 §Riesgos).
    op.create_index(
        'ix_rate_limit_buckets_window_started_at',
        'rate_limit_buckets',
        ['window_started_at'],
    )


def downgrade():
    op.drop_index(
        'ix_rate_limit_buckets_window_started_at', table_name='rate_limit_buckets'
    )
    op.drop_table('rate_limit_buckets')
