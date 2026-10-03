# Adaptador SQLAlchemy del puerto `RateLimitRepository`
# (domain/rate_limiting/repositories.py). Único punto del backend que traduce
# entre `rate_limit_buckets` (PostgreSQL) y el resto de las capas
# (BACKEND_ARCHITECTURE.md §17).
#
# Usa PostgreSQL y no memoria del proceso: un contador en memoria se pierde al
# reiniciar y no se comparte entre workers, así que con dos workers el límite
# real sería el doble del configurado. Mismo razonamiento por el que ADR-025
# descartó una lista negra en memoria para revocar tokens.

import hashlib
import math
import random

from sqlalchemy import case, delete, func, text
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.domain.rate_limiting.repositories import RateLimitRepository
from app.extensions import db
from app.infrastructure.persistence.models import RateLimitBucket

#: Cada cuántas llamadas a `hit()` se intenta purgar, en promedio. 1/200 mantiene
#: la tabla acotada sin añadir un DELETE a cada petición.
#:
#: Es una purga **oportunista**, no un proceso programado: el proyecto no tiene
#: tareas periódicas (DevOps sin documentación oficial, `CLAUDE.md` §15). No es
#: lo ideal y está registrado como tal (ADR-027 §Riesgos).
_PURGE_PROBABILITY_DENOMINATOR = 200

#: Las filas se purgan cuando su ventana venció hace más de esto. Holgado a
#: propósito: una fila vencida no afecta a ningún límite (el UPSERT la reinicia),
#: así que no hay prisa por borrarla.
_PURGE_AFTER_SECONDS = 24 * 60 * 60


def _hash_identity(identity):
    # SHA-256 y no scrypt: acá no se protege un secreto de baja entropía contra
    # fuerza bruta offline (como en password_hash o code_hash), solo se evita
    # guardar emails e IPs en claro. Además corre en el camino caliente de cada
    # intento de login, donde un hash lento sería un coste innecesario.
    return hashlib.sha256(str(identity).encode("utf-8")).hexdigest()


class SQLAlchemyRateLimitRepository(RateLimitRepository):
    def hit(self, scope, identity, window_seconds):
        identity_hash = _hash_identity(identity)

        # `INSERT ... ON CONFLICT DO UPDATE ... RETURNING` en UNA sentencia:
        # crear la fila, reiniciar la ventana vencida y sumar el intento son
        # atómicos. Si fueran tres pasos (leer, decidir, escribir), dos
        # peticiones simultáneas leerían el mismo valor y escribirían el mismo
        # incremento -- perdiendo uno. Y la concurrencia ES el escenario de un
        # ataque de fuerza bruta, no un caso raro.
        window_expired = RateLimitBucket.window_started_at < func.now() - text(
            f"interval '{int(window_seconds)} seconds'"
        )

        statement = (
            pg_insert(RateLimitBucket)
            .values(
                scope=scope,
                identity_hash=identity_hash,
                window_started_at=func.now(),
                attempts=1,
            )
            .on_conflict_do_update(
                constraint="uq_rate_limit_scope_identity",
                set_={
                    # Si la ventana venció, este intento abre una nueva (1);
                    # si no, se suma a la que está en curso.
                    "attempts": case(
                        (window_expired, 1),
                        else_=RateLimitBucket.attempts + 1,
                    ),
                    "window_started_at": case(
                        (window_expired, func.now()),
                        else_=RateLimitBucket.window_started_at,
                    ),
                },
            )
            # `elapsed` se calcula DENTRO del mismo RETURNING, no en una
            # consulta aparte. Dos motivos:
            #
            #  1. En RETURNING, `window_started_at` es el valor YA actualizado,
            #     así que `now() - window_started_at` da 0 cuando la ventana
            #     acaba de reiniciarse y el tiempo transcurrido real cuando no
            #     -- exactamente lo que hace falta para el `Retry-After`.
            #
            #  2. **Una consulta posterior al commit abriría una transacción
            #     nueva que quedaría abierta**, y en PostgreSQL `now()` es el
            #     instante de inicio de transacción: la siguiente llamada a
            #     `hit()` reutilizaría ese `now()` rancio y nunca vería la
            #     ventana como vencida. Era un bug real, detectado al probar el
            #     reinicio de ventana (ADR-027 §Decisión).
            .returning(
                RateLimitBucket.attempts,
                func.extract(
                    "epoch", func.now() - RateLimitBucket.window_started_at
                ).label("elapsed_seconds"),
            )
        )

        attempts, elapsed_seconds = db.session.execute(statement).one()
        db.session.commit()

        # Mínimo 1 segundo: un `Retry-After: 0` invita a reintentar de inmediato.
        retry_after = max(1, math.ceil(window_seconds - float(elapsed_seconds)))

        self._maybe_purge()

        return attempts, retry_after

    def clear(self, scope, identity):
        db.session.execute(
            delete(RateLimitBucket).where(
                RateLimitBucket.scope == scope,
                RateLimitBucket.identity_hash == _hash_identity(identity),
            )
        )
        db.session.commit()

    def clear_identity(self, identity):
        db.session.execute(
            delete(RateLimitBucket).where(
                RateLimitBucket.identity_hash == _hash_identity(identity)
            )
        )
        db.session.commit()

    def purge_expired(self, older_than_seconds=_PURGE_AFTER_SECONDS):
        result = db.session.execute(
            delete(RateLimitBucket).where(
                RateLimitBucket.window_started_at
                < func.now() - text(f"interval '{int(older_than_seconds)} seconds'")
            )
        )
        db.session.commit()
        return result.rowcount

    def _maybe_purge(self):
        # Purga oportunista: una de cada N llamadas. Un fallo acá no puede
        # afectar al límite que se acaba de aplicar -- la limpieza es
        # mantenimiento, no parte de la decisión de seguridad.
        if random.randrange(_PURGE_PROBABILITY_DENOMINATOR) != 0:
            return
        try:
            self.purge_expired()
        except Exception:
            db.session.rollback()
