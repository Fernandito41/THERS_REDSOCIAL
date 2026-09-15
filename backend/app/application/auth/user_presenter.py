# Forma pública compartida del objeto `user` devuelto por register/login/me
# (API_CONTRACT.md §5) -- centralizada acá para no duplicarla en los tres
# casos de uso (ADR-002 — docs/architecture/ADR-002-user-profile-fields.md).
# Nunca incluye password/password_hash/confirm_password/token/secret.
#
# followers_count/following_count (ADR-007-follows-minimal-model.md):
# defaults en 0 -- un usuario recién registrado no tiene seguidores/seguidos
# todavía (register/login no reciben estos contadores, solo GET/PATCH
# /api/users/me los calcula de verdad).
#
# email_verified (ADR-009-password-reset-and-email-verification.md): sí se
# lee directo de `user.email_verified` en los tres casos (a diferencia de
# followers_count/following_count, no requiere una consulta agregada aparte)
# -- una cuenta recién registrada siempre es `False` (DEFAULT false en la
# columna), coherente con que registrarse no verifica el email por sí solo.


def to_public_user(user, followers_count=0, following_count=0):
    return {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "name": user.name,
        "phone": user.phone,
        "country_code": user.country_code,
        "birth_date": user.birth_date.isoformat(),
        "followers_count": followers_count,
        "following_count": following_count,
        "email_verified": user.email_verified,
    }
