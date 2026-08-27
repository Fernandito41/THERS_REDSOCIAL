// Contenido real del Centro de Ayuda. Cada artículo describe funcionalidad
// que existe hoy en THERS (verificada contra el código de Frontend/src) o,
// cuando la funcionalidad todavía no está conectada a un backend real, lo
// marca explícitamente con status: "in-progress" -- mismo criterio de
// honestidad que ya usan ForgotPassword.jsx, ResetPassword.jsx y Settings.jsx
// ("función en construcción" / "todavía no hay backend para..."). No se
// documenta ninguna política legal, de privacidad o de moderación que el
// equipo no haya definido todavía (CLAUDE.md §14-15).
//
// `sections[].type`: "p" (párrafo), "steps" (lista ordenada), "list" (lista
// simple) o "note" (recuadro informativo, para aclaraciones de estado).

export const HELP_ARTICLES = [
  // ---------------------------------------------------------------- cuenta
  {
    id: "primeros-pasos",
    slug: "primeros-pasos",
    categoryId: "cuenta",
    title: "Primeros pasos en THERS",
    description: "Un recorrido rápido por lo esencial cuando recién llegás a THERS.",
    tags: ["inicio", "onboarding", "cuenta nueva"],
    updatedAt: "2026-08-24",
    readTimeMinutes: 3,
    status: "available",
    sections: [
      {
        type: "p",
        text:
          "THERS es un espacio para compartir Cápsulas (fotos, videos, música o pensamientos), Momentos que no quedan fijos para siempre, y conectar con personas a través de tu estado de ánimo y tus intereses.",
      },
      {
        heading: "Lo básico para empezar",
        type: "steps",
        items: [
          "Creá tu cuenta con tu nombre, usuario, correo y contraseña.",
          "Iniciá sesión y llegarás directo a tu Inicio (/feed).",
          "Completá tu perfil: bio, mood actual e intereses.",
          "Explorá Descubrir para encontrar personas y temas.",
          "Publicá tu primera Cápsula desde el botón Crear.",
        ],
      },
      {
        type: "note",
        text: "Podés cambiar entre modo claro y oscuro en cualquier momento desde el menú de tu perfil o desde Configuración.",
      },
    ],
    relatedSlugs: ["crear-una-cuenta", "editar-perfil", "crear-capsulas"],
  },
  {
    id: "crear-una-cuenta",
    slug: "crear-una-cuenta",
    categoryId: "cuenta",
    title: "¿Cómo creo una cuenta en THERS?",
    description: "Los datos que necesitás para registrarte y qué validamos en cada campo.",
    tags: ["registro", "cuenta nueva", "contraseña"],
    updatedAt: "2026-08-20",
    readTimeMinutes: 2,
    status: "available",
    sections: [
      {
        type: "steps",
        items: [
          "Andá a la pantalla de registro desde \"Crear cuenta\".",
          "Completá tu nombre completo y un nombre de usuario (entre 3 y 20 caracteres: letras, números o guion bajo).",
          "Ingresá tu correo electrónico y tu número de teléfono.",
          "Seleccioná tu fecha de nacimiento. THERS requiere al menos 13 años para crear una cuenta.",
          "Elegí una contraseña de al menos 8 caracteres y confirmala.",
          "Aceptá los Términos de Servicio y la Política de Privacidad, y seleccioná \"Crear cuenta\".",
        ],
      },
      {
        type: "note",
        text: "Registrarte con Google o Apple todavía no está disponible en THERS. Los botones existen en la pantalla, pero se avisa que esa opción está en desarrollo.",
      },
    ],
    relatedSlugs: ["iniciar-sesion", "editar-perfil", "seguridad-de-tu-cuenta"],
  },
  {
    id: "iniciar-sesion",
    slug: "iniciar-sesion",
    categoryId: "cuenta",
    title: "¿Cómo inicio sesión?",
    description: "Cómo entrar a tu cuenta y qué hacer si el sistema no reconoce tus datos.",
    tags: ["login", "acceso", "cuenta"],
    updatedAt: "2026-08-20",
    readTimeMinutes: 2,
    status: "available",
    sections: [
      {
        type: "steps",
        items: [
          "Ingresá el correo electrónico con el que te registraste.",
          "Ingresá tu contraseña.",
          "Seleccioná \"Iniciar sesión\". Si tus datos son correctos, vas a llegar directo a tu Inicio.",
        ],
      },
      {
        heading: "Si ves \"Email o contraseña incorrectos\"",
        type: "p",
        text: "Ese mensaje aparece cuando el correo no está registrado o la contraseña no coincide. Por seguridad, THERS muestra el mismo mensaje en ambos casos, para no revelar si un correo existe o no en la plataforma.",
      },
    ],
    relatedSlugs: ["no-puedo-iniciar-sesion", "recuperar-cuenta", "crear-una-cuenta"],
  },
  {
    id: "no-puedo-iniciar-sesion",
    slug: "no-puedo-iniciar-sesion",
    categoryId: "cuenta",
    title: "No puedo iniciar sesión",
    description: "Pasos para resolver los problemas más comunes al entrar a tu cuenta.",
    tags: ["login", "error", "acceso"],
    updatedAt: "2026-08-20",
    readTimeMinutes: 2,
    status: "available",
    sections: [
      {
        type: "list",
        items: [
          "Revisá que el correo esté escrito exactamente como lo usaste al registrarte.",
          "Verificá que no tengas Bloq Mayús activado al escribir tu contraseña.",
          "Si ves \"No se pudo conectar con el servidor\", el problema es de conexión: probá de nuevo en unos minutos.",
          "Si olvidaste tu contraseña, usá la opción de recuperación desde la pantalla de inicio de sesión.",
        ],
      },
      {
        type: "note",
        text: "Iniciar sesión con Google o Apple todavía está en desarrollo, así que esas opciones no van a completar el ingreso por ahora.",
      },
    ],
    relatedSlugs: ["recuperar-cuenta", "iniciar-sesion", "cuenta-comprometida"],
  },
  {
    id: "editar-perfil",
    slug: "editar-perfil",
    categoryId: "cuenta",
    title: "¿Cómo edito mi perfil?",
    description: "Cambiá tu nombre, usuario, bio, mood, intereses y los colores de tu perfil.",
    tags: ["perfil", "mood", "bio", "personalización"],
    updatedAt: "2026-08-25",
    readTimeMinutes: 3,
    status: "available",
    sections: [
      {
        type: "steps",
        items: [
          "Andá a tu Perfil desde el menú de tu avatar o desde la navegación principal.",
          "Seleccioná editar para cambiar tu nombre y tu nombre de usuario.",
          "Escribí o actualizá tu bio.",
          "Elegí tu mood actual (por ejemplo Inspirado, Tranquilo o Escuchando música) para mostrarlo junto a tus Cápsulas.",
          "Agregá tus intereses y, si querés, una canción favorita.",
          "Personalizá el color de acento y el banner de tu perfil.",
        ],
      },
      {
        type: "note",
        text: "Tu bio, mood, intereses y personalización visual se guardan en este dispositivo. Todavía no hay una columna oficial de perfil extendido en la base de datos de THERS, así que ese contenido no se sincroniza entre dispositivos por el momento.",
      },
    ],
    relatedSlugs: ["primeros-pasos", "apariencia-modo-oscuro", "quien-puede-ver-tu-perfil"],
  },
  {
    id: "recuperar-cuenta",
    slug: "recuperar-cuenta",
    categoryId: "cuenta",
    title: "¿Cómo recupero el acceso a mi cuenta?",
    description: "El flujo de recuperación por correo ya tiene pantallas, pero el envío real está en desarrollo.",
    tags: ["contraseña olvidada", "recuperación", "acceso"],
    updatedAt: "2026-08-21",
    readTimeMinutes: 2,
    status: "in-progress",
    sections: [
      {
        type: "p",
        text: "THERS ya tiene lista la experiencia para recuperar tu cuenta por correo electrónico, pero el envío real del correo todavía se está terminando de conectar del lado del servidor.",
      },
      {
        heading: "Así va a funcionar",
        type: "steps",
        items: [
          "Desde \"¿Olvidaste tu contraseña?\" en la pantalla de inicio de sesión, ingresás tu correo.",
          "THERS te va a enviar un enlace de recuperación a ese correo.",
          "Al abrir el enlace, vas a poder definir una contraseña nueva de al menos 8 caracteres.",
        ],
      },
      {
        type: "note",
        text: "Por ahora, al completar el formulario vas a ver un aviso de que esta función sigue en construcción. No se envía ningún correo todavía.",
      },
    ],
    relatedSlugs: ["no-puedo-iniciar-sesion", "cambiar-contrasena", "cuenta-comprometida"],
  },

  // ------------------------------------------------------------- seguridad
  {
    id: "seguridad-de-tu-cuenta",
    slug: "seguridad-de-tu-cuenta",
    categoryId: "seguridad",
    title: "Seguridad de tu cuenta",
    description: "Qué protege hoy tu contraseña en THERS y qué buenas prácticas te recomendamos.",
    tags: ["seguridad", "contraseña", "cuenta"],
    updatedAt: "2026-08-22",
    readTimeMinutes: 3,
    status: "available",
    sections: [
      {
        type: "p",
        text: "Tu contraseña nunca se guarda ni se muestra en texto plano: THERS la protege con un algoritmo de hash antes de almacenarla, y ni el equipo puede leerla directamente.",
      },
      {
        heading: "Recomendaciones generales",
        type: "list",
        items: [
          "Usá una contraseña de al menos 8 caracteres que no uses en otros sitios.",
          "No compartas tu contraseña con nadie, ni siquiera en soporte.",
          "Desconfiá de mensajes que te pidan tu contraseña fuera de la app.",
        ],
      },
      {
        type: "note",
        text: "Todavía no hay un panel de sesiones activas ni de verificación en dos pasos en THERS. Cuando estén disponibles, vas a poder revisarlas desde Configuración.",
      },
    ],
    relatedSlugs: ["cambiar-contrasena", "cuenta-comprometida", "privacidad-en-thers"],
  },
  {
    id: "cambiar-contrasena",
    slug: "cambiar-contrasena",
    categoryId: "seguridad",
    title: "¿Cómo cambio mi contraseña?",
    description: "Cambiar la contraseña desde Configuración todavía no está disponible; así se va a hacer.",
    tags: ["contraseña", "seguridad", "cuenta"],
    updatedAt: "2026-08-22",
    readTimeMinutes: 2,
    status: "in-progress",
    sections: [
      {
        type: "p",
        text: "Hoy, Configuración todavía no tiene una opción para cambiar tu contraseña estando dentro de tu cuenta -- esa función está en desarrollo.",
      },
      {
        heading: "Cómo hacerlo mientras tanto",
        type: "p",
        text: "Podés usar el flujo de recuperación de contraseña (\"¿Olvidaste tu contraseña?\" desde la pantalla de inicio de sesión). Ese flujo ya está listo en pantalla, aunque el envío del correo real también está en construcción por ahora.",
      },
    ],
    relatedSlugs: ["recuperar-cuenta", "seguridad-de-tu-cuenta", "gestionar-tu-cuenta-desde-configuracion"],
  },
  {
    id: "cuenta-comprometida",
    slug: "cuenta-comprometida",
    categoryId: "seguridad",
    title: "Creo que mi cuenta fue comprometida",
    description: "Qué podés hacer hoy si sospechás que alguien más accedió a tu cuenta.",
    tags: ["cuenta comprometida", "seguridad", "acceso no autorizado"],
    updatedAt: "2026-08-22",
    readTimeMinutes: 2,
    status: "in-progress",
    sections: [
      {
        type: "list",
        items: [
          "Cambiá tu contraseña apenas puedas usando el flujo de recuperación.",
          "Revisá que tu nombre, usuario y bio no hayan sido modificados sin que lo hicieras vos.",
          "No reutilices en THERS una contraseña que hayas usado en otro sitio que haya sufrido una filtración.",
        ],
      },
      {
        type: "note",
        text: "THERS todavía no tiene un panel de sesiones activas para cerrar accesos de otros dispositivos, ni un canal dedicado de reporte de cuentas comprometidas. Esta guía se va a actualizar en cuanto esas herramientas existan.",
      },
    ],
    relatedSlugs: ["cambiar-contrasena", "recuperar-cuenta", "seguridad-de-tu-cuenta"],
  },

  // ------------------------------------------------------------ privacidad
  {
    id: "privacidad-en-thers",
    slug: "privacidad-en-thers",
    categoryId: "privacidad",
    title: "Privacidad en THERS",
    description: "Qué información es visible hoy en THERS y qué controles de privacidad todavía no existen.",
    tags: ["privacidad", "visibilidad", "cuenta"],
    updatedAt: "2026-08-23",
    readTimeMinutes: 3,
    status: "in-progress",
    sections: [
      {
        type: "p",
        text: "Hoy, THERS no tiene cuentas privadas ni configuración de visibilidad por publicación: tu perfil, tus Cápsulas y tus Momentos son visibles para cualquier persona que use la plataforma.",
      },
      {
        heading: "Lo que sí controlás vos",
        type: "list",
        items: [
          "Qué compartís: vos decidís cada Cápsula, Momento, mood o interés que publicás.",
          "Tu bio, mood, intereses y personalización de perfil, que podés editar o vaciar cuando quieras.",
        ],
      },
      {
        type: "note",
        text: "Cuentas privadas, listas de bloqueados y controles de visibilidad granular están en el radar del equipo, pero todavía no están implementados ni ratificados oficialmente. No los des por hecho todavía.",
      },
    ],
    relatedSlugs: ["quien-puede-ver-tu-perfil", "bloquear-a-alguien", "editar-perfil"],
  },
  {
    id: "quien-puede-ver-tu-perfil",
    slug: "quien-puede-ver-tu-perfil",
    categoryId: "privacidad",
    title: "¿Quién puede ver mi perfil y mis publicaciones?",
    description: "El alcance real de la visibilidad de tu cuenta en THERS hoy.",
    tags: ["visibilidad", "perfil", "publicaciones"],
    updatedAt: "2026-08-23",
    readTimeMinutes: 1,
    status: "available",
    sections: [
      {
        type: "p",
        text: "Cualquier persona con una cuenta en THERS puede ver tu perfil, tus Cápsulas y tus Momentos. No hace falta que te sigan para verlos.",
      },
      {
        type: "note",
        text: "No existe todavía una opción de cuenta privada. Si esta función se implementa, se va a documentar acá y en la configuración de tu cuenta.",
      },
    ],
    relatedSlugs: ["privacidad-en-thers", "seguir-y-dejar-de-seguir", "editar-perfil"],
  },
  {
    id: "bloquear-a-alguien",
    slug: "bloquear-a-alguien",
    categoryId: "privacidad",
    title: "¿Cómo bloqueo a otro usuario?",
    description: "Bloquear cuentas todavía no está disponible en THERS.",
    tags: ["bloqueo", "privacidad", "seguridad"],
    updatedAt: "2026-08-23",
    readTimeMinutes: 1,
    status: "in-progress",
    sections: [
      {
        type: "p",
        text: "THERS todavía no tiene una función para bloquear a otras cuentas. Es una herramienta que el equipo tiene planeada dentro de privacidad y moderación.",
      },
      {
        type: "note",
        text: "Mientras tanto, podés reportar una publicación puntual desde el menú de opciones de esa Cápsula (aunque el envío del reporte también está en desarrollo -- ver \"Reportar una publicación\").",
      },
    ],
    relatedSlugs: ["reportar-un-usuario", "reportar-una-publicacion", "privacidad-en-thers"],
  },

  // --------------------------------------------------------- publicaciones
  {
    id: "crear-capsulas",
    slug: "crear-capsulas",
    categoryId: "publicaciones",
    title: "¿Cómo creo una Cápsula?",
    description: "Publicá fotos, videos, música o un pensamiento en tu Cápsula.",
    tags: ["cápsulas", "publicar", "contenido"],
    updatedAt: "2026-08-24",
    readTimeMinutes: 2,
    status: "available",
    sections: [
      {
        type: "steps",
        items: [
          "Tocá el botón Crear (el ícono \"+\") desde la barra de navegación o el menú móvil.",
          "Elegí el tipo de Cápsula: foto o video, música, o un pensamiento en texto.",
          "Agregá tu contenido, un texto opcional y hashtags si querés.",
          "Publicá la Cápsula. Va a aparecer en tu Inicio y en el de las personas que te siguen.",
        ],
      },
      {
        type: "note",
        text: "Tu mood actual (si lo configuraste en tu perfil) se muestra junto a tu nombre en cada Cápsula que publicás.",
      },
    ],
    relatedSlugs: ["hashtags-y-ubicacion", "momentos", "me-gusta-y-comentarios"],
  },
  {
    id: "momentos",
    slug: "momentos",
    categoryId: "publicaciones",
    title: "¿Qué son los Momentos y cuánto duran?",
    description: "La diferencia entre una Cápsula y un Momento en THERS.",
    tags: ["momentos", "contenido efímero", "publicar"],
    updatedAt: "2026-08-24",
    readTimeMinutes: 1,
    status: "available",
    sections: [
      {
        type: "p",
        text: "Los Momentos son contenido del día a día que acompaña tu perfil sin quedarse fijo para siempre, a diferencia de una Cápsula, que sí forma parte permanente de tu Inicio.",
      },
      {
        type: "list",
        items: [
          "Se muestran en la fila de Momentos, en la parte superior del Inicio.",
          "Podés ver el mood de la persona junto a su Momento.",
        ],
      },
    ],
    relatedSlugs: ["crear-capsulas", "primeros-pasos", "editar-perfil"],
  },
  {
    id: "hashtags-y-ubicacion",
    slug: "hashtags-y-ubicacion",
    categoryId: "publicaciones",
    title: "Hashtags y ubicación en tus Cápsulas",
    description: "Cómo etiquetar temas y, si querés, mostrar una ubicación en tu publicación.",
    tags: ["hashtags", "ubicación", "cápsulas"],
    updatedAt: "2026-08-24",
    readTimeMinutes: 1,
    status: "available",
    sections: [
      {
        type: "p",
        text: "Al crear una Cápsula podés agregar hashtags para relacionarla con un tema (por ejemplo #thers o #nuevosproyectos) y, si querés, una ubicación que se muestra debajo de tu nombre.",
      },
      {
        type: "note",
        text: "Agregar la ubicación es opcional. Si no la completás, la Cápsula se publica sin ella.",
      },
    ],
    relatedSlugs: ["crear-capsulas", "editar-o-eliminar-publicaciones"],
  },
  {
    id: "editar-o-eliminar-publicaciones",
    slug: "editar-o-eliminar-publicaciones",
    categoryId: "publicaciones",
    title: "¿Cómo edito o elimino una publicación?",
    description: "Editar y eliminar Cápsulas después de publicarlas todavía está en desarrollo.",
    tags: ["editar", "eliminar", "cápsulas"],
    updatedAt: "2026-08-24",
    readTimeMinutes: 1,
    status: "in-progress",
    sections: [
      {
        type: "p",
        text: "Hoy no hay una opción para editar o eliminar una Cápsula después de publicarla. Es una función que todavía está en desarrollo.",
      },
      {
        heading: "Lo que sí podés hacer hoy",
        type: "list",
        items: [
          "Copiar el enlace de la Cápsula desde el menú de opciones (el ícono ⋯).",
          "Ocultarla desde ese mismo menú, para dejar de verla en tu propio Inicio.",
        ],
      },
    ],
    relatedSlugs: ["crear-capsulas", "reportar-una-publicacion"],
  },

  // -------------------------------------------------------- interacciones
  {
    id: "me-gusta-y-comentarios",
    slug: "me-gusta-y-comentarios",
    categoryId: "interacciones",
    title: "Likes y comentarios",
    description: "Cómo reaccionar y comentar en las Cápsulas de otras personas.",
    tags: ["likes", "comentarios", "interacción"],
    updatedAt: "2026-08-21",
    readTimeMinutes: 1,
    status: "available",
    sections: [
      {
        type: "steps",
        items: [
          "Tocá el corazón en una Cápsula para darle Like. Volvé a tocarlo para quitarlo.",
          "Tocá \"Comentar\" para abrir la caja de comentarios y escribir el tuyo.",
          "El número de likes y comentarios se actualiza al instante debajo de la Cápsula.",
        ],
      },
    ],
    relatedSlugs: ["guardar-y-compartir", "crear-capsulas", "tipos-de-notificaciones"],
  },
  {
    id: "guardar-y-compartir",
    slug: "guardar-y-compartir",
    categoryId: "interacciones",
    title: "Guardar y compartir una Cápsula",
    description: "Guardá contenido para más tarde o copiá su enlace para compartirlo.",
    tags: ["guardados", "compartir", "interacción"],
    updatedAt: "2026-08-21",
    readTimeMinutes: 1,
    status: "available",
    sections: [
      {
        type: "list",
        items: [
          "Tocá el ícono de marcador (\"Guardar\") en una Cápsula para agregarla a tus guardados.",
          "Tocá \"Compartir\" para copiar el enlace directo a esa Cápsula al portapapeles.",
        ],
      },
      {
        type: "note",
        text: "Compartir copia el enlace a tu portapapeles; no lo publica en ningún otro lugar automáticamente.",
      },
    ],
    relatedSlugs: ["me-gusta-y-comentarios", "crear-capsulas"],
  },
  {
    id: "seguir-y-dejar-de-seguir",
    slug: "seguir-y-dejar-de-seguir",
    categoryId: "interacciones",
    title: "Seguir y dejar de seguir a alguien",
    description: "Cómo empezar (o dejar) de seguir a otras cuentas en THERS.",
    tags: ["seguir", "seguidores", "descubrir"],
    updatedAt: "2026-08-21",
    readTimeMinutes: 1,
    status: "available",
    sections: [
      {
        type: "steps",
        items: [
          "Andá a Descubrir para ver sugerencias de personas.",
          "Tocá \"Seguir\" en la tarjeta de esa persona.",
          "Para dejar de seguirla, volvé a tocar el mismo botón, que ahora muestra que ya la seguís.",
        ],
      },
      {
        type: "note",
        text: "Cuando alguien empieza a seguirte, te llega una notificación.",
      },
    ],
    relatedSlugs: ["tipos-de-notificaciones", "quien-puede-ver-tu-perfil"],
  },

  // ------------------------------------------------------- notificaciones
  {
    id: "tipos-de-notificaciones",
    slug: "tipos-de-notificaciones",
    categoryId: "notificaciones",
    title: "Tipos de notificaciones en THERS",
    description: "Qué te avisa THERS y dónde encontrarlo.",
    tags: ["notificaciones", "avisos"],
    updatedAt: "2026-08-19",
    readTimeMinutes: 1,
    status: "available",
    sections: [
      {
        type: "list",
        items: [
          "Reacciones: cuando alguien le da like a tu Cápsula o Momento.",
          "Comentarios: cuando alguien comenta tu Cápsula.",
          "Nuevos seguidores: cuando alguien empieza a seguirte.",
          "Menciones: cuando alguien te menciona en una Cápsula.",
        ],
      },
      {
        type: "p",
        text: "Todas se ven desde Notificaciones, con un contador de las que todavía no leíste en el ícono de campana.",
      },
    ],
    relatedSlugs: ["marcar-como-leidas", "preferencias-de-notificaciones", "me-gusta-y-comentarios"],
  },
  {
    id: "marcar-como-leidas",
    slug: "marcar-como-leidas",
    categoryId: "notificaciones",
    title: "Marcar notificaciones como leídas",
    description: "Cómo limpiar el contador de notificaciones sin leídas.",
    tags: ["notificaciones", "leídas"],
    updatedAt: "2026-08-19",
    readTimeMinutes: 1,
    status: "available",
    sections: [
      {
        type: "list",
        items: [
          "Tocá una notificación individual para marcarla como leída.",
          "Usá la opción de marcar todas como leídas para limpiar el contador de una sola vez.",
        ],
      },
    ],
    relatedSlugs: ["tipos-de-notificaciones", "preferencias-de-notificaciones"],
  },
  {
    id: "preferencias-de-notificaciones",
    slug: "preferencias-de-notificaciones",
    categoryId: "notificaciones",
    title: "¿Puedo elegir qué notificaciones recibir?",
    description: "Las preferencias de notificaciones todavía no están disponibles en THERS.",
    tags: ["notificaciones", "preferencias"],
    updatedAt: "2026-08-19",
    readTimeMinutes: 1,
    status: "in-progress",
    sections: [
      {
        type: "p",
        text: "Por ahora, THERS no tiene una pantalla para activar o desactivar tipos de notificaciones puntuales (likes, comentarios, seguidores, menciones) por separado. Todas se muestran juntas en Notificaciones.",
      },
      {
        type: "note",
        text: "Cuando esta opción esté disponible, se va a poder configurar desde Configuración.",
      },
    ],
    relatedSlugs: ["tipos-de-notificaciones", "gestionar-tu-cuenta-desde-configuracion"],
  },

  // ------------------------------------------------------------- reportes
  {
    id: "reportar-una-publicacion",
    slug: "reportar-una-publicacion",
    categoryId: "reportes",
    title: "¿Cómo reporto una publicación?",
    description: "El botón de reportar ya existe en cada Cápsula; el envío real está en desarrollo.",
    tags: ["reportes", "moderación", "cápsulas"],
    updatedAt: "2026-08-25",
    readTimeMinutes: 1,
    status: "in-progress",
    sections: [
      {
        type: "steps",
        items: [
          "Tocá el ícono ⋯ en la esquina superior derecha de la Cápsula que querés reportar.",
          "Seleccioná \"Reportar\" en el menú.",
        ],
      },
      {
        type: "note",
        text: "Esta opción ya está en la interfaz, pero todavía no envía el reporte a un equipo de moderación real -- esa conexión está en desarrollo del lado del servidor.",
      },
    ],
    relatedSlugs: ["reportar-un-usuario", "que-pasa-luego-de-un-reporte", "bloquear-a-alguien"],
  },
  {
    id: "reportar-un-usuario",
    slug: "reportar-un-usuario",
    categoryId: "reportes",
    title: "¿Cómo reporto a un usuario?",
    description: "Reportar una cuenta completa todavía no está disponible en THERS.",
    tags: ["reportes", "moderación", "usuarios"],
    updatedAt: "2026-08-25",
    readTimeMinutes: 1,
    status: "in-progress",
    sections: [
      {
        type: "p",
        text: "Hoy no hay una opción para reportar una cuenta completa desde su perfil. Podés reportar una publicación puntual de esa cuenta desde el menú de esa Cápsula (ver \"Reportar una publicación\").",
      },
    ],
    relatedSlugs: ["reportar-una-publicacion", "que-pasa-luego-de-un-reporte", "bloquear-a-alguien"],
  },
  {
    id: "que-pasa-luego-de-un-reporte",
    slug: "que-pasa-luego-de-un-reporte",
    categoryId: "reportes",
    title: "¿Qué pasa después de reportar algo?",
    description: "El proceso de revisión de reportes todavía no está implementado.",
    tags: ["reportes", "moderación"],
    updatedAt: "2026-08-25",
    readTimeMinutes: 1,
    status: "in-progress",
    sections: [
      {
        type: "p",
        text: "THERS todavía no tiene un proceso de moderación conectado que reciba y resuelva reportes. Por eso, hoy un reporte no dispara una revisión real ni una notificación de resultado.",
      },
      {
        type: "note",
        text: "Este artículo se va a actualizar en cuanto exista un flujo de moderación oficial, incluyendo tiempos y qué esperar después de reportar.",
      },
    ],
    relatedSlugs: ["reportar-una-publicacion", "reportar-un-usuario"],
  },

  // --------------------------------------------------------- configuración
  {
    id: "apariencia-modo-oscuro",
    slug: "apariencia-modo-oscuro",
    categoryId: "configuracion",
    title: "Cambiar entre modo claro y oscuro",
    description: "THERS nació oscura; así se cambia de tema cuando quieras.",
    tags: ["apariencia", "tema", "modo oscuro"],
    updatedAt: "2026-08-18",
    readTimeMinutes: 1,
    status: "available",
    sections: [
      {
        type: "steps",
        items: [
          "Abrí el menú de tu avatar, en la esquina superior derecha.",
          "Seleccioná \"Modo claro\" o \"Modo oscuro\" para alternar entre ambos.",
          "También podés cambiarlo desde la sección Apariencia en Configuración.",
        ],
      },
      {
        type: "note",
        text: "La primera vez que entrás a THERS, el modo oscuro es el predeterminado. A partir de ahí, tu elección se recuerda en este dispositivo.",
      },
    ],
    relatedSlugs: ["gestionar-tu-cuenta-desde-configuracion", "editar-perfil"],
  },
  {
    id: "gestionar-tu-cuenta-desde-configuracion",
    slug: "gestionar-tu-cuenta-desde-configuracion",
    categoryId: "configuracion",
    title: "Gestionar tu cuenta desde Configuración",
    description: "Qué encontrás hoy en la pantalla de Configuración de THERS.",
    tags: ["configuración", "cuenta"],
    updatedAt: "2026-08-18",
    readTimeMinutes: 1,
    status: "available",
    sections: [
      {
        type: "list",
        items: [
          "Cuenta: tu nombre, usuario y correo, con acceso directo a editar tu perfil.",
          "Apariencia: el interruptor de modo claro/oscuro.",
          "Cerrar sesión: para salir de tu cuenta en este dispositivo.",
        ],
      },
      {
        type: "note",
        text: "La gestión de contraseña, sesiones activas y privacidad de la cuenta todavía no está disponible en Configuración -- queda pendiente hasta que exista esa parte del backend.",
      },
    ],
    relatedSlugs: ["apariencia-modo-oscuro", "cerrar-sesion", "cambiar-contrasena"],
  },
  {
    id: "cerrar-sesion",
    slug: "cerrar-sesion",
    categoryId: "configuracion",
    title: "¿Cómo cierro sesión?",
    description: "Cerrar tu sesión de THERS en este dispositivo.",
    tags: ["cerrar sesión", "cuenta", "acceso"],
    updatedAt: "2026-08-18",
    readTimeMinutes: 1,
    status: "available",
    sections: [
      {
        type: "steps",
        items: [
          "Abrí el menú de tu avatar o andá a Configuración.",
          "Seleccioná \"Cerrar sesión\".",
          "Vas a volver a la pantalla de inicio de sesión.",
        ],
      },
      {
        type: "note",
        text: "THERS todavía no tiene una lista de sesiones activas en otros dispositivos -- cerrar sesión solo afecta al dispositivo donde lo hacés.",
      },
    ],
    relatedSlugs: ["gestionar-tu-cuenta-desde-configuracion", "seguridad-de-tu-cuenta"],
  },
];

export function getArticleBySlug(slug) {
  return HELP_ARTICLES.find((article) => article.slug === slug) || null;
}

export function getArticlesByCategory(categoryId) {
  return HELP_ARTICLES.filter((article) => article.categoryId === categoryId);
}

export function getRelatedArticles(article) {
  if (!article) return [];
  return article.relatedSlugs
    .map((slug) => getArticleBySlug(slug))
    .filter(Boolean);
}
