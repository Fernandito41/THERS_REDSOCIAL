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
    # ADR-004-posts-minimal-model.md) -- un TRUNCATE de una sola tabla falla
    # si la otra tiene filas dependientes, salvo que ambas se trunquen juntas
    # en la misma sentencia (Postgres lo permite sin necesitar CASCADE en el
    # propio TRUNCATE cuando la tabla referenciante también está en la lista).
    yield
    with app.app_context():
        db.session.execute(db.text("TRUNCATE TABLE posts, users"))
        db.session.commit()
