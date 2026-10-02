# Validación y normalización de imágenes subidas (ADR-015). Única pieza que
# importa Pillow. Decodifica el contenido real, aplica la orientación EXIF,
# recorta al aspecto pedido y re-codifica a WebP: el archivo original nunca
# se guarda tal cual, así se descartan EXIF/GPS y cualquier payload
# escondido dentro del archivo.

import io

from PIL import Image, ImageOps, UnidentifiedImageError

from app.domain.media.storage import ImageTooLargeError, InvalidImageError

ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}
MAX_UPLOAD_BYTES = 5 * 1024 * 1024
# Protege contra "decompression bombs" (archivo pequeño, píxeles enormes).
Image.MAX_IMAGE_PIXELS = 40_000_000

# kind -> (ancho, alto) de salida. El recorte es centrado.
TARGET_SIZES = {
    "avatar": (512, 512),
    "cover": (1600, 500),
}


def process_image(raw, kind):
    if len(raw) > MAX_UPLOAD_BYTES:
        raise ImageTooLargeError()

    try:
        with Image.open(io.BytesIO(raw)) as probe:
            if probe.format not in ALLOWED_FORMATS:
                raise InvalidImageError()
            probe.load()
            image = ImageOps.exif_transpose(probe)
            image = ImageOps.fit(image.convert("RGB"), TARGET_SIZES[kind], Image.LANCZOS)
    except InvalidImageError:
        raise
    except (UnidentifiedImageError, OSError, SyntaxError, Image.DecompressionBombError):
        raise InvalidImageError()

    out = io.BytesIO()
    image.save(out, format="WEBP", quality=85, method=4)
    return out.getvalue(), "image/webp"
