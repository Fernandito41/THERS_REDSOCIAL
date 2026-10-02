# Excepciones de dominio para `comments` (ADR-020-comment-deletion.md). El
# caso "post inexistente" sigue siendo PostNotFoundError (domain/posts/
# exceptions.py), ya usado por crear/listar comentarios.


class CommentNotFoundError(Exception):
    """`comment_id` no existe, o existe pero no pertenece a quien intenta
    borrarlo -- mismo mensaje/código en ambos casos, no se distingue cuál
    ocurrió (mismo criterio que MessageNotFoundError, ADR-014)."""
