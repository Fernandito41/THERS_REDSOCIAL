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