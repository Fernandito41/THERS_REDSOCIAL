"""add private accounts and follow status

Revision ID: c3e7b1d9a482
Revises: a2c6e9b3f571
Create Date: 2026-10-01 00:00:00.000000

Cuenta privada y solicitudes de seguimiento (ADR-018-private-accounts.md —
docs/architecture/ADR-018-private-accounts.md). Resuelve el primer control de
la pantalla de Privacidad (REF-SET-02), que hasta ahora era `pending` con el
motivo "Requiere que el servidor filtre cada consulta por relación de
seguimiento".

Dos cambios, uno por tabla:

1. `users.is_private` — `BOOLEAN NOT NULL DEFAULT false`. `false` preserva
   exactamente el comportamiento actual para todas las cuentas existentes:
   nadie se vuelve privado por efecto de esta migración.

2. `follows.status` — `VARCHAR(20) NOT NULL DEFAULT 'accepted'`. Un follow
   deja de ser un hecho binario (existe/no existe) y pasa a tener dos
   estados: 'pending' (solicitud sin responder, solo posible hacia una cuenta
   privada) y 'accepted'. El `server_default` 'accepted' hace de backfill de
   las filas que ya existían: todo follow previo a esta migración se hizo
   hacia una cuenta pública, así que ya estaba aceptado de hecho.

Discriminador como `VARCHAR(20)` validado en la aplicación, no `ENUM` de
PostgreSQL — mismo criterio que `notifications.type` (ADR-008): agregar un
estado nuevo no exige un `ALTER TYPE`.

Sin índice nuevo: listar solicitudes pendientes filtra por
`followed_id` + `status`, y el `ix_follows_followed_id` que ya existe
(ADR-007) lidera por `followed_id` — basta para esa consulta, que además
devuelve pocas filas (ADR-018 §Índices).

Escrita a mano (no autogenerada), mismo criterio que las migraciones
anteriores.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3e7b1d9a482'
down_revision = 'a2c6e9b3f571'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'users',
        sa.Column(
            'is_private',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
        ),
    )
    op.add_column(
        'follows',
        sa.Column(
            'status',
            sa.String(length=20),
            nullable=False,
            server_default=sa.text("'accepted'"),
        ),
    )


def downgrade():
    op.drop_column('follows', 'status')
    op.drop_column('users', 'is_private')
