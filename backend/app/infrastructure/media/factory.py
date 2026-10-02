# Elige el adaptador de almacenamiento según configuración (ADR-015).
# STORAGE_BACKEND=local (default, desarrollo) | s3 (staging/producción).

from app.infrastructure.media.local_storage import LocalMediaStorage


def build_media_storage(config):
    backend = (config.get("STORAGE_BACKEND") or "local").lower()

    if backend == "s3":
        from app.infrastructure.media.s3_storage import S3MediaStorage

        missing = [
            name
            for name in ("S3_BUCKET", "S3_ACCESS_KEY_ID", "S3_SECRET_ACCESS_KEY")
            if not config.get(name)
        ]
        if missing:
            raise RuntimeError("STORAGE_BACKEND=s3 requiere definir: " + ", ".join(missing))
        return S3MediaStorage(
            bucket=config["S3_BUCKET"],
            endpoint_url=config.get("S3_ENDPOINT_URL"),
            access_key_id=config["S3_ACCESS_KEY_ID"],
            secret_access_key=config["S3_SECRET_ACCESS_KEY"],
            region=config.get("S3_REGION"),
        )

    if backend != "local":
        raise RuntimeError(f"STORAGE_BACKEND desconocido: {backend!r}")

    return LocalMediaStorage(config["UPLOAD_DIR"])
