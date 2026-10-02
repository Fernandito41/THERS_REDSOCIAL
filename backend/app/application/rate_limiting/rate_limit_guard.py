# Guard de rate limiting (ADR-023-rate-limiting.md).
#
# Es el único punto que decide "este intento se pasa del límite". Lo usan todos
# los endpoints limitados, para que la regla no se reimplemente endpoint por
# endpoint con criterios distintos.
#
# Se aplica como una llamada explícita al principio de cada route y NO como un
# hook global `before_request`, a diferencia del registro de actividad
# (ADR-020/ADR-021, que sí es un hook). El motivo: un hook global tendría que
# saber qué scope y qué identidad corresponden a cada ruta, y esa correspondencia
# es justamente la decisión de producto de cada endpoint (¿se limita por IP o por
# cuenta? ¿cuenta los aciertos o solo los fallos?). Un mapa de rutas a reglas
# escondido en un hook sería más difícil de auditar que una línea visible en cada
# route -- y en un control de seguridad, poder auditarlo de un vistazo vale más
# que ahorrar la línea.

from app.domain.rate_limiting.exceptions import RateLimitExceededError


def enforce(rule, identity, rate_limit_repository):
    """Registra un intento y lanza `RateLimitExceededError` si se pasó del
    límite de `rule`.

    Se llama **antes** de evaluar la credencial, nunca después: si se contara
    solo después de fallar, el propio trabajo de verificar (scrypt, que es lento
    a propósito) ya se habría hecho, y eso es por sí mismo un vector de
    agotamiento de CPU.
    """
    attempts, retry_after = rate_limit_repository.hit(
        rule.scope, identity, rule.window_seconds
    )

    if attempts > rule.limit:
        raise RateLimitExceededError(retry_after_seconds=retry_after)


def clear(rule, identity, rate_limit_repository):
    """Borra el contador tras un intento exitoso, si la regla lo pide.

    Solo tiene efecto con `clear_on_success=True` (endpoints de credenciales):
    lo que hay que frenar ahí es *adivinar*, no *usar*. En los demás
    (`/forgot-password`, `/register`) el acierto **es** el abuso, así que el
    contador no se toca -- llamar a esto con una regla de esas es un no-op, no
    un error, para que cada route pueda invocarlo sin ramificar.
    """
    if rule.clear_on_success:
        rate_limit_repository.clear(rule.scope, identity)
