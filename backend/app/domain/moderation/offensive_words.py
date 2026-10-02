# Lista base de términos que activan "Ocultar comentarios ofensivos"
# (ADR-020-content-filters-and-privacy-preferences.md).
#
# ───────────────────────────────────────────────────────────────────────────
# ESTA LISTA ES UN PLACEHOLDER DE PRODUCTO, NO UNA POLÍTICA DE MODERACIÓN.
#
# THERS no tiene política de moderación documentada: `CLAUDE.md` §15 lo
# registra como hueco y `DATABASE_ARCHITECTURE.md` §4.B no tiene ninguna
# candidata de roles/moderación ratificada. El equipo decidió (ADR-020
# §Decisión) implementar el mecanismo con una lista base en el repositorio,
# explícitamente revisable, en vez de dejar el interruptor sin efecto.
#
# Criterio de lo que entra acá: insultos y marcadores de spam inequívocos, en
# español y en inglés, en su forma normalizada (minúsculas). NO entran términos
# que dependan del contexto, de la identidad de quien habla o de un juicio
# editorial -- eso exige moderación humana, que el producto no tiene.
#
# Cómo ajustarla: editar esta tupla. No hace falta migración ni endpoint, y es
# deliberado -- la lista es configuración del producto, no dato de usuario (los
# términos propios de cada persona son `muted_keywords`, otra cosa).
#
# Mismo criterio de "placeholder explícito y revisable" que MAX_CONTENT_LENGTH
# (domain/posts/validators.py) y MIN_AGE_YEARS (domain/auth/validators.py).
# ───────────────────────────────────────────────────────────────────────────

OFFENSIVE_WORDS = (
    # Insultos (español)
    "idiota",
    "imbecil",
    "imbécil",
    "estupido",
    "estúpido",
    "basura",
    "inutil",
    "inútil",
    "mediocre",
    "asqueroso",
    "callate",
    "cállate",
    # Insultos (inglés)
    "idiot",
    "stupid",
    "moron",
    "loser",
    "trash",
    "shut up",
    # Marcadores de spam inequívocos
    "compra seguidores",
    "seguidores gratis",
    "free followers",
    "click aqui",
    "click aquí",
    "click here",
    "gana dinero",
    "make money fast",
    "viagra",
    "casino online",
)


def is_offensive(text):
    """True si `text` contiene alguno de los términos de la lista base.

    Reutiliza deliberadamente la misma función de coincidencia que los
    keywords propios de cada persona (`text_matches_any`): las dos cosas son
    "buscar términos en un texto", y tener dos algoritmos distintos haría que
    el filtro del sistema y el del usuario se comportaran distinto sin motivo.
    """
    from app.domain.moderation.keyword_matching import text_matches_any

    return text_matches_any(text, OFFENSIVE_WORDS)
