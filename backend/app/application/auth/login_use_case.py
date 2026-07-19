from app.domain.auth.auth_service import validate_user


def login_user(email, password):

    if not validate_user(email, password):
        return None

    return {
        "email": email,
        "name": "Fernando"
    }