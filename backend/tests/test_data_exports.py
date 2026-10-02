# Pruebas de integración de la exportación de datos (REF-SET-09,
# ADR-024-data-export.md) contra PostgreSQL real (thers_test) -- no mocks.

import io
import json
import zipfile
from datetime import datetime, timedelta, timezone

from app.extensions import db
from app.infrastructure.persistence.models import DataExport
from tests.conftest import mark_email_verified

VALID_PASSWORD = "secretpass"


def _register_and_login(client, username="ada_lovelace", email="ada@example.com"):
    response = client.post(
        "/api/register",
        json={
            "name": "Ada Lovelace",
            "username": username,
            "email": email,
            "phone": "7000-1234",
            "country_code": "+503",
            "birth_date": "1990-01-01",
            "password": VALID_PASSWORD,
            "confirm_password": VALID_PASSWORD,
        },
    )
    user_id = response.get_json()["user"]["id"]
    mark_email_verified(user_id)
    token = client.post(
        "/api/login", json={"email": email, "password": VALID_PASSWORD}
    ).get_json()["token"]
    return token, user_id


def _headers(token):
    return {"Authorization": f"Bearer {token}"}


def _open_zip(response):
    return zipfile.ZipFile(io.BytesIO(response.data))


def test_endpoints_require_authentication(client):
    assert client.post("/api/data-exports").status_code == 401
    assert client.get("/api/data-exports").status_code == 401


def test_create_export_and_download_real_zip(client):
    token, _ = _register_and_login(client)
    client.post("/api/posts", json={"content": "Mi primera cápsula"}, headers=_headers(token))

    created = client.post("/api/data-exports", headers=_headers(token))
    assert created.status_code == 201
    export = created.get_json()["export"]
    assert export["status"] == "ready"
    assert export["file_name"].endswith(".zip")
    assert export["size_bytes"] > 0

    download = client.get(
        f"/api/data-exports/{export['id']}/download", headers=_headers(token)
    )
    assert download.status_code == 200
    assert download.mimetype == "application/zip"
    assert "attachment" in download.headers["Content-Disposition"]

    archive = _open_zip(download)
    names = set(archive.namelist())
    assert {"LEEME.txt", "profile.json", "posts.json", "messages.json"} <= names

    profile = json.loads(archive.read("profile.json"))
    assert profile["email"] == "ada@example.com"
    posts = json.loads(archive.read("posts.json"))
    assert [p["content"] for p in posts] == ["Mi primera cápsula"]


def test_archive_never_contains_secrets(client):
    token, _ = _register_and_login(client)
    created = client.post("/api/data-exports", headers=_headers(token)).get_json()["export"]
    download = client.get(
        f"/api/data-exports/{created['id']}/download", headers=_headers(token)
    )

    everything = b"".join(
        _open_zip(download).read(name) for name in _open_zip(download).namelist()
    ).decode("utf-8")

    assert "password_hash" not in everything
    assert "totp_secret" not in everything
    assert "jti" not in everything
    assert "scrypt" not in everything


def test_second_request_within_cooldown_is_rate_limited(client):
    token, _ = _register_and_login(client)
    assert client.post("/api/data-exports", headers=_headers(token)).status_code == 201

    second = client.post("/api/data-exports", headers=_headers(token))
    assert second.status_code == 429
    assert second.get_json()["retry_after_seconds"] > 0
    assert second.headers["Retry-After"]


def test_history_lists_requests_newest_first_with_download_count(client):
    token, _ = _register_and_login(client)
    created = client.post("/api/data-exports", headers=_headers(token)).get_json()["export"]
    client.get(f"/api/data-exports/{created['id']}/download", headers=_headers(token))

    listing = client.get("/api/data-exports", headers=_headers(token)).get_json()
    assert len(listing["exports"]) == 1
    assert listing["exports"][0]["download_count"] == 1
    assert listing["exports"][0]["downloaded_at"] is not None
    assert listing["ttl_days"] == 7


def test_cannot_download_another_users_export(client):
    token_a, _ = _register_and_login(client)
    token_b, _ = _register_and_login(client, username="grace_hopper", email="grace@example.com")

    created = client.post("/api/data-exports", headers=_headers(token_a)).get_json()["export"]

    stolen = client.get(
        f"/api/data-exports/{created['id']}/download", headers=_headers(token_b)
    )
    assert stolen.status_code == 404

    # Y el historial de B no incluye el archivo de A.
    assert client.get("/api/data-exports", headers=_headers(token_b)).get_json()["exports"] == []


def test_expired_export_returns_410_and_is_discarded(client, app):
    token, _ = _register_and_login(client)
    created = client.post("/api/data-exports", headers=_headers(token)).get_json()["export"]

    with app.app_context():
        row = db.session.get(DataExport, created["id"])
        row.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
        db.session.commit()

    download = client.get(
        f"/api/data-exports/{created['id']}/download", headers=_headers(token)
    )
    assert download.status_code == 410

    listing = client.get("/api/data-exports", headers=_headers(token)).get_json()
    assert listing["exports"][0]["status"] == "expired"

    with app.app_context():
        assert db.session.get(DataExport, created["id"]).content is None
