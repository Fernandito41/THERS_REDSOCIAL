# Excepciones de la moderación de la plataforma (ADR-032, fase 2).


class InvalidModerationRequestError(Exception):
    """La petición no es válida (acción, nota, motivo, filtro o paginación). Lleva
    el mensaje para el cliente; la route lo traduce a 400."""

    def __init__(self, message):
        super().__init__(message)
        self.message = message


class ModerationReportNotFoundError(Exception):
    """El reporte no existe. La route lo traduce a 404."""


class ReportAlreadyResolvedError(Exception):
    """El reporte ya estaba cerrado. 409: dos moderadores no deben pisarse."""


class CannotModerateSelfError(Exception):
    """Quien modera es la cuenta reportada (ADR-032 §3: no puede resolver un
    reporte sobre sí mismo ni suspenderse). 403."""


class ActionNotApplicableError(Exception):
    """La acción no se puede aplicar a este reporte (por ejemplo, retirar el
    contenido de un reporte sobre una cuenta). Lleva el mensaje; 400."""

    def __init__(self, message):
        super().__init__(message)
        self.message = message
