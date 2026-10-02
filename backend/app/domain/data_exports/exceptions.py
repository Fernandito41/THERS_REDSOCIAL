class DataExportNotFoundError(Exception):
    """No existe una exportación con ese id **para ese usuario**. Es la misma
    excepción si el id no existe o es de otra cuenta: no se revela cuál."""


class DataExportExpiredError(Exception):
    """La exportación existe pero su plazo de descarga venció."""


class DataExportCooldownError(Exception):
    def __init__(self, retry_after_seconds):
        super().__init__("Exportación solicitada hace muy poco")
        self.retry_after_seconds = retry_after_seconds
