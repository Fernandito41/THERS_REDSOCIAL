# Los tests corren contra PostgreSQL 16 real en Docker (thers_test, ver
# docker/postgres-init/01-create-test-db.sql) — no contra mocks ni SQLite.
# DATABASE_URL se fija explícitamente a `thers_test` aquí, ignorando
# cualquier DATABASE_URL heredada del entorno (p. ej. apuntando a
# thers_dev), para que un test nunca pueda tocar datos de desarrollo por
# accidente. TEST_DATABASE_URL permite apuntar a otra instancia si hace falta.

import os

os.environ["JWT_SECRET_KEY"] = "test-secret-key-not-for-real-use"
os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://thers:changeme@localhost:5432/thers_test",
)

import pytest

from app import create_app
from app.extensions import db


@pytest.fixture()
def app():
    app = create_app()
    app.config.update(TESTING=True)
    yield app
    # `create_app()` crea un engine/pool de SQLAlchemy nuevo por test (una
    # Flask app nueva por test, sin compartir el engine entre ellos) -- sin
    # liberarlo, las conexiones se acumulan a lo largo de la suite hasta
    # agotar `max_connections` de PostgreSQL (100 por defecto en el
    # contenedor de desarrollo), un fallo que solo aparece con suites
    # grandes, no test por test aislado.
    with app.app_context():
        db.engine.dispose()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def _clean_tables(app):
    # Todas las migraciones (backend/migrations/versions/) ya deben estar
    # aplicadas contra thers_test antes de correr los tests (`flask db
    # upgrade` con DATABASE_URL=.../thers_test) — este fixture solo limpia
    # filas entre tests, no crea estructura.
    #
    # `posts` referencia a `users` (author_id, ON DELETE CASCADE,
    # ADR-004-posts-minimal-model.md), `likes` referencia a ambas (post_id/
    # user_id, ON DELETE CASCADE, ADR-005-likes-minimal-model.md) y
    # `comments` también referencia a ambas (post_id/author_id, ON DELETE
    # CASCADE, ADR-006-comments-minimal-model.md) -- un TRUNCATE de una sola
    # tabla falla si otra tiene filas dependientes, salvo que todas se
    # trunquen juntas en la misma sentencia (Postgres lo permite sin
    # necesitar CASCADE en el propio TRUNCATE cuando la tabla referenciante
    # también está en la lista).
    yield
    with app.app_context():
        db.session.execute(db.text("TRUNCATE TABLE comments, likes, posts, users"))
        db.session.commit()
