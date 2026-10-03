# Excepciones de la aceptación de términos (ADR-032 §5).


class TermsNotAcceptedError(Exception):
    """Se intentó crear una cuenta sin aceptar los términos de uso, con la
    exigencia activada. La route la traduce a 400 con `terms_required: true`
    para que el cliente muestre la casilla sin tener que leer el texto."""


class InvalidTermsVersionError(Exception):
    """La versión que mandó el cliente no es la vigente. Lleva la vigente para
    que el cliente pueda mostrar los términos correctos y reintentar."""

    def __init__(self, current_version):
        super().__init__(current_version)
        self.current_version = current_version
