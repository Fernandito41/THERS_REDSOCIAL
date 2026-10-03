"""create account_deletion_codes (ADR-031)

Revision ID: c3f7a9d2e841
Revises: b6e1d9a4c2f8
Create Date: 2026-10-02

Códigos de un solo uso para confirmar la eliminación de una cuenta. Tabla
propia (no `password_reset_tokens`): un código de recuperación NUNCA debe
servir para borrar una cuenta (mismo razonamiento que ADR-011).
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "c3f7a9d2e841"
down_revision = "b6e1d9a4c2f8"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "account_deletion_codes",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("code_hash", sa.Text(), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    # A lo sumo un código activo por cuenta.
    op.create_index(
        "uq_account_deletion_codes_active_user",
        "account_deletion_codes",
        ["user_id"],
        unique=True,
        postgresql_where=sa.text("used_at IS NULL"),
    )


def downgrade():
    op.drop_index("uq_account_deletion_codes_active_user", table_name="account_deletion_codes")
    op.drop_table("account_deletion_codes")
