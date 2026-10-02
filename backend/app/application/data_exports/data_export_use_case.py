# Casos de uso de la exportación de datos (POST/GET /api/data-exports,
# GET /api/data-exports/<id>/download -- ADR-024-data-export.md).
#
# `user_id` sale exclusivamente del JWT en la route: nadie genera ni descarga
# el archivo de otra persona.

from datetime import datetime, timedelta, timezone

from app.application.data_exports.archive_builder import build_archive
from app.domain.data_exports import policy
from app.domain.data_exports.exceptions import (
    DataExportCooldownError,
    DataExportExpiredError,
    DataExportNotFoundError,
)


def _now():
    return datetime.now(timezone.utc)


def _is_expired(export):
    return export.content is None or export.expires_at <= _now()


def to_public_export(export):
    return {
        "id": str(export.id),
        "file_name": export.file_name,
        "size_bytes": export.size_bytes,
        "status": "expired" if _is_expired(export) else "ready",
        "created_at": export.created_at.isoformat(),
        "expires_at": export.expires_at.isoformat(),
        "downloaded_at": export.downloaded_at.isoformat() if export.downloaded_at else None,
        "download_count": export.download_count,
    }


def request_export(user_id, repository):
    """Genera el archivo en el momento. Es síncrono a propósito: el volumen de
    datos de una cuenta es chico y una cola de trabajos sería infraestructura
    que el proyecto no tiene (ADR-024 §Opciones consideradas)."""
    now = _now()

    latest = repository.latest_created_at(user_id)
    if latest is not None:
        elapsed = (now - latest).total_seconds()
        if elapsed < policy.EXPORT_COOLDOWN_SECONDS:
            raise DataExportCooldownError(int(policy.EXPORT_COOLDOWN_SECONDS - elapsed) + 1)

    data = repository.collect_user_data(user_id)
    content = build_archive(data, now, policy.EXPORT_TTL_DAYS)
    file_name = f"thers-datos-{data['profile']['username']}-{now:%Y%m%d}.zip"

    export = repository.create(
        user_id, file_name, content, now + timedelta(days=policy.EXPORT_TTL_DAYS)
    )
    return to_public_export(export)


def list_exports(user_id, repository):
    repository.discard_expired_content(user_id)
    exports = repository.list_for_user(user_id, policy.HISTORY_LIMIT)
    return [to_public_export(e) for e in exports]


def get_export_file(user_id, export_id, repository):
    """Devuelve `(file_name, bytes)`. Registra la descarga."""
    export = repository.get_for_user(export_id, user_id)
    if export is None:
        raise DataExportNotFoundError()
    if _is_expired(export):
        raise DataExportExpiredError()

    repository.mark_downloaded(export.id)
    return export.file_name, export.content
