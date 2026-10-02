# Reglas de negocio de la exportación de datos (ADR-028-data-export.md). Solo
# tipos nativos de Python -- domain/ no importa Flask ni SQLAlchemy
# (BACKEND_ARCHITECTURE.md §7/§17). Placeholders de producto explícitos y
# revisables, no parámetros de despliegue.

#: Días que el archivo queda disponible para descargar. Pasado ese plazo el
#: contenido se descarta y hay que pedir otro.
EXPORT_TTL_DAYS = 7

#: Mínimo entre dos solicitudes de la misma cuenta. Generar el archivo recorre
#: todas las tablas del usuario: sin tope, pedirlo en bucle es una forma barata
#: de cargar la base.
EXPORT_COOLDOWN_SECONDS = 60 * 60

#: Cuántas solicitudes recientes se listan en el historial.
HISTORY_LIMIT = 20
