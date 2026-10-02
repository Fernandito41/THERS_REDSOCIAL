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
 * preferencia local. Lo que todavía no tiene soporte de servidor (bloqueo,
 * pagos, tokens...) es `pending` con su motivo, porque guardar un booleano
 * en el navegador no protege ningún dato (archivo maestro §8.10 y §10.2).
 * Privacidad, sesiones, 2FA y exportación de datos ya se aplican en el
 * servidor (ADR-022..ADR-028) y usan sus propios tipos de fila.
 */

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
      tone: "info",
      text: "Estos controles SÍ se aplican en el servidor (ADR-022, ADR-023, ADR-024): filtran cada consulta, deciden permisos y ocultan datos. No son preferencias de este navegador. El único control de esta pantalla que sigue sin soporte es el de canales de audio, porque esa función todavía no existe en el producto.",
    },
    groups: [
      {
        title: "Cuenta privada",
        rows: [
          {
            type: "privacySwitch",
            key: "is_private",
            label: "Cuenta privada",
            description:
              "Solo los usuarios aprobados pueden ver tus cápsulas. Quien ya te seguía lo sigue haciendo; a partir de ahora, cada persona nueva tiene que pedirlo y aprobarlo vos.",
          },
          { type: "followRequests" },
        ],
      },
      {
        title: "Interacciones",
        description: "Quién puede conectar y amplificar tu contenido.",
        index: "Sección 01",
        rows: [
          {
            type: "privacyChoice",
            key: "who_can_mention",
            label: "Menciones y etiquetas",
            description:
              "Qué usuarios pueden etiquetarte escribiendo @tu_usuario en una cápsula o un comentario. Si no están autorizados, el texto queda como texto plano y no te llega ninguna notificación.",
            options: [
              { value: "everyone", label: "Cualquiera" },
              { value: "followers", label: "Solo mis seguidores" },
              { value: "nobody", label: "Nadie" },
            ],
          },
          {
            type: "privacySwitch",
            key: "hide_offensive_comments",
            label: "Ocultar comentarios ofensivos",
            description:
              "Filtra automáticamente los comentarios con insultos o spam evidente en TUS cápsulas, para todo el que las lea. Usa una lista de términos del sistema, revisable por el equipo — no hay moderación humana ni revisión caso por caso.",
          },
          { type: "mutedKeywords" },
          {
            type: "privacyChoice",
            key: "who_can_message",
            label: "Mensajes directos",
            description:
              "Quién puede escribirte por mensaje directo. A quien no esté autorizado le aparece un aviso al intentar enviarte algo; los mensajes que ya recibiste no se borran.",
            options: [
              { value: "everyone", label: "Cualquiera" },
              { value: "followers", label: "Solo mis seguidores" },
              { value: "nobody", label: "Nadie" },
            ],
          },
        ],
      },
      {
        title: "Conexiones y visibilidad",
        description: "Tu presencia y el alcance de tus transmisiones.",
        index: "Sección 02",
        rows: [
          {
            type: "privacySwitch",
            key: "show_activity_status",
            label: "Mostrar mi estado de actividad",
            description:
              "Deja ver la última vez que estuviste activo a las personas con las que tenés una conversación. Si lo apagas, para ellas se ve igual que si nunca hubieras estado activo — no se nota que lo desactivaste.",
          },
          {
            type: "pending",
            label: "Estado de actividad en los canales de audio",
            description: "Mostrar cuándo estuviste activo en los canales de audio.",
            reason:
              "Los canales de audio no existen en el producto: no hay modelo, endpoints ni interfaz. Un interruptor de privacidad sobre una función inexistente no protegería nada. La presencia general sí está implementada, en el control de arriba (ADR-024).",
          },
        ],
      },
    ],
  },

  // REF-SET-03
  security: {
    title: "Seguridad y contraseña",
    description: "Credenciales de acceso, verificación en dos pasos y control de sesiones.",
    notice: {
      tone: "info",
      text: "Todos los controles de esta pantalla se aplican en el servidor. La verificación en dos pasos usa una app autenticadora (TOTP, ADR-026); las sesiones se registran por dispositivo y cerrarlas invalida su token de inmediato (ADR-025).",
    },
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
        rows: [{ type: "twoFactor" }],
      },
      {
        title: "Sesiones activas",
        rows: [{ type: "activeSessions" }],
      },
      {
        title: "Alertas de inicio de sesión",
        rows: [
          {
            type: "securitySwitch",
            key: "login_alerts_enabled",
            label: "Avisarme de accesos nuevos",
            description:
              "Te mandamos un correo cuando alguien entre a tu cuenta desde un dispositivo que no habíamos visto antes. No se avisa en cada inicio de sesión: solo con dispositivos nuevos, para que el aviso signifique algo.",
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
      tone: "info",
      text: "Esta función SÍ se aplica en el servidor (ADR-028): el archivo es un ZIP real con los datos de tu cuenta, generado al momento de pedirlo.",
    },
    groups: [
      {
        title: "Solicitar descarga de información",
        rows: [{ type: "dataExportRequest" }],
      },
      {
        title: "Archivos listos para descargar (Historial)",
        rows: [{ type: "dataExportHistory" }],
      },
      {
        title: "Privacidad y seguridad de tu archivo",
        rows: [
          {
            type: "info",
            label: "Caducidad del enlace",
            description:
              "Pasado ese plazo el archivo se elimina del servidor y hay que pedir uno nuevo.",
            value: "7 días",
          },
          {
            type: "info",
            label: "Quién puede descargarlo",
            description:
              "Solo tu cuenta, con la sesión iniciada. El enlace no sirve sin tu sesión ni para otra persona.",
            value: "Solo tú",
          },
          {
            type: "info",
            label: "Cifrado del paquete",
            description:
              "El ZIP no está cifrado ni protegido con contraseña: guárdalo en un lugar seguro. No incluye tu contraseña ni el secreto de tu verificación en dos pasos.",
            value: "Sin cifrar",
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
      tone: "info",
      text: "Estos controles SÍ se aplican en el servidor (ADR-029): el bloqueo corta el acceso a tu contenido en cada consulta, no solo en la interfaz. También puedes bloquear o restringir desde el menú de cualquier publicación.",
    },
    groups: [
      {
        title: "¿Qué ocurre al bloquear a alguien?",
        rows: [{ type: "restrictedAccounts", kind: "block" }],
      },
      {
        title: "Protección sutil con Cuentas Restringidas",
        rows: [{ type: "restrictedAccounts", kind: "restrict" }],
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
    notice: {
      tone: "info",
      text: "Estos filtros SÍ se aplican en el servidor (ADR-024, ADR-030): `GET /api/posts` ya no devuelve lo que ocultaste, no se esconde solo en la interfaz.",
    },
    groups: [
      {
        title: "Control de contenido sensible",
        rows: [
          {
            type: "privacySwitch",
            key: "hide_sensitive_content",
            label: "Filtrar contenido sensible",
            description:
              "Oculta de tu feed las publicaciones que su autor marcó como sensibles al publicar. Es lo que declara quien escribe, no una clasificación automática. Tus propias publicaciones nunca se ocultan.",
          },
        ],
      },
      {
        title: "Palabras y frases ocultas",
        rows: [{ type: "mutedKeywords" }],
      },
      {
        title: "Temas y etiquetas silenciadas",
        rows: [{ type: "mutedTopics" }],
      },
      {
        title: "Cuentas sugeridas en el feed",
        rows: [
          {
            type: "switch",
            key: "content.suggestions",
            label: "Mostrar cuentas sugeridas",
            description:
              "Muestra u oculta el panel «Personas que resuenan» del feed, que sugiere cuentas reales que todavía no sigues. Es una preferencia de pantalla y se guarda en este navegador.",
            default: true,
          },
        ],
      },
    ],
  },
};
