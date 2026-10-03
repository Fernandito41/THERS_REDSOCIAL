# Política de aceptación de los términos de uso (ADR-032 §5). Solo tipos
# nativos de Python.

#: Versión vigente de los términos si el entorno no define `TERMS_VERSION`.
#: Es una **fecha de publicación**, y es un PLACEHOLDER hasta que el equipo
#: publique los términos definitivos (`docs/LAUNCH_CHECKLIST.md`): cuando cambien,
#: se sube esta versión y a todo el mundo se le vuelve a pedir la aceptación.
DEFAULT_TERMS_VERSION = "2026-10-02"

#: Largo máximo aceptado para el identificador de versión que manda un cliente.
MAX_TERMS_VERSION_LENGTH = 32


def has_accepted_current_terms(terms_version, current_version):
    """`True` si la versión que aceptó la persona es la vigente. Una cuenta que
    nunca aceptó (`None`) o que aceptó una versión anterior cuenta como no
    aceptada: ADR-032 §5 trata así a las cuentas existentes."""
    return terms_version is not None and terms_version == current_version
