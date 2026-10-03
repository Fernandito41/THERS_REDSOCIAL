# Versión vigente de los términos de uso (ADR-032 §5).
#
# Mismo patrón que `application/media/media_url.py`: la configuración se fija
# UNA vez al crear la app (`create_app`) y el resto del código la lee sin
# importar Flask. Así `to_public_user` puede decir si una cuenta aceptó la
# versión vigente sin depender de `current_app`.

from app.domain.terms.policy import DEFAULT_TERMS_VERSION

_current_version = DEFAULT_TERMS_VERSION


def configure_terms_version(version):
    global _current_version
    _current_version = (version or "").strip() or DEFAULT_TERMS_VERSION


def current_terms_version():
    return _current_version
