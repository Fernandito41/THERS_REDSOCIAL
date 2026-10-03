# Compuerta de "perfil completo" para las acciones que crean contenido o
# interactúan con otras personas (publicar, comentar, dar me gusta, seguir y
# escribir mensajes).
#
# Por qué existe: THERS es solo para personas de 18 años o más (decisión de
# producto, 2026-10-02) y la edad se declara con la fecha de nacimiento. Una
# cuenta creada con Google NO trae fecha de nacimiento (ADR-012): nace con
# `profile_completed=false` y la web la manda a "Completar perfil", donde se
# valida la mayoría de edad en el servidor (`PATCH /api/users/me`). Pero esa
# redirección es solo de interfaz: quien llame a la API directamente con ese
# token podría publicar sin haber declarado nunca su edad. Esta compuerta lo
# cierra en el servidor.
#
# No es una verificación documental: la fecha es la que la persona declara.
# Tampoco bloquea cuentas existentes con perfil completo: qué hacer con las
# que tengan menos de 18 años es una estrategia aparte
# (docs/architecture/ADR-034-minimum-age-18.md), no un bloqueo masivo.

from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt_identity

from app.infrastructure.persistence.repositories.user_repository import SQLAlchemyUserRepository

_user_repository = SQLAlchemyUserRepository()


def profile_completed_required(view):
    """Debe ir DESPUÉS de `@jwt_required()` (necesita la identidad del token)."""

    @wraps(view)
    def wrapper(*args, **kwargs):
        user = _user_repository.find_by_id(get_jwt_identity())
        if user is None or not user.profile_completed:
            return (
                jsonify({
                    "msg": "Completa tu perfil, incluida tu fecha de nacimiento, para usar THERS.",
                    "profile_incomplete": True,
                }),
                403,
            )
        return view(*args, **kwargs)

    return wrapper
