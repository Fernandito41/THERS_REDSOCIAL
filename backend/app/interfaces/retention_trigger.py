# Disparo oportunista del borrado por antigüedad (ADR-037-data-retention.md).
#
# Una de cada N sesiones iniciadas se aprovecha para borrar lo vencido. NO sustituye
# a un trabajo programado (`scripts/purge_expired_data.py`): es una red de seguridad
# para que, aunque nadie configure el cron, el plazo de 90 días se cumpla. Mismo
# criterio que la purga de `rate_limit_buckets` (ADR-027).

import random

from app.application.retention.purge_use_case import purge_expired_data
from app.extensions import db
from app.infrastructure.persistence.repositories.retention_repository import (
    SQLAlchemyRetentionRepository,
)

_ONE_IN = 50
_repository = SQLAlchemyRetentionRepository()


def maybe_purge():
    """Con probabilidad 1/50 borra lo vencido. **Nunca lanza**: un fallo de la limpieza
    no puede impedir un inicio de sesión."""
    if random.randrange(_ONE_IN) != 0:
        return
    try:
        purge_expired_data(_repository)
    except Exception:  # noqa: BLE001 -- mantenimiento, no parte de la decisión de acceso
        db.session.rollback()
