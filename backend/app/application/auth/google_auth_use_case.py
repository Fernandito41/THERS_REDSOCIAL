# Caso de uso: "Continuar con Google" (POST /api/auth/google,
# ADR-012-google-sign-in.md). Resuelve, en una sola operación, los tres
# caminos posibles de la FASE 3/7/9 de la tarea origen:
#
#   1. Ya existe una identidad de Google vinculada -> login directo.
#   2. No existe ninguna cuenta con ese email -> se crea una nueva, con
#      perfil incompleto (Google no da teléfono/fecha de nacimiento).
#   3. Ya existe una cuenta de THERS con ese email (tradicional o Google
#      sin vincular todavía) -> account linking, con la política de
#      seguridad de la FASE 9 (ver `_link_or_reclaim_existing_account`).
#
# `google_identity_verifier.verify()` es lo único que puede lanzar
# `InvalidGoogleCredentialError` -- a partir de ahí, todos los claims
# (`sub`, `email`, `email_verified`, `name`) ya están verificados
# criptográficamente contra las claves públicas reales de Google (firma,
# `iss`, `aud`, `exp`) -- este caso de uso nunca vuelve a cuestionar esos
# tres primeros, solo decide qué hacer con ellos.
#
# Google NO se convierte en sustituto del JWT de THERS (FASE 15): esta
# función nunca emite un token -- devuelve el `user` público, igual que
# login_user()/register_user(); la route (composition root) es quien llama
# a create_access_token() después, con el mismo mecanismo de siempre.

from app.application.auth.user_presenter import to_public_user
from app.domain.auth.exceptions import GoogleEmailNotVerifiedError
from app.domain.auth.placeholder_username import generate_placeholder_username

GOOGLE_PROVIDER = "google"


def authenticate_with_google(
    credential, google_identity_verifier, user_repository, user_identity_repository
):
    identity = google_identity_verifier.verify(credential)

    existing_identity = user_identity_repository.find_by_provider_and_subject(
        GOOGLE_PROVIDER, identity.sub
    )
    if existing_identity is not None:
        # Camino 1 -- cuenta de Google ya vinculada antes: login directo,
        # sin volver a tocar nada de `users` (ni siquiera si Google cambió
        # `name` desde la última vez -- eso es responsabilidad de
        # PATCH /api/users/me, no de este flujo).
        user = user_repository.find_by_id(existing_identity.user_id)
        return to_public_user(user)

    # A partir de acá, la cuenta de Google todavía no tiene una identidad
    # vinculada en THERS -- FASE 8: sin `email_verified=true` de parte de
    # Google, no hay ninguna garantía en la que THERS pueda apoyarse para
    # crear o vincular una cuenta a partir de este email. Se rechaza antes
    # de tocar `users`.
    if not identity.email_verified:
        raise GoogleEmailNotVerifiedError()

    existing_user = user_repository.find_by_email(identity.email)

    if existing_user is None:
        user = _create_new_google_user(identity, user_repository)
    else:
        user = _link_or_reclaim_existing_account(identity, existing_user, user_repository)

    user_identity_repository.create(user.id, GOOGLE_PROVIDER, identity.sub)

    return to_public_user(user)


def _create_new_google_user(identity, user_repository):
    # Camino 2 -- cuenta nueva. `email_verified=True` directo: la garantía
    # de Google ya cumple el mismo propósito que el OTP de THERS
    # (ADR-011-mandatory-email-verification.md) cumple para el registro
    # tradicional -- exigir además un código de THERS sería redundante
    # (FASE 8 §Decisión). `profile_completed=False`: Google no entrega
    # teléfono/fecha de nacimiento, y el username es un placeholder que la
    # persona todavía no eligió -- el Frontend redirige a "Complete your
    # profile" (mismo patrón que ya usa `email_verified` para verificación
    # de registro, ver Login.jsx/router.jsx).
    return user_repository.create(
        name=identity.name or identity.email.split("@")[0],
        username=generate_placeholder_username(),
        email=identity.email,
        email_verified=True,
        profile_completed=False,
    )


def _link_or_reclaim_existing_account(identity, existing_user, user_repository):
    # Camino 3 -- FASE 9 de la tarea origen (account linking). Política
    # determinística, sin pedirle a la persona un paso de confirmación
    # interactivo -- documentada en ADR-012-google-sign-in.md §Decisión:
    #
    # - Si la cuenta YA estaba verificada (`email_verified=True`, alguien ya
    #   probó controlar ese correo antes -- vía OTP tradicional, o vía un
    #   Google Sign-In anterior con otro proveedor): se vincula sin más.
    #   Cualquier contraseña que ya tuviera sigue existiendo -- Google se
    #   agrega como un método MÁS, no reemplaza al que había.
    #
    # - Si la cuenta NUNCA se verificó: nadie probó nunca que fuera su
    #   dueño real -- podría ser una cuenta que alguien registró con este
    #   email sin ser quien lo controla (mismo riesgo que
    #   ADR-011-mandatory-email-verification.md ya identificó para
    #   reintentos de registro). Ahora que Google SÍ prueba quién controla
    #   el correo, la cuenta se "reclama" para esa persona: se marca
    #   verificada y se anula cualquier `password_hash` existente (si quien
    #   la registró no era el dueño real, esa contraseña nunca debió dar
    #   acceso a nadie) -- mismo criterio que el reintento de registro de
    #   ADR-011 sobrescribe la fila entera. El resto del perfil (name,
    #   username, teléfono) se deja tal cual: no hay evidencia de que esos
    #   datos sean falsos, solo la contraseña es la pieza sin garantías.
    if existing_user.email_verified:
        return existing_user

    return user_repository.update(
        existing_user.id, {"email_verified": True, "password_hash": None}
    )
