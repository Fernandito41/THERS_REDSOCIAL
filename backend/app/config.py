import os
import sys

_DEV_FALLBACK_JWT_SECRET_KEY = "dev-only-insecure-key-CHANGE-ME"

# Antes de que existiera un despliegue real (Render, ver `_normalize_database_url`
# abajo), que este valor cayera al fallback inseguro solo importaba en un
# entorno local. Con un despliegue real ya en marcha, un `JWT_SECRET_KEY` sin
# definir en ese entorno firmaría JWTs con una clave pública (este mismo
# archivo, en el repositorio) -- cualquiera podría forjar un token válido para
# cualquier `user_id` y tomar cualquier cuenta. Por eso el fallback dejó de ser
# automático: hace falta pedirlo explícitamente con esta variable, pensada
# exclusivamente para desarrollo local -- nunca debe definirse en Render ni en
# ningún entorno accesible desde internet.
_ALLOW_INSECURE_JWT_FALLBACK_VAR = "ALLOW_INSECURE_JWT_DEV_FALLBACK"


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
        if os.environ.get(_ALLOW_INSECURE_JWT_FALLBACK_VAR) == "1":
            JWT_SECRET_KEY = _DEV_FALLBACK_JWT_SECRET_KEY
            print(
                "[config] JWT_SECRET_KEY no está definida; usando el valor de "
                f"desarrollo inseguro porque {_ALLOW_INSECURE_JWT_FALLBACK_VAR}=1 "
                "lo pidió explícitamente. Nunca definir esa variable fuera de "
                "desarrollo local (HB-001 §19.1/§20).",
                file=sys.stderr,
            )
        else:
            # Falla al arrancar la app, no en el primer login -- un secreto
            # ausente en un entorno desplegado es un hueco de seguridad, no
            # una advertencia. `backend/.env.example` ya trae
            # ALLOW_INSECURE_JWT_DEV_FALLBACK=1 para que el flujo de
            # desarrollo local (`cp .env.example .env`) siga funcionando sin
            # pasos extra; un despliegue real (Render u otro) nunca debe
            # copiar ese archivo ni definir esa variable.
            raise RuntimeError(
                "JWT_SECRET_KEY no está definida como variable de entorno. "
                "Esta aplicación ya no arranca con un secreto inseguro por "
                "defecto (HB-001 §19.1/§20). Para desarrollo local sin una "
                "clave real, definir explícitamente "
                f"{_ALLOW_INSECURE_JWT_FALLBACK_VAR}=1 (ver "
                "backend/.env.example) -- nunca en un entorno desplegado."
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