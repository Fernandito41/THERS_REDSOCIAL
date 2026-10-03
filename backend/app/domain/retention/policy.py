# Política de conservación de datos técnicos (ADR-037-data-retention.md).
#
# Solo tipos nativos de Python: domain/ no importa Flask ni SQLAlchemy
# (BACKEND_ARCHITECTURE.md §17).
#
# DECISIÓN DEL EQUIPO (2026-10-02): los datos de sesión se conservan **90 días**.
# Es un placeholder de producto explícito y revisable, no una variable de entorno.
# La política de privacidad debe decir lo mismo que este número.

# Qué cuenta como "viejo":
#  - sesión (con IP y agente de usuario): sin uso desde hace más de 90 días, o cerrada
#    (revocada) hace más de 90 días;
#  - token de renovación: creado hace más de 90 días (vale 30, así que ya no sirve ni
#    para detectar reutilización);
#  - códigos de verificación y de recuperación: creados hace más de 90 días (ya
#    vencidos o usados desde hace mucho; solo guardan el hash scrypt del código).
SESSION_RETENTION_DAYS = 90
