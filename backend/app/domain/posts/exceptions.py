# Excepciones de dominio para `posts` (ADR-005-likes-minimal-model.md).
# Primera excepción propia de `posts` -- hasta este ADR, el único caso de
# error de post_routes.py era validación de `content` (sin excepción, la
# route responde directo). Mismo patrón que domain/auth/exceptions.py.


class PostNotFoundError(Exception):
    """`post_id` no corresponde a ningún post real -- id inventado o con
    formato inválido (aunque el conversor `uuid` de Flask ya descarta el
    segundo caso antes de llegar acá, ver interfaces/routes/like_routes.py)."""
