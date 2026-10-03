# Respuesta uniforme `429` con `Retry-After` (ADR-027 §Contrato API).
#
# `auth_routes.py` tiene su propia copia privada (`_rate_limited_response`). Este
# módulo existe para que las rutas NUEVAS no tengan que importar un helper
# privado de otra route, sin tocar `auth_routes.py` en esta tarea. Cambiar
# `auth_routes` para que lo use es un cambio de una línea, aparte.

from flask import jsonify


def rate_limited_response(error):
    """El header es tan importante como el código: sin él el cliente reintenta a
    ciegas -- peor para la persona legítima (no sabe cuándo volver) y peor para
    el servidor (sigue recibiendo peticiones)."""
    response = jsonify({
        "msg": "Demasiados intentos. Esperá un momento antes de volver a probar.",
        "retry_after_seconds": error.retry_after_seconds,
    })
    response.status_code = 429
    response.headers["Retry-After"] = str(error.retry_after_seconds)
    return response
