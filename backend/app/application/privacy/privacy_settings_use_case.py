# Casos de uso: leer y actualizar las preferencias de privacidad
# (GET y PATCH /api/users/me/privacy -- ADR-022-private-accounts.md,
# ADR-023-mentions.md, ADR-024-content-filters-and-privacy-preferences.md).
#
# Los dos en el mismo módulo porque son las dos mitades del mismo recurso y
# comparten presenter, igual que get/update del perfil están repartidos por
# simetría con sus endpoints. `user_id` sale exclusivamente de
# get_jwt_identity() en la route: nadie lee ni cambia la privacidad de otro.

from app.application.privacy.privacy_presenter import to_privacy_settings
from app.domain.auth.exceptions import UserNotFoundError


def get_privacy_settings(user_id, user_repository, follow_repository):
    user = user_repository.find_by_id(user_id)
    if user is None:
        raise UserNotFoundError()

    return to_privacy_settings(
        user, follow_repository.pending_requests_count(user_id)
    )


def update_privacy_settings(user_id, fields, user_repository, follow_repository):
    # `fields` ya viene filtrado y validado por la route (whitelist explícita,
    # mismo principio anti mass-assignment que PATCH /api/users/me, ADR-003
    # §Seguridad) -- este caso de uso no decide qué es editable.
    user = user_repository.update(user_id, fields)
    if user is None:
        raise UserNotFoundError()

    # Volverse privado NO convierte a los seguidores actuales en solicitudes
    # pendientes: quien ya tenía acceso lo conserva (ADR-022 §Decisión). Por eso
    # acá no hay ningún recálculo de `follows` -- el interruptor solo cambia qué
    # pasa con los follows FUTUROS.
    return to_privacy_settings(
        user, follow_repository.pending_requests_count(user_id)
    )
