# Caso de uso: saber si otro usuario te está escribiendo en este momento
# (GET /api/users/<user_id>/typing, ADR-014-messages-ux-improvements.md).


def get_typing_status(
    current_user_id, other_user_id, typing_repository, restriction_repository
):
    if restriction_repository.is_blocked_between(current_user_id, other_user_id):
        return {"typing": False}

    typing = typing_repository.is_typing(other_user_id, current_user_id)
    return {"typing": typing}
