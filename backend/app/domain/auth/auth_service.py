# Reglas de negocio puras de autenticación. No conoce Flask, SQLAlchemy ni
# PostgreSQL (BACKEND_ARCHITECTURE.md §7/§17) — el algoritmo de hashing sigue
# siendo werkzeug.security (scrypt), ya aprobado como corrección puntual para
# la credencial de prueba (BACKEND_ARCHITECTURE.md §9) y mantenido aquí como
# el algoritmo real para `users.password_hash`.

from werkzeug.security import check_password_hash, generate_password_hash


def hash_password(password):
    return generate_password_hash(password)


def verify_password(password, password_hash):
    return check_password_hash(password_hash, password)
