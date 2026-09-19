# Excepciones de dominio para `messages` (ADR-013-messages-minimal-model.md).
# El caso "usuario destinatario no existe" reutiliza UserNotFoundError
# (domain/auth/exceptions.py) -- mismo caso que ya cubre follows/GET
# /api/users/me, no se duplica una excepción equivalente acá.


class CannotMessageSelfError(Exception):
    """Se intentó mandar un mensaje a sí mismo -- `user_id` de la URL
    coincide con `get_jwt_identity()`. Impuesto también a nivel de esquema
    (CHECK ck_messages_no_self_message, ADR-013 §Modelo de datos) -- esta
    excepción es la primera línea de defensa, con un mensaje claro."""
