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
#
# ADR-011-mandatory-email-verification.md: la cuenta se crea con
# `email_verified=false` (default de columna, ver models.py) y de inmediato
# se le envía un código de verificación -- no queda "plenamente activa"
# hasta que se verifique (login_use_case.py la bloquea mientras tanto).
#
# Estrategia A elegida en ADR-011 (usuario pendiente vía `email_verified`,
# no una tabla de "registros pendientes" separada): si ya existe una cuenta
# con este email pero NUNCA se verificó, esta llamada la actualiza con los
# datos nuevos (incluida la contraseña) y le reenvía un código, en vez de
# rechazarla con 409 o crear una fila duplicada -- así un registro que
# nunca se completó no bloquea el email para siempre (ADR-011 §Decisión).
# Si el email ya pertenece a una cuenta verificada, sigue siendo un 409
# real (EmailAlreadyExistsError), sin cambios de comportamiento ahí.

from app.application.auth.send_registration_code_use_case import send_registration_code
from app.application.auth.user_presenter import to_public_user
from app.domain.auth.auth_service import hash_password
from app.domain.auth.exceptions import EmailAlreadyExistsError


def register_user(
    name, username, email, phone, country_code, birth_date, password,
    user_repository, email_verification_token_repository, email_service,
):
    password_hash = hash_password(password)
    existing = user_repository.find_by_email(email)

    if existing is not None:
        if existing.email_verified:
            raise EmailAlreadyExistsError(email)
        # Reintento de un registro nunca verificado -- se actualiza la
        # misma fila con los datos nuevos. `UserRepository.update()` ya
        # lanza UsernameAlreadyExistsError si `username` pasa a pertenecer
        # a otra cuenta -- mismo camino que un registro nuevo.
        user = user_repository.update(existing.id, {
            "name": name,
            "username": username,
            "phone": phone,
            "country_code": country_code,
            "birth_date": birth_date,
            "password_hash": password_hash,
        })
    else:
        user = user_repository.create(
            name=name,
            username=username,
            email=email,
            phone=phone,
            country_code=country_code,
            birth_date=birth_date,
            password_hash=password_hash,
        )

    send_registration_code(user, email_verification_token_repository, email_service)

    return to_public_user(user)
