from flask import jsonify
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

jwt = JWTManager()
db = SQLAlchemy()
migrate = Migrate()


# GET /api/users/me (ADR-002 §3) es el primer endpoint protegido del backend
# -- por defecto, flask_jwt_extended responde 401 solo cuando falta el header
# o el token expiró, pero 422 cuando el token está malformado/es inválido.
# Fase 14 de la tarea pide 401 uniforme para "sin JWT", "JWT inválido" y "JWT
# expirado", así que se homogeniza acá (aplica a cualquier endpoint protegido
# futuro, no solo a /me) en vez de manejarlo caso por caso en cada route.
# Mismo formato de error que el resto de la API ({"msg": "..."}, ver
# API_CONTRACT.md §3).
@jwt.unauthorized_loader
def _missing_token_callback(reason):
    return jsonify({"msg": "Falta el header de autorización"}), 401


@jwt.invalid_token_loader
def _invalid_token_callback(reason):
    return jsonify({"msg": "Token inválido"}), 401


@jwt.expired_token_loader
def _expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"msg": "El token ha expirado"}), 401

# ---------------------------------------------------------------------------
# Registro de sesiones (ADR-025-session-registry.md)
# ---------------------------------------------------------------------------
# Acá el JWT de THERS deja de ser puramente *stateless*. Sigue siendo
# autocontenido y firmado, pero además su `jti` tiene que corresponder a una
# fila viva de `sessions`. Es lo que hace posible "ver y cerrar sesiones" --
# sin esto, un token firmado valía hasta expirar y no había forma de revocarlo
# (que es exactamente el motivo por el que ese control estaba `pending`).
#
# Consecuencias asumidas, documentadas en ADR-025 §Riesgos:
#   · Una consulta a la base de datos por cada petición protegida.
#   · Los tokens emitidos ANTES de esta migración no tienen fila, así que
#     dejan de valer: todo el mundo se desloguea una vez.
#
# `token_in_blocklist_loader` es el hook que flask_jwt_extended ya ofrece para
# esto; se usa tal cual en vez de inventar un decorador propio que habría que
# recordar poner en cada endpoint (y que se olvidaría en el endpoint número
# veinte).


@jwt.token_in_blocklist_loader
def _is_token_revoked(jwt_header, jwt_payload):
    # Import local, no al tope del módulo: `extensions.py` lo importa
    # `app/__init__.py` antes de registrar los modelos, y un import de
    # infraestructura acá arriba crearía un ciclo.
    from app.infrastructure.persistence.repositories.session_repository import (
        SQLAlchemySessionRepository,
    )

    # Los tokens de desafío de 2FA (ADR-026) se emiten a propósito SIN fila de
    # sesión: todavía no hay sesión, falta el segundo factor. Eso hace que este
    # loader los rechace en cualquier endpoint protegido, que es justo lo que
    # se quiere -- un token de desafío no debe servir para leer el feed. El
    # único endpoint que los acepta (POST /api/2fa/verify) los decodifica a
    # mano, sin @jwt_required().
    if jwt_payload.get("purpose") == "2fa_challenge":
        return True

    # Los refresh tokens (ADR-017) no son access tokens: no tienen fila propia
    # en `sessions` y se validan contra `refresh_tokens` en POST /api/refresh y
    # /api/logout. La librería ya impide usarlos en cualquier otro endpoint.
    if jwt_payload.get("type") == "refresh":
        return False

    jti = jwt_payload.get("jti")
    if not jti:
        # Un token sin `jti` no puede tener sesión asociada. No debería pasar
        # (flask_jwt_extended siempre lo pone), pero si pasara, denegar es la
        # única respuesta segura.
        return True

    return not SQLAlchemySessionRepository().is_active(jti)


@jwt.revoked_token_loader
def _revoked_token_callback(jwt_header, jwt_payload):
    # 401 con el mismo formato que el resto de errores de auth
    # (API_CONTRACT.md §3). Mensaje propio y distinto de "token expirado": acá
    # el token sigue siendo válido criptográficamente, lo que pasó es que esa
    # sesión se cerró -- desde otro dispositivo, al cambiar la contraseña o al
    # desactivar el 2FA. El Frontend lo trata igual (vuelve a /login), pero la
    # diferencia importa para depurar.
    return jsonify({"msg": "La sesión fue cerrada. Iniciá sesión de nuevo."}), 401
