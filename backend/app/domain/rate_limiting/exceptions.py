# Excepciones de dominio del rate limiting (ADR-023-rate-limiting.md).


class RateLimitExceededError(Exception):
    """Se superaron los intentos permitidos para esa combinacion de scope e
    identidad dentro de la ventana en curso.

    Lleva `retry_after_seconds` porque la route lo necesita para el header
    `Retry-After` del 429: decirle al cliente "demasiados intentos" sin decirle
    cuanto esperar lo deja reintentando a ciegas, que es peor para todos --
    para el usuario legitimo (no sabe cuando volver) y para el servidor (sigue
    recibiendo peticiones).

    La route lo traduce a **429**, primer uso de ese codigo en la API
    (`API_CONTRACT.md` §3). No se usa 403: el pedido no esta prohibido, esta
    de mas -- y 429 es lo que cualquier cliente HTTP sabe interpretar como
    "frena y reintenta"."""

    def __init__(self, retry_after_seconds):
        super().__init__("Demasiados intentos")
        self.retry_after_seconds = retry_after_seconds
