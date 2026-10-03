# Excepciones de dominio de los reportes (ADR-032).


class ReportTargetNotFoundError(Exception):
    """El objetivo no existe **o quien reporta no puede verlo**. Es una sola
    excepción a propósito, y la route la traduce a un único `404`: reportar no
    debe servir para averiguar si algo existe ni de quién es. Mismo criterio que
    `assert_post_visible` (ADR-022/ADR-029) y que el 404 indistinguible de
    ADR-019/ADR-020."""


class CannotReportSelfError(Exception):
    """Se intentó reportar contenido o una cuenta propios. La route lo traduce
    a 400: no hay nada que ocultar, quien reporta ya sabe que es suyo."""


class InvalidReportError(Exception):
    """El cuerpo del reporte no es válido (tipo, identificador, motivo o
    texto). Lleva el mensaje para el cliente; la route lo traduce a 400."""

    def __init__(self, message):
        super().__init__(message)
        self.message = message
