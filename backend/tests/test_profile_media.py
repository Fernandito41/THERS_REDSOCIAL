# Pruebas de integración de foto de perfil/portada y campos de perfil
# extendido (ADR-015-profile-media.md). PostgreSQL real + disco temporal
# (conftest.py).

import io
import os
from pathlib import Path

from PIL import Image

from tests.test_users_me import _register_and_login


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _image_bytes(fmt="PNG", size=(800, 600), color=(120, 40, 200)):
    buffer = io.BytesIO()
    Image.new("RGB", size, color).save(buffer, format=fmt)
    buffer.seek(0)
    return buffer


def _upload(client, token, kind, data, name="foto.png", content_type="image/png"):
    return client.post(
        f"/api/users/me/{kind}",
        data={"file": (data, name, content_type)},
        headers=_auth(token),
        content_type="multipart/form-data",
    )


def _stored_files():
    root = Path(os.environ["UPLOAD_DIR"])
    return {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}


class TestAvatar:
    def test_requires_jwt(self, client):
        response = client.post("/api/users/me/avatar")
        assert response.status_code == 401

    def test_upload_returns_url_and_serves_square_webp(self, client):
        token, _ = _register_and_login(client)

        response = _upload(client, token, "avatar", _image_bytes())

        assert response.status_code == 200
        url = response.get_json()["user"]["avatar_url"]
        assert url.startswith("http://testserver/api/media/avatars/")

        served = client.get(url.replace("http://testserver", ""))
        assert served.status_code == 200
        image = Image.open(io.BytesIO(served.data))
        assert image.format == "WEBP"
        assert image.size == (512, 512)

    def test_replacing_deletes_previous_file(self, client):
        token, _ = _register_and_login(client)

        _upload(client, token, "avatar", _image_bytes())
        first = _stored_files()
        _upload(client, token, "avatar", _image_bytes(color=(10, 200, 10)))
        second = _stored_files()

        assert len(first) == 1 and len(second) == 1
        assert first != second

    def test_delete_removes_file_and_url(self, client):
        token, _ = _register_and_login(client)
        _upload(client, token, "avatar", _image_bytes())

        response = client.delete("/api/users/me/avatar", headers=_auth(token))

        assert response.status_code == 200
        assert response.get_json()["user"]["avatar_url"] is None
        assert _stored_files() == set()

    def test_rejects_non_image_disguised_as_png(self, client):
        token, _ = _register_and_login(client)

        response = _upload(client, token, "avatar", io.BytesIO(b"<script>alert(1)</script>"))

        assert response.status_code == 400
        assert _stored_files() == set()

    def test_rejects_unsupported_format(self, client):
        token, _ = _register_and_login(client)

        response = _upload(client, token, "avatar", _image_bytes("GIF"), "a.gif", "image/gif")

        assert response.status_code == 400

    def test_rejects_missing_file(self, client):
        token, _ = _register_and_login(client)

        response = client.post(
            "/api/users/me/avatar", data={}, headers=_auth(token),
            content_type="multipart/form-data",
        )

        assert response.status_code == 400

    def test_rejects_oversized_file(self, client):
        token, _ = _register_and_login(client)
        big = io.BytesIO(b"\x89PNG" + b"0" * (5 * 1024 * 1024 + 10))

        response = _upload(client, token, "avatar", big)

        assert response.status_code == 413


class TestCover:
    def test_upload_crops_to_banner(self, client):
        token, _ = _register_and_login(client)

        response = _upload(client, token, "cover", _image_bytes("JPEG", (3000, 2000)), "c.jpg", "image/jpeg")

        assert response.status_code == 200
        url = response.get_json()["user"]["cover_url"]
        served = client.get(url.replace("http://testserver", ""))
        assert Image.open(io.BytesIO(served.data)).size == (1600, 500)


class TestExposure:
    def test_avatar_visible_to_others_in_posts_and_me(self, client):
        token, _ = _register_and_login(client)
        _upload(client, token, "avatar", _image_bytes())

        client.post("/api/posts", json={"content": "hola"}, headers=_auth(token))
        posts = client.get("/api/posts", headers=_auth(token)).get_json()["posts"]

        assert posts[0]["author"]["avatar_url"].startswith("http://testserver/api/media/avatars/")
        me = client.get("/api/users/me", headers=_auth(token)).get_json()["user"]
        assert me["avatar_url"] == posts[0]["author"]["avatar_url"]

    def test_no_avatar_is_null(self, client):
        token, _ = _register_and_login(client)
        me = client.get("/api/users/me", headers=_auth(token)).get_json()["user"]
        assert me["avatar_url"] is None and me["cover_url"] is None


class TestProfileText:
    def _patch(self, client, token, payload):
        return client.patch("/api/users/me", json=payload, headers=_auth(token))

    def test_set_bio_location_website(self, client):
        token, _ = _register_and_login(client)

        response = self._patch(client, token, {"bio": " Hola ", "location": "Quito", "website": "thers.app/x"})

        user = response.get_json()["user"]
        assert response.status_code == 200
        assert (user["bio"], user["location"], user["website"]) == ("Hola", "Quito", "thers.app/x")

    def test_empty_string_clears_field(self, client):
        token, _ = _register_and_login(client)
        self._patch(client, token, {"bio": "algo"})

        user = self._patch(client, token, {"bio": ""}).get_json()["user"]

        assert user["bio"] is None

    def test_rejects_too_long_bio(self, client):
        token, _ = _register_and_login(client)
        assert self._patch(client, token, {"bio": "x" * 161}).status_code == 400

    def test_rejects_javascript_website(self, client):
        token, _ = _register_and_login(client)
        assert self._patch(client, token, {"website": "javascript:alert(1)"}).status_code == 400

    def test_cannot_set_media_paths_via_patch(self, client):
        token, _ = _register_and_login(client)

        response = self._patch(client, token, {"avatar_path": "../../etc/passwd"})

        assert response.status_code == 400
