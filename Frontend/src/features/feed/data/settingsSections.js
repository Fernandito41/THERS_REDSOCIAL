/**
 * Contenido de las 12 secciones de Configuración.
 *
 * Los títulos de sección y de cada grupo están tomados literalmente de sus
 * referencias (REF-SET-01..12). Las descripciones NO: siete de las doce
 * referencias rellenan sus textos con «Lorem ipsum dolor sit amet», que es
 * relleno de maqueta y no copia de producto. Donde la referencia tenía lorem
 * ipsum se ha escrito una descripción real que explica lo que hace el control.
 *
 * Tipos de fila (ver components/settings/SettingsPrimitives.jsx):
 *   switch  — preferencia booleana, se guarda en este navegador
 *   choice  — preferencia de opción única, se guarda en este navegador
 *   pending — dibujado en la referencia, sin soporte de servidor
 *   info    — dato real de solo lectura
 *
 * REGLA APLICADA: nada que dependa de una decisión de servidor se modela como
 * preferencia local. Privacidad efectiva, bloqueo, 2FA, sesiones, pagos,
 * verificación, tokens y exportación son `pending` con su motivo, porque
 * guardar un booleano en el navegador no protege ningún dato
 * (archivo maestro §8.10 y §10.2).
 */

const NO_BACKEND = "No hay endpoint que lo aplique: guardarlo en el navegador no cambiaría nada en el servidor.";

