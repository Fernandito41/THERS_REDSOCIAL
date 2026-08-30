# Caso de uso: registro de un nuevo usuario. Orquesta domain/ (hashing) e
# infraestructura (repositorio, inyectado por quien llama — hoy
# interfaces/routes/auth_routes.py) sin importar Flask ni SQLAlchemy
# directamente (BACKEND_ARCHITECTURE.md §6/§17).
#
# Campos de perfil (username/phone/country_code/birth_date) agregados en
# ADR-002 (docs/architecture/ADR-002-user-profile-fields.md). `birth_date`
# ya llega como `datetime.date` (parseado y validado en la route con
# domain/auth/validators.py) -- este caso de uso no valida formato, solo
# orquesta.

from app.domain.auth.auth_service import hash_password
from app.application.auth.user_presenter import to_public_user


def register_user(name, username, email, phone, country_code, birth_date, password, user_repository):
    password_hash = hash_password(password)
    user = user_repository.create(
        name=name,
        username=username,
        email=email,
        phone=phone,
        country_code=country_code,
        birth_date=birth_date,
        password_hash=password_hash,
    )

    return to_public_user(user)
