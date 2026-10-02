"""create sessions table and login alerts preference

Revision ID: f1a4c8e2d573
Revises: e7b2d4f8c916
Create Date: 2026-10-01 00:00:00.000000

Registro de sesiones y alertas de inicio de sesión (ADR-025-session-registry.md
— docs/architecture/ADR-025-session-registry.md). Resuelve "Sesiones activas" y
"Alertas de inicio de sesión" de la pantalla de Seguridad (REF-SET-03), que
estaban marcadas como `pending` con el motivo "El JWT no se registra por
dispositivo, así que no hay nada que listar ni revocar de verdad".

Ese motivo era exacto, y esta migración es lo que lo deja de ser: el JWT pasa
de ser puramente *stateless* a tener una fila que lo representa. Es un cambio
arquitectónico, no una columna más -- ver ADR-025 §Opciones consideradas.

1. Tabla `sessions` — una fila por token emitido. `jti` (el identificador único
   que flask_jwt_extended ya pone en cada JWT) es la bisagra: el token sigue
   siendo autocontenido y firmado, pero ahora además se comprueba que su `jti`
   tenga una sesión viva. Revocar es un UPDATE sobre `revoked_at`, no una lista
   negra en memoria que se pierda al reiniciar.

2. `users.login_alerts_enabled` — `BOOLEAN NOT NULL DEFAULT true`. Nace
   **activada**, a diferencia de casi todas las preferencias añadidas hasta
   ahora: avisar de un acceso desconocido protege la cuenta, y una alerta de
   seguridad que hay que descubrir y encender no protege a nadie. Sin
   `RESEND_API_KEY` el envío es un no-op registrado por log (igual que el resto
   de correos), así que activarla por defecto no rompe el desarrollo local.

Escrita a mano (no autogenerada), mismo criterio que las migraciones anteriores.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'f1a4c8e2d573'
down_revision = 'e7b2d4f8c916'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'users',
        sa.Column(
            'login_alerts_enabled',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('true'),
        ),
    )

    op.create_table(
        'sessions',
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
        # `jti` del JWT: lo genera flask_jwt_extended (un UUID v4 en texto, 36
        # caracteres). VARCHAR(36) y no UUID nativo a propósito -- es un valor
        # que produce la librería, no el esquema, y tratarlo como texto evita
        # depender de que su formato siga siendo exactamente un UUID.
        sa.Column('jti', sa.String(length=36), nullable=False),
        # Lo que el navegador dijo de sí mismo. TEXT y nullable: un cliente
        # puede no mandar User-Agent, y no se valida ni se parsea en el
        # servidor -- se guarda crudo y es el Frontend quien lo resume para
        # mostrarlo (ADR-025 §Decisión).
        sa.Column('user_agent', sa.Text(), nullable=True),
        # 45 caracteres: longitud máxima de una IPv6 en texto, incluido el
        # formato mapeado a IPv4 (::ffff:255.255.255.255).
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
        # Se actualiza con throttle en cada petición autenticada, igual que
        # `users.last_seen_at` (ADR-024) y por el mismo motivo: sin throttle, el
        # polling del chat escribiría en cada request.
        sa.Column(
            'last_used_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
        # NULL = sesión viva. Revocar no borra la fila: así "cerrar sesión en
        # ese dispositivo" queda registrado y la lista puede distinguir una
        # sesión que terminó de una que nunca existió (ADR-025 §Decisión).
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint('jti', name='uq_sessions_jti'),
    )

    # Listar las sesiones de una persona, más reciente primero. La UNIQUE de
    # `jti` ya cubre el acceso caliente (la comprobación por token en cada
    # petición protegida), pero no este -- lidera por una columna distinta.
    op.create_index(
        'ix_sessions_user_id_created_at',
        'sessions',
        ['user_id', 'created_at'],
    )


def downgrade():
    op.drop_index('ix_sessions_user_id_created_at', table_name='sessions')
    op.drop_table('sessions')
    op.drop_column('users', 'login_alerts_enabled')
