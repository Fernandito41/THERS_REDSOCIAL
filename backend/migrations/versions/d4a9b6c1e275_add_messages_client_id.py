"""add messages.client_id for idempotent sends (ADR-035)

Revision ID: d4a9b6c1e275
Revises: c3f7a9d2e841
Create Date: 2026-10-02

Identificador que elige quien envía un mensaje, para que reintentar un envío que
falló a medias no cree el mensaje dos veces. NULL en los mensajes existentes y en
los de clientes que no lo mandan. Único por remitente (índice parcial).
"""
from alembic import op
import sqlalchemy as sa

revision = "d4a9b6c1e275"
down_revision = "c3f7a9d2e841"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("messages", sa.Column("client_id", sa.String(length=64), nullable=True))
    op.create_index(
        "uq_messages_sender_client_id",
        "messages",
        ["sender_id", "client_id"],
        unique=True,
        postgresql_where=sa.text("client_id IS NOT NULL"),
    )


def downgrade():
    op.drop_index("uq_messages_sender_client_id", table_name="messages")
    op.drop_column("messages", "client_id")
