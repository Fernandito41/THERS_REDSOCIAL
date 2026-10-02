"""create data exports table

Revision ID: c4d8e2a6f913
Revises: b6e3a9d4f270
Create Date: 2026-10-01 00:00:00.000000

Exportación de datos personales (ADR-028-data-export.md —
docs/architecture/ADR-028-data-export.md). Una fila por archivo ZIP generado.

`content` guarda el ZIP mientras no caduque y pasa a NULL al caducar; la fila
queda como historial. Va en la base y no en disco porque el proyecto no tiene
almacenamiento de archivos (mismo razonamiento que `rate_limit_buckets`).

Escrita a mano (no autogenerada), mismo criterio que las migraciones anteriores.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'c4d8e2a6f913'
down_revision = 'b6e3a9d4f270'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'data_exports',
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
        sa.Column('file_name', sa.String(length=120), nullable=False),
        sa.Column('size_bytes', sa.Integer(), nullable=False),
        sa.Column('content', sa.LargeBinary(), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('downloaded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            'download_count',
            sa.Integer(),
            nullable=False,
            server_default=sa.text('0'),
        ),
    )
    op.create_index(
        'ix_data_exports_user_created',
        'data_exports',
        ['user_id', 'created_at'],
    )


def downgrade():
    op.drop_index('ix_data_exports_user_created', table_name='data_exports')
    op.drop_table('data_exports')
