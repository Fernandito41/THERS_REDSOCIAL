# Casos de uso de la aceptación de términos (ADR-032 §5).

from datetime import datetime, timezone

from app.application.terms.terms_version import current_terms_version
from app.domain.terms.exceptions import InvalidTermsVersionError
from app.domain.terms.policy import MAX_TERMS_VERSION_LENGTH


def record_terms_acceptance(user_id, version, user_repository):
    """Guarda que `user_id` aceptó la versión `version` de los términos.

    Solo se acepta la versión **vigente**: aceptar una anterior o una inventada
    no vale como aceptación de lo que hoy rige, y un cliente que mostró términos
    viejos (caché, app sin actualizar) debe enterarse y mostrar los actuales.
    Idempotente: aceptar de nuevo la misma versión solo actualiza la fecha."""
    current = current_terms_version()

    if (
        not isinstance(version, str)
        or len(version) > MAX_TERMS_VERSION_LENGTH
        or version != current
    ):
        raise InvalidTermsVersionError(current)

    return user_repository.update(
        user_id, {"terms_accepted_at": datetime.now(timezone.utc), "terms_version": current}
    )
