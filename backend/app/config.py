import os
import sys

_DEV_FALLBACK_JWT_SECRET_KEY = "dev-only-insecure-key-CHANGE-ME"


class Config:
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")

    if not JWT_SECRET_KEY:
        JWT_SECRET_KEY = _DEV_FALLBACK_JWT_SECRET_KEY
        print(
            "[config] JWT_SECRET_KEY no está definida como variable de entorno; "
            "usando un valor de desarrollo inseguro. Definir JWT_SECRET_KEY antes de "
            "cualquier uso fuera de desarrollo local (HB-001 §19.1/§20).",
            file=sys.stderr,
        )