# Username provisorio para una cuenta nueva creada vía "Continuar con
# Google" (ADR-012-google-sign-in.md §Decisión, FASE 7 de la tarea origen).
#
# Google no entrega ningún dato utilizable como username único de THERS
# (`name` no es único, `email` tiene un formato distinto al de
# `domain/auth/validators.USERNAME_RE`) -- `users.username` sigue siendo
# NOT NULL UNIQUE, así que hace falta *algún* valor para poder insertar la
# fila antes de que la persona elija el suyo en la pantalla "Complete your
# profile". Generado con `secrets` (CSPRNG, no `random`) -- mismo criterio
# que el resto de identificadores sensibles de esta app (OTP, tokens de un
# solo uso) -- para que la probabilidad de colisión sea despreciable.
#
# Deliberadamente NUNCA se presenta como el username "real" de la cuenta:
# `users.username_changed_at` se deja en `NULL` (= "nunca cambió su
# username" para `domain/auth/username_policy.py`) hasta que la persona
# elija uno propio vía PATCH /api/users/me -- así elegir su username por
# primera vez en el onboarding nunca choca con el cooldown de 30 días.

import secrets

_PREFIX = "user_"
_RANDOM_HEX_CHARS = 12


def generate_placeholder_username():
    return _PREFIX + secrets.token_hex(_RANDOM_HEX_CHARS // 2)
