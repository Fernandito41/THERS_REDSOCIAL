# Comandos de línea de comandos de la moderación (ADR-032 §3).
#
# `is_moderator` se asigna SOLO por aquí, nunca por la API: así una cuenta
# comprometida no puede ascenderse a sí misma. Se ejecutan en el servidor, con
# acceso a la base de datos:
#
#   flask set-moderator persona@correo.com            # concede el rol
#   flask set-moderator persona@correo.com --revoke   # lo retira
#   flask unsuspend-user persona@correo.com           # levanta una suspensión

import click

from app.infrastructure.persistence.repositories.moderation_repository import (
    SQLAlchemyModerationRepository,
)
from app.infrastructure.persistence.repositories.user_repository import (
    SQLAlchemyUserRepository,
)


def register_cli(app):
    moderation_repository = SQLAlchemyModerationRepository()
    user_repository = SQLAlchemyUserRepository()

    def _find(email):
        user = user_repository.find_by_email(email.strip())
        if user is None:
            raise click.ClickException("No existe una cuenta con ese correo")
        return user

    @app.cli.command("set-moderator")
    @click.argument("email")
    @click.option("--revoke", is_flag=True, help="Retira el rol en vez de concederlo.")
    def set_moderator(email, revoke):
        """Concede o retira el rol de moderación a una cuenta."""
        user = _find(email)
        moderation_repository.set_moderator(user.id, not revoke)
        if revoke:
            click.echo("Rol de moderación retirado.")
            return
        click.echo("Rol de moderación concedido.")
        if not user.two_factor_enabled:
            # ADR-032 §Riesgos: una cuenta moderadora comprometida puede retirar
            # contenido y suspender cuentas. Exigir la 2FA sigue siendo decisión del equipo.
            click.echo(
                "AVISO: esta cuenta no tiene la verificación en dos pasos (2FA) activada. "
                "Se recomienda activarla antes de moderar."
            )

    @app.cli.command("unsuspend-user")
    @click.argument("email")
    def unsuspend_user(email):
        """Levanta la suspensión de una cuenta."""
        user = _find(email)
        if moderation_repository.unsuspend_user(user.id):
            click.echo("Suspensión levantada.")
        else:
            click.echo("La cuenta no estaba suspendida.")
