# Adaptador SQLAlchemy del puerto `UserRepository` (domain/auth/repositories.py).
# Único punto del backend que traduce entre `users` (PostgreSQL) y el resto de
# las capas — domain/ y application/ no importan SQLAlchemy directamente
# (BACKEND_ARCHITECTURE.md §17), solo reciben el objeto `User` ya resuelto.
#
# El `id` de `users` sigue generándose en PostgreSQL (`gen_random_uuid()`,
# ver models.py) — este repositorio nunca asigna un id manualmente.

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.domain.auth.exceptions import EmailAlreadyExistsError
from app.domain.auth.repositories import UserRepository
from app.extensions import db
from app.infrastructure.persistence.models import User


class SQLAlchemyUserRepository(UserRepository):
    def create(self, name, email, password_hash):
        user = User(name=name, email=email, password_hash=password_hash)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise EmailAlreadyExistsError(email)
        return user

    def find_by_email(self, email):
        return db.session.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()
