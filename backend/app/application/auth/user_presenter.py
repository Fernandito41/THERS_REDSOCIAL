# Forma pública compartida del objeto `user` devuelto por register/login/me
# (API_CONTRACT.md §5) -- centralizada acá para no duplicarla en los tres
# casos de uso (ADR-002 — docs/architecture/ADR-002-user-profile-fields.md).
# Nunca incluye password/password_hash/confirm_password/token/secret.


def to_public_user(user):
    return {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "name": user.name,
        "phone": user.phone,
        "country_code": user.country_code,
        "birth_date": user.birth_date.isoformat(),
    }
