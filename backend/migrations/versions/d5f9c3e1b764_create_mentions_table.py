"""create mentions table and who_can_mention preference

Revision ID: d5f9c3e1b764
Revises: c3e7b1d9a482
Create Date: 2026-10-01 00:00:00.000000

Menciones con @username (ADR-023-mentions.md —
docs/architecture/ADR-023-mentions.md). Resuelve el control "Menciones y
etiquetas" de la pantalla de Privacidad (REF-SET-02), que era `pending` con el
motivo "No existe el modelo de menciones ni etiquetas".

Dos cambios:

1. Tabla `mentions` — una fila por persona mencionada en una publicación **o**
   en un comentario. `post_id` y `comment_id` son ambas nullable con una CHECK
   que obliga a que exactamente una esté presente: es la misma entidad
   ("alguien fue mencionado en algo"), no dos tablas casi idénticas
   (ADR-023 §Opciones consideradas). Tercera CHECK del esquema, después de
   `ck_follows_no_self_follow` (ADR-007) y `ck_messages_no_self_message`
   (ADR-013).

   La mención se **persiste** en vez de derivarse del texto en cada lectura
   porque el permiso (`who_can_mention`) se evalúa al escribir: si mañana la
   persona cambia su preferencia, las menciones que ya aceptó siguen siendo
   válidas, y un @username que nunca tuvo permiso no se convierte en mención
   retroactivamente (ADR-023 §Decisión).

2. `users.who_can_mention` — `VARCHAR(20) NOT NULL DEFAULT 'everyone'`
   ('everyone' | 'followers' | 'nobody'). `'everyone'` preserva el
   comportamiento más abierto, que es el que había de hecho hasta ahora (no
   existían las menciones, así que nadie tenía una preferencia que respetar).
   Discriminador validado en la aplicación, no ENUM de PostgreSQL -- mismo
   criterio que `notifications.type` (ADR-008) y `follows.status` (ADR-022).

Escrita a mano (no autogenerada), mismo criterio que las migraciones
anteriores.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'd5f9c3e1b764'
down_revision = 'c3e7b1d9a482'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'users',
        sa.Column(
            'who_can_mention',
            sa.String(length=20),
            nullable=False,
            server_default=sa.text("'everyone'"),
        ),
    )

    op.create_table(
        'mentions',
        sa.Column(
            'id',
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text('gen_random_uuid()'),
        ),
        # A quién se mencionó.
        sa.Column(
            'mentioned_user_id',
            UUID(as_uuid=True),
            sa.ForeignKey('users.id', ondelete='CASCADE'),
            nullable=False,
        ),
        # Quién la escribió -- redundante con posts.author_id/comments.author_id,
        # pero guardarlo evita un JOIN en cada lectura y deja la fila
        # auto-explicativa (ADR-023 §Modelo de datos).
        sa.Column(
            'author_id',
            UUID(as_uuid=True),
            sa.ForeignKey('users.id', ondelete='CASCADE'),
            nullable=False,
        ),
        # Exactamente una de las dos, impuesto por la CHECK de abajo.
        sa.Column(
            'post_id',
            UUID(as_uuid=True),
            sa.ForeignKey('posts.id', ondelete='CASCADE'),
            nullable=True,
        ),
        sa.Column(
            'comment_id',
            UUID(as_uuid=True),
            sa.ForeignKey('comments.id', ondelete='CASCADE'),
            nullable=True,
        ),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
        sa.CheckConstraint(
            '(post_id IS NULL) <> (comment_id IS NULL)',
            name='ck_mentions_exactly_one_target',
        ),
    )

    # Dos UNIQUE parciales en vez de una sola: la misma persona no se menciona
    # dos veces en el mismo texto (escribir "@ana @ana" genera una sola
    # mención), pero una UNIQUE sobre (mentioned_user_id, post_id, comment_id)
    # no serviría -- en PostgreSQL dos filas con NULL en una columna del índice
    # no se consideran duplicadas, así que no impediría nada
    # (ADR-023 §Índices).
    op.create_index(
        'uq_mentions_user_post',
        'mentions',
        ['mentioned_user_id', 'post_id'],
        unique=True,
        postgresql_where=sa.text('post_id IS NOT NULL'),
    )
    op.create_index(
        'uq_mentions_user_comment',
        'mentions',
        ['mentioned_user_id', 'comment_id'],
        unique=True,
        postgresql_where=sa.text('comment_id IS NOT NULL'),
    )

    # Resolver "¿a quién menciona este post/comentario?" al renderizarlo.
    op.create_index('ix_mentions_post_id', 'mentions', ['post_id'])
    op.create_index('ix_mentions_comment_id', 'mentions', ['comment_id'])


def downgrade():
    op.drop_index('ix_mentions_comment_id', table_name='mentions')
    op.drop_index('ix_mentions_post_id', table_name='mentions')
    op.drop_index('uq_mentions_user_comment', table_name='mentions')
    op.drop_index('uq_mentions_user_post', table_name='mentions')
    op.drop_table('mentions')
    op.drop_column('users', 'who_can_mention')
