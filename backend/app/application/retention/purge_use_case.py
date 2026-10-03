# Caso de uso: borrar los datos técnicos que superaron su plazo de conservación
# (ADR-037-data-retention.md). Lo llaman dos caminos:
#  - `scripts/purge_expired_data.py`, pensado para un trabajo programado (cron de
#    Render o similar): el camino principal y predecible;
#  - un disparo oportunista y ocasional desde el inicio de sesión
#    (`interfaces/retention_trigger.py`), porque hoy el proyecto no tiene tareas
#    programadas (DevOps sin documentación oficial) y sin esto nada se borraría nunca.

from datetime import datetime, timedelta, timezone

from app.domain.retention.policy import SESSION_RETENTION_DAYS


def purge_expired_data(retention_repository, now=None):
    """Devuelve `{tabla: filas_borradas}`. `now` se inyecta para poder probar con una
    fecha fija."""
    now = now or datetime.now(timezone.utc)
    cutoff = now - timedelta(days=SESSION_RETENTION_DAYS)
    return retention_repository.purge_older_than(cutoff)
