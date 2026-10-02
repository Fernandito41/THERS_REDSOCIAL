# Tipos de relación de restricción entre cuentas
# (ADR-025-blocked-and-restricted-accounts.md). Strings y no ENUM de
# PostgreSQL, mismo criterio que domain/follows/follow_status.py.

#: Bloqueo: en ambos sentidos nadie ve ni interactúa con el otro.
BLOCK = "block"

#: Restricción: la cuenta restringida sigue viendo todo, pero sus comentarios
#: en las publicaciones de quien restringe quedan ocultos para los demás.
RESTRICT = "restrict"
