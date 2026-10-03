# POST /api/users/me/terms-acceptance (ADR-032-content-reports-and-moderation.md §5).
#
# Para las cuentas que ya existían: no aceptaron nada al registrarse, así que al
# iniciar sesión se les pide aceptar los términos vigentes antes de crear
# contenido. Las cuentas nuevas aceptan en el propio registro.

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.application.auth.user_presenter import to_public_user
from app.application.terms.terms_use_cases import record_terms_acceptance
from app.domain.terms.exceptions import InvalidTermsVersionError
from app.infrastructure.persistence.repositories.user_repository import (
    SQLAlchemyUserRepository,
)

terms_bp = Blueprint("terms", __name__)

_user_repository = SQLAlchemyUserRepository()


@terms_bp.route("/users/me/terms-acceptance", methods=["POST"])
@jwt_required()
def accept_terms():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"msg": "No se enviaron datos"}), 400

    try:
        user = record_terms_acceptance(
            get_jwt_identity(), data.get("version"), _user_repository
        )
    except InvalidTermsVersionError as error:
        # 409: la petición es válida, pero el cliente mostró términos que ya no
        # rigen. Devuelve la versión vigente para que pueda reintentar.
        return jsonify({
            "msg": "Los términos de uso cambiaron. Revísalos y vuelve a aceptar.",
            "current_version": error.current_version,
        }), 409

    return jsonify({"user": to_public_user(user)}), 200
