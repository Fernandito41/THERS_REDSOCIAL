# Prueba el fail-fast de JWT_SECRET_KEY (backend/app/config.py). Corre en un
# subproceso aislado a propósito: `Config` es una clase cuyo cuerpo se
# ejecuta una sola vez, en el primer `import` -- Python cachea el módulo, y
# conftest.py ya importa `app.config` con un JWT_SECRET_KEY real antes de
# que corra cualquier otro test de este proceso. No hay forma de probar "la
# variable no está definida" reimportando dentro del mismo proceso de
# pytest; un subproceso nuevo sí arranca con el import-cache vacío.

import os
import subprocess
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent


def _import_config_in_subprocess(env_overrides):
    env = os.environ.copy()
    env.pop("JWT_SECRET_KEY", None)
    env.pop("ALLOW_INSECURE_JWT_DEV_FALLBACK", None)
    # DATABASE_URL no se conecta al importar Config (solo se arma el string),
    # pero se define igual para que su propia advertencia no ensucie stderr
    # y el test se quede enfocado en JWT_SECRET_KEY.
    env.setdefault(
        "DATABASE_URL", "postgresql+psycopg://thers:changeme@localhost/thers_test"
    )
    env.update(env_overrides)

    return subprocess.run(
        [sys.executable, "-c", "from app.config import Config"],
        cwd=str(BACKEND_DIR),
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )


class TestJwtSecretKeyFailFast:
    def test_missing_key_without_opt_in_flag_fails_to_start(self):
        result = _import_config_in_subprocess({})

        assert result.returncode != 0
        assert "JWT_SECRET_KEY" in result.stderr
        assert "ALLOW_INSECURE_JWT_DEV_FALLBACK" in result.stderr

    def test_missing_key_with_opt_in_flag_uses_dev_fallback(self):
        result = _import_config_in_subprocess({"ALLOW_INSECURE_JWT_DEV_FALLBACK": "1"})

        assert result.returncode == 0, result.stderr

    def test_opt_in_flag_with_wrong_value_still_fails(self):
        # "true"/"yes"/etc. no cuentan -- solo "1" exacto, para que no sea
        # fácil dejarlo mal configurado sin darse cuenta.
        result = _import_config_in_subprocess({"ALLOW_INSECURE_JWT_DEV_FALLBACK": "true"})

        assert result.returncode != 0

    def test_real_key_never_needs_the_opt_in_flag(self):
        result = _import_config_in_subprocess({"JWT_SECRET_KEY": "a-real-secret-value"})

        assert result.returncode == 0, result.stderr
