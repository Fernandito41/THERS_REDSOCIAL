# Puerto de almacenamiento de imágenes de perfil (ADR-015-profile-media.md).
# El dominio/aplicación solo conocen este contrato; el adaptador concreto
# (disco local, S3-compatible) se elige por configuración en
# infrastructure/media/factory.py -- así pasar de disco local a Supabase
# Storage/R2 no toca ningún caso de uso.


class MediaStorage:
    def save(self, key, data, content_type):
        """Guarda `data` (bytes) bajo `key`. Sobrescribe si existe."""
        raise NotImplementedError

    def delete(self, key):
        """Elimina `key`. No falla si no existe."""
        raise NotImplementedError


class InvalidImageError(Exception):
    """El archivo no es una imagen JPEG/PNG/WebP válida (se valida por
    contenido, no por extensión ni Content-Type declarado)."""


class ImageTooLargeError(Exception):
    """El archivo o sus dimensiones superan los límites permitidos."""
