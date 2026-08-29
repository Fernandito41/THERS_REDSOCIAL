import os
import sys

_DEV_FALLBACK_JWT_SECRET_KEY = "dev-only-insecure-key-CHANGE-ME"


def _normalize_database_url(url):
    # Render (y otros proveedores de PostgreSQL gestionado) entregan la
    # connection string como `postgres://` o `postgresql://`, sin driver
    # explícito. SQLAlchemy 2.x resuelve ese dialecto "a secas" contra
    # psycopg2 por defecto -- que no está instalado (solo `psycopg[binary]`
    # v3, ver requirements.txt) -- y falla con
    # `ModuleNotFoundError: No module named 'psycopg2'` recién al conectar,
    # no al arrancar. Reescribir a `postgresql+psycopg://` aquí hace que la
    # variable de entorno funcione igual venga con o sin driver explícito,
    # sin depender de que cada proveedor la formatee como el proyecto espera.
    if url and url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://"):]
    if url and url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


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

    # Conexión a PostgreSQL (ver docs/architecture/DATABASE_ARCHITECTURE.md).
    # No existe un valor de desarrollo "seguro" para sustituir esta variable como
    # se hace con JWT_SECRET_KEY: sin DATABASE_URL, la app arranca pero cualquier
    # acceso a la base de datos falla al primer uso real.
    SQLALCHEMY_DATABASE_URI = _normalize_database_url(os.environ.get("DATABASE_URL"))
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    if not SQLALCHEMY_DATABASE_URI:
        print(
            "[config] DATABASE_URL no está definida como variable de entorno; "
            "la app arrancará, pero cualquier operación contra la base de datos "
            "fallará. Definir DATABASE_URL "
            "(postgresql+psycopg://usuario:password@host:puerto/nombre_bd) antes de "
            "usar la persistencia real.",
            file=sys.stderr,
        )