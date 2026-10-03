# Pruebas de `CORS_ORIGINS` (ADR-018-hosting-and-environments.md §Riesgos, ítem 5).
# No tocan la base de datos: solo comprueban qué orígenes reciben cabeceras CORS.

from flask import Flask

from app import create_app
from app.config import Config

ALLOWED = "https://thersweb.com"
OTHER = "https://sitio-ajeno.example"


def _client(monkeypatch, origins):
    monkeypatch.setattr(Config, "ALLOWED_WEB_ORIGINS", origins)
    return create_app().test_client()


def _origin_header(response):
    return response.headers.get("Access-Control-Allow-Origin")


class TestCorsOrigins:
    def test_without_the_variable_cors_stays_open_for_local_development(self, monkeypatch):
        client = _client(monkeypatch, [])

        response = client.get("/api/users/me", headers={"Origin": OTHER})

        # Comportamiento de siempre: cualquier origen es aceptado (se refleja tal cual).
        assert _origin_header(response) == OTHER

    def test_an_allowed_origin_gets_the_header(self, monkeypatch):
        client = _client(monkeypatch, [ALLOWED])

        response = client.get("/api/users/me", headers={"Origin": ALLOWED})

        assert _origin_header(response) == ALLOWED

    def test_any_other_origin_gets_no_header(self, monkeypatch):
        client = _client(monkeypatch, [ALLOWED])

        response = client.get("/api/users/me", headers={"Origin": OTHER})

        assert _origin_header(response) is None

    def test_the_preflight_of_a_foreign_origin_is_not_approved(self, monkeypatch):
        client = _client(monkeypatch, [ALLOWED])

        response = client.options(
            "/api/posts",
            headers={
                "Origin": OTHER,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "authorization,content-type",
            },
        )

        assert _origin_header(response) is None

    def test_several_origins_can_be_allowed(self, monkeypatch):
        staging = "https://staging.thersweb.com"
        client = _client(monkeypatch, [ALLOWED, staging])

        assert _origin_header(client.get("/api/users/me", headers={"Origin": staging})) == staging
        assert _origin_header(client.get("/api/users/me", headers={"Origin": ALLOWED})) == ALLOWED

    def test_the_variable_is_parsed_from_a_comma_separated_list(self, monkeypatch):
        monkeypatch.setenv("CORS_ORIGINS", f" {ALLOWED} , ,https://staging.thersweb.com ")
        import importlib

        import app.config as config

        try:
            reloaded = importlib.reload(config)
            assert reloaded.Config.ALLOWED_WEB_ORIGINS == [ALLOWED, "https://staging.thersweb.com"]
        finally:
            monkeypatch.delenv("CORS_ORIGINS")
            importlib.reload(config)

    def test_it_is_a_flask_app(self, monkeypatch):
        assert isinstance(create_app(), Flask)
