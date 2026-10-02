# Regla de visibilidad de contenido de una cuenta privada
# (ADR-022-private-accounts.md). Función pura: recibe hechos ya resueltos y
# devuelve una decisión -- sin Flask, sin SQLAlchemy, sin repositorios
# (BACKEND_ARCHITECTURE.md §7/§17). Quien la llama es responsable de averiguar
# esos hechos; esta es la única definición de la regla en todo el backend, para
# que ningún endpoint la reimplemente con un criterio distinto.
#
# El feed (`GET /api/posts`) NO la usa: ahí el filtro tiene que vivir en SQL
# para no romper el límite de la página (si se filtrara en Python, una página
# de 50 podría devolver 3). La condición de aquel WHERE es la traducción
# literal de esta función -- ver SQLAlchemyPostRepository.list_recent, que la
# cita explícitamente.


def can_view_content_of(author_is_private, author_id, viewer_id, viewer_is_accepted_follower):
    """¿Puede `viewer_id` ver el contenido de `author_id`?

    Tres caminos dan `True`, en este orden:
      1. La cuenta del autor no es privada -- el caso de la inmensa mayoría.
      2. El espectador es el propio autor. Nadie se oculta su propio
         contenido, y nadie se sigue a sí mismo (`ck_follows_no_self_follow`,
         ADR-007), así que sin este caso una cuenta privada no vería sus
         propias publicaciones.
      3. El espectador tiene un follow **aceptado** hacia el autor. Una
         solicitud en `pending` no alcanza: pedir no es seguir
         (ADR-022 §Decisión).
    """
    if not author_is_private:
        return True
    if str(author_id) == str(viewer_id):
        return True
    return viewer_is_accepted_follower
