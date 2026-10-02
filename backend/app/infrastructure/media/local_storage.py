# Adaptador de disco local del puerto MediaStorage (ADR-015). Solo para
# desarrollo: en un servicio desplegado el disco es efímero y los archivos
# se perderían en cada despliegue -- usar S3MediaStorage allí.

from pathlib import Path

from app.domain.media.storage import MediaStorage


class LocalMediaStorage(MediaStorage):
    def __init__(self, root):
        self.root = Path(root).resolve()

    def _path(self, key):
        path = (self.root / key).resolve()
        if self.root not in path.parents:
            raise ValueError("clave de almacenamiento fuera del directorio raíz")
        return path

    def save(self, key, data, content_type):
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def delete(self, key):
        self._path(key).unlink(missing_ok=True)
