# Adaptador SQLAlchemy del puerto `UserRepository` (domain/auth/repositories.py).
# Único punto del backend que traduce entre `users` (PostgreSQL) y el resto de
# las capas — domain/ y application/ no importan SQLAlchemy directamente
# (BACKEND_ARCHITECTURE.md §17), solo reciben el objeto `User` ya resuelto.
#
# El `id` de `users` sigue generándose en PostgreSQL (`gen_random_uuid()`,
# ver models.py) — este repositorio nunca asigna un id manualmente.

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.domain.auth.exceptions import EmailAlreadyExistsError, UsernameAlreadyExistsError
from app.domain.auth.repositories import UserRepository
from app.extensions import db
from app.infrastructure.persistence.models import User

# Nombre de la constraint única de `username` (migración
# a1edcbff74d8_add_profile_fields_to_users.py, ADR-002) -- se inspecciona el
# `constraint_name` del error de PostgreSQL para distinguir cuál de las dos
# columnas únicas (`email`/`username`) violó el INSERT, en vez de adivinar
# por el texto del mensaje de error.
_USERNAME_UNIQUE_CONSTRAINT = "uq_users_username"


class SQLAlchemyUserRepository(UserRepository):
    def create(self, name, username, email, phone, country_code, birth_date, password_hash):
        user = User(
            name=name,
            username=username,
            email=email,
            phone=phone,
            country_code=country_code,
            birth_date=birth_date,
            password_hash=password_hash,
        )
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            constraint_name = getattr(getattr(exc.orig, "diag", None), "constraint_name", None)
            if constraint_name == _USERNAME_UNIQUE_CONSTRAINT:
                raise UsernameAlreadyExistsError(username)
            raise EmailAlreadyExistsError(email)
        return user

    def find_by_email(self, email):
        return db.session.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()

    def find_by_id(self, user_id):
        return db.session.get(User, user_id)

    def update(self, user_id, fields):
        user = db.session.get(User, user_id)
        if user is None:
            return None

        # `fields` ya viene filtrado por la whitelist del caso de uso/route
        # (ADR-003 §Seguridad) -- este repositorio no decide qué columnas
        # son editables, solo las persiste.
        for column, value in fields.items():
            setattr(user, column, value)

        try:
            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            constraint_name = getattr(getattr(exc.orig, "diag", None), "constraint_name", None)
            if constraint_name == _USERNAME_UNIQUE_CONSTRAINT:
                raise UsernameAlreadyExistsError(fields.get("username"))
            raise

        db.session.refresh(user)
        return user
