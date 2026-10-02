"""add edited_at to posts, comments and messages

Revision ID: a2c6e9b3f571
Revises: f7a2c9e4d1b8
Create Date: 2026-10-01 00:00:00.000000

Edición de contenido propio (ADR-017-content-editing.md —
docs/architecture/ADR-017-content-editing.md). Una única columna `edited_at`
nullable en las tres tablas que ganan edición: NULL = nunca editado, y la API
la expone como el booleano `edited`, nunca como timestamp crudo (mismo criterio
que `messages.read_at`/`notifications.read_at`, ADR-008/ADR-013).

No reutiliza `updated_at` (que `posts`/`comments` ya tienen y `messages` no):
ese timestamp nace igual a `created_at` por su server_default, así que
"editado" tendría que inferirse de `updated_at > created_at` -- una condición
implícita que cualquier escritura futura sobre la fila volvería falsa. Ver
ADR-017 §Opciones consideradas.

Una sola revisión para las tres tablas, no tres: es la misma decisión aplicada
a tres entidades, con el mismo tipo de columna y la misma semántica.

Escrita a mano (no autogenerada), mismo criterio que las migraciones anteriores.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a2c6e9b3f571'
down_revision = 'f7a2c9e4d1b8'
branch_labels = None
depends_on = None


# Las tres tablas reciben exactamente la misma columna -- se recorren en vez
# de repetir el mismo add_column tres veces.
_TABLES = ('posts', 'comments', 'messages')


def upgrade():
    for table in _TABLES:
        # nullable=True sin server_default: las filas que ya existen quedan en
        # NULL, que es precisamente "nunca editado" -- no hace falta backfill
        # ni un valor centinela.
        op.add_column(
            table,
            sa.Column('edited_at', sa.DateTime(timezone=True), nullable=True),
        )


def downgrade():
    for table in reversed(_TABLES):
        op.drop_column(table, 'edited_at')
