# GET /api/notifications y PATCH /api/notifications/<id>/read
# (ADR-008-notifications-minimal-model.md). Blueprint propio -- "notifications"
# es su propia entidad (mismo criterio que separa likes_bp/comments_bp/
# follows_bp de posts_bp/users_bp), sin anidar bajo ningún otro recurso: a
# diferencia de likes/comments (sub-recurso de un post) o follows
# (sub-recurso de un usuario), una notificación no cuelga de la URL de su
# post/actor de origen -- siempre se listan/marcan desde la perspectiva del
# destinatario autenticado.
#
# `<uuid:notification_id>`: el conversor `uuid` de Flask/Werkzeug ya
# devuelve 404 (ninguna ruta matchea) para cualquier segmento que no sea un
# UUID válido, sin necesidad de validarlo a mano (mismo criterio que
# like_routes.py/follow_routes.py).

from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.application.notifications.list_notifications_use_case import (
    DEFAULT_LIMIT,
    list_notifications,
)
from app.application.notifications.mark_notification_read_use_case import (
    mark_notification_read,
)
from app.domain.notifications.exceptions import NotificationNotFoundError
from app.infrastructure.persistence.repositories.notification_repository import (
    SQLAlchemyNotificationRepository,
)

notifications_bp = Blueprint("notifications", __name__)

_notification_repository = SQLAlchemyNotificationRepository()


@notifications_bp.route("/notifications", methods=["GET"])
@jwt_required()
def list_all():
    # Identidad exclusivamente del JWT -- nunca de query string (mismo
    # principio que el resto de endpoints protegidos). Un usuario solo
    # puede listar sus propias notificaciones, nunca las de otro.
    user_id = get_jwt_identity()

    notifications = list_notifications(user_id, _notification_repository, DEFAULT_LIMIT)
    return jsonify({"notifications": notifications}), 200


@notifications_bp.route("/notifications/<uuid:notification_id>/read", methods=["PATCH"])
@jwt_required()
def mark_read(notification_id):
    user_id = get_jwt_identity()

    try:
        result = mark_notification_read(
            str(notification_id), user_id, _notification_repository
        )
    except NotificationNotFoundError:
        # Mismo mensaje/código tanto si el id no existe como si existe pero
        # es de otro usuario -- no revela cuál de los dos ocurrió (ADR-008
        # §Contrato API).
        return jsonify({"msg": "Notificación no encontrada"}), 404

    return jsonify(result), 200
