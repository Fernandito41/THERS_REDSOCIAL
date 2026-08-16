from werkzeug.security import check_password_hash

# Credencial de prueba temporal (ver BACKEND_ARCHITECTURE.md §9). El hash corresponde
# a la contraseña "123456", generado con werkzeug.security.generate_password_hash.
# Se reemplaza por una consulta real a la tabla `users` (DATABASE_ARCHITECTURE.md §5)
# cuando la capa de persistencia se implemente.
_TEST_USER_EMAIL = "test@test.com"
_TEST_USER_PASSWORD_HASH = (
    "scrypt:32768:8:1$xtvTwCsjfHDhcG71$02b458e2725e058ac7b963e0429ebe4606888921691c"
    "f2cd9603b45d2287d55957ea8280c0f84353cad816a38ddd68ee1f053dd33e2804e6b6d20b4ece6"
    "697a2"
)


def validate_user(email, password):

    return (
        email == _TEST_USER_EMAIL
        and check_password_hash(_TEST_USER_PASSWORD_HASH, password)
    )
