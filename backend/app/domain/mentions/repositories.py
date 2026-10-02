# Puerto (interfaz) del repositorio de mentions. Vive en domain/ porque es un
# contrato de negocio puro -- sin SQLAlchemy, sin Flask, sin PostgreSQL --
# que application/ consume y que infraestructura implementa (mismo patrón
# Repository que domain/follows/repositories.py ya estableció).

from abc import ABC, abstractmethod


class MentionRepository(ABC):
    @abstractmethod
    def replace_for_post(self, post_id, author_id, mentioned_user_ids):
        """Deja las menciones de `post_id` siendo exactamente
        `mentioned_user_ids`: borra las que ya no están y crea las que faltan.
        Devuelve los ids **recién agregados** -- solo a esos hay que
        notificarles (ADR-019 §Decisión: editar un texto no re-notifica a
        quien ya estaba mencionado).

        Es "replace" y no "add" porque editar el texto (ADR-017) tiene que
        poder quitar una mención, no solo sumar."""

    @abstractmethod
    def replace_for_comment(self, comment_id, author_id, mentioned_user_ids):
        """Igual que `replace_for_post`, sobre un comentario."""

    @abstractmethod
    def list_for_posts(self, post_ids):
        """`{post_id: [usuario_mencionado, ...]}` para varios posts a la vez
        -- evita el N+1 de preguntar las menciones post por post al listar el
        feed, mismo patrón que LikeRepository.counts_for_posts.

        Devuelve los **usuarios**, no las filas de `mentions`: la fila en sí
        (su id, su `created_at`) no forma parte del contrato HTTP, y
        devolverla obligaría a cada consumidor a hacer el mismo
        `.mentioned_user`."""

    @abstractmethod
    def list_for_comments(self, comment_ids):
        """`{comment_id: [usuario_mencionado, ...]}`, mismo criterio que
        `list_for_posts`."""
