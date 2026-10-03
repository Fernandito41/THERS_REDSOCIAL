"""add terms acceptance to users and create reports table

Revision ID: a8d2f5c1b937
Revises: f8c2d6a4b190
Create Date: 2026-10-02 00:00:00.000000

ADR-032-content-reports-and-moderation.md, fase 1:
- `users.terms_accepted_at` y `users.terms_version` (ambas NULL: las cuentas
  existentes cuentan como no aceptadas, ADR-032 §5);
- tabla `reports`.

Todo es aditivo: ninguna columna ni tabla existente cambia. Las columnas de
moderación y suspensión (`is_moderator`, `suspended_at`, ...) NO van aquí: son de
la fase 2 y se migran cuando se implemente.

Escrita a mano (no autogenerada), mismo criterio que las migraciones anteriores.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'a8d2f5c1b937'
down_revision = 'f8c2d6a4b190'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('terms_accepted_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('terms_version', sa.String(length=32), nullable=True))

    op.create_table(
        'reports',
        sa.Column(
            'id',
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text('gen_random_uuid()'),
        ),
        # SET NULL: si quien reporta (o el reportado) elimina su cuenta, el
        # reporte sigue (ADR-032 §1, ADR-031).
        sa.Column(
            'reporter_id',
            UUID(as_uuid=True),
            sa.ForeignKey('users.id', ondelete='SET NULL'),
            nullable=True,
        ),
        sa.Column('target_type', sa.String(length=10), nullable=False),
        # Sin clave foránea: apunta a tablas distintas según `target_type`.
        sa.Column('target_id', UUID(as_uuid=True), nullable=False),
        sa.Column(
            'reported_user_id',
            UUID(as_uuid=True),
            sa.ForeignKey('users.id', ondelete='SET NULL'),
            nullable=True,
        ),
        sa.Column('reason', sa.String(length=20), nullable=False),
        sa.Column('details', sa.String(length=500), nullable=True),
        sa.Column('status', sa.String(length=10), nullable=False, server_default=sa.text("'open'")),
        sa.Column('content_snapshot', sa.Text(), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            'resolved_by',
            UUID(as_uuid=True),
            sa.ForeignKey('users.id', ondelete='SET NULL'),
            nullable=True,
        ),
        sa.Column('resolution_note', sa.String(length=500), nullable=True),
    )

    # Reportar lo mismo dos veces es idempotente (ADR-032 §1).
    op.create_index(
        'uq_reports_reporter_target',
        'reports',
        ['reporter_id', 'target_type', 'target_id'],
        unique=True,
    )
    op.create_index('ix_reports_status_created_at', 'reports', ['status', 'created_at'])
    op.create_index('ix_reports_reported_user_id', 'reports', ['reported_user_id'])


def downgrade():
    op.drop_index('ix_reports_reported_user_id', table_name='reports')
    op.drop_index('ix_reports_status_created_at', table_name='reports')
    op.drop_index('uq_reports_reporter_target', table_name='reports')
    op.drop_table('reports')
    op.drop_column('users', 'terms_version')
    op.drop_column('users', 'terms_accepted_at')
