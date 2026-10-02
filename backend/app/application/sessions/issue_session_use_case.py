# Emisión de una sesión: el paso que convierte un JWT recién creado en una
# sesión revocable (ADR-025-session-registry.md).
#
# Lo llaman los tres caminos que emiten un token de sesión: `POST /api/login`,
# `POST /api/auth/google` y `POST /api/2fa/verify`. Está centralizado acá
# justamente para que no se pueda emitir un token sin registrar su sesión --
# si eso pasara, ese token funcionaría pero sería invisible e irrevocable
# desde la pantalla de Seguridad.
#
# También es donde se decide si corresponde una alerta de inicio de sesión:
# el momento en que se sabe que hay un dispositivo nuevo es exactamente este.

from app.application.email.email_service import EmailService


def issue_session(
    user, token_jti, user_agent, ip_address, session_repository, email_service=None,
    refresh_family_id=None,
):
    """Registra la sesión del token y, si corresponde, avisa por correo.

    `user` es la entidad completa (no el dict público): hacen falta `email`,
    `name` y `login_alerts_enabled`, que el presenter no expone.

    Devuelve la sesión creada.
    """
    # La comprobación de "dispositivo conocido" tiene que hacerse ANTES de
    # crear la fila: después, el propio `user_agent` que acabamos de guardar
    # haría que cualquier dispositivo pareciera conocido.
    is_new_device = not session_repository.has_seen_user_agent(user.id, user_agent)

    session = session_repository.create(
        user.id, token_jti, user_agent, ip_address, refresh_family_id
    )

    if is_new_device and user.login_alerts_enabled and email_service is not None:
        # Un fallo de correo NO puede impedir el login: la alerta es un aviso,
        # no un requisito de autenticación. Mismo criterio que el hook de
        # presencia (ADR-024), que tampoco tumba la respuesta.
        try:
            email_service.send_login_alert_email(
                user.email, user.name, user_agent, ip_address, session.created_at
            )
        except Exception:
            pass

    return session
