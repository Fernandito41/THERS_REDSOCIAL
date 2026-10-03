# Envío de correo que NO rompe el flujo si el proveedor falla.
#
# Por qué existe: `EmailService` deja propagar las excepciones de Resend a propósito
# (no traga errores en silencio). Pero cuando falla un correo DESPUÉS de haber
# cambiado algo (crear la cuenta, cambiar la contraseña), responder 500 es peor que el
# fallo: la persona cree que no pasó nada, y en `forgot-password` la diferencia entre
# 200 y 500 revelaría qué correos tienen cuenta.
#
# El caso real que lo motiva: el plan gratuito de Resend corta a los 100 correos al
# día, y un dominio sin verificar o una clave de otro equipo dan el mismo síntoma.
#
# QUÉ SE REGISTRA: la clase del error y el código/tipo que informa el proveedor. NUNCA
# el cuerpo del correo (lleva el código de 6 dígitos), ni el destinatario, ni el
# mensaje del proveedor (puede incluir direcciones).

import logging

_logger = logging.getLogger("thers.email")


def attempt_delivery(send, kind):
    """Ejecuta `send()` (una llamada a `EmailService`). Devuelve `True` si se entregó
    al proveedor y `False` si falló; en ese caso lo registra y NO lanza.

    `kind` es una etiqueta fija del tipo de correo («registration_code», ...), nunca
    datos de la persona."""
    try:
        send()
        return True
    except Exception as error:  # noqa: BLE001 -- justo lo que se quiere aislar
        _logger.warning(
            "No se pudo enviar el correo '%s': %s (code=%s, type=%s)",
            kind,
            type(error).__name__,
            getattr(error, "code", None),
            getattr(error, "error_type", None),
        )
        return False
