"""add content filters, DM privacy and activity status

Revision ID: e7b2d4f8c916
Revises: d5f9c3e1b764
Create Date: 2026-10-01 00:00:00.000000

Filtros de contenido, privacidad de mensajes directos y estado de actividad
(ADR-024-content-filters-and-privacy-preferences.md). Resuelve los tres
controles restantes de la pantalla de Privacidad (REF-SET-02):
"Ocultar comentarios ofensivos", "Filtros de palabras clave personalizadas",
"Mensajes directos" y "Estado de actividad".

Cambios:

1. Tabla `muted_keywords` — términos que cada persona define para no ver.
   `keyword` se guarda ya normalizada en minúsculas (lo hace la aplicación,
   domain/moderation/keyword_matching.py) y la UNIQUE (user_id, keyword)
   impide duplicados. Es una tabla y no un array/JSON en `users` porque hay
   que poder buscar "¿algún keyword de este usuario aparece en este texto?"
   desde SQL, dentro del mismo WHERE que lista los comentarios
   (ADR-024 §Opciones consideradas).

2. `users.hide_offensive_comments` — `BOOLEAN NOT NULL DEFAULT false`.
   `false` preserva el comportamiento actual: nadie empieza a ver su hilo
   filtrado sin haberlo pedido. La lista de términos del sistema vive en el
   repositorio (domain/moderation/offensive_words.py), no en la base de datos
   -- es un placeholder revisable por el equipo, igual que
   MAX_CONTENT_LENGTH, no dato de usuario (ADR-024 §Decisión).

3. `users.who_can_message` — `VARCHAR(20) NOT NULL DEFAULT 'everyone'`
   ('everyone' | 'followers' | 'nobody'). `'everyone'` es el comportamiento
   que ya tenía `POST /api/users/<id>/messages` desde ADR-013.

4. `users.show_activity_status` — `BOOLEAN NOT NULL DEFAULT true`, y
   `users.last_seen_at` — `TIMESTAMPTZ` nullable (NULL = nunca visto, o
   actividad oculta). El DEFAULT true es deliberado y es la única preferencia
   de esta migración que nace "abierta": hasta ahora no había ningún dato de
   presencia, así que activarlo no expone nada retroactivo -- `last_seen_at`
   arranca en NULL para todo el mundo y solo se llena con actividad posterior
   a esta migración.

Escrita a mano (no autogenerada), mismo criterio que las migraciones
anteriores.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'e7b2d4f8c916'
down_revision = 'd5f9c3e1b764'
branch_labels = None
depends_on = None


_NEW_USER_COLUMNS = (
    ('hide_offensive_comments', sa.Boolean(), sa.text('false')),
    ('who_can_message', sa.String(length=20), sa.text("'everyone'")),
    ('show_activity_status', sa.Boolean(), sa.text('true')),
)


def upgrade():
    for name, type_, default in _NEW_USER_COLUMNS:
        op.add_column(
            'users',
            sa.Column(name, type_, nullable=False, server_default=default),
        )

    # Nullable y sin default: NULL = "nunca se registró actividad". No se
    # rellena con now() -- eso afirmaría que todo el mundo estuvo activo en el
    # instante de la migración (ADR-024 §Modelo de datos).
    op.add_column(
        'users',
        sa.Column('last_seen_at', sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        'muted_keywords',
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
        # Normalizada a minúsculas por la aplicación antes de insertar, así
        # que la UNIQUE de abajo distingue términos de verdad distintos y no
        # variaciones de mayúsculas. Longitud acotada en el esquema (a
        # diferencia de `content`, que es TEXT): un keyword no es un texto
        # libre, y el límite real (60) lo valida la aplicación.
        sa.Column('keyword', sa.String(length=100), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
        sa.UniqueConstraint('user_id', 'keyword', name='uq_muted_keywords_user_keyword'),
    )

    # Sin índice adicional: la UNIQUE (user_id, keyword) ya lidera por
    # `user_id`, que es el único patrón de acceso real ("los keywords de este
    # usuario") -- mismo razonamiento que `likes` (ADR-005 §Índices), que
    # tampoco necesitó uno aparte.


def downgrade():
    op.drop_table('muted_keywords')
    op.drop_column('users', 'last_seen_at')
    for name, _type, _default in reversed(_NEW_USER_COLUMNS):
        op.drop_column('users', name)
