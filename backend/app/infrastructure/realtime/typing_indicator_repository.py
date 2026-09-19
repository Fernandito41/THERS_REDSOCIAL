# Adaptador en memoria del puerto `TypingRepository` (domain/messages/repositories.py,
# ADR-014-messages-ux-improvements.md). Vive fuera de `persistence/` a
# propósito -- nunca toca PostgreSQL, ni falta que le hace: "escribiendo..."
# deja de ser cierto a los pocos segundos, así que no hay nada que valga la
# pena recuperar después de que la ventana de vigencia expira.
#
# El diccionario es un atributo de MÓDULO (no de instancia) para que todas
# las requests del mismo proceso de Flask compartan el mismo estado --
# message_routes.py instancia SQLAlchemyMessageRepository() una vez por
# proceso igual que el resto de repositorios (composition root), y esta
# clase necesita el mismo efecto de "una sola fuente compartida" aunque no
# haya una base de datos detrás. No sobrevive un reinicio del backend ni se
# comparte entre varios procesos/workers (ADR-014 §Riesgos) -- aceptable
# para un único proceso de desarrollo.

import time

TYPING_INDICATOR_TTL_SECONDS = 3

_last_ping_at = {}


class InMemoryTypingIndicatorRepository:
    def ping(self, sender_id, recipient_id):
        _last_ping_at[(str(sender_id), str(recipient_id))] = time.monotonic()

    def is_typing(self, sender_id, recipient_id):
        last_ping = _last_ping_at.get((str(sender_id), str(recipient_id)))
        if last_ping is None:
            return False
        return (time.monotonic() - last_ping) < TYPING_INDICATOR_TTL_SECONDS
