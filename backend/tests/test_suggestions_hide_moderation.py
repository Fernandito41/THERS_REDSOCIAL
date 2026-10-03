# Las cuentas de moderación y las suspendidas no aparecen en las sugerencias de personas
# («Personas que resuenan», Buscar). ADR-032: se usan solo para moderar.

from app.extensions import db
from app.infrastructure.persistence.models import User
from tests.test_content_preferences import _h, _register_and_login


def _usernames(client, token):
    body = client.get("/api/users/suggestions", headers=_h(token)).get_json()
    return {s["username"] for s in body["suggestions"]}


def _set(app, user_id, **fields):
    with app.app_context():
        user = db.session.get(User, user_id)
        for key, value in fields.items():
            setattr(user, key, value)
        db.session.commit()


class TestSuggestionsHideModerationAccounts:
    def test_a_regular_account_is_suggested(self, client):
        viewer, _ = _register_and_login(client, "viewer")
        _register_and_login(client, "otrapersona")

        assert "otrapersona" in _usernames(client, viewer)

    def test_a_moderator_account_is_not_suggested(self, app, client):
        viewer, _ = _register_and_login(client, "viewer")
        _, mod_id = _register_and_login(client, "diego_mod")
        _register_and_login(client, "otrapersona")
        _set(app, mod_id, is_moderator=True)

        names = _usernames(client, viewer)

        assert "diego_mod" not in names
        assert "otrapersona" in names

    def test_a_suspended_account_is_not_suggested(self, app, client):
        viewer, _ = _register_and_login(client, "viewer")
        _, other_id = _register_and_login(client, "suspendida")
        _set(app, other_id, suspended_at=db.func.now())

        assert "suspendida" not in _usernames(client, viewer)

    def test_removing_the_role_makes_the_account_suggestible_again(self, app, client):
        viewer, _ = _register_and_login(client, "viewer")
        _, mod_id = _register_and_login(client, "ex_mod")
        _set(app, mod_id, is_moderator=True)
        assert "ex_mod" not in _usernames(client, viewer)

        _set(app, mod_id, is_moderator=False)

        assert "ex_mod" in _usernames(client, viewer)
