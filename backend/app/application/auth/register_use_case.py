# Caso de uso: registro de un nuevo usuario. Orquesta domain/ (hashing) e
# infraestructura (repositorio, inyectado por quien llama — hoy
# interfaces/routes/auth_routes.py) sin importar Flask ni SQLAlchemy
# directamente (BACKEND_ARCHITECTURE.md §6/§17).

from app.domain.auth.auth_service import hash_password


def register_user(name, email, password, user_repository):
    password_hash = hash_password(password)
    user = user_repository.create(name=name, email=email, password_hash=password_hash)

    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
    }
