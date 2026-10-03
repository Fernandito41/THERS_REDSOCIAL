"""add priority to reports (child safety, ADR-038)

Revision ID: b6e1d9a4c2f8
Revises: a8d2f5c1b937
Create Date: 2026-10-02

Prioridad de revisión de un reporte: `normal` o `critical` (los reportes de
explotación o abuso de menores son siempre `critical`; la asigna el servidor).

Migración ADITIVA y no destructiva: los reportes existentes quedan como `normal` (el
valor por defecto), no se borra ni se recrea nada. El motivo `child_safety` NO necesita
migración: el motivo es un texto validado en la aplicación, no un ENUM de PostgreSQL.
"""
from alembic import op
import sqlalchemy as sa

revision = "b6e1d9a4c2f8"
down_revision = "a8d2f5c1b937"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "reports",
        sa.Column("priority", sa.String(length=10), nullable=False, server_default=sa.text("'normal'")),
    )
    op.create_check_constraint("ck_reports_priority", "reports", "priority IN ('normal', 'critical')")
    # Cola de revisión futura: lo crítico primero.
    op.create_index(
        "ix_reports_status_priority_created_at", "reports", ["status", "priority", "created_at"]
    )


def downgrade():
    op.drop_index("ix_reports_status_priority_created_at", table_name="reports")
    op.drop_constraint("ck_reports_priority", "reports", type_="check")
    op.drop_column("reports", "priority")
