# Puerto (interfaz) del repositorio de usuarios. Vive en domain/ porque es un
# contrato de negocio puro — sin SQLAlchemy, sin Flask, sin PostgreSQL — que
# application/ consume y que infraestructura implementa (Repository pattern,
# BACKEND_ARCHITECTURE.md §8/§18: "la forma exacta del repositorio... queda
# PENDIENTE", esta tarea la resuelve). Cumple la regla de dependencia: domain/
# no depende de nada externo; es infraestructura la que depende de este
# módulo, no al revés.

from abc import ABC, abstractmethod


class UserRepository(ABC):
    @abstractmethod
    def create(
        self,
        name,
        username,
        email,
        phone=None,
        country_code=None,
        birth_date=None,
        password_hash=None,
        email_verified=False,
        profile_completed=True,
    ):
        """Crea un usuario y devuelve el registro creado (con `id` generado
        por PostgreSQL). Debe lanzar `EmailAlreadyExistsError` si el email ya
        existe, o `UsernameAlreadyExistsError` si el username ya existe
        (ambas en domain/auth/exceptions.py; columnas de perfil agregadas en
        ADR-002 — docs/architecture/ADR-002-user-profile-fields.md).

        `phone`/`country_code`/`birth_date`/`password_hash` son opcionales
        desde ADR-012-google-sign-in.md -- una cuenta creada vía Google no
        los tiene. `register_use_case.py` (registro tradicional) siempre los
        pasa (ya validados en la route); `google_auth_use_case.py` los deja
        en `None` y pasa `email_verified=True`/`profile_completed=False`
        explícitamente."""

    @abstractmethod
    def find_by_email(self, email):
        """Devuelve el registro de usuario cuyo email coincide
        (case-insensitive), o `None` si no existe."""

    @abstractmethod
    def find_by_id(self, user_id):
        """Devuelve el registro de usuario cuyo `id` (UUID) coincide, o
        `None` si no existe. Usado por GET /api/users/me a partir de
        get_jwt_identity() (ADR-002 §3)."""

    @abstractmethod
    def find_by_usernames(self, usernames):
        """Devuelve los usuarios cuyo `username` está en `usernames`,
        comparando **sin distinguir mayúsculas**. Usado para resolver las
        menciones de un texto en una sola consulta en vez de una por
        @username (ADR-019-mentions.md) -- mismo criterio anti N+1 que
        FollowRepository.follow_statuses.

        La comparación es case-insensitive aunque `users.username` sea
        case-sensitive en el esquema (ADR-002 §3): escribir "@Ada" tiene que
        mencionar a `ada`, que es lo que cualquiera espera al teclear."""

    @abstractmethod
    def touch_last_seen(self, user_id, min_interval_seconds):
        """Marca `last_seen_at = now()` para `user_id`, pero solo si la marca
        anterior es más vieja que `min_interval_seconds`
        (ADR-020-content-filters-and-privacy-preferences.md).

        El throttle vive en el propio WHERE, no en memoria del proceso: así
        funciona igual con varios workers, que es justo donde un caché en
        memoria fallaría (el indicador de "escribiendo" de ADR-014 aceptó esa
        limitación porque es efímero; `last_seen_at` se persiste)."""

    @abstractmethod
    def update(self, user_id, fields):
        """Actualiza únicamente las columnas presentes en `fields` (dict
        `{columna: valor}`) para el usuario `user_id`, persiste el cambio
        (un único commit) y devuelve el registro ya refrescado. Devuelve
        `None` si el usuario no existe.

        Esta capa NO decide qué campos puede editar el usuario -- la
        whitelist de campos editables pertenece al contrato/API/caso de uso
        (ADR-003 §Seguridad — docs/architecture/ADR-003-profile-update-contract.md).
        Debe lanzar `UsernameAlreadyExistsError` si `fields` incluye
        `username` y la actualización viola `uq_users_username` (mismo
        patrón que `create()`)."""


class TwoFactorRecoveryCodeRepository(ABC):
    """Puerto de los codigos de recuperacion de 2FA
    (ADR-022-two-factor-authentication.md). Separado de `UserRepository`
    porque es otra tabla con su propio ciclo de vida, aunque siempre cuelgue
    de un usuario -- mismo criterio que separa `MutedKeywordRepository` de
    las preferencias que viven en columnas de `users` (ADR-020)."""

    @abstractmethod
    def replace_all(self, user_id, code_hashes):
        """Reemplaza el juego completo de codigos: borra los anteriores y
        guarda estos. Regenerar invalida los viejos en la misma operacion --
        si no, quedarian dos juegos validos y la persona no sabria cual tiene
        anotado."""

    @abstractmethod
    def delete_all(self, user_id):
        """Borra todos los codigos. Se llama al desactivar el 2FA: dejarlos
        permitiria entrar con un codigo de recuperacion de un 2FA que ya no
        existe."""

    @abstractmethod
    def list_unused(self, user_id):
        """Los codigos sin usar, con su `code_hash` -- hay que compararlos uno
        a uno contra el que la persona escribio, porque scrypt usa sal y no se
        puede buscar por hash directamente."""

    @abstractmethod
    def count_unused(self, user_id):
        """Cuantos quedan sin usar -- se expone para poder avisar cuando se
        estan agotando."""

    @abstractmethod
    def mark_used(self, code_id):
        """Marca un codigo como usado. Devuelve True si lo marco, False si ya
        estaba usado -- la condicion va en el propio WHERE, asi que dos
        peticiones simultaneas con el mismo codigo no pueden consumirlo las
        dos."""
