# Generación y hashing de tokens de un solo uso (recuperación de contraseña,
# verificación de email -- ADR-009-password-reset-and-email-verification.md).
# Solo `secrets`/`hashlib` de la librería estándar -- domain/ no debe
# importar Flask ni SQLAlchemy (BACKEND_ARCHITECTURE.md §7/§17), mismo
# criterio que domain/auth/validators.py.
#
# Deliberadamente NO se reutiliza el JWT normal de login como token de
# recuperación/verificación (ADR-009 §Opciones consideradas): un JWT es
# válido para autenticar cualquier request mientras no expire y es stateless
# -- no hay forma de invalidarlo individualmente tras un solo uso sin una
# lista de revocación aparte, que sería más trabajo que este mecanismo
# dedicado. Un token de un solo uso, opaco, respaldado por una fila en la
# base de datos que se marca usada, es más simple y más seguro para este
# caso.

import hashlib
import secrets

# 32 bytes de entropía (256 bits) codificados en base64 URL-safe -- muy por
# encima de lo necesario para hacer inviable la fuerza bruta (mismo orden de
# magnitud que un UUID v4, con más entropía real). `secrets.token_urlsafe`
# usa `os.urandom` internamente -- criptográficamente seguro, no `random`.
_TOKEN_BYTES = 32


def generate_raw_token():
    """Genera un token de un solo uso, criptográficamente seguro. Este es el
    valor que viaja en el enlace del correo y que el usuario nunca vuelve a
    ver una vez consumido -- nunca se persiste tal cual (ver hash_token)."""
    return secrets.token_urlsafe(_TOKEN_BYTES)


def hash_token(raw_token):
    """SHA-256 del token crudo, en hexadecimal -- lo único que se persiste
    en la base de datos (ADR-009 §Seguridad). No hace falta un hash lento
    tipo scrypt/bcrypt (a diferencia de password_hash, domain/auth/auth_service.py):
    el token ya tiene 256 bits de entropía propios, no una contraseña de baja
    entropía elegida por una persona -- SHA-256 alcanza para que, aunque la
    tabla se filtre, nadie pueda reconstruir el token original ni forjar uno
    que produzca el mismo hash."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
