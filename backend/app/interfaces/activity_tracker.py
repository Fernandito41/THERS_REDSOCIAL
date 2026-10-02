# Registro de "última vez activo" (ADR-024-content-filters-and-privacy-preferences.md).
#
# Vive en interfaces/ y no en application/ porque es un hook del ciclo de vida
# de la petición HTTP, no una regla de negocio: se engancha a `after_request`
# para que CUALQUIER endpoint autenticado actualice la marca, sin tener que
# acordarse de llamarlo en cada caso de uso (que es exactamente el tipo de
# cosa que se olvida al agregar el endpoint número veinte).
#
# Por qué after_request y no before_request: si la petición falla con 401 (token
# inválido/expirado), no hay actividad real que registrar. Después de resolver
# la respuesta ya se sabe si la identidad era buena.

from flask import request
from flask_jwt_extended import get_jwt, get_jwt_identity, verify_jwt_in_request

from app.infrastructure.persistence.repositories.session_repository import (
    SQLAlchemySessionRepository,
)
from app.infrastructure.persistence.repositories.user_repository import (
    SQLAlchemyUserRepository,
)

#: Cada cuánto se reescribe `last_seen_at`. Cinco minutos: suficiente para que
#: "activo hace un rato" sea cierto, y lo bastante espaciado para que el
#: polling del chat (cada 4 s, ADR-014) no genere un UPDATE por petición. El
#: throttle se evalúa en el propio WHERE del UPDATE, así que no hace falta
#: estado en el proceso y funciona igual con varios workers.
TOUCH_INTERVAL_SECONDS = 300

_user_repository = SQLAlchemyUserRepository()
# ADR-025-session-registry.md: la misma petición que actualiza la presencia de
# la persona actualiza el "último uso" de ESTA sesión -- es lo que hace que la
# lista de sesiones pueda decir "activa hace 3 horas" por dispositivo, no solo
# por cuenta.
_session_repository = SQLAlchemySessionRepository()


def register_activity_tracker(app):
    @app.after_request
    def touch_last_seen(response):
        # Solo peticiones que resolvieron bien: un 4xx/5xx no es actividad que
        # valga la pena anunciar como presencia.
        if response.status_code >= 400:
            return response

        # OPTIONS son el preflight de CORS, no actividad de la persona.
        if request.method == "OPTIONS":
            return response

        try:
            # optional=True: la inmensa mayoría de endpoints son protegidos,
            # pero register/login/forgot-password no lo son y no deben fallar
            # por esto.
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
            # `jti` del token de ESTA petición. Puede faltar si no había token.
            jti = (get_jwt() or {}).get("jti")
        except Exception:
            # Cualquier problema leyendo el token: no es actividad registrable.
            # Nunca se propaga -- este hook no puede hacer fallar una respuesta
            # que ya estaba lista.
            return response

        if user_id is None:
            return response

        try:
            _user_repository.touch_last_seen(user_id, TOUCH_INTERVAL_SECONDS)
            if jti:
                _session_repository.touch(jti, TOUCH_INTERVAL_SECONDS)
        except Exception:
            # Un fallo al registrar presencia no puede tumbar la respuesta:
            # `last_seen_at` es cosmético, igual que el indicador de
            # "escribiendo" (ADR-014 §Riesgos).
            pass

        return response
