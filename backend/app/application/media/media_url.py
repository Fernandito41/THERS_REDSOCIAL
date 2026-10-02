# Resuelve la URL pública de un objeto de almacenamiento (ADR-015). Los
# presenters (user/post/comment/message) llaman a `media_url(path)` sin
# conocer Flask ni el proveedor: `create_app()` fija la base una sola vez.

_base_url = ""


def configure_media_url(base_url):
    global _base_url
    _base_url = (base_url or "").rstrip("/")


def media_url(path):
    if not path:
        return None
    return f"{_base_url}/{path}"
