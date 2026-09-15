import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# `flask db ...` (Flask-Migrate) ya cargaba backend/.env solo -- el CLI de
# Flask detecta python-dotenv instalado y llama a load_dotenv() internamente
# antes de ejecutar cualquier comando. `python run.py` (el punto de entrada
# real de THERS, CLAUDE.md §11) es un script Python plano que nunca pasa por
# ese CLI, así que nunca cargaba `.env` -- cualquier variable definida
# únicamente ahí (p. ej. RESEND_API_KEY) nunca llegaba a os.environ al
# arrancar así, aunque `flask db upgrade` sí la viera. Se llama acá,
# explícitamente, para que ambos caminos de arranque (y pytest, y gunicorn)
# se comporten igual.
#
# Ruta explícita a backend/.env (no el default de find_dotenv(), que busca
# hacia arriba desde el CWD/el archivo que llama) -- así funciona igual sin
# importar desde qué directorio se invoque `python run.py`. `override=False`
# (el default) significa que una variable ya presente en el entorno real
# (p. ej. inyectada por Render en producción, o fijada explícitamente antes
# de este import por backend/tests/conftest.py) nunca se pisa con lo que
# diga `.env` -- load_dotenv() solo completa lo que falte.
#
# THERS_SKIP_DOTENV: escape hatch exclusivo para
# tests/test_config_jwt_secret.py, que arranca subprocesos aislados
# justamente para simular un entorno SIN JWT_SECRET_KEY (fail-fast, HB-001
# §19.1/§20) -- sin este flag, esos subprocesos igual encontrarían el
# `backend/.env` real de quien corre los tests (siempre en la misma ruta,
# sin importar el cwd del subproceso) y el escenario que intentan simular
# dejaría de ser reproducible. Nadie más debe definir esta variable.
if not os.environ.get("THERS_SKIP_DOTENV"):
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")

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

    # Correo electrónico vía Resend (ADR-009-password-reset-and-email-verification.md).
    # Sin RESEND_API_KEY, infrastructure/email/ nunca instancia un
    # ResendEmailSender real -- usa un NullEmailSender que solo registra el
    # intento por log, sin fallar (mismo criterio explícito-nunca-silencioso
    # que ALLOW_INSECURE_JWT_DEV_FALLBACK arriba, pero sin necesitar una
    # variable extra para "permitirlo": no enviar emails de verdad en
    # desarrollo local es un fallback razonable por defecto, a diferencia de
    # firmar JWTs con una clave pública).
    RESEND_API_KEY = os.environ.get("RESEND_API_KEY")

    if not RESEND_API_KEY:
        print(
            "[config] RESEND_API_KEY no está definida; los correos "
            "(recuperación de contraseña, verificación de email) no se "
            "enviarán de verdad -- se usará un EmailSender nulo que solo "
            "registra el intento por log. Definir RESEND_API_KEY en "
            "backend/.env para probar el envío real con Resend.",
            file=sys.stderr,
        )

    # Dirección "from" de los correos enviados por THERS. "onboarding@resend.dev"
    # es el valor que la propia documentación de onboarding de Resend ofrece
    # para probar envíos sin verificar un dominio propio -- válido como
    # fallback de desarrollo, no para un entorno real (ver backend/.env.example).
    EMAIL_FROM = os.environ.get("EMAIL_FROM", "onboarding@resend.dev")

    # Origen del Frontend -- usado para construir los enlaces de recuperación
    # de contraseña/verificación de email que van dentro de esos correos
    # (nunca hardcodeados en la plantilla, ver application/email/templates.py).
    FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")