export const SETTINGS_CONTENT = {
  // REF-SET-01
  profile: {
    title: "Editar perfil",
    description:
      "Tu identidad pública en THERS. Nombre y usuario se guardan en el servidor; el resto del perfil extendido vive en este navegador.",
    groups: [
      {
        title: "Identidad",
        description: "Los únicos campos que el backend persiste hoy (ADR-003).",
        rows: [{ type: "profileLink" }],
      },
    ],
  },

  // REF-SET-02
  privacy: {
    title: "Privacidad de la cuenta",
    description:
      "Gestiona la exposición de tu identidad en THERS, define quién puede interactuar con tus resonancias y mantén el control de tu visibilidad.",
    notice: {
      tone: "warning",
      text: "Ninguno de estos controles se aplica todavía en el servidor. THERS no tiene aún reglas de privacidad en el backend, así que estas opciones no protegen tus datos: quedan registradas como preferencia hasta que existan.",
    },
    groups: [
      {
        title: "Cuenta privada",
        rows: [
          {
            type: "pending",
            label: "Cuenta privada",
            description:
              "Solo los usuarios aprobados podrían ver tus cápsulas y resonancias.",
            reason: "Requiere que el servidor filtre cada consulta por relación de seguimiento.",
          },
        ],
      },
      {
        title: "Interacciones",
        description: "Quién puede conectar y amplificar tu contenido.",
        index: "Sección 01",
        rows: [
          {
            type: "pending",
            label: "Menciones y etiquetas",
            description: "Qué usuarios pueden etiquetarte en cápsulas compartidas.",
            reason: "No existe el modelo de menciones ni etiquetas.",
          },
          {
            type: "pending",
            label: "Ocultar comentarios ofensivos",
            description: "Filtrar automáticamente respuestas agresivas o spam en tus cápsulas.",
            reason: "No hay moderación de comentarios en el servidor.",
          },
          {
            type: "pending",
            label: "Filtros de palabras clave personalizadas",
            description: "Términos que activarían moderación silenciosa en cualquier hilo.",
            reason: NO_BACKEND,
          },
          {
            type: "pending",
            label: "Mensajes directos",
            description: "Quién puede escribirte y qué peticiones van a solicitudes pendientes.",
            reason: "No existe mensajería en el backend.",
          },
        ],
      },
      {
        title: "Conexiones y visibilidad",
        description: "Tu presencia y el alcance de tus transmisiones.",
        index: "Sección 02",
        rows: [
          {
            type: "pending",
            label: "Estado de actividad en el radar sonoro",
            description: "Mostrar cuándo estuviste activo en los canales de audio.",
            reason: "No hay sistema de presencia ni canales de audio.",
          },
        ],
      },
    ],
  },

  // REF-SET-03
  security: {
    title: "Seguridad y contraseña",
    description: "Credenciales de acceso, verificación en dos pasos y control de sesiones.",
    groups: [
      {
        title: "Cambiar contraseña",
        description: "El flujo de recuperación por correo sí está implementado (ADR-009).",
        rows: [{ type: "passwordReset" }],
      },
      {
        title: "Verificación de correo",
        rows: [{ type: "emailVerification" }],
      },
      {
        title: "Autenticación en dos pasos (2FA)",
        rows: [
          {
            type: "pending",
            label: "Activar 2FA",
            description: "Un segundo factor además de la contraseña al iniciar sesión.",
            reason:
              "No está implementado. Mostrarlo como activo sería afirmar una protección inexistente (archivo maestro §10.2).",
          },
        ],
      },
      {
        title: "Sesiones activas",
        rows: [
          {
            type: "pending",
            label: "Ver y cerrar sesiones",
            action: "Ver sesiones",
            description: "Dispositivos con la sesión abierta y opción de revocarlos.",
            reason:
              "El JWT no se registra por dispositivo, así que no hay nada que listar ni revocar de verdad.",
          },
        ],
      },
      {
        title: "Alertas de inicio de sesión",
        rows: [
          {
            type: "pending",
            label: "Avisarme de accesos nuevos",
            description: "Un correo cuando alguien entre desde un dispositivo desconocido.",
            reason: "Requiere registro de sesiones, que no existe.",
          },
        ],
      },
    ],
  },

  // REF-SET-04
  subscription: {
    title: "Suscripción y verificación de creador",
    description: "Plan de la cuenta, facturación y requisitos de verificación.",
    notice: {
      tone: "warning",
      text: "THERS no tiene pasarela de pagos ni proceso de verificación. No se recogen documentos de identidad ni datos de tarjeta en ninguna pantalla.",
    },
    groups: [
      {
        title: "Beneficios activos de la cuenta",
        rows: [{ type: "info", label: "Plan actual", description: "Todas las cuentas son iguales hoy.", value: "Estándar" }],
      },
      {
        title: "Plan y facturación",
        rows: [
          {
            type: "pending",
            label: "Gestionar suscripción",
            action: "Gestionar",
            description: "Cambiar de plan y método de pago.",
            reason: "No hay pasarela de pagos integrada y no se procesarán cobros reales.",
          },
        ],
      },
      {
        title: "Historial reciente de recibos",
        rows: [
          {
            type: "pending",
            label: "Descargar recibos",
            action: "Descargar",
            description: "Comprobantes de los cobros realizados.",
            reason: "No existen cobros, así que no hay recibos que emitir.",
          },
        ],
      },
      {
        title: "Requisitos de verificación y documentos",
        rows: [
          {
            type: "pending",
            label: "Solicitar verificación",
            action: "Solicitar",
            description: "Acreditar la identidad del creador.",
            reason:
              "No se recogen documentos de identidad: haría falta un flujo autorizado y almacenamiento seguro que no existe.",
          },
        ],
      },
    ],
  },

  // REF-SET-05
  tools: {
    title: "Herramientas y Resonancias",
    description: "Centro de control de audio y radar para creadores.",
    groups: [
      {
        title: "Parámetros del Radar Urbano",
        rows: [
          {
            type: "pending",
            label: "Radar urbano",
            description: "Alcance y precisión con que tu actividad aparece en el radar.",
            reason: "Radar no tiene servicio conectado (archivo maestro §8.8).",
          },
        ],
      },
      {
        title: "Telemetría y grabación de cápsulas",
        rows: [
          {
            type: "pending",
            label: "Grabación de telemetría",
            description: "Registro de métricas de escucha de tus cápsulas.",
            reason:
              "No se activa ningún rastreo ni grabación desde una maqueta (archivo maestro §8.10).",
          },
        ],
      },
      {
        title: "Métricas y analíticas públicas",
        rows: [
          {
            type: "pending",
            label: "Mostrar métricas en tu perfil",
            description: "Hacer visibles tus estadísticas de alcance.",
            reason: "No se registran métricas de alcance.",
          },
        ],
      },
    ],
  },

  // REF-SET-06 — preferencias, NO el centro de notificaciones
  notifications: {
    title: "Notificaciones",
    description:
      "Qué quieres que THERS te avise. Esto son preferencias de aviso, no el centro de notificaciones.",
    notice: {
      tone: "info",
      text: "Estas preferencias se guardan en este navegador y son independientes del permiso de notificaciones del navegador. Cambiar un interruptor aquí no envía ningún correo.",
    },
    groups: [
      {
        title: "Interacciones y Cápsulas",
        rows: [
          { type: "switch", key: "notif.likes", label: "Me gusta en mis cápsulas", default: true },
          { type: "switch", key: "notif.comments", label: "Comentarios en mis cápsulas", default: true },
          { type: "switch", key: "notif.follows", label: "Nuevos seguidores", default: true },
        ],
      },
      {
        title: "Radar y Ubicación",
        rows: [
          {
            type: "pending",
            label: "Actividad cercana",
            description: "Avisos cuando ocurra algo en tu zona.",
            reason: "Radar no tiene servicio conectado.",
          },
        ],
      },
      {
        title: "Mensajes y Llamadas",
        rows: [
          {
            type: "pending",
            label: "Mensajes directos",
            description: "Avisos de mensajes nuevos.",
            reason: "No existe mensajería en el backend.",
          },
        ],
      },
      {
        title: "Notificaciones por Correo Electrónico",
        rows: [
          {
            type: "pending",
            label: "Resumen por correo",
            description: "Un resumen periódico de tu actividad.",
            reason:
              "El envío de correo está limitado a recuperación y verificación (ADR-009); no hay resúmenes.",
          },
        ],
      },
    ],
  },

  // REF-SET-07
  audio: {
    title: "Audio y reproducción",
    description: "Calidad, motor espacial, descargas y reproducción automática.",
    notice: {
      tone: "warning",
      text: "THERS todavía no reproduce audio: no hay modelo de cápsulas sonoras ni reproductor. «Lossless», «48 kHz», «96 kHz» y «binaural» describirían capacidades que el motor no procesa, así que no se ofrecen como opciones activas.",
    },
    groups: [
      {
        title: "Calidad de Streaming de Audio",
        rows: [
          {
            type: "pending",
            label: "Calidad de reproducción",
            description: "Resolución con la que se transmitiría el audio.",
            reason: "No hay motor de audio que aplique la preferencia.",
          },
        ],
      },
      {
        title: "Audio Espacial y Motor Binaural",
        rows: [
          {
            type: "pending",
            label: "Audio espacial",
            description: "Procesado binaural para escucha con auriculares.",
            reason: "No existe procesamiento de audio en el producto.",
          },
        ],
      },
      {
        title: "Descargas y Caché Offline",
        rows: [
          {
            type: "pending",
            label: "Descargas sin conexión",
            description: "Guardar cápsulas para escucharlas sin red.",
            reason: "No hay archivos de audio que descargar.",
          },
        ],
      },
      {
        title: "Reproducción automática",
        rows: [
          {
            type: "switch",
            key: "audio.autoplay",
            label: "Reproducir automáticamente",
            description:
              "Preferencia registrada desde ya: cuando exista reproductor, se respetará sin tener que volver aquí.",
            default: false,
          },
        ],
      },
    ],
  },

  // REF-SET-08
  links: {
    title: "Enlaces y Redes Conectadas",
    description: "Tu enlace principal, redes vinculadas y enlaces personalizados.",
    notice: {
      tone: "info",
      text: "Un enlace público no es lo mismo que una cuenta conectada por OAuth. THERS no tiene integración OAuth con ninguna plataforma: lo que se guarda aquí es texto, no una cuenta vinculada.",
    },
    groups: [
      {
        title: "Enlace Principal de Perfil (Bio Link)",
        description: "Se edita desde «Editar perfil» y se muestra en tu perfil público.",
        rows: [{ type: "profileLink" }],
      },
      {
        title: "Plataformas y Redes Vinculadas",
        rows: [
          {
            type: "pending",
            label: "Conectar una plataforma",
            action: "Conectar",
            description: "Vincular tu cuenta de otra red mediante OAuth.",
            reason:
              "No hay integración OAuth. Mostrar una cuenta como «conectada» sería falso (archivo maestro §10.2).",
          },
        ],
      },
      {
        title: "Añadir enlace personalizado",
        rows: [
          {
            type: "pending",
            label: "Enlaces adicionales",
            action: "Añadir",
            description: "Varios enlaces listados en tu perfil.",
            reason: "El perfil admite un único enlace y se guarda localmente.",
          },
        ],
      },
    ],
  },

  // REF-SET-09
  data: {
    title: "Descarga de datos y archivo",
    description: "Solicita una copia de tu información y consulta el historial de descargas.",
    notice: {
      tone: "warning",
      text: "No se genera ningún archivo. Un ZIP de muestra no sería una exportación real de tus datos (archivo maestro §8.10), así que la función queda declarada como no disponible.",
    },
    groups: [
      {
        title: "Solicitar descarga de información",
        rows: [
          {
            type: "pending",
            label: "Solicitar mi archivo",
            action: "Solicitar",
            description: "Una copia de tus publicaciones, perfil y actividad.",
            reason: "No existe el trabajo de exportación en el servidor.",
          },
        ],
      },
      {
        title: "Archivos listos para descargar (Historial)",
        rows: [
          {
            type: "pending",
            label: "Historial de solicitudes",
            action: "Ver historial",
            description: "Estado de tus exportaciones anteriores.",
            reason: "Sin exportaciones que registrar.",
          },
        ],
      },
      {
        title: "Privacidad y seguridad de tu archivo",
        rows: [
          {
            type: "pending",
            label: "Protección del archivo",
            description: "Caducidad del enlace de descarga y cifrado del paquete.",
            reason: NO_BACKEND,
          },
        ],
      },
    ],
  },

  // REF-SET-10
  blocked: {
    title: "Cuentas bloqueadas y restringidas",
    description: "Bloquear y restringir son dos cosas distintas y se listan por separado.",
    notice: {
      tone: "warning",
      text: "No existe el modelo de bloqueo ni de restricción en la base de datos. Ocultar a alguien solo en la interfaz no le impediría acceder a tu contenido, así que no se simula.",
    },
    groups: [
      {
        title: "¿Qué ocurre al bloquear a alguien?",
        rows: [
          {
            type: "pending",
            label: "Cuentas bloqueadas",
            action: "Ver lista",
            description:
              "Una cuenta bloqueada no podría ver tu contenido ni interactuar contigo.",
            reason: "Requiere comprobación de acceso en el servidor, que no existe.",
          },
        ],
      },
      {
        title: "Protección sutil con Cuentas Restringidas",
        rows: [
          {
            type: "pending",
            label: "Cuentas restringidas",
            action: "Ver lista",
            description:
              "Una cuenta restringida sigue viendo tu perfil, pero sus comentarios quedan ocultos para los demás.",
            reason: "Sin modelo de restricción ni moderación de comentarios.",
          },
        ],
      },
    ],
  },

  // REF-SET-11
  permissions: {
    title: "Permisos y aplicaciones de terceros",
    description: "Aplicaciones autorizadas y tokens de desarrollador.",
    notice: {
      tone: "warning",
      text: "No se muestran ni se generan tokens. Un token ficticio en pantalla sería un secreto falso, y revocar una fila de una tabla no revocaría ninguna autorización real.",
    },
    groups: [
      {
        title: "Aplicaciones autorizadas",
        rows: [
          {
            type: "pending",
            label: "Aplicaciones conectadas",
            action: "Ver aplicaciones",
            description: "Aplicaciones con acceso a tu cuenta y sus permisos.",
            reason: "THERS no tiene sistema de autorización de aplicaciones de terceros.",
          },
        ],
      },
      {
        title: "Tokens de Acceso de API y Desarrollador",
        rows: [
          {
            type: "pending",
            label: "Generar token",
            action: "Generar",
            description: "Credenciales para usar la API desde tus propias herramientas.",
            reason: "No existe emisión de tokens de API ni forma de revocarlos.",
          },
        ],
      },
    ],
  },

  // REF-SET-12
  content: {
    title: "Preferencias de contenido y feed",
    description: "Qué ves en tu feed y qué prefieres no ver.",
    groups: [
      {
        title: "Control de contenido sensible",
        rows: [
          {
            type: "pending",
            label: "Filtrar contenido sensible",
            description: "Ocultar publicaciones marcadas como sensibles.",
            reason: "No existe clasificación de contenido en el servidor.",
          },
        ],
      },
      {
        title: "Palabras y frases ocultas",
        rows: [
          {
            type: "pending",
            label: "Lista de palabras ocultas",
            action: "Editar lista",
            description: "Publicaciones con estos términos no aparecerían en tu feed.",
            reason: "El feed no admite filtros: `GET /api/posts` devuelve la lista completa.",
          },
        ],
      },
      {
        title: "Temas y etiquetas silenciadas",
        rows: [
          {
            type: "pending",
            label: "Temas silenciados",
            action: "Editar",
            description: "Temas que prefieres no ver.",
            reason: "No existe el modelo de temas ni etiquetas.",
          },
        ],
      },
      {
        title: "Cuentas sugeridas en el feed",
        rows: [
          {
            type: "switch",
            key: "content.suggestions",
            label: "Mostrar cuentas sugeridas",
            description:
              "Controla el panel «Personas que resuenan» del feed, que hoy usa datos de ejemplo.",
            default: true,
          },
        ],
      },
    ],
  },
};
