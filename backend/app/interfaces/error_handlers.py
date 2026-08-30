# Manejador global de errores para toda la API (BACKEND_ARCHITECTURE.md §20
# item 6, API_CONTRACT.md §9 item 1). Traduce cualquier error HTTP de
# Flask/Werkzeug y cualquier excepción no controlada al mismo formato de
# error que el resto del backend ya produce ({"msg": "..."}, API_CONTRACT.md
# §3) -- sin esto, una URL inexistente, un verbo no permitido, un JSON mal
# formado (request.get_json() sin silent=True en auth_routes.py) o un error
# inesperado caían en las páginas HTML por defecto de Flask, rompiendo el
# contrato JSON para cualquier consumidor real (Frontend, Postman, curl).
#
# Vive en interfaces/ (no en interfaces/routes/) porque es responsabilidad de
# la capa de entrada HTTP -- "traducir un resultado a una respuesta HTTP",
# BACKEND_ARCHITECTURE.md §3 -- pero no es un blueprint ni una ruta:
# routes/ queda reservado a auth_routes.py/user_routes.py, mismo criterio que
# ya separa config.py/extensions.py de las routes concretas.
#
# No interfiere con:
# - los errores que cada route ya construye a mano (`jsonify(...), 4xx`)
#   -- esos son valores de retorno normales de la vista, nunca son
#   excepciones, nunca pasan por este módulo;
# - los callbacks de flask_jwt_extended (app/extensions.py) -- flask_jwt_extended
#   resuelve sus propios errores (401 por token ausente/inválido/expirado)
#   con sus propios *_loader *antes* de que la excepción llegue al manejo de
#   errores de Flask, no vía @app.errorhandler.
#
# Nota técnica: registrar @app.errorhandler(Exception) SÍ intercepta
# cualquier excepción no controlada incluso con debug=True (Flask localiza el
# handler registrado antes de decidir si propagar hacia el debugger
# interactivo de Werkzeug) -- alcanza para blindar el 500 sin depender de
# cambiar la configuración de debug en run.py.

from flask import jsonify
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):
    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({"msg": "Recurso no encontrado"}), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        return jsonify({"msg": "Método no permitido"}), 405

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        # Cualquier otro error HTTP estándar de Werkzeug que ninguna route
        # construye a mano hoy (400 por JSON mal formado, 413 payload
        # demasiado grande, etc.) -- mismo formato que el resto de la API en
        # vez de la página HTML por defecto de Flask. `error.description` ya
        # es un mensaje pensado para mostrarse (nunca incluye traceback ni
        # detalles internos -- eso es responsabilidad exclusiva del handler
        # de abajo, para excepciones no-HTTP).
        return jsonify({"msg": error.description or error.name}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        # Última línea de defensa: cualquier excepción no controlada por
        # ninguna capa anterior (dominio, aplicación, infraestructura). El
        # detalle real va al logger del servidor (incluye el traceback
        # completo ahí, nunca en la respuesta) -- la respuesta pública nunca
        # expone traceback, rutas internas, ni el mensaje/tipo real de la
        # excepción, que podría contener datos sensibles si el error ocurrió
        # en la capa de conexión (DATABASE_URL, JWT_SECRET_KEY -- HB-001 §19.1).
        app.logger.exception("Error interno no controlado")
        return jsonify({"msg": "Error interno del servidor"}), 500
