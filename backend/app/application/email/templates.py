# Plantillas HTML reutilizables de los correos de THERS (ADR-009-password-reset-and-email-verification.md
# §Fase 6 de la tarea: "plantilla HTML reutilizable en lugar de construir
# HTML desordenado dentro de las rutas"). Cada función devuelve
# `(subject, html_body)` -- application/email/email_service.py las usa, las
# routes nunca construyen HTML directamente.
#
# Deliberadamente sin Jinja/`flask.render_template`: application/ no debe
# depender de Flask (mismo principio ya aplicado en el resto de application/,
# p. ej. application/auth/login_use_case.py no importa Flask) -- HTML inline
# con estilos en línea (`style="..."` en cada elemento, no un `<style>` en
# el `<head>`) porque la mayoría de clientes de correo (Gmail, Outlook)
# ignoran o eliminan hojas de estilo externas/embebidas.
#
# Todo el texto va en español, mismo idioma que el resto de mensajes de la
# API (API_CONTRACT.md §3, `{"msg": "..."}`).

_BRAND_COLOR = "#6C4DF6"  # mismo morado de marca que Frontend/tailwind.config.js (pulse-600)


def _shell(preheader, title, body_html, footer_note):
    # `preheader`: texto oculto que muchos clientes de correo muestran como
    # resumen junto al asunto en la bandeja de entrada -- mejora la
    # previsualización sin alterar el diseño visible del correo.
    return f"""<!doctype html>
<html lang="es">
  <body style="margin:0;padding:0;background-color:#f4f4f7;font-family:Helvetica,Arial,sans-serif;">
    <span style="display:none;font-size:1px;color:#f4f4f7;line-height:1px;max-height:0;max-width:0;opacity:0;overflow:hidden;">{preheader}</span>
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f4f7;padding:32px 16px;">
      <tr>
        <td align="center">
          <table role="presentation" width="480" cellpadding="0" cellspacing="0" style="background-color:#ffffff;border-radius:16px;overflow:hidden;max-width:480px;width:100%;">
            <tr>
              <td style="background-color:{_BRAND_COLOR};padding:24px 32px;">
                <span style="color:#ffffff;font-size:20px;font-weight:700;letter-spacing:0.02em;">THERS</span>
              </td>
            </tr>
            <tr>
              <td style="padding:32px;">
                <h1 style="margin:0 0 16px;font-size:20px;color:#1a1a1a;">{title}</h1>
                {body_html}
              </td>
            </tr>
            <tr>
              <td style="padding:20px 32px;background-color:#fafafa;border-top:1px solid #eeeeee;">
                <p style="margin:0;font-size:12px;color:#888888;line-height:1.5;">{footer_note}</p>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>"""


def _button(href, label):
    return (
        f'<a href="{href}" '
        f'style="display:inline-block;background-color:{_BRAND_COLOR};color:#ffffff;'
        'text-decoration:none;font-weight:600;font-size:14px;padding:12px 28px;'
        'border-radius:999px;margin:8px 0 20px;">'
        f"{label}</a>"
    )


def password_reset_email(name, reset_link, ttl_minutes):
    subject = "Recuperá tu contraseña de THERS"
    body = f"""
        <p style="margin:0 0 16px;font-size:14px;color:#333333;line-height:1.6;">
          Hola {name},
        </p>
        <p style="margin:0 0 16px;font-size:14px;color:#333333;line-height:1.6;">
          Recibimos una solicitud para restablecer la contraseña de tu cuenta de THERS.
          Tocá el siguiente botón para elegir una nueva contraseña:
        </p>
        {_button(reset_link, "Restablecer contraseña")}
        <p style="margin:0 0 16px;font-size:13px;color:#666666;line-height:1.6;">
          Este enlace vence en {ttl_minutes} minutos y solo puede usarse una vez.
        </p>
        <p style="margin:0;font-size:13px;color:#666666;line-height:1.6;">
          Si vos no solicitaste este cambio, podés ignorar este correo con tranquilidad:
          tu contraseña actual sigue siendo válida y no se realizó ningún cambio en tu cuenta.
        </p>
    """
    footer = (
        "Este es un mensaje automático de THERS. Si el botón no funciona, "
        f"copiá y pegá este enlace en tu navegador:<br>{reset_link}"
    )
    return subject, _shell(
        preheader="Restablecé tu contraseña de THERS",
        title="Restablecer tu contraseña",
        body_html=body,
        footer_note=footer,
    )


def password_changed_email(name):
    subject = "Tu contraseña de THERS fue actualizada"
    body = f"""
        <p style="margin:0 0 16px;font-size:14px;color:#333333;line-height:1.6;">
          Hola {name},
        </p>
        <p style="margin:0 0 16px;font-size:14px;color:#333333;line-height:1.6;">
          Te confirmamos que la contraseña de tu cuenta de THERS se cambió correctamente.
        </p>
        <p style="margin:0;font-size:13px;color:#666666;line-height:1.6;">
          Si vos no hiciste este cambio, tu cuenta puede estar comprometida --
          te recomendamos restablecer tu contraseña de nuevo de inmediato desde
          la pantalla de inicio de sesión.
        </p>
    """
    footer = "Este es un mensaje automático de THERS, enviado por seguridad en cada cambio de contraseña."
    return subject, _shell(
        preheader="Tu contraseña fue actualizada",
        title="Contraseña actualizada",
        body_html=body,
        footer_note=footer,
    )


def email_verification_email(name, verify_link, ttl_hours):
    subject = "Verificá tu correo en THERS"
    body = f"""
        <p style="margin:0 0 16px;font-size:14px;color:#333333;line-height:1.6;">
          Hola {name},
        </p>
        <p style="margin:0 0 16px;font-size:14px;color:#333333;line-height:1.6;">
          Confirmá que esta es tu dirección de correo para terminar de activar
          tu cuenta de THERS:
        </p>
        {_button(verify_link, "Verificar mi correo")}
        <p style="margin:0 0 16px;font-size:13px;color:#666666;line-height:1.6;">
          Este enlace vence en {ttl_hours} horas y solo puede usarse una vez.
        </p>
        <p style="margin:0;font-size:13px;color:#666666;line-height:1.6;">
          Si vos no creaste esta cuenta, podés ignorar este correo.
        </p>
    """
    footer = (
        "Este es un mensaje automático de THERS. Si el botón no funciona, "
        f"copiá y pegá este enlace en tu navegador:<br>{verify_link}"
    )
    return subject, _shell(
        preheader="Verificá tu correo para activar tu cuenta de THERS",
        title="Verificar tu correo",
        body_html=body,
        footer_note=footer,
    )
