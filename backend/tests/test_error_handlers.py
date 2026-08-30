# Pruebas del manejador global de errores (app/interfaces/error_handlers.py,
# BACKEND_ARCHITECTURE.md §20 item 6, API_CONTRACT.md §9 item 1). Cubren:
# - 404 en una URL que Flask no puede enrutar (nunca una route real);
# - 405 en un verbo HTTP no permitido sobre una URL real;
# - 500 ante una excepción no controlada, forzada con monkeypatch sobre una
#   ruta real y protegida (GET /api/users/me) -- sin agregar ninguna ruta
#   insegura solo para testing.
#
# Las tres verifican, además del status code y el "msg" esperado, que la
# respuesta sea JSON (nunca la página HTML por defecto de Flask/Werkzeug) y,
# en el caso del 500, que el cuerpo nunca exponga traceback, el tipo/mensaje
# real de la excepción, ni datos sensibles.

from app.infrastructure.persistence.repositories.user_repository import (
    SQLAlchemyUserRepository,
)

VALID_PASSWORD = "secretpass"


def _register_payload(**overrides):
    payload = {
        "name": "Grace Hopper",
        "username": "grace_hopper",
        "email": "grace@example.com",
        "phone": "7000-5678",
        "country_code": "+503",
        "birth_date": "1990-01-01",
        "password": VALID_PASSWORD,
        "confirm_password": VALID_PASSWORD,
    }
    payload.update(overrides)
    return payload


def _register_and_login(client):
    client.post("/api/register", json=_register_payload())
    res = client.post(
        "/api/login",
        json={"email": "grace@example.com", "password": VALID_PASSWORD},
    )
    return res.get_json()["token"]


class TestNotFoundHandler:
    def test_unknown_url_returns_json_404(self, client):
        response = client.get("/api/esta-ruta-no-existe")

        assert response.status_code == 404
        assert response.content_type.startswith("application/json")
        body = response.get_json()
        assert body == {"msg": "Recurso no encontrado"}
        # nunca la página HTML por defecto de Flask/Werkzeug
        assert b"<html" not in response.data.lower()


class TestMethodNotAllowedHandler:
    def test_disallowed_method_returns_json_405(self, client):
        # /api/login solo acepta POST -- DELETE está fuera de su whitelist de
        # métodos (auth_routes.py, @auth_bp.route(..., methods=["POST"])).
        response = client.delete("/api/login")

        assert response.status_code == 405
        assert response.content_type.startswith("application/json")
        body = response.get_json()
        assert body == {"msg": "Método no permitido"}
        assert b"<html" not in response.data.lower()


class TestMalformedJsonHandler:
    def test_malformed_json_body_returns_json_400(self, client):
        # auth_routes.py usa request.get_json() sin silent=True en
        # /api/register y /api/login -- un body no-JSON hace que Werkzeug
        # levante BadRequest (400) antes de que la route lo controle. Cubre
        # el handler genérico de HTTPException, no solo 404/405.
        response = client.post(
            "/api/login",
            data="esto no es json",
            content_type="application/json",
        )

        assert response.status_code == 400
        assert response.content_type.startswith("application/json")
        body = response.get_json()
        assert "msg" in body
        assert b"<html" not in response.data.lower()


class TestUnexpectedExceptionHandler:
    def test_unhandled_exception_returns_generic_500_without_leaking_details(
        self, client, monkeypatch
    ):
        token = _register_and_login(client)

        # Fuerza una excepción no controlada dentro de un flujo real
        # (GET /api/users/me con JWT válido) parcheando el repositorio --
        # nunca se agrega una ruta nueva solo para poder probar el 500. El
        # mensaje simulado incluye texto que, si el handler filtrara el
        # error real, aparecería literalmente en la respuesta -- exactamente
        # lo que las aserciones de abajo verifican que NUNCA ocurra.
        def _boom(self, user_id):
            raise RuntimeError(
                "fallo simulado -- DATABASE_URL=postgresql://user:secret@host/db "
                "no debe aparecer en la respuesta"
            )

        monkeypatch.setattr(SQLAlchemyUserRepository, "find_by_id", _boom)

        response = client.get(
            "/api/users/me", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 500
        assert response.content_type.startswith("application/json")
        assert response.get_json() == {"msg": "Error interno del servidor"}

        raw_body = response.get_data(as_text=True)
        assert "Traceback" not in raw_body
        assert "RuntimeError" not in raw_body
        assert "fallo simulado" not in raw_body
        assert "DATABASE_URL" not in raw_body
        assert "secret" not in raw_body
        assert b"<html" not in response.data.lower()
