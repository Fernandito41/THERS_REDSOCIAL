# Endpoints de la pantalla "Descarga de datos y archivo" (REF-SET-09,
# ADR-028-data-export.md):
#   · POST /api/data-exports                    genera un archivo nuevo
#   · GET  /api/data-exports                    historial de solicitudes
#   · GET  /api/data-exports/<id>/download      descarga el ZIP
#
# Todos protegidos: la identidad sale del JWT, nunca del body ni de la URL.
# Composition root igual que el resto de interfaces/routes/
# (BACKEND_ARCHITECTURE.md §17).

from flask import Blueprint, Response, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.application.data_exports.data_export_use_case import (
    get_export_file,
    list_exports,
    request_export,
)
from app.domain.data_exports import policy
from app.domain.data_exports.exceptions import (
    DataExportCooldownError,
    DataExportExpiredError,
    DataExportNotFoundError,
)
from app.infrastructure.persistence.repositories.data_export_repository import (
    SQLAlchemyDataExportRepository,
)

data_exports_bp = Blueprint("data_exports", __name__)

_repository = SQLAlchemyDataExportRepository()


@data_exports_bp.route("/data-exports", methods=["POST"])
@jwt_required()
def create_data_export():
    user_id = get_jwt_identity()

    try:
        export = request_export(user_id, _repository)
    except DataExportCooldownError as error:
        response = jsonify({
            "msg": "Ya pediste una copia hace poco. Esperá antes de pedir otra.",
            "retry_after_seconds": error.retry_after_seconds,
        })
        response.status_code = 429
        response.headers["Retry-After"] = str(error.retry_after_seconds)
        return response

    return jsonify({"export": export, "ttl_days": policy.EXPORT_TTL_DAYS}), 201


@data_exports_bp.route("/data-exports", methods=["GET"])
@jwt_required()
def get_data_exports():
    user_id = get_jwt_identity()
    return jsonify({
        "exports": list_exports(user_id, _repository),
        "ttl_days": policy.EXPORT_TTL_DAYS,
        "cooldown_seconds": policy.EXPORT_COOLDOWN_SECONDS,
    }), 200


@data_exports_bp.route("/data-exports/<uuid:export_id>/download", methods=["GET"])
@jwt_required()
def download_data_export(export_id):
    user_id = get_jwt_identity()

    try:
        file_name, content = get_export_file(user_id, export_id, _repository)
    except DataExportNotFoundError:
        # Mismo 404 si el id no existe o es de otra cuenta.
        return jsonify({"msg": "Exportación no encontrada"}), 404
    except DataExportExpiredError:
        return jsonify({"msg": "Este archivo caducó. Pedí uno nuevo."}), 410

    return Response(
        content,
        mimetype="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{file_name}"',
            "Cache-Control": "no-store",
        },
    )
