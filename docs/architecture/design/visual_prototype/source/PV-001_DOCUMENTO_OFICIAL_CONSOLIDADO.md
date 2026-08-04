# PV-001 — THERS Engineering Handbook Visual Prototype

## Documento Oficial Consolidado

| Campo | Valor |
|---|---|
| Documento | PV-001 |
| Nombre | THERS Engineering Handbook Visual Prototype |
| Versión | 1.0 |
| Estado | Aprobado para Implementación — condicionado a la ratificación pendiente registrada en la Parte 7 (Anexo) y confirmada en la Parte 10 |
| Tipo | Documento Oficial |
| Dependencias | HB-001 · STD-001 · ARC-001 · DS-001 · WF-001 |
| Uso | Referencia oficial única para la implementación del THERS Engineering Handbook en React + Vite + Tailwind CSS |

Este documento consolida en un solo archivo las diez partes desarrolladas de PV-001, previamente entregadas como documentos de trabajo independientes durante el proceso de diseño. No contiene diseño nuevo — es la unión, sin contradicciones, de todo lo ya revisado y aprobado por fases.

---

## Nota de consolidación

Al integrar las fases en un único documento se retiraron los contenidos que quedaron **superados por una versión posterior más completa**, para que este documento no contenga dos respuestas distintas a la misma pregunta:

- Las versiones compactas originales de Home, Página de Documento, Página de Categoría y Responsive (del primer borrador de PV-001) fueron reemplazadas aquí por sus versiones detalladas — son las que se presentan en las Partes 1 a 4.
- La Accesibilidad, la Microinteracciones y la Preparación para React del primer borrador quedaron reemplazadas por sus versiones de cierre, desarrolladas en la Parte 10.
- La Escalabilidad del primer borrador (que incluía el Riesgo R-06 todavía sin resolver) fue reemplazada por su resolución real, ya cerrada en la Parte 3, y por la consolidación final de la Parte 10.
- **Dark Mode y Animaciones no recibieron una fase de desarrollo detallado propia** — se incluyen en las Partes 5 y 8 en su nivel de especificación original, con esa limitación señalada explícitamente donde corresponde.

Ninguna de estas exclusiones elimina información: todo lo retirado fue, por definición, una versión anterior de algo que este documento ya contiene de forma más completa.

---

## Índice general

- [Parte 0 — Introducción y Filosofía Visual](#parte-0--introducción-y-filosofía-visual)
- [Parte 1 — Home](#parte-1--home)
- [Parte 2 — Página de Documento](#parte-2--página-de-documento)
- [Parte 3 — Página de Categoría](#parte-3--página-de-categoría)
- [Parte 4 — Responsive Design](#parte-4--responsive-design)
- [Parte 5 — Dark Mode](#parte-5--dark-mode)
- [Parte 6 — Sistema de Navegación e Interacciones](#parte-6--sistema-de-navegación-e-interacciones)
- [Parte 7 — Sistema de Componentes Visuales](#parte-7--sistema-de-componentes-visuales)
- [Parte 8 — Animaciones (Tabla de Referencia)](#parte-8--animaciones-tabla-de-referencia)
- [Parte 9 — Consistencia Visual](#parte-9--consistencia-visual)
- [Parte 10 — Preparación para la Implementación](#parte-10--preparación-para-la-implementación)


---

# Parte 0 — Introducción y Filosofía Visual

## 1. Introducción

### Objetivo

WF-001 definió *qué zonas existen* en cada plantilla (Header, Sidebar, Hero, Cards...) mediante wireframes ASCII de baja fidelidad. DS-001 definió *el vocabulario visual* (tokens de color, tipografía, espaciado, componentes). Ninguno de los dos, por diseño, especifica cómo se combinan ambos en una composición final: cuánto espacio exacto separa el Hero de la primera fila de tarjetas, cuántas columnas tiene la grilla en cada breakpoint, qué tamaño exacto tiene la franja de iconos del Sidebar colapsado. **Ese es el vacío que cierra PV-001.**

Este documento es la referencia oficial que cualquier implementación en React + Vite + Tailwind debe seguir sin margen de interpretación en las decisiones ya tomadas aquí.

### Alcance

Cubre la especificación visual completa de las tres plantillas ya wireframeadas en WF-001 (Home, Página de Documento, Página de Categoría), su comportamiento responsive, modo oscuro, accesibilidad aplicada a nivel visual, microinteracciones y animaciones. **No** reabre ninguna decisión de arquitectura de información, sitemap o flujo de navegación (ARC-001, WF-001 Parte 1) — esas permanecen exactamente como están. **No** introduce tokens nuevos de color, tipografía o espaciado fuera de los ya definidos en DS-001.

### Público objetivo

Principalmente el **Frontend Architect** y cualquier desarrollador que construya PV-002 (la implementación en código, fuera del alcance de este documento). Secundariamente, el **Comité Técnico** y el **Design System Architect**, como referencia de aprobación antes de iniciar desarrollo.

---

## 2. Filosofía Visual

El Handbook no debe *verse* como una herramienta de documentación genérica descargada de una plantilla; debe verse como una extensión natural de un equipo que ya construye software con disciplina (THERS usa React, Vite, Tailwind, Flask, PostgreSQL con convenciones propias — STD-001). El lenguaje visual comunica seis atributos, cada uno con una traducción visual directa:

| Atributo | Cómo se traduce visualmente |
|---|---|
| **Profesionalismo** | Paleta restringida (un primario, un secundario, cuatro semánticos — DS-001 §4), sin gradientes decorativos, sin ilustraciones genéricas de stock. El color se usa para comunicar estado, nunca para decorar. |
| **Minimalismo** | Cada pantalla tiene un solo punto focal por vez (un Hero, un título de documento, una descripción de categoría). El espacio en blanco no es "espacio sin usar": es el mecanismo principal para separar bloques de información, antes que bordes o fondos de color. |
| **Escalabilidad** | Ninguna composición depende del volumen actual de contenido — una grilla de 8 categorías y una de 40 documentos usan la misma lógica de columnas y gutters (sección 12). |
| **Legibilidad** | Columna de lectura limitada a 760px (DS-001 §8.1), interlineado amplio en cuerpo de texto (1.7), contraste verificado en ambos temas (DS-001 §4.3) — el texto es el contenido, no un elemento decorativo alrededor de otra cosa. |
| **Tecnología** | Tipografía monoespaciada (JetBrains Mono) visible y protagonista en bloques de código, no escondida; iconografía de trazo fino y consistente (Lucide, DS-001 §6); densidad de información alta pero ordenada, propia de herramientas developer-first (no de un sitio de marketing). |
| **Consistencia** | Cada plantilla comparte exactamente los mismos componentes (DS-001 §9) con las mismas medidas — lo único que cambia entre Home, Documento y Categoría es qué combinación de zonas se usa, nunca cómo se ve cada zona individual. |

---


---

# Parte 1 — Home

| Campo | Valor |
|---|---|
| Documento | PV-001 — Desarrollo detallado de Home |
| Versión | 1.0 |
| Estado | Borrador para revisión |
| No modifica | Introducción, Objetivos, Alcance, Filosofía Visual (ya aprobados) |
| Reemplaza / expande | La versión compacta de la Sección 3 (Home) del documento PV-001 base |

---

## Notas de diseño previas al desarrollo

Dos elementos solicitados requieren una decisión explícita antes de especificarlos, porque no estaban resueltos —o apuntaban en otra dirección— en los documentos ya aprobados. Se señalan aquí, como en el resto de la serie de documentos oficiales, en vez de resolverse en silencio.

**Perfil de usuario.** ARC-001 define el Handbook como un sitio 100% estático (SSG), sin backend ni sistema de autenticación propio — es intencional, para no depender de que Flask/PostgreSQL estén disponibles (ARC-001 §1). Un "perfil de usuario" tradicional (login, avatar de cuenta) está fuera de ese alcance y requeriría una decisión de arquitectura nueva (un ADR, STD-001 §12), no una decisión de este documento visual. Resolución propuesta para esta especificación: el elemento se implementa como un **Selector de Integrante** — sin autenticación, solo una preferencia local del navegador que identifica cuál de los 4 integrantes del equipo está usando el Handbook en ese dispositivo. Sirve para personalizar atribuciones (ej. "Editar esta página" pre-completa el autor) y sienta la base para la función de favoritos ya anticipada como pendiente en ARC-001 §4 y en las Preguntas Abiertas de WF-001 §15. **Queda marcado como pendiente de ratificación** — si en el futuro el equipo decide que el Handbook sí necesita autenticación real, este elemento deberá rediseñarse.

**Tarjetas principales.** La lista solicitada (Manuales, Arquitectura, Academy, Playbooks, Roadmap) son 5 elementos, no las 8 categorías raíz completas del sitemap (ARC-001: Organización, Estrategia, Arquitectura, Ingeniería, Academy, Playbooks, Roadmap, Meta). Resolución propuesta: estas 5 tarjetas son una **curaduría editorial de accesos principales**, no un reemplazo del sitemap — las 8 categorías completas siguen siendo accesibles en todo momento desde el Sidebar (rail de iconos, sección 2 de este documento), que no cambia. "Manuales" se mapea a la categoría **Organización** (donde viven el Manual de Organización y el Manual Operativo), renombrada aquí a un título más reconocible para un usuario nuevo. Se deja constancia de que Estrategia, Ingeniería y Meta quedan fuera de esta curaduría de 5 — accesibles igual, solo no destacadas en Home — y se recomienda que el equipo revise esta selección específicamente, dado que Ingeniería es, por volumen de documentos esperado, una de las categorías de mayor consulta.

Con ambos puntos señalados, se desarrolla la especificación completa.

---

## 1. Header

**Altura aproximada:** 64px fijos (hereda DS-001 §9.1, sin variación en Home respecto a las demás plantillas).

**Distribución:** tres zonas horizontales dentro de `container-app` (1440px máx.), con `space-6` (24px) de margen respecto a los bordes del contenedor:

- **Zona izquierda:** Logo/wordmark.
- **Zona central:** Buscador.
- **Zona derecha:** Acciones rápidas + separador vertical sutil (1px `color-border`, 20px de alto) + Selector de integrante (Perfil de usuario).

**Logo:** wordmark "THERS" en Inter Bold, altura de caja mínima 20px (DS-001 §3.2). Es el elemento de mayor peso tipográfico del Header — el único en peso 700 — y actúa como ancla de retorno: un click, desde cualquier punto del Handbook, regresa a Home. Tooltip "Ir a inicio" al hover/foco.

**Buscador:** campo de 320px de ancho, 40px de alto, borde 1px `color-border`, radio 6px, con el texto "Buscar en el Handbook..." como placeholder y el atajo `Ctrl/Cmd+K` visible alineado a la derecha dentro del propio campo, en `text-caption`. Es el único elemento del Header con fondo diferenciado (`color-surface` sobre el `color-bg` del resto del Header), lo que lo hace visualmente el segundo elemento más prominente después del logo — intencional, porque buscar es la ruta más rápida hacia contenido (WF-001 §6.2).

**Perfil de usuario (Selector de integrante):** un control compacto de 32px de alto, compuesto por un círculo de iniciales (2 letras, fondo `color-secondary` al 15%, texto `color-secondary`) seguido del nombre corto del integrante en `text-body-sm`, con un ícono `chevron-down` de `icon-xs` a la derecha. Al hacer click, despliega una lista simple de los 4 integrantes (mismo patrón visual que un Dropdown, DS-001 §10). Ver justificación de su naturaleza no autenticada en "Notas de diseño".

**Acciones rápidas:** dos íconos en `icon-md` (20px), sin texto, área interactiva de 40×40px cada uno (excede el mínimo de 24×24px de DS-001 §12 dando además más comodidad de click): toggle de tema (sol/luna) y enlace al repositorio de GitHub. Se mantienen en `color-text-secondary` en reposo — nunca en `color-primary` — para que no compitan visualmente con el Buscador como punto focal de la zona derecha.

**Espaciado:** `space-6` entre cada una de las tres zonas y los bordes del Header; `space-4` entre los dos íconos de Acciones rápidas; `space-2` entre el ícono `chevron-down` y el nombre en el Selector de integrante.

**Jerarquía visual:** Logo (peso 700, ancla) > Buscador (único con fondo propio) > Selector de integrante (texto + color secundario) > Acciones rápidas (solo ícono, color muted). Esta jerarquía no es decorativa: comunica en qué orden el ojo debería registrar los elementos del Header al entrar por primera vez a la página.

**Propósito UX de cada elemento:**

| Elemento | Propósito |
|---|---|
| Logo | Identidad del sistema + retorno instantáneo, predecible en cualquier punto del Handbook (principio de Predictibilidad, WF-001 §4). |
| Buscador | Punto de entrada al plano Utilitario; para un usuario recurrente, suele ser más rápido que cualquier navegación visual. |
| Selector de integrante | Personalización mínima sin fricción de login; sienta la base para favoritos/atribución futura sin comprometer la arquitectura estática del Handbook. |
| Acciones rápidas | Utilidades de bajo uso pero necesarias (cambiar tema, ir al repositorio) — deliberadamente discretas para no distraer del contenido. |

---

## 2. Sidebar

**Organización:** franja vertical fija de 64px de ancho, adosada al borde izquierdo del viewport, fondo `color-surface`, borde derecho 1px `color-border`. Contiene los 8 íconos de categoría en el mismo orden en que aparecen en el sitemap de ARC-001 (Organización, Estrategia, Arquitectura, Ingeniería, Academy, Playbooks, Roadmap, Meta) — el orden nunca se reordena por frecuencia de uso ni personalización, para que su posición sea memorizable con el tiempo (un usuario recurrente termina navegando por posición, no por lectura).

**Categorías:** cada ícono representa una categoría raíz completa (no subcategorías — esas solo aparecen al entrar a la categoría). Mapeo íntegro heredado de DS-001 §8 (Iconografía): Organización → `building-2`, Estrategia → `brain-circuit`, Arquitectura → `layout-template`, Ingeniería → `layout-panel-left`, Academy → `graduation-cap`, Playbooks → `list-checks`, Roadmap → `map`, Meta → `settings`.

**Iconografía:** `icon-lg` (24px), stroke 2px (DS-001 §6.2), color `text-secondary` en reposo. Centrados horizontalmente dentro de la franja de 64px, apilados verticalmente con `space-4` (16px) de separación entre cada ícono, comenzando con `space-6` (24px) de margen superior respecto al borde inferior del Header.

**Estados activos:** en Home, específicamente, **ningún ícono se muestra en estado activo** — el usuario no está "dentro" de ninguna categoría todavía. Esto es una decisión deliberada: no se resalta la "última categoría visitada" al volver a Home, porque generaría una lectura ambigua (¿significa que sigo ahí? ¿es solo un recuerdo?). Home siempre se presenta visualmente neutral en este componente.

**Estados hover:** fondo `color-surface` +4% de opacidad detrás del ícono (radio 8px, como un botón ghost cuadrado de 40×40px centrado sobre el ícono de 24px), el ícono pasa de `text-secondary` a `text-primary`. Tooltip con el nombre completo de la categoría aparece tras 400ms de hover o inmediatamente al recibir foco por teclado (DS-001 §9.19).

**Colapsado:** este es el **único estado que existe en Home** — no hay expansión en línea dentro de esta plantilla. Un click en cualquier ícono navega directo a la Category Index correspondiente; la expansión a árbol completo (con las páginas hijas visibles) ocurre recién en esa página de destino, no en Home.

**Expandido:** no aplica a Home — se documenta aquí solo para dejar constancia de que la ausencia de este estado en esta plantilla es intencional, no un olvido. El estado expandido (árbol completo de contenido) corresponde a las plantillas Documento y Categoría, ya especificadas en la versión base de PV-001.

**Justificación de conjunto:** mantener el Sidebar visible (aunque colapsado) desde Home, en lugar de ocultarlo por completo, preserva el plano Global de navegación (WF-001 §5) accesible en un click desde el primer segundo, sin que compita visualmente con el Hero y las Tarjetas principales como protagonistas de la página — que es, precisamente, el rol que Home debe cumplir (WF-001 §6.1).

---

## 3. Hero

**Mensaje principal:** "THERS Engineering Handbook", en `text-display` (36px/44px, peso 700) — el único uso permitido de este token tipográfico en todo el Handbook (DS-001 §5.2), reservado exclusivamente para este lugar.

**Subtítulo:** una sola línea, en `text-body` (16px), color `text-secondary`, que responde en una frase qué es el Handbook y para quién es (ej. una descripción funcional del propósito, no un eslogan). Nunca se permite que ocupe más de una línea — si el contenido no cabe, se acorta el texto, no se permite que el Hero crezca en altura de forma variable.

**Jerarquía tipográfica:** dos niveles únicamente — título y subtítulo. No hay un tercer nivel tipográfico dentro del Hero (ej. no se agrega una etiqueta o badge adicional); el atajo de búsqueda que puede acompañarlo es un componente funcional (un input), no un elemento tipográfico que compita por jerarquía.

**Espaciado:** `space-2` (8px) entre título y subtítulo; `space-6` (24px) entre el subtítulo y el atajo de búsqueda opcional, si está presente; padding vertical `3XL` (64px) por encima y por debajo del bloque completo del Hero, respecto al Header y a la primera fila de Tarjetas principales respectivamente.

**Distribución:** contenido centrado horizontalmente dentro de `container-wide` (1120px), con alineación de texto centrada — el único bloque de todo Home (y de todo el Handbook) con texto centrado. Esta es una ruptura deliberada del patrón "todo el contenido se alinea a la izquierda" que rige el resto del sistema (DS-001 §9.5, Cards), y funciona precisamente porque es una excepción única: comunica, sin necesidad de texto adicional, que este es el mensaje más importante de la página.

**Por qué existe:** es el primer momento de orientación para un usuario nuevo — responde "¿qué es esto?" antes de que se le pida tomar ninguna decisión de navegación (WF-001 §6.1). Para un usuario recurrente que entra por costumbre, el Hero es lo primero que confirma "estoy en el lugar correcto" antes de ir directo al Buscador o a una tarjeta específica.

---

## 4. Tarjetas principales

*(Manuales · Arquitectura · Academy · Playbooks · Roadmap — ver justificación de esta curaduría de 5 en "Notas de diseño")*

**Tamaño:** cada tarjeta con altura uniforme fija (definida por el contenido más largo del conjunto, convención DS-001 §14), ancho fluido: en desktop, las 5 tarjetas ocupan una sola fila dentro de `container-wide` (1120px), con gutter `space-6` (24px) entre cada una — el ancho resultante de cada tarjeta es de aproximadamente 205px.

**Distribución:** una sola fila de 5 columnas en desktop, deliberadamente distinta de una grilla estándar de 4 o 6 — comunica que las 5 tarjetas tienen exactamente el mismo nivel de jerarquía entre sí, sin sugerir subgrupos. En tablet, pasan a 2–3 por fila con wrap; en mobile, 1 columna (detalle completo de responsive fuera del alcance de este documento).

**Iconografía:** `icon-lg` (24px) alineado arriba a la izquierda de cada tarjeta, mismo mapeo de DS-001 §8 para las 4 categorías que sí corresponden 1:1 (Arquitectura, Academy, Playbooks, Roadmap); la tarjeta "Manuales" usa el ícono de Organización (`building-2`), heredado del mapeo de esa categoría real.

**Jerarquía:** dentro de cada tarjeta, de arriba hacia abajo — ícono → `space-2` → título (`text-h4`, ej. "Manuales") → `space-1` → descripción de una línea (`text-body-sm`, `text-secondary`, ej. "Manual de Organización, Manual Operativo y más"). Alineación de todo el contenido a la izquierda, consistente con el resto de los componentes Card del sistema (DS-001 §9.5) — el Hero es la única excepción centrada, no las tarjetas.

**Hover:** borde de `color-border` a `color-border-strong` + sombra sutil de un solo nivel (DS-001 §9.5), transición en `motion-fast` (120ms, DS-001 §13.1). No hay cambio de color de fondo completo ni desplazamiento/escala del elemento — el hover confirma "esto es clickable", no simula profundidad física adicional.

**Estados:** `default` (borde estándar) → `hover` (descrito arriba) → `focus-visible` (anillo de foco 2px `color-primary`, 2px de separación, además del hover si coincide) → no existe estado `disabled` en este componente, porque las 5 categorías destacadas siempre están disponibles por definición.

---

## 5. Últimas actualizaciones

**Organización:** lista vertical (no grilla), orden estrictamente cronológico descendente (más reciente arriba), ancho igual a `container-wide`. Cada fila: altura mínima 48px, separada de la siguiente por un borde inferior 1px `color-border`, padding vertical `space-2`.

**Distribución de cada fila**, de izquierda a derecha: fecha en `text-caption`/`text-secondary` (ancho fijo ~80px) → título del documento en `text-body` (texto con link, ocupa el espacio disponible) → badge de categoría (DS-001 §9.11) alineado a la derecha.

**Cantidad de entradas:** un número acotado (orientativamente 5 a 8, a definir según densidad editorial real una vez el Handbook tenga historial suficiente) — este bloque es una vista previa, no el registro completo. El Changelog completo ya vive en `/meta/changelog-del-handbook` (ARC-001 §2); duplicar el historial completo aquí violaría el principio de una sola fuente de verdad (ARC-001 §15). Por eso, la última fila del bloque es un enlace "Ver todas las actualizaciones →", en `text-body-sm`, `color-primary`, sin badge ni fecha asociada — visualmente distinto del resto de las filas para que se entienda como una acción, no como una entrada más de la lista.

**Por qué existe:** comunica que el Handbook es un documento vivo y mantenido activamente, no un documento estático que se escribió una vez — está ligado a la cadencia de revisión mensual ya establecida (STD-001 §6) y funciona como incentivo para que un usuario recurrente revisite Home en vez de ir siempre directo a un bookmark interno.

---

## 6. Accesos rápidos

**Propósito distinto de las Tarjetas principales:** mientras las Tarjetas principales (sección 4) son puntos de entrada a categorías completas para un usuario que aún está decidiendo qué necesita, los Accesos rápidos son atajos directos a documentos individuales específicos de alta frecuencia de consulta (ej. "Convención de commits", "Onboarding", "Cómo contribuir") — sin descripción adicional, porque el usuario que los usa ya sabe exactamente qué va a encontrar.

**Visual:** fila horizontal de chips compactos, altura ~32px, radio de esquina completo (píldora), padding horizontal `space-4`, borde 1px `color-border`, fondo `color-bg` (no `color-surface`, para diferenciarse visualmente de las Tarjetas principales y no leerse como una "card pequeña"). Cada chip contiene un ícono `icon-sm` opcional + el nombre corto del documento en `text-body-sm`.

**Importante — no son Badges:** aunque comparten la forma de píldora con el componente Badge de DS-001 §9.11, estos chips son **interactivos** (funcionan como enlaces), mientras que un Badge es puramente un indicador de estado, no clicable. Visualmente se diferencian en el estado hover: el chip de Accesos rápidos cambia su borde y texto a `color-primary` al hover (comportamiento de botón `ghost` pequeño, DS-001 §9.6); un Badge nunca tiene estado hover porque no es interactivo.

**Distribución:** `space-2` (8px) entre cada chip, con salto de línea automático en pantallas angostas — no hay scroll horizontal forzado.

**Curaduría:** al igual que las Tarjetas principales, esta es una selección editorial manual, no generada automáticamente por frecuencia de visitas real (evita que el propio bloque cambie de contenido sin control, lo cual sería confuso para un usuario que vuelve buscando el mismo atajo que usó ayer).

---

## 7. Footer

Contiene únicamente información de utilidad directa para un equipo técnico — sin enlaces sociales, sin boilerplate legal extenso, sin newsletter. Estructura en cuatro bloques horizontales dentro de `container-app`, separados entre sí por `space-8`:

| Bloque | Contenido |
|---|---|
| **Versión** | Número de versión actual del Handbook + enlace directo a "Ver historial de cambios" (`/meta/changelog-del-handbook`). |
| **Contribuir** | Enlace a "Cómo contribuir" + enlace a "Convenciones de documentación" (ambos en `/meta`). |
| **Documentos de referencia** | Enlaces directos a los documentos que gobiernan el propio Handbook: STD-001, ARC-001, DS-001, WF-001 — transparencia deliberada sobre la propia metodología, coherente con la cultura docs-as-code del equipo. |
| **Equipo** | Copyright + nombre del equipo THERS. |

Padding vertical `space-8` (32px), fondo `color-surface`, borde superior 1px `color-border`, todo el texto en `text-caption`/`text-secondary` — visualmente el bloque de menor peso jerárquico de toda la página, como corresponde a información de referencia, no de acción.

---

## 8. Espaciado

Sistema de ritmo vertical, usando exclusivamente los tokens ya definidos en DS-001 §7 — ningún valor nuevo se introduce en esta especificación:

| Transición | Token | Valor |
|---|---|---|
| Header → Hero | (Hero define su propio padding superior) | `3XL` = 64px |
| Hero → Tarjetas principales | `3XL` (padding inferior del Hero) | 64px |
| Tarjetas principales → Accesos rápidos | Divisor + `XL` | 32px |
| Accesos rápidos → Últimas actualizaciones | Divisor + `XL` | 32px |
| Últimas actualizaciones → Footer | `2XL` | 48px (mayor que las anteriores: marca la transición de "contenido de la página" a "chrome de cierre") |
| Interno del Footer (padding) | `XL` | 32px |

**Regla de consistencia:** cada divisor horizontal (`color-border`, 1px) entre bloques de contenido va acompañado siempre del mismo token de espaciado (`XL`, 32px) en ambos lados — el divisor nunca se usa sin ese espaciado, ni el espaciado sin divisor, para que la señal visual de "sección nueva" sea siempre doble (línea + aire), nunca una sola.

---

## 9. Jerarquía visual

Cómo un usuario distingue, sin tener que leer instrucciones, las cuatro categorías de información en Home:

| Categoría | Cómo se identifica |
|---|---|
| **Qué es importante** | Tipografía de mayor tamaño (`text-display`, único en toda la página) + alineación centrada (única excepción al patrón de alineación izquierda) — ambas señales coinciden solo en el Hero, por eso no hay ambigüedad sobre cuál es el mensaje principal. |
| **Qué es secundario** | Color `text-secondary` + tamaños `text-body-sm`/`text-caption` — se aplica de forma idéntica a taglines, descripciones de tarjetas, metadatos de "Últimas actualizaciones" y todo el Footer. Es secundario por *tratamiento*, no por posición: puede estar arriba de la página (subtítulo del Hero) y seguir leyéndose como secundario. |
| **Qué es navegación** | Se concentra estructuralmente en los bordes de la pantalla (Header arriba, Sidebar a la izquierda) y usa un tratamiento visual deliberadamente discreto — íconos sin relleno, color `text-secondary` en reposo. La navegación está siempre presente pero nunca compite en peso visual con el contenido central. |
| **Qué es contenido** | Todo lo que vive dentro de `container-wide`/`container-app`, con el patrón de alineación izquierda + Cards como unidad repetible. El uso de `color-primary` se reserva casi exclusivamente para estados activos/interactivos dentro de esta zona (nunca como color decorativo), lo que hace que cualquier aparición de `color-primary` funcione como una señal fiable de "esto es interactivo" en cualquier parte de la página. |

---

## 10. Validación UX

| Documento | Cumplimiento |
|---|---|
| **STD-001** | La curaduría editorial de Tarjetas principales y Accesos rápidos, y la personalización mínima del Selector de integrante, son responsabilidad de mantenimiento humano explícito — consistente con el estándar de ownership y revisión mensual ya definido. |
| **DS-001** | Todos los colores, tipografías, espaciados e íconos usados provienen del catálogo ya aprobado (§4, §5, §6, §7, §9); no se introduce ningún token nuevo. El único componente sin precedente exacto en el catálogo (Selector de integrante) se especifica reutilizando el patrón visual de Dropdown ya existente (DS-001 §10), y queda señalado como pendiente de incorporación formal al catálogo. |
| **WF-001** | Respeta íntegramente los cinco planos de navegación (el Sidebar sigue siendo el plano Global, el Buscador el plano Utilitario) y el rol de Home definido en la Parte 1 (§6.1): punto de entrada orientador, no un árbol de navegación completo. |
| **ARC-001** | El sitemap de 8 categorías permanece intacto y completamente accesible vía Sidebar; la curaduría de 5 Tarjetas principales no reemplaza ni oculta ninguna categoría, solo prioriza visualmente un subconjunto en Home — decisión que, como se señaló al inicio, se recomienda revisar explícitamente con el equipo antes de considerarse definitiva. |

**Conclusión:** la especificación de Home es consistente con los cuatro documentos base, con dos puntos explícitamente marcados como pendientes de ratificación (Selector de integrante, curaduría de 5 Tarjetas principales) que se recomienda resolver formalmente antes de avanzar a la implementación.


---

# Parte 2 — Página de Documento

| Campo | Valor |
|---|---|
| Documento | PV-001 — Desarrollo detallado de Página de Documento |
| Versión | 1.0 |
| Estado | Borrador para revisión |
| No modifica | Introducción, Objetivos, Alcance, Filosofía Visual, Especificación Visual de la Home (ya aprobados) |
| Alcance de esta plantilla | Es la plantilla universal de contenido — todo documento oficial del proyecto (HB-001, ARC-001, DS-001, WF-001, PV-001 mismo, futuros ADR, documentos de Academy, Playbooks) se renderiza sobre esta misma especificación, sin variantes por tipo de documento. |

---

## Notas de diseño previas al desarrollo

Tres puntos requieren una decisión explícita de reconciliación antes de especificar el detalle. Se señalan aquí, siguiendo la misma disciplina del resto de la serie.

**"Navegación" dentro del Header.** No hay, hasta ahora, un elemento de Header llamado así. Se interpreta como el control que faltaba en la especificación base: un ícono de **toggle de Sidebar** (tipo panel/hamburguesa), ubicado junto al Logo, que colapsa/expande el árbol completo del Sidebar de contenido sin salir de la página — la acción de colapsado a franja de iconos que DS-001 §10 ya preveía como posible en desktop, pero que no tenía un lugar visual asignado hasta ahora. Se define aquí, en la sección 1.

**Campos nuevos en el Encabezado del Documento.** ARC-001 §14 define el frontmatter mínimo obligatorio (`title`, `category`, `order`, `status`, `owner`, `last_updated`, `tags`). Esta tarea solicita además **Código del documento**, **Versión** y **Revisores** (plural), que no estaban en ese frontmatter. Se incorporan aquí como una extensión natural — el propio conjunto de documentos oficiales del proyecto (STD-001, ARC-001, DS-001, WF-001, PV-001) ya usa códigos y versiones, así que formalizarlo en la plantilla es consistente con una práctica que el equipo ya sigue. **Se recomienda incorporar estos tres campos formalmente a ARC-001 §14** en su próxima revisión.

**Formato del Breadcrumb.** El ejemplo de la tarea (`Inicio / Handbook / Manuales / HB-001`) usa separador `/`, un nivel adicional ("Handbook") y el código del documento como último segmento. Se mantiene la convención ya aprobada en DS-001 §9.4: separador `›`, sin nivel "Handbook" (Home ya es la raíz, no necesita un segundo nombre para el propio sistema), y el **título legible** del documento como último segmento en vez del código — el código ya es visible en el Encabezado del Documento (sección 4). Ejemplo real bajo esta plantilla: `Inicio › Organización › HB-001 — Manual de Organización`.

Con los tres puntos señalados, se desarrolla la especificación completa.

---

## 1. Header

**Distribución:** cuatro zonas horizontales (una más que en Home), dentro de `container-app` (1440px): **Toggle de Sidebar** + **Logo** (agrupados a la izquierda, `space-2` entre ambos) → **Buscador** (centro) → **Selector de integrante** + **Acciones rápidas** (derecha) — mismos componentes ya definidos en la especificación de Home, sin variación.

**Logo:** idéntico a Home (wordmark Inter Bold, 20px de altura mínima, retorno a Home). En esta plantilla convive con el Toggle de Sidebar inmediatamente a su izquierda, ambos alineados verticalmente al centro del Header de 64px.

**Buscador:** idéntico a Home en tamaño y comportamiento (320px, 40px alto). Su posición centrada no cambia entre plantillas — es una de las señales de Predictibilidad (WF-001 §4) más importantes del sistema: el usuario nunca tiene que reubicar el buscador al cambiar de tipo de página.

**Navegación (Toggle de Sidebar):** ícono `panel-left` (`icon-md`, 20px), área interactiva 40×40px, ubicado inmediatamente a la izquierda del Logo. Colapsa el Sidebar expandido (sección 2) a una franja de solo iconos —mismo patrón visual que el Sidebar de Home— y lo vuelve a expandir al segundo click. Estado del toggle persistente durante la sesión de navegación (si el usuario lo colapsa, se mantiene colapsado al navegar a otro documento, hasta que lo vuelva a expandir).

**Perfil del usuario (Selector de integrante):** idéntico al definido en la especificación de Home — mismo componente, misma posición relativa, sin reinterpretación.

**Acciones rápidas:** idénticas a Home (toggle de tema + enlace a GitHub).

**Jerarquía visual:** Logo (ancla, peso 700) > Buscador (único con fondo propio) > Toggle de Sidebar (ícono, funcional pero de bajo peso) = Selector de integrante = Acciones rápidas (mismo nivel, todos en `text-secondary`). El Toggle es el único elemento nuevo respecto a Home, y deliberadamente no compite en peso visual con el Logo pese a estar junto a él — es una utilidad, no una segunda ancla de identidad.

**Propósito UX:** en Home, el Sidebar ya está colapsado por defecto y no hace falta un control para cambiarlo. En una Página de Documento, el Sidebar expandido (260px) ocupa espacio de pantalla real — darle al usuario control directo para recuperar ese espacio durante una sesión de lectura larga (sin tener que salir del documento) es la razón de ser de este control.

---

## 2. Sidebar

**Organización por categorías:** árbol de tres niveles como máximo — Categoría → Subcategoría (cuando exista, ej. Ingeniería) → Documento. No se permite un cuarto nivel de anidación bajo ninguna circunstancia; si un documento necesitara un nivel adicional, la respuesta correcta es dividirlo en más documentos, no anidar más el árbol (regla nueva, ver justificación en Escalabilidad, sección 2 más abajo y sección 12).

**Estados activos:** el documento actual se muestra con fondo `color-primary` al 8%, texto en `color-primary`, barra de acento izquierda de 2px (heredado sin cambios de DS-001 §9.2). La rama completa que contiene al documento activo (categoría y, si aplica, subcategoría) se muestra expandida por defecto; el resto del árbol permanece colapsado.

**Estados hover:** fondo `color-surface` +4% de opacidad sobre el ítem completo (no solo el texto), radio 6px, sin cambio de color de texto en items no activos — el hover comunica "esto es clickable", no "esto está seleccionado" (esa señal se reserva exclusivamente al estado activo).

**Secciones expandibles:** cada categoría y subcategoría con hijos lleva un ícono `chevron-right` (`icon-sm`) a la izquierda de su nombre, que rota 90° al expandir (`motion-base`, 200ms, DS-001 §13.1). Click en cualquier parte de la fila (no solo el chevron) expande/colapsa — evita que el usuario tenga que apuntar a un ícono pequeño para una acción tan frecuente.

**Indicadores visuales:** un punto de 6px de diámetro alineado al borde derecho del ítem, visible únicamente para documentos en estado `Draft` (color `warning`) o `Deprecado` (color `danger`) — los documentos `Estable` no llevan indicador, para no saturar el árbol con una señal que sería la mayoría de los casos. Este indicador es intencionalmente más pequeño y discreto que el Badge completo (DS-001 §9.11) que sí aparece en el Encabezado del Documento (sección 4): en el Sidebar, el espacio es limitado y la señal solo necesita decir "atención" sin explicar por qué — el detalle completo se resuelve al entrar al documento.

**Escalabilidad cuando existan muchos documentos:**

- El árbol tiene scroll vertical propio, independiente del contenido (ya establecido en DS-001 §9.2); al cargar una página, el Sidebar hace auto-scroll para que el ítem activo quede visible sin que el usuario tenga que buscarlo manualmente — crítico una vez que el árbol supera la altura del viewport.
- El límite de tres niveles (Categoría → Subcategoría → Documento) es la regla estructural que evita que el árbol crezca en profundidad de forma descontrolada; crece en *cantidad* de documentos dentro de cada subcategoría, no en niveles de anidación — un problema de longitud de lista, no de complejidad de árbol, que ya está mitigado por el punto anterior (scroll + auto-scroll).
- Si una subcategoría individual creciera lo suficiente como para que desplazarse dentro de ella sea incómodo (criterio cualitativo, a evaluar por el equipo caso por caso, no un número fijo), la categoría correspondiente debería dividirse en más subcategorías — es una decisión de arquitectura de información (ARC-001), no algo que este documento visual pueda resolver unilateralmente.

**Justificación de conjunto:** el árbol expandido es, junto con el Breadcrumb, el mecanismo principal del plano Local (WF-001 §5) en esta plantilla — el usuario necesita ver, de un vistazo, tanto dónde está como qué más hay alrededor de ese punto, sin tener que salir del documento actual.

---

## 3. Breadcrumb

**Ubicación:** inmediatamente debajo del Header, dentro de `container-content` (760px), con `space-6` de margen superior y `space-4` de margen inferior antes del Título del documento.

**Formato:** `Inicio › [Categoría] › [Subcategoría, si aplica] › [Título del documento]`, separador `›` en `color-text-secondary`, tipografía `text-body-sm`. Ejemplo real: `Inicio › Organización › HB-001 — Manual de Organización`. Ver nota de reconciliación sobre por qué se usa el título completo y no solo el código.

**Jerarquía:** todos los niveles intermedios son enlaces en `color-text-secondary` que pasan a `color-primary` en hover; el último nivel (documento actual) se muestra en `color-text-primary`, sin subrayado, no interactivo — es información, no una acción.

**Beneficio para la navegación:** es el único componente que responde "¿dónde estoy dentro de la jerarquía completa?" en una sola línea, sin depender de que el Sidebar esté visible (relevante si el usuario lo colapsó con el Toggle de la sección 1) — funciona como una red de seguridad de orientación independiente del resto de la interfaz.

---

## 4. Encabezado del Documento

Bloque inmediatamente debajo del Breadcrumb, organizado en tres filas dentro de `container-content`, con `space-6` de margen inferior antes de que comience el Contenido principal — el separador visual más marcado de toda la página (mismo criterio ya establecido en la versión base de PV-001 §4.5).

**Fila 1 — Identidad:** código del documento en `text-caption`, tipografía **JetBrains Mono** (no Inter — es el único metadato de la página que usa la fuente monoespaciada fuera de un bloque de código, para que se lea inequívocamente como un identificador técnico), color `text-secondary`, con `space-1` de margen inferior antes del título. Debajo, el Título en `text-h1` (heredado sin cambios de la especificación base).

**Fila 2 — Estado y versión:** inmediatamente debajo del título, con `space-2` de margen. Badge de estado (DS-001 §9.11) alineado a la izquierda, seguido por "v[número]" en `text-caption`/`text-secondary`, separados por `space-4`.

**Fila 3 — Autoría y fechas:** con `space-1` de margen respecto a la Fila 2. Todo en `text-caption`/`text-secondary`, separado por el carácter `·`: `Autor: [nombre]` · `Revisores: [nombre, nombre]` · `Creado: [fecha]` · `Última actualización: [fecha]`. En documentos con más de dos revisores, se muestran los dos primeros seguidos de "+N" en vez de listar todos — mantiene la fila en una sola línea incluso en documentos con revisión extensa.

**Etiquetas:** fila final del bloque, con `space-2` de margen respecto a la Fila 3, usando el mismo componente chip de Etiquetas ya definido para la Página de Categoría (tamaño ~24px de alto, sin borde, fondo `color-surface`).

**Organización visual general:** de mayor a menor peso, de arriba hacia abajo — Título (mayor tamaño) → Estado/Versión (color, pero sin tamaño dominante) → Autoría/fechas (más pequeño y más gris) → Etiquetas (más pequeño aún, pero con más color por la variedad de chips). El código del documento, pese a ir primero en el orden de lectura, es visualmente el elemento *más* discreto de todo el bloque — es un identificador para referencia y trazabilidad (Decision Log, Matriz de Trazabilidad), no información que un lector nuevo necesite priorizar.

---

## 5. Tabla de Contenidos

**Posición:** riel fijo de 220px (heredado de DS-001 §8.1), alineado al borde derecho de `container-app`, comienza a la misma altura que el Encabezado del Documento (sección 4), no del Breadcrumb.

**Comportamiento:** `position: sticky` respecto al scroll vertical de la página — permanece visible mientras el usuario lee, deteniéndose antes de superponerse al Footer condensado al llegar al final del documento.

**Navegación:** click en cualquier ítem hace scroll suave hasta el heading correspondiente dentro del Contenido principal; no recarga la página ni cambia de URL visible más allá de un ancla.

**Seguimiento de la sección activa:** scroll-spy — el ítem correspondiente a la sección visible en el viewport se muestra en `color-primary` con barra de acento izquierda de 2px, mismo lenguaje visual que el ítem activo del Sidebar (sección 2), reforzando que ambos responden "dónde estoy" en distinta escala (documento vs. Handbook completo).

**Comportamiento en documentos extensos** (caso de estudio: HB-001, con más de 20 secciones de nivel H2 y varias subsecciones H3): para evitar que el riel de 220px se convierta en una lista tan larga como el propio documento, **solo se muestran expandidos los H3 de la sección H2 actualmente activa**; el resto de las secciones H2 muestran sus H3 colapsados aunque el documento entero esté indexado. Esto es una extensión del principio de Divulgación progresiva (WF-001 §4) aplicada específicamente al TOC, no definida hasta ahora en DS-001 §13 — **se recomienda incorporar esta regla formalmente en la próxima revisión de ese documento**. El propio riel del TOC tiene scroll vertical interno independiente si, aun con H3 colapsados, la lista de H2 no cabe en la altura del viewport.

---

## 6. Contenido Principal

Ancho limitado a `container-content` (760px), heredado sin cambios de la especificación base.

| Elemento | Especificación |
|---|---|
| **Títulos (H2/H3/H4)** | Escala ya definida en DS-001 §5.2; `space-8` antes de cada H2 nuevo, `space-6` antes de cada H3, `space-4` antes de cada H4 — la jerarquía de espaciado refuerza la jerarquía tipográfica, nunca al revés. |
| **Subtítulos** | No existe un token tipográfico de "subtítulo" independiente — cualquier texto que acompañe a un título como aclaración usa `text-body-sm`/`text-secondary` inmediatamente debajo, con `space-1` de margen. |
| **Párrafos** | `text-body` (16px/27px), `space-4` entre párrafos consecutivos dentro de una misma sección. |
| **Listas** | Heredadas sin cambios de DS-001 §9.16 (viñetas, numeradas, listas de tareas). |
| **Tablas** | Heredadas sin cambios de DS-001 §9.7 y de la especificación base (§4.11): ancho de `container-content`, o scroll horizontal propio si excede ese ancho. |
| **Diagramas** | Se tratan como el componente `Figure`: imagen centrada dentro de `container-content` (o `container-wide` si el diagrama lo requiere, excepción explícita al ancho de lectura), con un caption en `text-caption`/`text-secondary` centrado debajo, numerado ("Figura N"), `space-2` entre imagen y caption, `space-6` de margen vertical respecto al texto circundante. |
| **Citas (blockquote)** | Componente nuevo, no catalogado hasta ahora en DS-001 §9 — se define aquí como un bloque con borde izquierdo de 2px en `color-border-strong` (no un color semántico: una cita no es una alerta), texto en `text-body` cursiva, color `text-primary`, sin fondo diferenciado, con una línea de atribución opcional debajo en `text-caption`/`text-secondary` precedida por un guion. **Se recomienda incorporar este componente formalmente al catálogo de DS-001 §9.** |

**Cómo mantener excelente legibilidad:** la columna de 760px, el interlineado de 1.7 en `text-body`, y el uso de `space-4`/`space-8` como único vocabulario de separación (nunca un valor intermedio "porque se ve mejor" en un caso puntual) son, en conjunto, la estrategia de legibilidad completa de esta plantilla — no depende de ningún truco adicional por página.

---

## 7. Componentes Especiales

Se reutilizan, sin ampliar la paleta semántica de colores, los componentes ya definidos en DS-001 §9.10 (Alerta) y §9.15 (Callout) — cuatro variantes semánticas más una variante neutral nueva, justificada abajo.

| Tipo | Color/Ícono | Cuándo usarlo |
|---|---|---|
| **Info / Nota / Nota técnica** | `color-info`, ícono `info` | Aclaraciones que no son obligatorias de leer para entender el flujo principal, pero aportan contexto — incluyendo detalles técnicos de implementación que solo interesan a quien va a tocar ese código. |
| **Success / Tip / Buena práctica** | `color-success`, ícono `lightbulb` | Recomendaciones positivas, atajos, o formas preferidas de hacer algo frente a alternativas menos óptimas. |
| **Warning / Advertencia** | `color-warning`, ícono `alert-triangle` | Algo que puede salir mal si se ignora, pero no es destructivo — ej. una configuración fácil de olvidar. |
| **Danger / Peligro** | `color-danger`, ícono `alert-octagon` | Consecuencias serias o irreversibles si se ignora — ej. una acción que borra datos. |
| **Ejemplo** *(nueva variante, neutral)* | `color-border-strong` (sin color semántico), ícono `terminal` | Contenido de muestra (un caso de uso, un fragmento ilustrativo) que no es ni una alerta ni una recomendación — es material de referencia. Se separa de las cuatro variantes semánticas porque forzar un ejemplo dentro de "Nota" diluiría el significado de "Nota" como aclaración real. **Se recomienda ratificar esta quinta variante en DS-001 §9.15.** |

**Alertas (banner de página completa) vs. Callouts (inline):** distinción ya fijada en la especificación base (§4.8, §4.9) y sin cambios aquí. Una aclaración adicional: no existe una variante "Success" de Alerta de página completa — un estado de éxito es, por naturaleza, momentáneo (ya cubierto como microinteracción en la especificación base §9), no un estado persistente que amerite un banner fijo en el contenido.

---

## 8. Bloques de Código

Especificación completa para documentos técnicos futuros (Backend, PostgreSQL, Docker, Git), aunque HB-001 no los use hoy.

**Encabezado del bloque:** franja de 40px de alto sobre el cuerpo del código, fondo ligeramente distinto al cuerpo (`color-surface` sobre `color-code-bg`), radio de esquina superior 8px (compartiendo el radio con el cuerpo como una sola unidad visual, ya definido en la especificación base §4.10).

**Nombre del archivo:** alineado a la izquierda dentro del encabezado, `text-caption`, tipografía JetBrains Mono (coherente con el propio bloque de código).

**Lenguaje:** cuando no hay nombre de archivo específico (ej. un fragmento sin archivo real), se muestra el nombre del lenguaje en el mismo lugar y estilo ("bash", "sql", "python") — nunca se dejan ambos vacíos; un bloque de código siempre se identifica.

**Botón de copiar:** alineado a la derecha del encabezado, ícono `icon-sm` + sin texto en desktop (con tooltip "Copiar"), cambia a un ícono de check en `color-success` por 2 segundos tras copiar (heredado de DS-001 §9.14).

**Numeración opcional:** línea de números a la izquierda del cuerpo, en `text-code`, color `text-secondary`, separada del código por un borde vertical 1px `color-border` — activada automáticamente solo cuando el bloque supera 6 líneas (regla ya fijada en DS-001 §9.14, sin cambios).

**Espaciado:** padding `space-4` en las cuatro direcciones dentro del cuerpo del bloque; `space-6` de margen vertical respecto al párrafo anterior y siguiente del contenido — mismo tratamiento que un Callout (sección 6), para que cualquier bloque "especial" dentro del flujo de lectura se perciba con la misma pausa visual.

**Legibilidad:** tipografía `text-code` (14px/21px) en JetBrains Mono; líneas largas de código **no se envuelven** (`no-wrap`) — el bloque tiene su propio scroll horizontal, para no romper la indentación real del código, que es información en sí misma en la mayoría de los lenguajes.

---

## 9. Navegación entre Documentos

**Documento anterior / siguiente:** heredado sin cambios de la especificación base (§4.12) — fila horizontal al final del contenido, "‹ Anterior" (botón `ghost`) a la izquierda, "Siguiente ›" (botón `secondary`) a la derecha, visible únicamente en categorías con orden editorial definido (WF-001 §6.5).

**Documentos relacionados:** bloque nuevo, ubicado antes de la fila Anterior/Siguiente, con `space-8` de separación respecto al final del contenido y `space-6` respecto al propio Anterior/Siguiente. Título "Documentos relacionados" en `text-h4`, seguido de una lista de 2 a 4 ítems que reutiliza exactamente el mismo patrón visual de fila que "Últimas actualizaciones" en Home (ícono de categoría + título del documento enlazado + badge de categoría, alineados en una fila de 48px de alto) — reutilización deliberada: el usuario ya aprendió a leer ese patrón en Home, así que no tiene que aprender uno nuevo aquí.

**Cómo facilitar la continuidad de lectura:** los tres mecanismos (Anterior/Siguiente, Documentos relacionados, TOC con scroll-spy) cubren tres necesidades distintas y no se solapan — Anterior/Siguiente es para quien sigue un recorrido curado, Documentos relacionados es para quien quiere profundizar lateralmente en un tema mencionado, y el TOC es para quien todavía está dentro del documento actual. Ningún usuario tiene que preguntarse cuál de los tres usar, porque cada uno resuelve una pregunta distinta (mismo principio de planos de navegación sin superposición ya establecido en WF-001 §5).

---

## 10. Footer

Variante condensada de una sola línea, heredada de la especificación base (§4.13), con un tercer elemento agregado específico para documentos técnicos: altura ~48px, contenido centrado dentro de `container-content`, tres bloques separados por `space-6`: **"Editar esta página en GitHub"** (izquierda) · **"Reportar un problema"** (centro, abre un Issue prellenado con el código del documento) · **versión del Handbook** (derecha). Tipografía `text-caption`, color `text-secondary`, sin fondo diferenciado del `color-bg` de la página — mismo criterio de discreción ya establecido en la base.

**Por qué "Reportar un problema" y no otra utilidad:** es información accionable específica del contexto de documentación técnica (encontrar un error, un enlace roto, una imprecisión) — no un enlace genérico de contacto, que no aportaría valor puntual a alguien leyendo un documento técnico específico.

---

## 11. Jerarquía Visual

| Categoría | Cómo se identifica en esta plantilla |
|---|---|
| **Información crítica** | Badge de estado (color + posición fija en la Fila 2 del Encabezado del Documento) y Alertas de página completa (banner con borde de color, ubicación fija justo debajo del Encabezado) — ambos usan color semántico de forma exclusiva para esto, reforzando que "si hay color de alerta, hay algo que atender". |
| **Contenido principal** | Todo dentro de `container-content`, en `color-text-primary`, sin ningún tratamiento decorativo adicional — es, deliberadamente, la parte más "silenciosa" visualmente de la página, porque es donde se concentra el 90% del tiempo de lectura. |
| **Navegación** | Se concentra en los bordes (Header arriba, Sidebar izquierda, TOC derecha), todos en tonos `text-secondary` en reposo — exactamente el mismo tratamiento ya establecido para Home, sin variación entre plantillas. |
| **Documentación relacionada** | Vive al final del flujo de contenido, nunca intercalada entre secciones del documento actual — su posición fija comunica "esto es lo próximo a leer", no "esto es parte de lo que estás leyendo ahora". |

---

## 12. Escalabilidad

Esta plantilla soporta cientos de documentos sin perder consistencia porque **ninguna de sus zonas depende de contenido hardcodeado por página**:

- Breadcrumb, Encabezado del Documento y TOC se generan íntegramente desde el frontmatter y la estructura de headings del documento (ARC-001 §14) — un documento nuevo no requiere que nadie diseñe su cabecera o su tabla de contenidos, solo que complete los campos ya definidos (más los tres nuevos de esta especificación, sección "Notas de diseño").
- El límite de tres niveles del Sidebar (sección 2) es una restricción estructural, no una recomendación — evita que la arquitectura de información se vuelva más compleja de navegar a medida que crece el volumen de documentos, en vez de solo más larga.
- Los componentes de Contenido principal y Componentes especiales (secciones 6 y 7) son agnósticos al tema del documento: un documento de PostgreSQL con 15 bloques de código usa exactamente los mismos componentes, en las mismas medidas, que HB-001 con cero bloques de código — no existe una "versión técnica" distinta de la plantilla.
- El TOC con colapso progresivo de H3 (sección 5) es, específicamente, la respuesta a qué pasa cuando un documento individual crece mucho en extensión — sin esa regla, esta plantilla no habría soportado bien un caso como HB-001 con más de 20 secciones.

---

## 13. Validación

| Documento | Cumplimiento |
|---|---|
| **STD-001** | Los campos nuevos del Encabezado del Documento (código, versión, revisores) formalizan una práctica de identificación y trazabilidad que el propio conjunto de documentos oficiales del proyecto ya sigue — es coherencia con el estándar, no una desviación de él. |
| **ARC-001** | El frontmatter mínimo (§14) se respeta íntegramente y se propone extender, no reemplazar. El límite de tres niveles del Sidebar formaliza, sin contradecirla, la arquitectura de categorías/subcategorías/documentos ya definida en el sitemap. |
| **DS-001** | Se reutilizan los componentes ya catalogados (Badge, Callout, Alert, CodeBlock, Table, List, Tooltip, Dropdown) sin alterar sus tokens. Dos adiciones quedan explícitamente señaladas como pendientes de ratificación: el componente `Quote`/Cita (sección 6) y la quinta variante neutral "Ejemplo" del Callout (sección 7) — ninguna de las dos se declara aprobada por aparecer en este documento. |
| **WF-001** | Las cinco zonas ya wireframeadas para esta plantilla (Header, Sidebar, Breadcrumbs, Contenido, TOC, Prev/Next, Footer) están presentes y desarrolladas en detalle; se agregan dos zonas no wireframeadas explícitamente pero coherentes con los planos de navegación ya definidos (Toggle de Sidebar como extensión del plano Global, Documentos relacionados como formalización visual de la "navegación cruzada" ya descrita en WF-001 §6.5). |


---

# Parte 3 — Página de Categoría

| Campo | Valor |
|---|---|
| Documento | PV-001 — Desarrollo detallado de Página de Categoría |
| Versión | 1.0 |
| Estado | Borrador para revisión |
| No modifica | Introducción, Objetivos, Alcance, Filosofía Visual, Home, Página de Documento (ya aprobados) |
| Alcance de esta plantilla | Se aplica por igual a categorías raíz (Organización/"Manuales", Estrategia, Arquitectura, Ingeniería, Academy, Playbooks, Roadmap, Meta) y a subcategorías con documentos propios (Frontend, Backend, PostgreSQL, Docker, Git, dentro de Ingeniería) — es la misma composición visual en ambos niveles; lo único que cambia es la profundidad del Breadcrumb heredado de la Página de Documento (§3). |

---

## Notas de diseño previas al desarrollo

Tres puntos requieren decisión explícita antes de especificar el detalle.

**Nuevo campo de frontmatter: `type`.** El Sistema de Filtros solicitado pide filtrar por "Tipo" de documento (ej. Manual, Guía, Playbook, ADR, Referencia). Ese campo no existe en el frontmatter ya definido (ARC-001 §14, ampliado con código/versión/revisores en la Página de Documento). Se incorpora aquí como `type`, con un conjunto cerrado de valores (`manual`, `guia`, `referencia`, `playbook`, `adr`) — **se recomienda ratificarlo junto con los campos ya pendientes de la Página de Documento**, en la misma revisión de ARC-001 §14.

**Tiempo estimado de lectura: dato derivado, no campo manual.** A diferencia de los demás metadatos de la tarjeta, este valor **no se escribe a mano** en el frontmatter — se calcula automáticamente en el Build Layer (ARC-001 §1) a partir del conteo de palabras del documento, en el mismo paso donde ya se genera el índice de búsqueda. Se señala explícitamente para que quede claro que no es una carga adicional de mantenimiento para quien escribe el documento.

**Filtro multi-faceta: componente nuevo.** DS-001 §9 solo definía un patrón simple de chips de filtro de una sola dimensión (usado en la especificación base para "Frontend/Backend/PostgreSQL"). Filtrar simultáneamente por Estado, Tipo, Fecha, Autor y Versión requiere un componente más robusto (`FilterBar`, desarrollado en la sección 3), que **se recomienda catalogar formalmente en DS-001 §9** antes de pasar a implementación.

Con los tres puntos señalados, se desarrolla la especificación completa.

---

## 1. Encabezado de Categoría

**Icono representativo:** se reutiliza `icon-lg` (24px, DS-001 §6.2) sin crear un tamaño nuevo, pero se le da mayor peso visual mediante un contenedor propio: un cuadrado de 48×48px, fondo `color-surface`, borde 1px `color-border`, radio 8px, ícono centrado — el mismo tratamiento que ya reciben los íconos dentro de una Card (DS-001 §9.5), aquí escalado como elemento de identidad de página completa en lugar de elemento interno de tarjeta.

**Nombre de la categoría:** `text-h1` (30px/38px, peso 700), alineado verticalmente al centro del contenedor de ícono de 48px, con `space-2` de separación horizontal respecto a él.

**Descripción:** inmediatamente debajo del bloque ícono+nombre, con `space-2` de margen superior, en `text-body`/`text-secondary`, limitada a dos líneas (heredado sin cambios de la especificación base §5.3) — la Página de Categoría indexa, no explica en profundidad.

**Cantidad de documentos y Estado de actualización:** una línea compacta debajo de la descripción, `space-1` de margen, en `text-caption`/`text-secondary`: "N documentos · Actualizado hace N días". Si hubo alguna actualización dentro de una ventana reciente (a definir editorialmente, no un número fijo en esta especificación), se antepone un punto de 6px en `color-primary` — mismo lenguaje visual ya usado como indicador discreto en el Sidebar de la Página de Documento (§2 de ese documento). El detalle numérico completo (documentos oficiales, en revisión, autores) no vive aquí — se desarrolla en la sección 5 (Estadísticas), para no duplicar información en dos lugares de la misma página.

**Etiquetas relacionadas:** tag cloud, heredado sin cambios de la especificación base (§5.5) — chips de 24px de alto, sin borde, fondo `color-surface`, en flujo libre con salto de línea.

**Función UX de cada elemento:**

| Elemento | Función |
|---|---|
| Ícono en contenedor de 48px | Ancla de identidad visual de la categoría — el primer elemento que el ojo registra al entrar, antes incluso de leer el nombre. |
| Nombre | Confirma en qué categoría está el usuario, reforzando el plano Local (WF-001 §5) justo al entrar. |
| Descripción | Da contexto a un usuario que llegó por búsqueda o enlace directo, sin haber pasado por la tarjeta de Home que ya describía brevemente esta categoría. |
| Cantidad de documentos / Estado de actualización | Señal rápida de "¿vale la pena que explore esto ahora mismo?" sin tener que desplazarse hasta la sección de Estadísticas. |
| Etiquetas relacionadas | Ruta de descubrimiento alternativa a la jerarquía de carpetas — permite saltar a un tema específico sin escanear visualmente toda la grilla de tarjetas. |

---

## 2. Buscador Local

**Ubicación:** fila propia inmediatamente debajo del Encabezado de Categoría, con `space-8` de margen superior — separada del Sistema de Filtros (sección 3), que va en la misma fila pero alineado a la derecha en desktop.

**Tamaño:** 40px de alto, ancho fluido con un mínimo de 280px y máximo de 400px (crece dentro de ese rango si hay espacio disponible tras los Filtros, se contrae si no) — deliberadamente más flexible que el Buscador del Header (320px fijo), porque aquí es la herramienta principal de la página, no una utilidad secundaria.

**Comportamiento:** filtra la grilla de Tarjetas de documentos (sección 4) en tiempo real, sin recarga de página ni llamada a un servicio externo — el contenido de la categoría ya está disponible en el cliente (arquitectura SSG, ARC-001 §1), así que la búsqueda local es instantánea. El texto coincidente se resalta en `color-primary` dentro del título o la descripción breve de cada tarjeta que haga match, igual que en el Buscador global (DS-001 §9.12).

**Estados:**

| Estado | Comportamiento visual |
|---|---|
| Vacío (default) | Placeholder "Buscar en [Categoría]...", ícono de lupa (`icon-sm`) a la izquierda. |
| Escribiendo | Aparece un ícono de limpiar (`x`, `icon-xs`) a la derecha del campo. |
| Con resultados | La grilla de Tarjetas se actualiza en vivo, mostrando solo las coincidencias. |
| Sin resultados | La grilla se reemplaza por un Empty State acotado (no el Estado Vacío de categoría completo de la sección 7 — es un estado distinto: "no hay resultados para tu búsqueda", con la sugerencia de limpiar el término o los filtros activos). |

**Beneficios:** cuando el usuario ya sabe en qué categoría está parado (llegó ahí a propósito), una búsqueda acotada evita el ruido de resultados de otras categorías que el Buscador global sí incluiría — es más rápida de escanear y más precisa para esa intención específica.

---

## 3. Sistema de Filtros

Componente `FilterBar`, alineado a la derecha de la misma fila que el Buscador Local en desktop (sección 2), con `space-2` entre cada control.

**Diseño por facetas**, elegido según cuántos valores posibles tiene cada una:

| Faceta | Tipo de control | Justificación del tipo elegido |
|---|---|---|
| **Estado** | 3 chips de toggle en línea (Estable / Draft / Deprecado) | Solo 3 valores fijos — un chip visible es más rápido de usar que abrir un desplegable. |
| **Tipo** | Desplegable de selección múltiple | Conjunto cerrado pero con más de 3 valores (manual, guía, referencia, playbook, ADR) — un desplegable evita saturar la fila con 5 chips adicionales. |
| **Autor** | Desplegable, poblado dinámicamente con los `owner` presentes en esa categoría | La lista de autores varía por categoría y puede crecer — no tiene sentido como chips fijos. |
| **Fecha** | Desplegable con rangos preestablecidos (última semana / mes / trimestre / todo) | Un selector de rango simple es suficiente para el caso de uso real ("qué se tocó recientemente"); un calendario completo sería sobre-ingeniería para esta necesidad. |
| **Versión** | Agrupado dentro de un control secundario "+ más filtros" | Es la faceta de menor uso esperado — mantenerla fuera de la fila principal evita saturarla, consistente con el principio de Minimalismo (Filosofía Visual, ya aprobada). |
| **Etiquetas** | No es un control adicional — se resuelve con el tag cloud ya definido en la sección 1 (Encabezado), cuyos chips ya son clicables como filtro | Evita duplicar la misma función en dos componentes distintos de la misma página. |

**Estado activo:** cualquier control con un valor distinto al default (`Todos`) se muestra con borde y texto en `color-primary`, igual que el estado activo de navegación (mismo lenguaje visual reutilizado, DS-001 §9.2/§9.13). Cuando hay uno o más filtros activos, aparece un enlace "Limpiar filtros" en `text-body-sm`/`color-primary` al final de la fila.

**Justificación de utilidad:** un sistema de filtros faceteado deja de ser opcional en cuanto una categoría crece más allá de una decena de documentos — permite responder preguntas operativas concretas sin abrir cada tarjeta, como "qué está en Draft ahora mismo" o "qué escribió [integrante]", que son exactamente el tipo de pregunta que surge durante la revisión mensual de documentación ya establecida en STD-001 §6.

---

## 4. Tarjetas de Documentos

Grilla de 12 columnas dentro de `container-wide` (heredado sin cambios de la especificación base §5.6): cada tarjeta ocupa 4 columnas → 3 tarjetas por fila en desktop, gutter `space-6`.

**Jerarquía interna de cada tarjeta**, de arriba hacia abajo:

1. **Código + Versión** (misma fila): código en `text-caption`, JetBrains Mono, `color-text-secondary` (mismo tratamiento que en el Encabezado del Documento, PV-001 §4) alineado a la izquierda; versión ("v1.2") en `text-caption` alineada a la derecha de la misma fila.
2. **Título** (`space-1` de margen): `text-h4`, único elemento en peso 600 dentro de la tarjeta — el punto focal.
3. **Descripción breve** (`space-1`): `text-body-sm`/`text-secondary`, limitada a dos líneas con truncado (`...`) si excede ese espacio.
4. **Estado + Tiempo de lectura** (`space-2`, misma fila): Badge de estado (DS-001 §9.11) a la izquierda; tiempo de lectura a la derecha, en `text-caption`/`text-secondary`, con un ícono `clock` (`icon-xs`) — ej. "6 min de lectura".
5. **Etiquetas** (`space-2`): hasta 3 chips de etiqueta visibles, con "+N" si hay más (heredado del patrón ya definido en la especificación base §5.6).
6. **Fecha de actualización** (`space-2`, separada por un borde superior 1px `color-border` a modo de pie de tarjeta): formato relativo ("Actualizado hace 3 días") en vez de fecha absoluta — más rápido de escanear en una grilla con muchas tarjetas a la vez; la fecha absoluta exacta ya vive en el Encabezado del Documento al abrir la tarjeta, donde sí importa precisión (ej. para trazabilidad).

**Indicador de novedad:** si la fecha de actualización cae dentro de una ventana reciente, un punto de 6px en `color-primary` aparece en la esquina superior derecha de la tarjeta completa (fuera del bloque de texto) — reutiliza el mismo lenguaje visual del indicador de novedad ya definido en el Encabezado de Categoría (sección 1) y en el Sidebar (Página de Documento §2), consistente en las tres ubicaciones.

**Comportamiento esperado:** toda la superficie de la tarjeta es clicable (no solo el título), navega directo a la Página de Documento correspondiente. Hover: borde a `color-border-strong` + sombra sutil de un nivel, `motion-fast` (heredado de DS-001 §9.5, sin variación). Altura uniforme forzada por la tarjeta con más contenido del conjunto visible en ese momento (convención DS-001 §14).

---

## 5. Estadísticas de la Categoría

Se organiza como una franja de "tiles" de estadística, no como texto corrido de una sola línea (expande lo ya definido de forma compacta en la especificación base §5.7) — franja horizontal ubicada después de la grilla de Tarjetas, con `space-8` de margen superior, separada por divisores verticales de 1px `color-border` entre cada tile en lugar de bordes de tarjeta individuales, para que se lea como un panel de resumen unificado y no compita visualmente con la grilla de Tarjetas como un segundo grid de "cards".

| Tile | Contenido |
|---|---|
| Total de documentos | Número grande (`text-h3`, peso 600) + etiqueta "documentos" (`text-caption`) debajo |
| Documentos oficiales | Cantidad en estado `Estable` |
| En revisión | Cantidad en estado `Draft` |
| Última actualización | Fecha relativa del documento más reciente de la categoría |
| Autores principales | En vez de un número, una fila compacta de círculos de iniciales (mismo componente que el Selector de integrante del Header, PV-001 Home §1) mostrando hasta 3 autores con más documentos en esa categoría, con "+N" si hay más |

**Por qué es útil:** da un diagnóstico rápido de salud editorial de la categoría sin abrir ningún documento — tanto para un lector que quiere saber si el contenido es confiable, como para el propio equipo durante la revisión mensual (STD-001 §6), donde "cuántos documentos siguen en Draft" es exactamente el tipo de pregunta operativa que este panel responde de un vistazo.

---

## 6. Navegación Relacionada

Bloque final de contenido antes del Footer, con `space-8` de margen superior. Se organiza en tres subsecciones apiladas, cada una con `space-6` de separación respecto a la anterior:

**Categorías relacionadas:** fila de chips (mismo componente que Filtros, sección 3, pero sin estado activo/inactivo — son enlaces puros) hacia 2–3 categorías cuyo contenido suele consultarse junto con la actual (ej. desde Ingeniería, un enlace a Arquitectura). Es una curaduría editorial, no calculada automáticamente.

**Documentos destacados:** lista de 2–3 documentos, con el mismo tratamiento visual que "Manuales destacados" en Home (borde izquierdo de 2px en `color-primary`, señal de curaduría editorial) — documentos que el equipo quiere asegurar que no pasen desapercibidos aunque no encabecen la grilla ordenada cronológicamente.

**Recursos adicionales:** enlaces hacia fuera del Handbook (ej. el repositorio de código del producto THERS, un tablero operativo de Notion) — cada enlace lleva un ícono `external-link` (`icon-xs`) al final del texto, señal visual explícita de que el destino sale del sistema. Esto no contradice el principio de una sola fuente de verdad (ARC-001 §15): son recursos que legítimamente viven fuera del Handbook, no contenido duplicado.

**Cómo mejora la exploración:** evita que la Página de Categoría sea un punto final de recorrido — después de escanear la grilla de Tarjetas, el usuario tiene tres salidas deliberadas hacia adelante (otra categoría, un documento que quizás no habría encontrado solo, o una herramienta externa relevante) en vez de tener que volver al Sidebar o a Home para decidir su siguiente paso.

---

## 7. Estado Vacío

Cuando una categoría (o subcategoría) todavía no contiene documentos:

- El Buscador Local (sección 2) y el Sistema de Filtros (sección 3) **no se muestran** — no hay nada que buscar o filtrar todavía.
- La grilla de Tarjetas (sección 4) se reemplaza por un bloque `EmptyState` centrado, con `2XL` (48px) de padding vertical: ícono neutro (`folder-open`, `icon-lg` dentro del mismo contenedor de 48px ya usado en el Encabezado de Categoría, pero en `color-text-secondary` en vez de `color-primary`) → `space-4` → título `text-h4`: **"Todavía no hay documentos en [Categoría]"** → `space-2` → texto de apoyo `text-body-sm`/`text-secondary`: *"Esta categoría está en preparación. Si tienes contenido que debería vivir aquí, puedes proponerlo siguiendo la guía de contribución."* → `space-4` → botón `secondary` (DS-001 §9.6): **"Cómo contribuir"**, enlazando a la guía ya definida en Meta.
- Las Estadísticas (sección 5) **no se muestran** — no hay datos que resumir.
- La Navegación Relacionada (sección 6) **sí se muestra**, específicamente el bloque de Categorías relacionadas, para que el usuario tenga una salida inmediata hacia contenido que sí existe, en vez de quedar en un punto muerto.
- El Footer (sección 8) no cambia.

---

## 8. Footer

Footer completo, idéntico en estructura y medidas al ya definido para Home (PV-001, especificación de Home, sección 7) — sin variación específica para esta plantilla, por diseño: DS-001 §9.3 ya establece que toda página índice (Home y Category Index, sin distinción entre categoría raíz y subcategoría) usa esta misma variante completa, a diferencia de la Página de Documento, que usa la variante condensada. Los cuatro bloques (Versión, Contribuir, Documentos de referencia, Equipo) se mantienen sin cambios.

---

## 9. Jerarquía Visual

| Pregunta del usuario | Cómo se resuelve visualmente |
|---|---|
| **¿Qué categoría estoy consultando?** | El bloque Ícono + Nombre del Encabezado (sección 1) es el elemento de mayor tamaño y el primero en la página — no hay ambigüedad posible. |
| **¿Qué documentos son más importantes?** | Dos señales convergen: dentro de cada tarjeta, el Título es el único texto en peso 600 (sección 4); a nivel de página, la subsección "Documentos destacados" (sección 6) usa el mismo acento de borde izquierdo en `color-primary` que ya significa "curaduría editorial" en Home — el usuario aprende esa señal una sola vez y la reconoce en cualquier plantilla. |
| **¿Qué contenido es nuevo?** | El punto de 6px en `color-primary`, reutilizado de forma idéntica en tres lugares (Encabezado de categoría, esquina de una tarjeta individual, e ítems de Sidebar en la Página de Documento) — una sola señal visual, tres contextos, ningún significado nuevo que aprender. |
| **¿Qué documentos están en revisión?** | El Badge de estado en color `warning` dentro de cada tarjeta (sección 4) es visible sin necesidad de abrir el documento; el tile "En revisión" de Estadísticas (sección 5) da además el conteo agregado de un vistazo. |

---

## 10. Escalabilidad

Esta plantilla soporta decenas o cientos de documentos por categoría sin perder claridad, y resuelve explícitamente el **Riesgo R-06** que WF-001 §14 había dejado pendiente ("falta de paginación/agrupamiento en categorías grandes"):

- **El mecanismo principal de escalabilidad es arquitectónico, no de interfaz**: cuando una categoría crece lo suficiente como para que su grilla se sienta abrumadora, la respuesta correcta —ya establecida desde ARC-001— es dividirla en subcategorías (como ya ocurre con Ingeniería → Frontend/Backend/PostgreSQL/Docker/Git), no agregar controles de paginación a esta plantilla. Esta plantilla, al aplicarse igual a categorías raíz y subcategorías (ver alcance, encabezado del documento), ya está preparada para ese patrón sin ningún cambio adicional.
- **Para categorías sin agrupamiento natural** (ej. Playbooks, donde los documentos son independientes entre sí y no ameritan subcategorías): el Buscador Local y el Sistema de Filtros (secciones 2–3) reducen activamente el conjunto visible antes de que el usuario tenga que desplazarse por una grilla larga. Como mecanismo adicional, la grilla de Tarjetas revela un lote inicial y agrega un control "Cargar más" al final en vez de paginación numerada tradicional — evita la fricción de "página 3 de 12" en un contexto de exploración, no de lectura secuencial.
- **Rendimiento**: como el Handbook es enteramente estático (ARC-001 §1), el Buscador Local y los Filtros operan sobre los datos de esa categoría ya cargados en el cliente, no sobre una consulta a un servicio — el tiempo de respuesta no se degrada con el tamaño total del Handbook, solo (marginalmente) con el tamaño de la categoría individual, que ya está acotado por el punto anterior.

---

## 11. Validación

| Documento | Cumplimiento |
|---|---|
| **STD-001** | El Sistema de Filtros y el panel de Estadísticas están diseñados para dar soporte directo a la revisión mensual de documentación ya exigida en STD-001 §6 — no son features genéricas, resuelven una necesidad operativa ya documentada. |
| **ARC-001** | Se propone un campo de frontmatter nuevo (`type`) como extensión de §14, en la misma línea que las extensiones ya señaladas en la Página de Documento — pendiente de la misma ratificación conjunta. El principio de una sola fuente de verdad (§15) se respeta explícitamente en "Recursos adicionales" (sección 6), marcados como externos y no duplicados. |
| **DS-001** | Se reutilizan sin alteración los componentes ya catalogados (Card, Badge, Tag, Button, EmptyState, Tooltip). El componente `FilterBar` de faceta múltiple es nuevo y queda señalado como pendiente de catálogo formal (ver Notas de diseño). |
| **WF-001** | Cumple la plantilla Category Index ya wireframeada en la Parte 2 (§10), con las 8 zonas originales desarrolladas en profundidad. Adicionalmente, **cierra el Riesgo R-06** registrado en la Parte 2 (§14, Riesgos de Diseño) — la falta de paginación/agrupamiento ya no es un punto abierto: queda resuelta en la sección 10 de este documento. |


---

# Parte 4 — Responsive Design

| Campo | Valor |
|---|---|
| Documento | PV-001 — Responsive Design |
| Versión | 1.0 |
| Estado | Borrador para revisión |
| No modifica | Introducción, Objetivos, Alcance, Filosofía Visual, Home, Página de Documento, Página de Categoría (ya aprobados) |
| Objetivo | Definir el comportamiento adaptable del Handbook en cualquier dispositivo, traduciendo las tres plantillas ya especificadas en composición fija (desktop) a un sistema de reglas de reorganización por tamaño de viewport. |

---

## Notas de diseño previas al desarrollo

**Cinco nombres de dispositivo, cuatro breakpoints reales.** Esta tarea pide especificar Mobile, Tablet, Laptop, Desktop y Monitores grandes. DS-001 §8.2 ya define exactamente cuatro breakpoints (`bp-mobile`, `bp-tablet`, `bp-desktop`, `bp-wide`) y esta especificación no introduce un quinto. Resolución: **Laptop y Desktop son el mismo breakpoint** (`bp-desktop`, 1024–1439px) — una laptop de 13–15" y un monitor de escritorio estándar caen en el mismo rango de viewport lógico y no requieren layouts distintos; se nombran por separado aquí solo porque son los dos dispositivos físicos más comunes en ese rango, no porque tengan comportamiento diferente. El detalle completo está en la sección 2.

**Dos variantes de componente nuevas.** El Sistema de Filtros de la Página de Categoría necesita un patrón específico para mobile (sección 5) y las Tablas técnicas se benefician de una columna fija al hacer scroll horizontal (sección 8). Ambas son extensiones de componentes ya catalogados en DS-001 §9, no componentes nuevos — se señalan igualmente como pendientes de incorporar al catálogo formal.

Con ambos puntos señalados, se desarrolla la especificación completa.

---

## 1. Filosofía Responsive

Tres principios heredados de documentos ya aprobados, y uno nuevo específico de este documento:

- **Mobile-first en construcción, desktop-first en prioridad de pulido** (principio ya establecido en ARC-001 §9): cada componente se diseña primero para el viewport más restrictivo, pero el estándar de calidad visual más exigente se reserva para desktop, porque es donde el equipo realmente consulta el Handbook durante el trabajo diario.
- **Reflow, no rediseño**: ningún componente cambia su identidad visual (color, tipografía, forma) entre breakpoints — solo cambia su disposición, tamaño relativo y agrupamiento. Un Badge sigue siendo el mismo Badge en mobile que en un monitor grande; lo que cambia es qué lo rodea.
- **Ningún contenido desaparece, solo se reorganiza** (ya establecido en DS-001 §11 y WF-001 §11, reafirmado aquí como principio rector de todo este documento): un elemento puede colapsarse detrás de un ícono, moverse a un Drawer o convertirse en un Accordion, pero nunca deja de estar disponible.
- **La densidad de información se adapta al espacio disponible, no al revés**: en vez de forzar que quepa la misma cantidad de información visible simultáneamente en cualquier tamaño de pantalla (lo que obligaría a miniaturizar todo en mobile), se acepta que un usuario en mobile ve menos por pantalla y navega en más pasos — es preferible a una interfaz técnicamente completa pero ilegible.

---

## 2. Breakpoints Oficiales

| Nombre de uso común | Token (DS-001 §8.2) | Rango | Propósito |
|---|---|---|---|
| **Mobile** | `bp-mobile` | < 640px | Teléfonos. Layout de una sola columna, navegación completamente oculta tras overlays, interacción táctil como caso primario. |
| **Tablet** | `bp-tablet` | 640px – 1023px | Tablets y ventanas de laptop en modo dividido. Espacio suficiente para 2 columnas de contenido, pero todavía insuficiente para sostener Sidebar y TOC simultáneamente sin sacrificar la columna de lectura — la navegación lateral sigue en overlay. |
| **Laptop** | `bp-desktop` | 1024px – 1439px | Laptops de 13–15" y monitores estándar. Es el punto donde se desbloquea el layout completo de 3 columnas (Sidebar + Contenido + TOC) definido en las tres plantillas ya aprobadas. |
| **Desktop** | `bp-desktop` (mismo token que Laptop) | 1024px – 1439px | Mismo comportamiento que Laptop — se nombra por separado solo por asociación de dispositivo físico, no por diferencia de layout. |
| **Monitores grandes** | `bp-wide` | ≥ 1440px | El layout de 3 columnas no gana una cuarta columna ni se expande sin límite: `container-app` sigue capado en 1440px (DS-001 §8.1) y el espacio adicional se convierte en padding lateral — evita líneas de texto excesivamente largas o un Sidebar/TOC flotando con vacío alrededor en monitores ultrawide. |

**Regla de gobernanza:** ningún componente de esta especificación introduce un breakpoint fuera de esta tabla. Si en el futuro se detecta la necesidad de un quinto punto de quiebre real (no solo un nombre de dispositivo nuevo), eso es un cambio a DS-001 §8.2 y sigue el proceso de gobernanza de DS-001 §16 — no se decide de forma aislada en una plantilla individual.

---

## 3. Home Responsive

| Componente | Mobile (< 640px) | Tablet (640–1023px) | Desktop (≥ 1024px) |
|---|---|---|---|
| **Header** | Logo + ícono de búsqueda + ícono de menú (Sidebar Drawer). El campo de texto del Buscador se oculta por completo, no se encoge — al tocar el ícono, se expande a un campo de ancho completo superpuesto sobre el Header. | Buscador reaparece como campo compacto (~200px) sin superposición. Ícono de menú se mantiene (el Sidebar de Home sigue sin espacio propio hasta desktop). | Header completo tal como está especificado: Logo, Buscador de 320px, Selector de integrante, Acciones rápidas — sin cambios. |
| **Sidebar** (rail de iconos colapsado) | Oculto. Se accede vía el ícono de menú del Header, que abre un Drawer de 240px con los 8 íconos de categoría **más su etiqueta de texto visible** (a diferencia de desktop, donde el ícono va solo con tooltip) — en mobile no hay hover para revelar el tooltip, así que el texto debe estar siempre visible. | Igual que mobile. | Franja fija de 64px, tal como está especificada — sin cambios. |
| **Hero** | Título baja de `text-display` (36px) a `text-h1` (30px); padding vertical de `3XL` (64px) se reduce a `XL` (32px); el atajo de búsqueda del Hero, si está presente, ocupa el ancho completo disponible. | Título en `text-h1`; padding `2XL` (48px). | Título en `text-display`; padding `3XL` completo — comportamiento ya definido en la especificación de Home, sin cambios aquí. |
| **Tarjetas principales** (5 tarjetas: Manuales, Arquitectura, Academy, Playbooks, Roadmap) | 1 columna, ancho completo menos padding de página. | 2–3 por fila con salto de línea (`wrap`), sin forzar una distribución exacta — la quinta tarjeta simplemente cae en la siguiente fila. | 1 sola fila de 5 columnas, tal como está especificado. |
| **Buscador** | Cubierto en Header arriba; el atajo de búsqueda del Hero (si existe) se convierte en el campo de búsqueda principal visible de la página en mobile, dado que el del Header está oculto tras un ícono. | Ambos coexisten, tamaños reducidos según contexto. | Sin cambios respecto a la especificación base. |
| **Accesos rápidos** | Los chips se envuelven en múltiples líneas libremente (ya es su comportamiento fluido por defecto, sin ajuste adicional necesario). | Igual que mobile. | Fila horizontal, según especificación base. |
| **Últimas actualizaciones** | Cada fila mantiene su estructura (fecha, título, badge), pero el ancho fijo de ~80px reservado a la fecha se elimina — fecha y título comparten una primera línea, el badge de categoría baja a una segunda línea dentro de la misma fila, para no comprimir el título. | Estructura de fila única, como desktop. | Fila única de tres bloques, según especificación base. |
| **Footer** | Los cuatro bloques (Versión, Contribuir, Documentos de referencia, Equipo) se apilan verticalmente, centrados, separados por `space-4`. | Se apilan igual que mobile si el ancho no alcanza para los 4 bloques en línea, o en dos columnas de 2 bloques cada una si alcanza. | Fila horizontal de cuatro bloques, según especificación base. |

---

## 4. Página de Documento Responsive

| Elemento | Comportamiento adaptable |
|---|---|
| **Breadcrumb** | Se trunca a 2 niveles en mobile (`Inicio › … › [Página actual]`), con el `…` central expandible al tocarlo (ya definido como regla general en DS-001 §9.4). En tablet, se permiten 3 niveles antes de truncar. En desktop, siempre completo. |
| **Tabla de contenidos** | Oculta en mobile y tablet; reemplazada por un `Accordion` colapsado por defecto, titulado "En esta página", ubicado entre el Encabezado del Documento y el Contenido principal. La regla de divulgación progresiva ya definida para desktop (solo se expanden los H3 de la sección H2 activa) se mantiene idéntica dentro del Accordion — no se relaja ni se simplifica solo por estar en mobile. En desktop, riel fijo de 220px sin cambios. |
| **Contenido principal** | En mobile, ocupa el ancho completo del viewport menos `space-4` (16px) de padding lateral — no se preserva el ancho fijo de `container-content` (760px) porque en mobile el viewport ya es más angosto que ese máximo. En tablet, si el viewport supera los 760px disponibles tras el padding, el contenido se centra dentro de ese máximo en vez de estirarse — la longitud de línea sigue siendo la prioridad, no el uso completo del ancho disponible. |
| **Alertas** | Ancho completo del contenido disponible en cualquier breakpoint — no requieren ajuste adicional, ya que su ancho siempre es relativo al contenedor de contenido, nunca un valor fijo en px. |
| **Tablas** | Ver especificación completa en la sección 8. |
| **Bloques de código** | Ver especificación completa en la sección 9. |
| **Navegación Anterior/Siguiente** | En mobile y tablet, los dos botones se apilan verticalmente ("Anterior" arriba, "Siguiente" abajo), cada uno a ancho completo — más fácil de tocar con precisión que dos botones angostos lado a lado. En desktop, fila horizontal con "Anterior" a la izquierda y "Siguiente" a la derecha, según especificación base. |

**Decisión UX para documentos largos en mobile:** sin el riel de TOC persistente, un documento extenso como HB-001 (más de 20 secciones) deja al usuario sin ninguna señal de cuánto le falta por leer mientras hace scroll. Se agrega un **indicador de progreso de lectura**: una barra delgada de 2px, fija inmediatamente debajo del Header, en `color-primary`, cuyo ancho representa el porcentaje de scroll ya recorrido dentro del documento — visible únicamente en mobile y tablet (en desktop, el scroll-spy del TOC ya cumple esa función de orientación).

---

## 5. Página de Categoría Responsive

| Elemento | Comportamiento adaptable |
|---|---|
| **Buscador local** | En mobile y tablet, ocupa el ancho completo de la página, en su propia fila, por encima del control de Filtros (en desktop conviven en la misma fila). |
| **Filtros** | En desktop, fila de controles (chips de Estado, desplegables de Tipo/Autor, "+ más filtros"). En mobile y tablet, los seis controles no caben cómodamente en una fila — se colapsan en un único botón **"Filtros"** (con un contador de filtros activos, ej. "Filtros (2)"), que al tocarlo abre una hoja inferior (variante mobile del componente Modal, DS-001 §9.18, a pantalla completa en vez de centrada) listando todas las facetas apiladas verticalmente, con botones "Limpiar" y "Aplicar" fijos al pie de la hoja. Esta variante de Modal a pantalla completa **se señala como pendiente de incorporar al catálogo de DS-001 §9.18**, que hasta ahora solo definía tamaños centrados (sm/md/lg). |
| **Tarjetas de documentos** | 1 columna en mobile, 2 columnas en tablet, 3 columnas en desktop — sin cambios respecto a lo ya definido en la especificación de Categoría. |
| **Estadísticas de la categoría** | En desktop, franja horizontal de 5 tiles separados por divisores verticales. En mobile, se reorganiza en una **grilla de 2 columnas** (el quinto tile, Autores principales, ocupa el ancho completo de la última fila) en vez de forzar scroll horizontal — se prioriza que los cinco datos sean visibles sin necesidad de un gesto adicional que el usuario podría no descubrir. En tablet, la franja horizontal ya cabe con los 5 tiles más angostos, sin necesidad de reorganizar. |
| **Categorías relacionadas / Documentos destacados / Recursos adicionales** | Comportamiento fluido ya inherente a estos bloques (chips y listas que se envuelven o apilan según ancho disponible) — no requieren una regla adicional específica de breakpoint. |

**Cómo se mantiene una navegación cómoda:** el punto crítico en esta plantilla es el Sistema de Filtros, porque es el único componente cuya versión desktop no cabe físicamente en mobile sin rediseño de interacción (no solo de layout) — de ahí que reciba un patrón distinto (hoja inferior) en vez de solo reflow, a diferencia del resto de los componentes de esta plantilla.

---

## 6. Sidebar Responsive

**Menú colapsable (desktop/laptop):** ya especificado en la Página de Documento — un toggle en el Header (ícono `panel-left`) colapsa el árbol expandido de 260px a una franja de solo íconos de 64px, sin overlay ni animación de entrada/salida más allá de la transición de ancho (`motion-base`, 200ms). El usuario permanece en la misma página; el contenido simplemente gana ancho disponible.

**Drawer (mobile/tablet):** patrón distinto al colapsado de desktop — no es una franja más angosta, es una superposición completa que se retira de la vista cuando está cerrada.

| Plantilla | Ancho del Drawer | Contenido |
|---|---|---|
| Home | 240px | 8 íconos de categoría + etiqueta de texto visible (justificación en sección 3). |
| Página de Documento / Categoría | 280px | Árbol completo de contenido (mismo contenido que el Sidebar expandido de desktop, a ancho completo del Drawer). |

**Overlay:** fondo semitransparente (`color-overlay`, DS-001 §4.1) cubre el contenido detrás del Drawer mientras está abierto; un tap fuera del Drawer o sobre el overlay lo cierra. El overlay evita que el usuario interactúe accidentalmente con el contenido de fondo mientras navega el árbol.

**Estados abiertos y cerrados:** cerrado = Drawer trasladado completamente fuera del viewport (fuera del borde izquierdo); abierto = se desliza a su posición completa. Transición en `motion-slow` (300ms, DS-001 §13.1) — mismo peso de animación que un Modal, porque funcionalmente es el mismo tipo de interacción (una superposición completa que exige la atención del usuario).

**Justificación de las decisiones:** un Drawer, a diferencia de un menú desplegable simple, permite mostrar el árbol de navegación completo (con su jerarquía de expansión/colapso intacta) sin comprometer espacio de pantalla mientras está cerrado — es la única forma de preservar la misma profundidad de navegación en mobile que la disponible en desktop, consistente con el principio de que ningún contenido desaparece, solo se reorganiza (sección 1).

---

## 7. Tipografía Responsive

**Regla general: la escala tipográfica de DS-001 §5.2 se mantiene fija en todos los breakpoints.** No se reduce el tamaño de H1, H2, H3, H4 ni `text-body` entre mobile y desktop — un H1 de 30px en un viewport angosto simplemente ocupa más líneas al envolverse, lo cual es preferible a introducir una segunda escala tipográfica completa que el equipo tendría que mantener. La única excepción, ya establecida en la especificación de Home, es `text-display` (36px), exclusivo del Hero, que baja a `text-h1` (30px) en mobile — porque ese token no se usa en ningún otro lugar del sistema y su único propósito (impacto visual de bienvenida) se cumple igual de bien a un tamaño menor en una pantalla pequeña.

**Espaciados y márgenes:** a diferencia de la tipografía, el **ritmo vertical entre bloques sí se comprime** en mobile, siguiendo una regla de "un escalón menos" en la escala de espaciado de DS-001 §7 para separaciones de nivel de página (no para espaciados internos de un componente):

| Contexto | Desktop | Mobile/Tablet |
|---|---|---|
| Separación entre secciones mayores de una página | `2XL` (48px) | `XL` (32px) |
| Separación entre bloques dentro de una sección | `XL` (32px) | `LG` (24px) |
| Padding lateral de página | `space-6`/`space-8` (24–32px) | `space-4` (16px) |
| Espaciado interno de un componente (padding de Card, gap dentro de un Callout) | Sin cambio | Sin cambio — un componente se ve idéntico por dentro en cualquier breakpoint |

**Cómo se mantiene la legibilidad:** el límite de longitud de línea (`container-content`, 760px máx.) sigue aplicando incluso en tablet en orientación horizontal, donde el ancho disponible podría superar ese máximo — la columna de lectura nunca se estira más allá de ese límite solo porque hay espacio de sobra.

---

## 8. Tablas Responsive

**Mecanismo base (ya establecido, DS-001 §9.7 y §11):** cuando una tabla excede el ancho de `container-content`, se envuelve en un contenedor con scroll horizontal propio (nunca scroll de la página completa), con una sombra lateral leve que indica que hay más contenido fuera de vista.

**Decisión deliberada: sin ocultamiento de columnas.** Se descarta un patrón de "columnas prioritarias" que oculte columnas menos importantes en mobile, porque requeriría que cada autor de contenido técnico marque manualmente qué columnas son prescindibles en cada tabla que escriba — una carga de mantenimiento por documento que contradice el principio de que los metadatos derivados (como el tiempo de lectura, PV-001 Página de Categoría) se calculan automáticamente en vez de mantenerse a mano. El scroll horizontal simple es la solución que no requiere ninguna configuración adicional por parte de quien escribe el documento.

**Columna fija para tablas de referencia técnica (extensión nueva):** en tablas donde la primera columna es un identificador de fila (ej. nombre de parámetro en una referencia de API, nombre de campo en un esquema de base de datos), esa primera columna permanece fija (`sticky`) mientras el resto de la tabla se desplaza horizontalmente — fondo sólido `color-bg` y borde derecho 1px `color-border` para separarla visualmente del contenido en movimiento. Sin esta columna fija, el usuario perdería de vista a qué fila corresponde cada valor al hacer scroll en una tabla ancha, que es exactamente el tipo de tabla más común en los futuros manuales técnicos (Backend, PostgreSQL). **Se señala como extensión nueva del componente Table, pendiente de catálogo formal en DS-001 §9.7.**

**Interacción táctil:** el scroll horizontal usa el comportamiento nativo de inercia del dispositivo (momentum scrolling), sin una barra de scroll personalizada — mantiene la tabla legible y evita introducir un elemento de interfaz adicional que DS-001 no ha definido.

---

## 9. Bloques de Código Responsive

- **Sin reducción de tamaño de fuente:** `text-code` (14px, JetBrains Mono) se mantiene igual en cualquier breakpoint — reducirlo further en mobile perjudicaría exactamente la legibilidad de caracteres ambiguos (`0`/`O`, `1`/`l`) que fue la razón original para elegir esa tipografía (DS-001 §5.1).
- **Scroll horizontal, nunca wrap:** las líneas largas de código nunca se envuelven, en ningún breakpoint — envolver código rompe la indentación real, que es información funcional en la mayoría de los lenguajes. El bloque mantiene su propio scroll horizontal independiente del resto de la página, igual que en desktop.
- **Ancho completo en mobile (excepción deliberada al padding de página):** en mobile, el bloque de código se extiende al ancho completo del viewport, ignorando el `space-4` de padding lateral que respeta el resto del contenido — gana algunos caracteres adicionales visibles antes de que el scroll horizontal sea necesario, una ganancia real de legibilidad en el contexto donde más se necesita (pantallas angostas). Es una excepción señalada explícitamente porque contradice, solo para este componente, la regla general de que el contenido respeta el padding de página.
- **Encabezado del bloque sin cambios:** la franja de 40px con nombre de archivo/lenguaje y botón de copiar mantiene su altura y disposición en cualquier breakpoint — el botón de copiar necesita seguir siendo fácil de tocar, no de reducirse.
- **Numeración de líneas:** permanece visible en cualquier breakpoint donde ya aplique (bloques de más de 6 líneas, DS-001 §9.14) — no se oculta selectivamente en mobile, lo que rompería la Predictibilidad (WF-001 §4) de un componente que el usuario ya aprendió a leer en desktop.

---

## 10. Rendimiento

Recomendaciones específicas para mantener fluidez en dispositivos de menor capacidad, más allá de lo ya cubierto por la arquitectura estática del Handbook:

- **Carga diferida del índice de búsqueda** (ya establecido en ARC-001 §11 y DS-001 §11): el índice no bloquea el render inicial de ninguna página — se carga recién cuando el usuario interactúa con el Buscador, relevante especialmente en conexiones móviles más lentas.
- **Imágenes y diagramas con dimensiones reservadas:** todo `Figure` (PV-001 Página de Documento §6) declara su relación de aspecto de antemano, para que el navegador reserve el espacio correspondiente antes de que la imagen cargue — evita el salto de layout (contenido que "brinca" mientras la página termina de cargar), especialmente notorio en conexiones lentas.
- **Carga diferida de imágenes bajo el pliegue:** diagramas que no son visibles al cargar la página (más abajo del viewport inicial) se cargan solo cuando el usuario se acerca a ellos con el scroll, usando el comportamiento nativo del navegador, sin una librería adicional.
- **Tipografía con fallback inmediato:** tanto Inter como JetBrains Mono ya declaran una pila de fuentes de sistema como respaldo (DS-001 §5.1) — el texto es legible desde el primer instante aunque la fuente personalizada tarde en descargarse, evitando texto invisible mientras carga.
- **Animaciones económicas por diseño:** los tokens de movimiento (DS-001 §13.1) son transiciones simples de propiedades visuales (color, transform, opacity), no animaciones complejas basadas en JavaScript — de bajo costo computacional en cualquier dispositivo, y ya se desactivan por completo con `prefers-reduced-motion` (DS-001 §13.2), lo cual también reduce carga en equipos de gama baja aunque el usuario no haya activado esa preferencia por razones de accesibilidad sino de rendimiento de su dispositivo.
- **Sin dependencias de UI pesadas para patrones responsive:** Drawer, Modal/hoja inferior y Accordion (secciones 5 y 6) se construyen sobre los mismos componentes ya catalogados en DS-001 — no se introduce una librería de interfaz adicional solo para resolver comportamiento responsive.

---

## 11. Buenas Prácticas Responsive

- Nunca ocultar contenido al reducir el viewport — solo reorganizarlo, colapsarlo detrás de un control, o moverlo a un overlay (principio rector de todo este documento, sección 1).
- Construir y probar cada componente nuevo primero en el breakpoint Mobile; validar el pulido visual final en Desktop, que sigue siendo la prioridad de calidad (Filosofía Visual ya aprobada).
- No introducir un breakpoint fuera de los cuatro definidos en la sección 2 sin pasar por el proceso de gobernanza de DS-001 §16.
- Probar cada componente exactamente en los límites de cada rango (ej. 639px y 640px), no solo en anchos "cómodos" intermedios donde los problemas de reflow no siempre son visibles.
- Reutilizar los patrones responsive ya resueltos (Drawer, Accordion, hoja inferior tipo Modal) para cualquier necesidad futura similar, en vez de crear una solución ad-hoc por página o por componente nuevo.
- Mantener siempre un `max-width` de lectura controlado — ningún bloque de texto de prosa se estira libremente al ancho completo del contenedor solo porque hay espacio disponible.
- Todo elemento interactivo conserva el mínimo de 24×24px de área táctil en cualquier breakpoint, incluyendo dentro de Drawers y hojas inferiores (detalle completo de accesibilidad, próxima fase de PV-001).
- Validar cada plantilla con el contenido real de mayor longitud esperada (ej. HB-001 completo, con más de 20 secciones), nunca solo con contenido de prueba corto — la mayoría de los problemas responsive reales aparecen únicamente con contenido largo genuino.

---

## 12. Validación

| Documento | Cumplimiento |
|---|---|
| **STD-001** | Las buenas prácticas de la sección 11 (probar con contenido real, no introducir breakpoints sin gobernanza) siguen el mismo estándar de disciplina de proceso ya exigido para el resto del proyecto. |
| **ARC-001** | Respeta íntegramente la arquitectura estática (§1) como base de las recomendaciones de rendimiento (sección 10) — ninguna solución responsive introduce una dependencia de backend o de datos en tiempo real. |
| **DS-001** | Los cuatro breakpoints (§8.2), el sistema de espaciado (§7) y los componentes reutilizados (Modal, Drawer, Accordion) se aplican sin alterar sus tokens base. Dos extensiones quedan señaladas como pendientes de catálogo formal: la variante de Modal a pantalla completa para Filtros en mobile (sección 5) y la columna fija de Tabla (sección 8). |
| **WF-001** | El principio de "ningún contenido desaparece, solo se reorganiza" (§11) se mantiene como regla central de todo este documento, aplicado de forma consistente en las tres plantillas ya validadas (Home, Documento, Categoría). |

**Base para la implementación en React + Vite + Tailwind:** los cuatro breakpoints de la sección 2 mapean directamente a un conjunto de breakpoints personalizado de Tailwind (uno por token: `bp-mobile`, `bp-tablet`, `bp-desktop`, `bp-wide`), sin necesidad de reconciliar nombres distintos entre el sistema de diseño y la configuración del framework. Los patrones de Drawer, Accordion y hoja inferior, al reutilizar componentes ya catalogados en DS-001, no requieren nueva lógica de estado más allá de la ya prevista para sus versiones desktop (abierto/cerrado, expandido/colapsado) — la diferencia entre breakpoints es, en la mayoría de los casos, una cuestión de qué variante del mismo componente se renderiza, no de lógica de aplicación distinta.


---

# Parte 5 — Dark Mode

El modo oscuro no es un tema alternativo con su propia composición: es el mismo layout, la misma jerarquía y las mismas medidas ya definidas en las Partes 1–4 de este documento (Home, Página de Documento, Página de Categoría y Responsive Design), con los tokens de color de DS-001 §4.1 sustituidos por su par oscuro. Ningún valor de esta especificación (tamaños, espaciados, proporciones de grilla) cambia entre temas — solo el color.

> **Nota de consolidación:** esta sección de Dark Mode no recibió una fase de desarrollo detallado propia, a diferencia de Home, Documento, Categoría, Responsive, Navegación y Componentes — permanece en su nivel de especificación original. Se deja registrado como vacío conocido en la Fase Final (Parte 10, Riesgos).

Comportamientos específicos que sí ameritan mención:

- **Bloques de código**: el resaltado de sintaxis usa una paleta de tema propia (no una simple inversión de brillo del tema claro), consistente con DS-001 §9.14.
- **Imágenes/diagramas**: los diagramas actuales del Manual de Organización (PNG con fondo claro) se muestran dentro de un contenedor con fondo blanco fijo en ambos temas, hasta que se migren a SVG/Mermaid heredando tokens (recomendación ya registrada en DS-001 §17). Esto evita que un diagrama "flote" con bordes visibles sobre un fondo oscuro.
- **Elevación (`surface-raised`)**: modales, tooltips y dropdowns usan un tono más claro que `surface` en modo oscuro (en vez de una sombra más pronunciada, que es el recurso típico en modo claro) — en fondos oscuros, la sombra por sí sola comunica poco; el cambio de tono es lo que separa visualmente los planos.
- **Transición entre temas**: el cambio de `data-theme` no anima una transición de color por defecto (evita un "flash" de colores intermedios incorrectos); el único elemento que anima es el ícono del toggle de tema (sol/luna) en `motion-fast` (DS-001 §13.1).

---


---

# Parte 6 — Sistema de Navegación e Interacciones

| Campo | Valor |
|---|---|
| Documento | PV-001 — Fase 6: Sistema de Navegación e Interacciones |
| Versión | 1.0 |
| Estado | Borrador para revisión |
| No modifica | Introducción, Filosofía Visual, Home, Página de Documento, Página de Categoría, Responsive Design (ya aprobados) |
| Naturaleza de esta fase | A diferencia de las fases anteriores, que especificaron medidas y composición por plantilla, esta fase es **transversal**: consolida cómo se comporta la navegación y la interacción *a través* de las tres plantillas, como un sistema único. Donde algo ya fue especificado en detalle en una fase previa, se referencia en vez de repetirse; el desarrollo completo aquí se concentra en el comportamiento que todavía no tenía una definición explícita. |

---

## Nota de síntesis

Esta fase no reabre ninguna medida, token o composición ya aprobada. Su función es responder una pregunta distinta a la de las fases anteriores: no "¿cómo se ve esto?", sino "¿qué hace la interfaz cuando el usuario actúa?". Un puñado de comportamientos se definen aquí por primera vez (búsquedas recientes, botón "Volver arriba", gestos de cierre del Drawer, cierre automático de overlays) — se distinguen del resto porque no tenían una decisión previa que referenciar. Se señala explícitamente cuál es cuál a lo largo del documento.

---

## 1. Filosofía de navegación

El sistema de navegación completo del Handbook descansa sobre los **cinco planos** ya definidos en WF-001 §5 (Global, Local, Contextual, Secuencial, Utilitario) — esta fase no agrega un sexto plano, sino que explica los principios que hacen que esos cinco planos funcionen como un sistema coherente en la práctica:

- **Simplicidad**: cada acción de navegación tiene un único mecanismo esperado, nunca dos formas ambiguas de lograr lo mismo. Esta es la razón por la que WF-001 §6.3 descartó un botón "Volver" genérico a favor de tres mecanismos específicos e inequívocos — el mismo criterio se aplica a cualquier interacción nueva definida en esta fase.
- **Consistencia**: un mismo tipo de interacción se comporta idénticamente sin importar en qué plantilla ocurra. El estado activo de un ítem de Sidebar usa el mismo lenguaje visual (fondo `color-primary` al 8%, barra de acento de 2px) en Home, Documento y Categoría — el usuario aprende el patrón una sola vez.
- **Descubrimiento del contenido**: la interfaz siempre ofrece más de una vía razonable hacia el mismo destino (exploración por Sidebar, búsqueda, enlaces cruzados, navegación secuencial — WF-001 §6.2), porque distintos usuarios llegan con distintos niveles de certeza sobre qué buscan.
- **Jerarquía visual**: la navegación se mantiene deliberadamente discreta frente al contenido (íconos sin relleno, color `text-secondary` en reposo, ya establecido en las tres especificaciones de plantilla) — está siempre disponible, pero nunca compite por atención con lo que el usuario vino a leer.

---

## 2. Sidebar

Las medidas, estados visuales base y reglas de escalabilidad del Sidebar ya están completamente definidas: estado colapsado en Home (Home §2), estado expandido en Documento/Categoría (Documento §2), comportamiento en Tablet/Mobile vía Drawer (Responsive §6). Esta sección consolida la **secuencia de interacción** y cierra los estados que no habían recibido tratamiento explícito.

**Categorías y Subcategorías:** el click en una categoría con hijos no navega de inmediato — expande la rama in situ (chevron rota 90°, `motion-base`, ya definido en Documento §2). El click en una subcategoría (ej. Frontend dentro de Ingeniería) repite el mismo comportamiento un nivel más adentro. Solo el click en un documento final navega y cierra cualquier otra rama previamente expandida que no sea la del documento activo — el árbol nunca muestra dos ramas de nivel raíz expandidas simultáneamente (Filosofía Visual, Minimalismo).

**Focus (nuevo — no definido en fases anteriores):** cada ítem del árbol es alcanzable por `Tab`, en el mismo orden en que aparece visualmente de arriba hacia abajo. El anillo de foco (DS-001 §12) se dibuja alrededor de la fila completa del ítem, no solo del texto — consistente con el tratamiento de hover, que también cubre la fila completa (Documento §2). `Enter` o `Espacio` sobre un ítem con hijos lo expande/colapsa exactamente igual que un click; sobre un documento final, navega.

**Animaciones esperadas (consolidado):**

| Interacción | Token | Comportamiento |
|---|---|---|
| Expansión/colapso de rama | `motion-base` (200ms) | Ya definido en Documento §2 y DS-001 §13.1 |
| Colapso del árbol completo a franja de íconos (toggle del Header) | `motion-base` (200ms) | Ya definido en Documento §1 |
| Apertura/cierre del Drawer (mobile/tablet) | `motion-slow` (300ms) | Ya definido en Responsive §6 |
| Hover sobre un ítem | `motion-fast` (120ms) | Ya definido en DS-001 §9 (Microinteracciones) |

---

## 3. Header

El Header es el único componente verdaderamente idéntico en las tres plantillas (Home §1, Documento §1) — esta sección no repite sus medidas, solo aclara el comportamiento de cada elemento como parte del sistema de interacción global.

- **Logo:** interacción de una sola función — click navega a Home. No tiene menú desplegable ni comportamiento secundario.
- **Breadcrumb:** no vive en el Header (vive debajo de él, Documento §3) — se excluye de esta sección para no introducir ambigüedad de ubicación; ver sección 4.
- **Buscador:** abre el modal de búsqueda global (sección 6) al click o al atajo `Ctrl/Cmd+K` desde cualquier punto del Handbook, sin excepción de plantilla.
- **Botón Dark Mode:** alterna el tema (DS-001 §7, comportamiento completo se especificará en la fase de Dark Mode); a nivel de interacción, es un toggle binario sin estados intermedios — un click cambia el tema inmediatamente, sin confirmación.
- **Perfil (Selector de integrante, si aplica):** ya resuelto como elemento no autenticado (Home, "Notas de diseño") — su interacción es un desplegable simple de 4 opciones, sin flujo de login.
- **Acciones rápidas:** cada ícono ejecuta su acción en un solo click, sin menú intermedio (a diferencia del Perfil, que sí despliega opciones).

**Principio de interacción del Header en su conjunto:** ningún elemento del Header requiere más de una interacción para completar su propósito principal, salvo el Selector de integrante (que por naturaleza ofrece una elección) — es la zona de la interfaz con menor fricción esperada por diseño, porque está presente en el 100% de las páginas y cualquier fricción ahí se multiplica por cada visita.

---

## 4. Sistema de Breadcrumbs

Jerarquía, formato y truncado a nivel visual ya están definidos (DS-001 §9.4, Documento §3, Responsive §4) — esta sección cierra el único detalle que faltaba: el criterio exacto de truncado.

**Longitud máxima (nuevo):** en desktop, el Breadcrumb se muestra completo mientras su ancho total no exceda el ancho de `container-content` (760px); si lo excede (poco frecuente, solo en documentos anidados en una subcategoría con nombres largos), el o los niveles intermedios se colapsan en un `…` clicable, dejando siempre visibles el primer nivel (Inicio) y el último (página actual) — nunca se trunca el nivel actual, porque es la información más relevante de ese componente.

**Navegación:** cada nivel intermedio, incluido el colapsado tras `…` al expandirlo, navega directamente a la Página de Categoría correspondiente — un solo click, sin pasos intermedios, consistente con el principio de Simplicidad (sección 1).

**Responsive:** comportamiento ya definido en Responsive §4 (2 niveles en mobile, 3 en tablet, completo en desktop) — sin cambios aquí.

---

## 5. Tabla de Contenidos (TOC)

Ubicación, ancho, y la regla de divulgación progresiva (solo se expanden los H3 de la sección H2 activa) ya están definidos en Documento §5. Se consolida aquí el comportamiento de scroll como parte del sistema de interacción:

- **Comportamiento Sticky:** el riel completo permanece fijo respecto al viewport mientras el usuario recorre el contenido, deteniéndose antes de superponerse al Footer condensado (Documento §6) al llegar al final del documento — el TOC nunca "flota" sobre el Footer.
- **Sincronización con el scroll:** un observador de posición (scroll-spy) determina qué sección del contenido está actualmente en el viewport y actualiza el ítem resaltado del TOC en consecuencia, sin retraso perceptible ni parpadeo entre secciones adyacentes.
- **Resaltado de sección activa:** mismo lenguaje visual que el ítem activo del Sidebar (`color-primary` + barra de acento de 2px, Documento §5) — la repetición intencional de esta señal es lo que permite que el usuario entienda "estoy aquí" sin tener que aprender un código de color distinto para cada componente.
- **Navegación mediante clic (nuevo detalle):** el click en un ítem del TOC ejecuta un scroll suave (no un salto instantáneo) hasta el heading correspondiente, con una compensación de offset equivalente a `space-6` por encima del heading — evita que el título quede pegado al borde superior del viewport, justo debajo del Header sticky.

---

## 6. Buscador Global

Ubicación, agrupamiento de resultados por categoría y ranking ya están definidos en DS-001 §9.12. Dos comportamientos no tenían definición previa y se cierran aquí.

**Búsqueda en tiempo real:** los resultados se actualizan con cada carácter ingresado (sin necesidad de presionar Enter), con un debounce breve para no re-renderizar en cada pulsación individual si el usuario escribe rápido — el buscador nunca muestra un estado de carga visible en este proceso, porque opera sobre el índice ya cargado en el cliente (ARC-001 §11).

**Historial (nuevo — búsquedas recientes):** al abrir el modal de búsqueda con el campo vacío, se muestran hasta 5 búsquedas recientes del usuario (almacenadas localmente en el navegador, nunca sincronizadas a un servidor — coherente con la arquitectura sin backend, ARC-001 §1), bajo el encabezado "Búsquedas recientes", con la misma estructura visual que un resultado normal pero sin snippet de contexto. Un ícono de reloj (`icon-xs`) precede cada entrada para distinguirlas visualmente de un resultado real. Esta función es distinta de la "historial de páginas visitadas" que WF-001 §15 dejó como Pregunta Abierta sin resolver — esta sección responde únicamente qué pasa dentro del propio Buscador, no introduce un historial de navegación general del Handbook.

**Vacíos y sin resultados:** ambos estados ya están definidos a nivel visual (DS-001 §9.12, Página de Categoría §2 para el equivalente local) — el estado "vacío" (campo sin texto, sin historial disponible aún) muestra únicamente el placeholder y el atajo de teclado; el estado "sin resultados" ofrece categorías relacionadas como siguiente paso, nunca una pantalla en blanco.

---

## 7. Navegación entre documentos

Documento anterior/siguiente y Documentos relacionados ya están completamente definidos en Documento §9. Se aclaran aquí los dos mecanismos restantes, ninguno de los cuales requiere un componente nuevo:

- **Categoría superior:** se resuelve exclusivamente a través del nivel correspondiente del Breadcrumb (sección 4) — no existe un botón adicional "subir un nivel"; introducir uno duplicaría una función que el Breadcrumb ya cumple, violando el principio de Simplicidad (sección 1).
- **Regresar al índice (de categoría):** mismo mecanismo — el nivel de categoría dentro del Breadcrumb navega directo a su Category Index. El Sidebar (sección 2) ofrece una ruta alternativa equivalente para quien lo prefiera, pero no es un componente adicional dedicado a esta función.

**Principio general de esta sección:** ninguna de las cuatro necesidades de navegación entre documentos requirió, en conjunto, más de tres componentes reales (Prev/Next, Documentos relacionados, Breadcrumb) — es la prueba de que los planos de navegación ya definidos (WF-001 §5) cubren el espacio de necesidades sin superposición ni huecos.

---

## 8. Estados de interacción

Consolidación de los estados ya definidos de forma dispersa en DS-001 §9 y en las especificaciones de plantilla, presentados aquí como una matriz única aplicable a cualquier componente interactivo del sistema.

| Estado | Comportamiento visual | Dónde ya se definió |
|---|---|---|
| **Hover** | Cambio de borde/fondo sutil (`color-border-strong` o `+4%` de opacidad de fondo, según el componente), `motion-fast` | DS-001 §9.5–9.6, aplicado consistentemente en Sidebar, Cards, botones |
| **Focus** | Anillo de 2px en `color-primary`, 2px de separación, nunca reemplaza al hover si ambos coinciden | DS-001 §12 |
| **Pressed** *(aclaración nueva)* | Para botones: el color de fondo pasa momentáneamente a `color-primary-hover` durante el click, antes de ejecutar la acción — es un estado transitorio (dura lo que dura la presión), no uno persistente como hover o focus | Extiende DS-001 §9.6, que ya agrupaba "active/pressed" sin distinguir el matiz temporal |
| **Disabled** | Opacidad 40%, cursor `not-allowed`, sin respuesta a hover/focus/click | DS-001 §9.6 |
| **Loading** | Skeleton loader (bloques grises sin texto) para el índice de búsqueda; nunca un spinner tradicional | PV-001 base, Microinteracciones |
| **Empty State** | Ícono neutro + mensaje + siguiente paso sugerido (nunca una pantalla en blanco sin salida) | Página de Categoría §7, Buscador (sección 6 de esta fase) |
| **Success** | Confirmación momentánea (ej. check verde al copiar código), nunca un banner persistente | PV-001 base, Microinteracciones |
| **Warning** | Badge o Callout en `color-warning`, persistente mientras la condición exista (ej. documento en Draft) | DS-001 §9.11, §9.15 |
| **Error** | Alerta de página completa en `color-danger` (documento deprecado) o mensaje puntual (ej. fallo al copiar código) según el contexto | Documento §7 (Componentes Especiales), PV-001 base |

**Por qué se consolida en una sola tabla:** un desarrollador implementando cualquier componente nuevo del sistema puede verificar, sin buscar en cinco documentos distintos, qué estados se esperan de él y cómo deben verse — reduce el riesgo de que un componente futuro invente un tratamiento de estado inconsistente con el resto del sistema.

---

## 9. Comportamiento del Scroll

- **Scroll suave:** aplicado consistentemente en cualquier navegación por ancla dentro de la misma página (clicks en el TOC, sección 5) — nunca un salto instantáneo.
- **Sticky Header:** ya definido (DS-001 §9.1) — permanece fijo en la parte superior del viewport en cualquier plantilla y breakpoint, sin excepción.
- **Sticky TOC:** ya definido (Documento §5, reafirmado en sección 5 de esta fase).
- **Indicador de progreso de lectura:** ya definido y limitado a mobile/tablet (Responsive §4) — en desktop, el scroll-spy del TOC ya cumple esa función de orientación, por lo que no se duplica la señal.
- **Botón "Volver arriba" (nuevo):** botón circular de 40×40px, ícono `arrow-up` (`icon-sm`), fondo `color-surface`, borde 1px `color-border`, sombra sutil — posición fija en la esquina inferior derecha, con `space-6` de margen respecto a los bordes del viewport. Aparece únicamente después de que el usuario se desplaza más allá del Encabezado del Documento (o del Encabezado de Categoría, en esa plantilla), con una transición de aparición/desaparición en `motion-fast`. Al hacer click, ejecuta scroll suave hasta el inicio de la página. No aparece en Home, donde la extensión de la página no lo justifica.

---

## 10. Navegación Mobile

El comportamiento estructural del Drawer (ancho, overlay, apertura/cierre) ya está completamente definido en Responsive §6. Se cierran aquí los detalles de interacción que faltaban.

- **Menú hamburguesa:** ícono en el Header (ya definido en Home/Responsive §3), única función es abrir el Drawer correspondiente a la plantilla actual.
- **Overlay:** ya definido (Responsive §6) — un tap sobre el overlay cierra el Drawer.
- **Gestos (nuevo):** además del tap fuera y de un botón de cierre explícito, el Drawer se cierra con un gesto de deslizamiento hacia la izquierda sobre el propio panel — comportamiento táctil esperado por convención en cualquier plataforma móvil, complementario a los otros dos métodos, no un reemplazo.
- **Cierre automático (nuevo):** seleccionar cualquier ítem de navegación dentro del Drawer lo cierra automáticamente antes de completar la navegación al destino — el usuario nunca tiene que cerrar el Drawer manualmente después de elegir algo. La misma regla aplica a la hoja inferior de Filtros de la Página de Categoría (Responsive §5): se cierra automáticamente al tocar "Aplicar", no al tocar "Limpiar" (que solo reinicia los valores sin cerrar, permitiendo seguir ajustando filtros).
- **Experiencia táctil:** todo elemento interactivo dentro de cualquier overlay mobile mantiene el mínimo de 24×24px de área táctil ya exigido en todo el sistema (DS-001 §12); dentro del Drawer específicamente, cada fila del árbol de navegación tiene una altura mínima de 44px (superior al mínimo general) para reducir el riesgo de toques accidentales sobre el ítem vecino en una lista densa.

---

## 11. Accesibilidad

Esta sección cubre exclusivamente la accesibilidad **de navegación e interacción** — el tratamiento completo de WCAG 2.2 AA (contraste sistemático, compatibilidad con lectores de pantalla, tamaños mínimos) corresponde a una fase dedicada de PV-001, todavía pendiente. Lo que sigue es el contrato de accesibilidad específico del sistema descrito en esta fase.

- **Navegación mediante teclado:** el orden de tabulación recorre, en cualquier plantilla, el mismo trayecto visual ya establecido en Documento §8: Header (logo → buscador → utilidades) → Sidebar → Breadcrumb (si existe) → Contenido → TOC → Prev/Next → Footer. Un enlace "Saltar al contenido", oculto hasta recibir foco, es siempre el primer elemento tabulable de cualquier página.
- **Focus visible:** anillo de 2px en `color-primary` (DS-001 §12), aplicado de forma idéntica en los 19+ componentes del sistema, incluidos los nuevos de esta fase (botón "Volver arriba", ítems de búsquedas recientes) — ningún componente nuevo introducido en esta fase queda exento de esta regla.
- **ARIA (nivel conceptual):** además de los landmarks ya mencionados en fases previas (`header`, `nav`, `main`, `aside`, `footer`), esta fase aporta dos roles conceptuales nuevos por la naturaleza interactiva de sus componentes: el estado expandido/colapsado de una rama del Sidebar se comunica como expandido/contraído a tecnología de asistencia, y el ítem activo de navegación (Sidebar, TOC) se identifica como "actual" dentro de su región — ninguno de los dos implica una decisión de implementación (queda para la fase de desarrollo), solo el requisito conceptual de que la información debe estar disponible para quien no usa un mouse ni ve la pantalla.
- **Contraste:** todos los estados de esta fase (hover, focus, pressed, disabled) reutilizan exclusivamente los tokens ya verificados en DS-001 §4.1 — ninguna combinación de color nueva se introduce en este documento.
- **Orden lógico:** todo componente nuevo de esta fase (búsquedas recientes, botón "Volver arriba") se inserta en el orden de tabulación en el lugar donde aparece visualmente, sin excepciones que alteren el recorrido ya definido — un componente que apareciera fuera de orden en el DOM aunque se vea en el lugar correcto visualmente rompería esta regla.

---

## 12. Buenas prácticas UX

Recomendaciones para que el sistema de navegación se mantenga coherente a medida que el Handbook crezca durante varios años, más allá del volumen actual de contenido:

- **Ningún patrón de navegación nuevo se introduce sin pasar por los cinco planos ya definidos (WF-001 §5).** Si una necesidad futura no encaja en Global, Local, Contextual, Secuencial o Utilitario, es señal de que la necesidad está mal planteada, no de que hace falta un sexto plano — la disciplina de mantenerlos en cinco es lo que evita que la navegación se fragmente con el tiempo.
- **Todo estado de interacción nuevo se valida contra la matriz de la sección 8 antes de implementarse** — si un componente futuro necesita un estado que no está en esa tabla, se actualiza la tabla primero (vía el proceso de gobernanza de DS-001 §16), no se inventa un tratamiento aislado para ese componente.
- **La búsqueda, no el árbol de navegación, es el mecanismo que debe absorber el crecimiento del contenido.** El Sidebar tiene un límite estructural de tres niveles (Documento §2) precisamente para que, cuando el volumen de documentos crezca, la presión se traslade a mejorar la búsqueda y el filtrado (ya resueltos para la Página de Categoría) en vez de a seguir anidando el árbol.
- **Ningún mecanismo de retorno o navegación secuencial se duplica.** Antes de agregar un atajo nuevo (un botón, un enlace), se verifica si alguno de los mecanismos ya existentes (Breadcrumb, Sidebar, Prev/Next, Documentos relacionados) ya resuelve esa necesidad — la sección 7 de esta fase es un ejemplo directo de esa disciplina aplicada.
- **Todo comportamiento de interacción se documenta en el mismo lugar donde se documenta su equivalente visual**, no en un documento separado sin trazabilidad — es la razón por la que esta fase referencia explícitamente cada sección previa en vez de asumir que el lector recuerda dónde se definió cada cosa.


---

# Parte 7 — Sistema de Componentes Visuales

| Campo | Valor |
|---|---|
| Documento | PV-001 — Fase 7: Sistema de Componentes Visuales |
| Versión | 1.0 |
| Estado | Borrador para revisión |
| No modifica | Introducción, Filosofía Visual, Home, Página de Documento, Página de Categoría, Responsive Design, Sistema de Navegación e Interacciones (ya aprobados) |
| Naturaleza de esta fase | Es el **catálogo consolidado** de todo componente visual del Handbook — el equivalente ampliado de DS-001 §9, siete fases después. Donde un componente ya fue especificado en una fase anterior, se referencia sin repetir la medida; esta fase agrega los componentes que todavía no tenían una entrada formal (Inputs, Tooltips, Modales, Acordeones, Tabs, Timeline, Checklists, y los componentes propios del Handbook) y cierra, en un solo lugar, el registro de todas las extensiones a DS-001 acumuladas durante PV-001. |

---

## 1. Filosofía del Sistema de Componentes

**Objetivo:** que ningún desarrollador del equipo de Frontend tenga que decidir, por su cuenta, cómo debe verse o comportarse un elemento de interfaz — cada necesidad visual del Handbook tiene una respuesta ya definida en este documento o en DS-001, y si no la tiene, la respuesta correcta es extender el catálogo, no improvisar dentro de una página.

**Consistencia visual:** todo componente de este catálogo se construye exclusivamente con los tokens ya definidos en DS-001 §4–§8 (color, tipografía, espaciado, iconografía, breakpoints) — ningún componente de esta fase introduce un valor de diseño nuevo fuera de esa base.

**Reutilización:** el sistema deliberadamente tiene menos componentes de los que un catálogo ingenuo tendría, porque un mismo componente base cubre varios contextos — la Card de categoría (Home), la Card de documento (Categoría) y la ADRCard (sección 19) son la misma estructura con variaciones de contenido, no tres componentes distintos; el mismo patrón de chip resuelve Filtros, Etiquetas y Accesos rápidos (sección 10).

**Escalabilidad:** el catálogo crece por decisión explícita de gobernanza (DS-001 §16), nunca por acumulación silenciosa página por página — es la razón por la que cada fase de PV-001 fue señalando sus extensiones en vez de darlas por aprobadas, y es la razón por la que esta fase cierra con un registro único de todo lo pendiente (sección final).

**Relación con DS-001:** este documento no reemplaza a DS-001 — lo extiende. DS-001 sigue siendo la fuente de verdad de tokens (color, tipografía, espaciado, iconografía) y del catálogo original de 19 componentes (§9); esta fase documenta el comportamiento completo de esos 19 más los que se fueron necesitando durante el desarrollo visual de las tres plantillas, y dejará de tener razón de existir como documento separado en cuanto DS-001 incorpore formalmente estas extensiones en su próxima revisión mayor.

---

## 2. Tarjetas (Cards)

| Variante | Dónde se usa | Rasgo distintivo | Fuente |
|---|---|---|---|
| Card de categoría | Home — Tarjetas principales | Alineación izquierda, ícono en contenedor de 48px | Home §4 |
| Card destacada/featured | Home — Manuales destacados; Categoría — Documentos destacados | Borde izquierdo de 2px en `color-primary` (curaduría editorial) | Home §4, Categoría §6 |
| Card de documento | Página de Categoría — grilla principal | Incluye código, versión, estado, etiquetas y tiempo de lectura | Categoría §4 |
| ADRCard | Documentos de tipo `adr` | Estructura de campos fijos (ver sección 19) | DS-001 §9.15, formalizada en sección 19 |

**Jerarquía visual (regla común a las cuatro variantes):** el título es siempre el único texto en `text-h4`/peso 600 dentro de la tarjeta — ninguna variante rompe esta regla, incluso cuando agrega metadatos adicionales (código, versión, tiempo de lectura), que se mantienen siempre en `text-caption`/`text-secondary`.

**Estados:** `default` → `hover` (borde a `color-border-strong` + sombra sutil, `motion-fast`) → `focus-visible` (anillo de 2px) — ya definidos en DS-001 §9.5, sin variación entre las cuatro variantes.

**Espaciados:** padding interno `space-4` en las cuatro variantes; gap entre tarjetas de una misma grilla `space-6` en desktop, `space-4` en mobile (DS-001 §8.3).

**Uso recomendado:** la variante "destacada" (borde de acento) se reserva exclusivamente para curaduría editorial explícita — nunca se aplica automáticamente por ningún criterio calculado (ni popularidad, ni fecha), porque su significado visual es "el equipo decidió que esto importa", y ese significado se pierde si empieza a aparecer por una regla algorítmica.

---

## 3. Alertas

Ya definidas por completo en DS-001 §9.10 y Documento §7. Consolidado:

| Variante | Color/Ícono | Cuándo usarla |
|---|---|---|
| Información | `color-info`, ícono `info` | Contexto relevante no crítico para la comprensión del documento |
| Advertencia | `color-warning`, ícono `alert-triangle` | Algo que puede salir mal si se ignora, no destructivo |
| Error/Peligro | `color-danger`, ícono `alert-octagon` | Consecuencias serias o irreversibles |
| Nota | `color-info`, ícono `info` | Sinónimo funcional de "Información" — incluido en el catálogo por su uso frecuente en documentos de gobernanza como STD-001 |

**Sin variante de Éxito:** decisión ya tomada y reafirmada aquí — un estado de éxito es momentáneo por naturaleza (sección 8 de la Fase 6), nunca amerita un banner persistente de página completa.

---

## 4. Callouts

Ya definidos en DS-001 §9.15 y ampliados en Documento §7. Consolidado como catálogo cerrado de cinco variantes:

| Variante | Semántica | Ícono |
|---|---|---|
| Nota | Info | `info` |
| Tip / Buena práctica | Success | `lightbulb` |
| Advertencia | Warning | `alert-triangle` |
| Peligro | Danger | `alert-octagon` |
| Ejemplo | Neutral (`color-border-strong`, sin color semántico) | `terminal` |

**Objetivo:** ofrecer una pausa visual dentro del flujo de lectura para contenido que no debe leerse "al mismo nivel" que el párrafo circundante, sin interrumpir la continuidad del documento.

**Jerarquía:** borde izquierdo de 3px + fondo al 6% de opacidad del color correspondiente (variante Ejemplo usa `color-border-strong` en lugar de un color semántico) — nunca fondo sólido, para no fatigar la lectura en documentos con varios callouts seguidos.

**Casos de uso:** distinción clave frente a Alertas (sección 3) — un Callout vive dentro del contenido y puede aparecer varias veces en un mismo documento; una Alerta es un banner único de página completa, ubicado siempre en el mismo lugar (debajo del Encabezado del Documento).

---

## 5. Bloques de Código

Apariencia, encabezado, botón de copiar, numeración y scroll ya están completamente definidos (DS-001 §9.14, Documento §8, Responsive §9). Se agrega aquí el único elemento sin definición previa:

**Selector de lenguaje (nuevo):** cuando un mismo ejemplo técnico está disponible en más de un lenguaje o herramienta (ej. un mismo llamado de API mostrado en `curl`, JavaScript y Python — previsible para los futuros manuales de Backend), el encabezado del bloque reemplaza la etiqueta estática de lenguaje por el componente Tabs (sección 16) en miniatura: una fila de pestañas cortas ("curl" / "JS" / "Python") dentro de la misma franja de 40px, alineadas donde antes iba el nombre del archivo. Solo un lenguaje se muestra a la vez; cambiar de pestaña reemplaza el contenido del bloque sin desplazar la página. Para el caso general de un solo lenguaje (el más común), el comportamiento no cambia respecto a lo ya definido — el selector solo aparece cuando hay más de una variante real.

**Estados:** `default` → `con numeración` (bloques de más de 6 líneas) → `copiado` (2 segundos, ícono de check en `color-success`) → `error al copiar` (ícono de alerta en `color-danger`, poco frecuente) — ya definidos en conjunto entre DS-001 §9.14 y Fase 6 §8.

---

## 6. Tablas

Comportamiento base, encabezados y legibilidad ya definidos (DS-001 §9.7, Responsive §8). Se agrega el tratamiento de tablas comparativas, no cubierto antes:

**Tablas comparativas (nuevo):** cuando una tabla compara opciones (ej. alternativas técnicas evaluadas en un ADR), una columna puede marcarse como recomendada — fondo `color-primary` al 4% de opacidad en toda la columna (encabezado incluido) y un badge pequeño "Recomendado" en la celda de encabezado de esa columna. Es una marca editorial explícita, nunca automática, igual criterio que las Cards destacadas (sección 2).

**Tablas extensas:** scroll horizontal propio + columna fija opcional para la primera columna cuando es un identificador de fila — ya definido en Responsive §8, sin cambios.

**Responsive:** ya definido en Responsive §8 — scroll horizontal sin ocultamiento de columnas, sin variación aquí.

---

## 7. Diagramas

Definidos como instancia del componente `Figure` en Documento §6; DS-001 §17 ya recomienda migrar a Mermaid/SVG. Se formaliza aquí la relación completa:

**Relación con Mermaid y SVG:** todo diagrama nuevo se autoría preferentemente en sintaxis Mermaid (texto versionable en Git, coherente con la filosofía docs-as-code de ARC-001) y se renderiza a SVG en tiempo de build; diagramas que requieran un diseño personalizado no representable en Mermaid se autoría directamente como SVG. Ambos casos heredan los tokens de color de DS-001 (a diferencia de una imagen rasterizada, que no puede adaptarse a modo oscuro — razón original de esta recomendación).

**Ubicación:** centrado dentro de `container-content`, o `container-wide` si el diagrama lo requiere (excepción ya prevista en Documento §6).

**Escalado (nuevo):** el diagrama nunca excede el ancho de su contenedor; si el contenido del diagrama es más denso de lo que ese ancho permite mostrar con claridad, se ofrece una interacción de "click para ampliar" que abre el mismo diagrama dentro de un Modal tamaño `lg` (960px, DS-001 §9.18) — reutiliza el componente Modal ya existente, no introduce uno nuevo.

**Leyendas:** mismo tratamiento que el caption de Figure — `text-caption`/`text-secondary`, centrado, numerado ("Figura N").

---

## 8. Imágenes

**Relación con Diagramas:** Imágenes y Diagramas comparten el mismo componente `Figure` (Documento §6) — no son dos componentes distintos, solo dos tipos de contenido dentro del mismo wrapper visual (imagen/diagrama + caption).

**Tamaños:** ancho máximo igual a `container-content`; alto automático, preservando la relación de aspecto original — con dimensiones reservadas de antemano para evitar salto de layout (Responsive §10).

**Márgenes:** `space-6` de margen vertical respecto al contenido de texto circundante — mismo valor que un Callout o un bloque de código, para que cualquier elemento "no textual" dentro del flujo de lectura reciba la misma pausa visual.

**Pie de imagen / Captions:** obligatorio cuando la imagen no es autoexplicativa por el texto que la rodea; mismo estilo que el caption de un Diagrama.

**Agrupación (nuevo):** cuando dos imágenes se relacionan directamente (ej. un antes/después), se muestran en una grilla de 2 columnas dentro de `container-content`, cada una con su propio caption individual; un caption de grupo opcional puede ubicarse por encima de ambas si la relación entre ellas no es evidente solo con los captions individuales.

---

## 9. Etiquetas (Badges)

Ya definidos en DS-001 §9.11 (Estable/Draft/Deprecado/Beta). Se agrega la variante de prioridad:

| Variante | Color | Uso |
|---|---|---|
| Estable | `color-success` | Estado de documento |
| Draft | `color-warning` | Estado de documento |
| Deprecado | `color-danger` | Estado de documento |
| Beta | `color-secondary` | Estado de documento (funcionalidad o contenido en prueba) |
| **Prioridad Alta** *(nuevo)* | `color-danger` | Playbooks, tareas de ADR — reutiliza el color de mayor urgencia ya existente, sin introducir un color nuevo |
| **Prioridad Media** *(nuevo)* | `color-warning` | Ídem |
| **Prioridad Baja** *(nuevo)* | `color-info` | Ídem |

**Prioridades como concepto visual:** cuando un Badge de estado y uno de prioridad coexisten en el mismo contexto (ej. una tarjeta de Playbook), el de estado se posiciona primero (izquierda) — el estado de un documento (¿es confiable?) siempre antecede a su prioridad (¿qué tan urgente es?) en el orden de lectura.

**Uso:** nunca interactivos (a diferencia de los Chips, sección 10) — un Badge no se clickea, solo informa.

---

## 10. Chips

**Función:** a diferencia de un Badge, un Chip siempre es interactivo — funciona como filtro, enlace o selector.

| Variante | Caso de uso | Comportamiento |
|---|---|---|
| Chip de filtro (toggle) | Filtros de Estado en Categoría | Alterna entre activo/inactivo, no navega |
| Chip de etiqueta | Etiquetas de documento/categoría | Navega a una búsqueda filtrada por esa etiqueta |
| Chip de acceso rápido | Home — Accesos rápidos | Navega directo a un documento específico |
| Chip de categoría relacionada | Categoría — Navegación relacionada | Navega a otra Category Index |

**Agrupaciones:** los chips de una misma familia siempre se presentan en una fila con salto de línea libre (`wrap`), nunca en scroll horizontal forzado — permite que el usuario vea el conjunto completo de opciones disponibles sin un gesto adicional (mismo criterio ya aplicado a las Estadísticas de Categoría en mobile, Responsive §5).

---

## 11. Botones

Primario, Secundario, Ghost y Danger ya definidos en DS-001 §9.6, con tamaños sm/md/lg. Dos aclaraciones formalizadas aquí:

**"Terciario" = Ghost:** no se introduce una quinta variante — el nivel de énfasis más bajo del sistema ya existe bajo el nombre `ghost` (texto sin fondo ni borde). "Terciario" y "Ghost" son dos nombres para el mismo nivel de jerarquía visual en distintas convenciones de la industria; este catálogo usa `ghost` de forma exclusiva para evitar ambigüedad.

**Icon Button (formalizado):** variante cuadrada del botón, sin texto, un ícono centrado — ya usado de forma implícita en varios lugares (Acciones rápidas del Header, Toggle de Sidebar, botón de copiar código) pero nunca definido como entrada propia del catálogo hasta ahora. Alturas idénticas a las ya definidas para botones de texto (32/40/48px), con ancho igual a la altura (cuadrado). Las cuatro variantes semánticas (primario/secundario/ghost/danger) aplican igual que en un botón con texto. Todo Icon Button lleva un Tooltip obligatorio (sección 13) — sin texto visible, el tooltip es la única forma de que su propósito sea claro.

**Estados:** default → hover → pressed (aclarado en Fase 6 §8) → focus-visible → disabled — sin variación entre las cinco variantes de botón (incluyendo Icon Button).

---

## 12. Inputs

Solo el campo de búsqueda (DS-001 §9.17) y el patrón general de input de texto tenían definición previa. Se formalizan aquí los controles de formulario restantes, reservados para usos actuales (Selectores, en Filtros) y futuros (Checkbox, Radio, Switch, sin un caso de uso activo en las plantillas ya definidas, pero parte del catálogo para cuando se necesiten):

| Control | Apariencia | Uso actual / previsto |
|---|---|---|
| **Selector (Select/Dropdown)** | Igual altura que un input de texto (40px), ícono `chevron-down` a la derecha, despliega una lista con el mismo tratamiento visual que el Sidebar/menús (DS-001 §10) | Filtros de Categoría (Tipo, Autor, Fecha — sección Sistema de Filtros); Selector de integrante |
| **Checkbox** | Cuadrado de 16px, borde `color-border-strong`, relleno `color-primary` + check blanco al marcar | Ya usado dentro de listas de tareas (DS-001 §9.16); reservado como control de formulario independiente para casos futuros (ej. la hoja de Filtros de mobile, Responsive §5, si se decide usar checkboxes en vez de chips dentro de ese panel) |
| **Radio Button** | Círculo de 16px, punto interior en `color-primary` cuando está seleccionado | Sin caso de uso activo en las plantillas actuales — reservado para una futura necesidad de selección única entre opciones mutuamente excluyentes (ej. un componente interactivo de Academy) |
| **Switch** | Píldora de 36×20px, círculo deslizante, fondo `color-border-strong` (apagado) o `color-primary` (encendido) | Reservado para preferencias persistentes de usuario que no sean el tema (ya resuelto como Icon Button, sección 11) — ej. una futura preferencia de "mostrar siempre la numeración de líneas" |

**Nota sobre Radio y Switch:** se documentan por completitud del catálogo, no porque una plantilla ya aprobada los requiera — su inclusión aquí evita que, cuando surja la necesidad real, alguien invente un tratamiento visual aislado en vez de usar el ya definido.

---

## 13. Tooltips

Ya definidos en DS-001 §9.19. Consolidado:

- **Cuándo utilizarlos:** cualquier elemento cuyo propósito no sea evidente solo con su apariencia visual — todo Icon Button (sección 11), badges con significado no obvio, texto truncado (ej. un breadcrumb colapsado).
- **Contenido:** texto corto, máximo 240px de ancho, nunca truncado con "..." — si el contenido no cabe en ese ancho, se reformula más corto, no se corta.
- **Posicionamiento:** por defecto aparece por encima del elemento que lo activa; si no hay espacio suficiente cerca del borde superior del viewport, se invierte automáticamente hacia abajo — nunca se posiciona de forma que quede parcialmente fuera de la pantalla.
- **Accesibilidad:** aparece tanto al hover (400ms de espera) como al recibir foco por teclado (inmediato) — nunca exclusivamente por hover, ya remarcado en Fase 6 §11.

---

## 14. Modales

Comportamiento base, tamaños (sm/md/lg) y la variante de hoja inferior para mobile ya están definidos (DS-001 §9.18, Responsive §5). Se agrega el uso de confirmación, sin caso activo todavía pero parte del catálogo:

**Apertura/cierre:** ya definidos — overlay + foco atrapado dentro del modal; cierre por botón "X", tecla `Esc`, o click en el overlay (excepto en la hoja inferior de Filtros, donde el cierre está condicionado a la acción "Aplicar", Fase 6 §10).

**Tamaños:** `sm` (400px, confirmaciones) · `md` (640px, Buscador global) · `lg` (960px, visor de diagramas ampliados, sección 7) — sin cambios respecto a DS-001 §9.18.

**Confirmaciones (formalizado):** el tamaño `sm` está reservado específicamente para acciones con consecuencia real, si en el futuro el Handbook incorpora alguna (el catálogo actual de plantillas es de solo lectura, sin acciones destructivas) — estructura de dos botones en el pie: `ghost` ("Cancelar") y `danger` o `primary` según la severidad ("Confirmar"), nunca solo un botón.

**Casos de uso:** Buscador global (`md`), diagramas ampliados (`lg`), hoja de Filtros en mobile (variante especial, Responsive §5), confirmaciones futuras (`sm`, reservado).

---

## 15. Acordeones

Mencionado de forma dispersa en DS-001 §9 (nota final), FAQ (§9.9) y TOC mobile (Responsive §4). Se consolida como entrada formal única:

- **Expansión/colapso:** cabecera clicable con ícono `chevron-right` que rota 90° al expandir (mismo lenguaje visual que las ramas del Sidebar, Documento §2 — reutilización deliberada del mismo patrón de "esto se puede desplegar").
- **Animación esperada:** `motion-base` (200ms), altura animada del contenido revelado — ya definida en DS-001 §13.1.
- **Casos de uso:** FAQ (un ítem abierto a la vez por defecto, comportamiento especial ya documentado en DS-001 §9.9), TOC en mobile/tablet (Responsive §4), grupo "+ más filtros" en la Página de Categoría (Categoría §3).

---

## 16. Tabs

Mencionado brevemente en DS-001 §9 sin desarrollo. Se formaliza aquí:

- **Navegación horizontal:** fila de etiquetas de pestaña, la activa marcada con un subrayado de 2px en `color-primary` y texto en `color-primary`; las inactivas en `text-secondary`.
- **Estados:** default → hover (texto a `text-primary`) → active (subrayado + `color-primary`) → focus-visible (anillo de foco además del subrayado si coincide).
- **Responsive:** si la fila de pestañas excede el ancho disponible, scroll horizontal propio con el mismo efecto de sombra lateral ya usado en tablas anchas (sección 6) — nunca se ocultan pestañas ni se comprimen sus etiquetas.
- **Casos de uso:** comandos específicos por sistema operativo (Windows/Mac/Linux, ejemplo original de DS-001 §9), selector de lenguaje dentro de un bloque de código (sección 5).

---

## 17. Timeline

Ya definido en DS-001 §9.8. Consolidado:

- **Orientación:** exclusivamente vertical en todo el sistema — se evaluó una variante horizontal para el Roadmap específicamente, pero se descarta a favor de un único patrón de Timeline, consistente con el principio de Simplicidad (Fase 6 §1): dos orientaciones del mismo componente obligarían a decidir caso por caso cuál usar, sin un criterio claro.
- **Uso:** Roadmap, historial de decisiones (ADR Index), Changelog global.
- **Relación con Roadmaps:** es el componente que estructura visualmente la página de Roadmap completa — cada hito es una entrada de Timeline con su fecha, título y estado (completado/pendiente/en progreso, mismos colores semánticos ya definidos en DS-001 §9.8).

---

## 18. Checklists

DS-001 §9.16 ya define la lista de tareas estática (`- [ ]` de Markdown, sin seguimiento). Se agrega aquí una variante con estado, necesaria específicamente para Playbooks:

**Checklist con progreso (nuevo):** cuando una lista de tareas vive dentro de un documento de tipo `playbook` (campo `type`, Categoría — Notas de diseño), se muestra con una barra de progreso delgada (2px, relleno `color-primary`) y un contador "X de Y completados" encima de la lista. A diferencia de cualquier otro componente del catálogo, **este es interactivo y con estado persistente**: marcar una casilla se guarda localmente en el navegador del usuario (sin sincronización a un servidor, coherente con la arquitectura sin backend de ARC-001 §1) y persiste entre visitas a esa misma página desde el mismo dispositivo.

**Por qué se señala como un caso distinto:** todo el resto del sistema de componentes es puramente presentacional — no guarda nada sobre el usuario. Este es el primer y único componente del catálogo con estado personal persistente, y el equipo de Frontend debe tratarlo con esa consideración adicional (no es solo un componente visual, requiere una decisión de almacenamiento del lado del cliente).

**Validación:** al alcanzar el 100% de casillas marcadas, la barra de progreso cambia a `color-success` como confirmación visual de cierre del playbook — sin ningún otro cambio de comportamiento (no bloquea, no navega automáticamente).

---

## 19. Componentes Especiales del Handbook

**Architecture Decision Record (ADR):** se renderiza usando la plantilla `ADRCard` dentro del Encabezado del Documento (Documento §4), con un campo de Estado propio de tres valores — distinto del Badge de estado general de documento (Estable/Draft/Deprecado): **Propuesta** (`color-info`), **Aceptada** (`color-success`), **Reemplazada** (`color-warning`, con un enlace obligatorio al ADR que la reemplaza). El cuerpo del documento sigue la estructura fija ya definida en STD-001 §12.1 (Contexto, Opciones consideradas, Decisión, Consecuencias), cada campo como una subsección `H3` estándar — no requiere componentes adicionales más allá de los ya catalogados.

**Playbooks:** estructura de contenido obligatoria, ya anticipada en ARC-001 §16 y formalizada aquí: un Callout de tipo Nota al inicio ("Cuándo usar este playbook"), seguido de una sección de Pasos que usa el Checklist con progreso (sección 18), y cerrado con una sección "Rollback" — mismo patrón en todo playbook del Handbook, sin variación libre por autor.

**Best Practices / Quick Tips:** no son componentes nuevos — son el Callout variante Tip (sección 4) con distinto texto de encabezado ("Buena práctica" o "Tip rápido" según el contexto editorial). Documentarlos aquí como entrada separada sería duplicar el catálogo; se aclara explícitamente para que ningún desarrollador construya un componente nuevo para esto.

**References (Referencias):** bloque simple al final de un documento técnico, encabezado `text-h4` "Referencias" precedido de un borde superior 1px `color-border`, seguido de una lista numerada (componente List ya catalogado, DS-001 §9.16) de enlaces externos o cruzados — no es un componente nuevo, es un patrón de uso del componente Lista ya existente.

**Version Badge:** el texto "v[número]" ya definido en el Encabezado del Documento (Documento §4) y en la Card de documento (Categoría §4) — no es un Badge en el sentido del componente de la sección 9 (no usa color semántico), es texto plano `text-caption`.

**Document Status:** es el Badge de estado ya definido en la sección 9 — Estable/Draft/Deprecado, presente en Encabezado del Documento, Card de documento y como indicador discreto en el Sidebar.

**Reading Time:** dato derivado en build time (no manual, Categoría — Notas de diseño), mostrado con ícono `clock` en la Card de documento (Categoría §4).

**Last Update:** fecha, mostrada en formato absoluto en el Encabezado del Documento (precisión para trazabilidad) y en formato relativo en la Card de documento (escaneabilidad en grilla) — misma decisión ya justificada en Categoría §4.

---

## 20. Reglas de Consistencia

- Ningún componente de este catálogo usa un color fuera de los tokens de DS-001 §4 — incluyendo los componentes nuevos de esta fase (Badge de Prioridad, Selector, Checkbox, Radio, Switch), que reutilizan exclusivamente los cuatro colores semánticos ya existentes.
- Todo componente interactivo implementa el conjunto completo de estados de la matriz de Fase 6 §8 (hover, focus, pressed, disabled cuando aplique) — un componente que solo defina hover sin focus no cumple el catálogo.
- La distinción Badge (no interactivo) vs. Chip (interactivo) se respeta sin excepción — ningún componente nuevo combina ambos comportamientos en un mismo elemento.
- Todo ícono usado en cualquier componente de este catálogo proviene de Lucide, en uno de los cuatro tamaños ya definidos (DS-001 §6.2) — ninguna entrada de esta fase introduce un tamaño de ícono nuevo.
- El único componente con estado personal persistente es el Checklist con progreso (sección 18) — cualquier futuro componente que considere guardar información del usuario debe evaluarse con el mismo nivel de atención antes de aprobarse, no darse por sentado como "solo otro componente más".

---

## 21. Recomendaciones Finales

- **Antes de crear un componente nuevo, se verifica si una variante de uno ya existente lo resuelve** — la mayoría de las entradas nuevas de esta fase (Icon Button, Badge de Prioridad, Selector de lenguaje) fueron exactamente eso: variantes de componentes ya catalogados, no invenciones desde cero.
- **Todo componente se prueba de forma aislada antes de integrarse a una plantilla** — un componente que solo se ve bien dentro del contexto específico donde se lo diseñó probablemente tiene dependencias ocultas de esa página, lo que compromete su reutilización futura.
- **Este documento y DS-001 se mantienen sincronizados**, no como dos fuentes de verdad paralelas — la intención declarada es que las extensiones registradas aquí se incorporen formalmente a DS-001 en su próxima revisión mayor (ver registro final), momento en el cual esta fase de PV-001 pasa a ser un documento histórico de referencia, no la fuente activa.
- **El crecimiento del catálogo es una señal a vigilar, no un objetivo:** un sistema de componentes saludable crece lentamente después de su fase inicial de diseño — si el Handbook empieza a necesitar componentes nuevos con frecuencia una vez esté implementado, es más probable que sea una señal de que un patrón de contenido no anticipado se volvió común, que una falla del catálogo en sí.

---

## Anexo — Registro Consolidado de Extensiones a DS-001

Todas las extensiones señaladas como "pendientes de ratificación" a lo largo de las fases de PV-001 (Home, Documento, Categoría, Responsive, Navegación e Interacciones) más las introducidas en esta fase, en un solo lugar — para que la revisión formal de DS-001 se resuelva en una sola pasada en vez de siete dispersas.

| # | Extensión | Afecta a | Introducida en |
|---|---|---|---|
| 1 | Sidebar en Home mostrado colapsado a íconos (no ausente) | ARC-001 §14, DS-001 §5/§10 | Home |
| 2 | Selector de integrante (Perfil no autenticado) | DS-001 §9 (nuevo componente) | Home |
| 3 | Curaduría de 5 Tarjetas principales en Home, no las 8 categorías completas | ARC-001 (decisión de IA, no de componente) | Home |
| 4 | Footer condensado de la Página de Documento (variante de 3 elementos) | DS-001 §9.3 | Documento |
| 5 | Campos de frontmatter: `code`, `version`, `reviewers` | ARC-001 §14 | Documento |
| 6 | Toggle de colapso de Sidebar en el Header | DS-001 §9 (nuevo componente) | Documento |
| 7 | TOC con colapso progresivo de H3 (solo la sección activa expandida) | DS-001 §13 | Documento |
| 8 | Componente Quote/Cita (blockquote) | DS-001 §9 (nuevo componente) | Documento |
| 9 | Callout — quinta variante neutral "Ejemplo" | DS-001 §9.15 | Documento |
| 10 | Campo de frontmatter: `type` (manual/guía/referencia/playbook/adr) | ARC-001 §14 | Categoría |
| 11 | Componente `FilterBar` de faceta múltiple | DS-001 §9 (nuevo componente) | Categoría |
| 12 | Modal — variante de hoja inferior a pantalla completa (mobile) | DS-001 §9.18 | Responsive |
| 13 | Tabla — columna fija (sticky) para tablas de referencia técnica | DS-001 §9.7 | Responsive |
| 14 | Regla de espaciado responsive ("un escalón menos" en mobile para separaciones de página) | DS-001 §7 | Responsive |
| 15 | Botón "Volver arriba" | DS-001 §9 (nuevo componente) | Navegación e Interacciones |
| 16 | Búsquedas recientes dentro del Buscador global | DS-001 §9.12 | Navegación e Interacciones |
| 17 | Selector de lenguaje en Bloques de código (multi-idioma) | DS-001 §9.14 | Esta fase |
| 18 | Columna destacada en tablas comparativas | DS-001 §9.7 | Esta fase |
| 19 | "Click para ampliar" en Diagramas (abre Modal `lg`) | DS-001 §9 | Esta fase |
| 20 | Icon Button como variante formal de Botón | DS-001 §9.6 | Esta fase |
| 21 | Inputs de formulario: Selector, Checkbox, Radio, Switch | DS-001 §9 (4 componentes nuevos, sin caso de uso activo salvo Selector) | Esta fase |
| 22 | Badge de Prioridad (Alta/Media/Baja) | DS-001 §9.11 | Esta fase |
| 23 | ADRCard con Estado de tres valores (Propuesta/Aceptada/Reemplazada) | DS-001 §9.15 | Esta fase |
| 24 | Estructura de contenido obligatoria para Playbooks | ARC-001 §16 (ya anticipado, ahora formalizado) | Esta fase |
| 25 | Checklist con progreso y estado persistente (único componente con estado personal) | DS-001 §9.16 | Esta fase |

**Siguiente paso recomendado:** esta tabla, no las notas dispersas de cada fase individual, debería ser el insumo que se lleve al Comité Técnico y al Design System Architect para una única sesión de ratificación, antes de iniciar cualquier implementación en código.


---

# Parte 8 — Animaciones (Tabla de Referencia)

Únicamente recomendaciones de uso sobre los tokens de duración y easing ya definidos en DS-001 §13 — ningún valor nuevo se introduce aquí.

| Interacción | Token de duración | Justificación |
|---|---|---|
| Expansión/colapso de rama en Sidebar | `motion-base` (200ms) | Suficientemente perceptible para comunicar jerarquía revelada, sin sentirse lento en un componente de uso muy frecuente. |
| Apertura del modal de Buscador | `motion-slow` (300ms) en la entrada, `motion-base` en la salida | La entrada necesita sentirse "sólida" (es una superposición completa de foco); la salida puede ser más rápida porque el usuario ya decidió irse. |
| Apertura del Drawer mobile (Sidebar) | `motion-slow` (300ms), deslizamiento desde el borde izquierdo | Mismo criterio que el modal — es una superposición completa en mobile. |
| Hover de Cards | `motion-fast` (120ms) | Cambios de borde/sombra deben sentirse instantáneos, no como una transición "animada" perceptible. |
| Toggle de tema (ícono sol/luna) | `motion-fast` (120ms), crossfade | Es el único elemento que anima durante el cambio de tema (Parte 5, Dark Mode) — su animación comunica que *algo* cambió, mientras el resto del layout cambia sin transición. |
| Accordion (TOC mobile, FAQ) | `motion-base` (200ms), altura animada + rotación del ícono chevron 180° | Ya definido como patrón base en DS-001 §9 (nota final). |
| Copiar código (confirmación) | `motion-fast` (120ms) para el crossfade entre ícono de copiar y check | Debe sentirse inmediato — es una confirmación de una acción que el usuario ya completó, no un proceso en curso. |

Se recuerda, sin repetir el detalle ya fijado en DS-001 §13.2: ninguna de estas animaciones se ejecuta si el sistema indica `prefers-reduced-motion: reduce`.

---


---

# Parte 9 — Consistencia Visual

La consistencia entre páginas futuras no depende de que cada autor "recuerde" las medidas de esta especificación — depende de que ninguna página nueva pueda construirse sin pasar por los componentes ya definidos:

- Toda página nueva es, sin excepción, una instancia de una de las plantillas de WF-001 §3.2. No existe una cuarta composición posible fuera de Home, Category Index, Document Page (y sus variantes ADR/Changelog), y 404.
- Ninguna medida de esta especificación (anchos, alturas, espaciados) se redefine por página individual. Si una página necesita algo que esta especificación no cubre, la respuesta correcta es actualizar PV-001 (vía el proceso de gobernanza de DS-001 §16), no improvisar un valor puntual.
- Los tres bloques de contenido "curado" que aparecen en Home (Accesos rápidos, Manuales destacados, Últimas actualizaciones) son los únicos elementos de la plantilla Home que requieren mantenimiento editorial manual — todo lo demás (Categorías, Sidebar) se deriva automáticamente del sitemap y el frontmatter, sin intervención manual, lo que reduce el riesgo de que la página quede visualmente desactualizada.

---


---

# Parte 10 — Preparación para la Implementación

| Campo | Valor |
|---|---|
| Documento | PV-001 — Fase Final: Preparación para la Implementación |
| Versión | 1.0 |
| Estado de esta fase | Borrador para revisión — cierra oficialmente PV-001 |
| No modifica | Fases 1–7 (Introducción y Filosofía Visual, Home, Página de Documento, Página de Categoría, Responsive Design, Sistema de Navegación e Interacciones, Sistema de Componentes Visuales) |

---

## Notas de cierre

Tres puntos deben quedar explícitos antes de declarar PV-001 cerrado, porque afectan directamente la ficha de estado de la sección 10:

**Dark Mode no recibió una fase dedicada.** El comportamiento de tema oscuro tiene una especificación base (definida en el primer borrador consolidado de PV-001, antes de la descomposición en fases) que nunca fue revisitada con el mismo nivel de detalle que Home, Documento o Categoría recibieron individualmente. No se desarrolla retroactivamente aquí, porque esta Fase Final no fue convocada para eso — se deja registrado como un vacío conocido, no como un olvido silencioso, y se incorpora como riesgo en la sección 7.

**Internacionalización sigue siendo una Pregunta Abierta sin resolver.** WF-001 §15 ya había dejado explícitamente pendiente "¿se traducirá el Handbook a otro idioma?". Esta fase no la responde — la sección 4 (Escalabilidad) da únicamente una guía preparatoria condicional, no una decisión.

**El Estado "Aprobado para Implementación" de la sección 10 se entrega con una condición explícita**, no de forma incondicional — el Anexo de la Fase 7 registra 25 extensiones a DS-001 todavía sin ratificación formal. Se detalla en la sección 10.

---

## 1. Objetivo de esta fase

Esta fase no agrega diseño nuevo — conecta lo ya diseñado (Fases 1–7) con el trabajo de implementación que sigue. Su función es doble: (a) traducir las decisiones visuales y de interacción ya tomadas en información que un equipo de Frontend pueda usar para planificar su propia arquitectura de código, sin que eso implique escribir esa arquitectura por ellos; y (b) declarar formalmente el cierre de PV-001 como documento de diseño, dejando registrado qué debe ser verdad para que la implementación pueda comenzar con confianza.

**Alcance:** accesibilidad final, principios de microinteracción, lineamientos de escalabilidad a largo plazo, mapeo conceptual hacia una arquitectura React (sin código), un checklist de verificación, riesgos de implementación, criterios de aprobación y la ficha de cierre. **No** incluye ninguna medida, token o composición visual nueva — todo lo que se referencia aquí ya fue decidido en una fase anterior.

**Esta fase concluye PV-001.** No se planifican fases adicionales de diseño visual después de esta; cualquier necesidad de diseño que surja durante la implementación se gestiona como una revisión versionada de este documento o como un ADR (ver sección 9).

---

## 2. Accesibilidad

Cierre del compromiso de accesibilidad distribuido en fases anteriores (DS-001 §12, Fase de Documento §8, Fase 6 §11), presentado aquí como una matriz única de trazabilidad contra WCAG 2.2 AA — el formato que un equipo de Frontend necesita para auditar, no una repetición de cada regla.

| Criterio WCAG 2.2 AA | Cómo lo cumple el sistema | Dónde se definió |
|---|---|---|
| 1.4.3 Contraste mínimo | Todos los pares de color (texto/fondo) verificados en 4.5:1 (texto normal) y 3:1 (texto grande/UI), en ambos temas | DS-001 §4.1 |
| 1.4.10 Reflow | Ningún breakpoint introduce scroll horizontal de página completa; solo componentes específicos (tablas, código, tabs) lo tienen de forma contenida | Responsive §8–9 |
| 1.4.12 Espaciado de texto | `line-height` 1.7 en cuerpo de texto, escala de espaciado por tokens, nunca valores ajustados a mano | DS-001 §5, §7 |
| 2.1.1 Accesible por teclado | El 100% de la interfaz es operable sin mouse; orden de tabulación canónico definido una sola vez y heredado por las tres plantillas | Fase 6 §11 |
| 2.4.3 Orden de foco | El foco sigue siempre el orden visual de lectura, sin excepciones por plantilla | Fase 6 §11 |
| 2.4.6 Encabezados y etiquetas | Ningún documento salta un nivel de heading; todo control interactivo tiene una etiqueta accesible (texto visible o Tooltip obligatorio en Icon Buttons) | DS-001 §5.3, Fase 7 §11 |
| 2.4.7 Foco visible | Anillo de 2px en `color-primary`, 2px de separación, aplicado sin excepción a los 25+ componentes del catálogo | DS-001 §12 |
| **2.4.11 Foco no obstruido** *(cierre nuevo)* | El Header y el TOC son `sticky`; cualquier scroll disparado por navegación de teclado (no solo por click en el TOC) aplica el mismo offset de `space-6` ya definido para clicks del TOC, para que un elemento recién enfocado nunca quede oculto detrás del Header fijo | Extiende Fase 6 §5, cierre en esta fase |
| 2.5.7 Movimientos de arrastre | El cierre por gesto del Drawer (Fase 6 §10) siempre tiene una alternativa sin arrastre (tap fuera, botón, `Esc`) | Fase 6 §10 |
| 2.5.8 Tamaño mínimo de objetivo | 24×24px en cualquier elemento interactivo, en cualquier breakpoint | DS-001 §12 |
| 3.2.3 Navegación consistente | Los cinco planos de navegación y los componentes del catálogo se comportan idénticamente en cualquier plantilla | WF-001 §5, Fase 6 §1 |
| 4.1.2 Nombre, rol, valor | Landmarks semánticos, `aria-current` en navegación activa, `aria-expanded` en ramas colapsables del Sidebar — a nivel conceptual, sin implementación | Fase 6 §11 |

**Contenido legible:** columna de lectura acotada a 760px, jerarquía tipográfica fija en cualquier breakpoint (Responsive §7), ningún tamaño de texto por debajo de 13px en todo el sistema.

**Componentes accesibles:** todo componente interactivo del catálogo de Fase 7 implementa, sin excepción, el conjunto completo de estados de la matriz de Fase 6 §8 — un componente que solo defina `hover` sin `focus-visible` no es una implementación válida de este sistema.

---

## 3. Microinteracciones

Cierre de lo ya definido en DS-001 §13 y Fase 6 §8–9. Se agrega aquí el criterio general de uso que hasta ahora solo existía aplicado caso por caso.

**Cuándo deben utilizarse:** exclusivamente para comunicar un cambio de estado real (algo pasó, algo está pasando, algo va a pasar) — nunca por razones decorativas. Toda microinteracción debe poder responder la pregunta "¿qué le estoy confirmando al usuario?"; si no hay respuesta clara, no se implementa.

**Cuándo deben evitarse:** cuando el cambio visual ya es autoexplicativo sin necesidad de refuerzo adicional (un Badge que cambia de color ya comunica su punto, no necesita además un destello); cuando retrasarían la disponibilidad percibida del contenido (ninguna animación de entrada de página, DS-001 §13.2); cuando el sistema operativo indica `prefers-reduced-motion` (se desactivan sin excepción); cuando duplicarían una señal que otro componente ya está dando en simultáneo.

| Elemento | Definición de cierre |
|---|---|
| Hover / Focus / Pressed | Matriz completa ya cerrada en Fase 6 §8 — sin cambios. |
| Loading | Skeleton loader (no spinner) para cualquier contenido que dependa de carga diferida — patrón único del sistema, no varía por componente. |
| Skeleton Screens | Generalización del patrón ya usado para el índice de búsqueda (DS-001 §11): bloques grises sin texto, con la misma altura que el contenido esperado, para que el layout no salte cuando el contenido real aparece. |
| Tooltips | Ya cerrados en Fase 7 §13 — sin cambios. |
| Mensajes de éxito | Confirmación momentánea (`motion-fast`), nunca un banner persistente — copiar código, envío del widget de feedback. |
| Mensajes de error | Alerta persistente si la condición persiste (documento deprecado); mensaje puntual y transitorio si es un fallo momentáneo (no se pudo copiar). |
| Animaciones suaves | Tokens de duración/easing ya cerrados en DS-001 §13.1 — ninguna animación de este sistema usa un valor de tiempo fuera de esos tres tokens. |
| Feedback visual (principio de cierre) | Toda acción iniciada por el usuario produce una respuesta visible dentro de `motion-fast` (120ms) — no existe ninguna acción "silenciosa" en el sistema completo. |

---

## 4. Escalabilidad

Consolidación final de lo ya distribuido en ARC-001, DS-001 §15–16 y Fase 7 §20–21, más los ángulos que no habían sido cubiertos todavía.

- **Nuevas categorías:** siguen el proceso de decisión de alto impacto ya vigente (STD-001 §11) — sin cambios respecto a lo ya establecido.
- **Nuevos documentos:** cualquier integrante puede agregarlos vía PR dentro de una categoría existente, sin proceso especial — sin cambios respecto a ARC-001 §14.
- **Versionado del Handbook (cierre):** el número de versión global del Handbook (visible en el Footer, DS-001 §9.3) sigue el mismo esquema `MAJOR.MINOR` ya definido para DS-001 (§16) — `MINOR` para adiciones de contenido sin romper estructura, `MAJOR` para cambios que alteren la navegación o el sistema visual de forma perceptible para el usuario. No se introduce un esquema de versionado distinto solo porque ahora se aplica al conjunto del Handbook en vez de al Design System.
- **Internacionalización:** sigue siendo una Pregunta Abierta sin resolver (WF-001 §15). Guía preparatoria, condicional a que esa pregunta se resuelva afirmativamente en el futuro: de decidirse, la recomendación es un prefijo de ruta por locale (ej. `/es/`, `/en/`) sin alterar la estructura de categorías ya definida en ARC-001 — no es una decisión tomada en este documento, solo una nota para no cerrar esa puerta arquitectónicamente si el equipo la abre más adelante.
- **Nuevos componentes:** siguen el proceso de gobernanza ya cerrado en Fase 7 §21 — extender antes que crear, y pasar por DS-001 §16 antes de considerarse parte del catálogo oficial.
- **Expansión del menú:** el Sidebar tiene un límite estructural de tres niveles (Documento §2) que no cambia con el volumen de contenido — el crecimiento se absorbe en cantidad de documentos por rama, no en profundidad de anidación, tal como ya se estableció.
- **Mantenimiento:** ligado a la cadencia de revisión mensual ya vigente (STD-001 §6), que ahora incluye auditar tanto la documentación de contenido como el propio catálogo de componentes (Fase 7 §21) contra lo realmente implementado.
- **Compatibilidad futura:** el sistema asume navegadores modernos evergreen (sin soporte a versiones legacy) — coherente con el contexto de un equipo interno de cuatro integrantes usando su propio stack (React, Vite, Tailwind) sin restricciones de audiencia externa que justifiquen soporte extendido.

---

## 5. Preparación para React

Mapeo conceptual, sin código, de cómo esta especificación se traduce en categorías de arquitectura de aplicación.

| Categoría conceptual | Qué contiene | Ejemplos |
|---|---|---|
| **Layouts** | Tres, uno por plantilla — cada uno envuelve el chrome persistente de esa plantilla (Header + variante de Sidebar + variante de Footer) y expone un espacio de contenido | `HomeLayout`, `DocumentLayout`, `CategoryLayout` |
| **Pages** | Capa delgada de enrutamiento — recibe el contenido y frontmatter ya parseados de un documento MDX y los entrega al Layout correspondiente según su `category`/`type`; no contiene lógica visual propia | Una página por documento del Handbook, resuelta dinámicamente por ruta |
| **Components** | El catálogo completo de la Fase 7 — Cards, Badges, Chips, Callouts, Tabs, Timeline, etc. | Los 25+ componentes ya catalogados |

**Qué información provendrá de Markdown:** todo el contenido de cada página (prosa, headings, listas, tablas, código) y todo su frontmatter (`title`, `category`, `order`, `status`, `owner`, `last_updated`, `tags`, `code`, `version`, `reviewers`, `type`) — ninguna Page, Layout o Component contiene texto de contenido hardcodeado; su única fuente es el archivo MDX correspondiente.

**Qué partes deberán ser reutilizables:** por definición, todo el catálogo de la Fase 7 — es la razón de ser de esa fase. Ningún Layout ni Page implementa su propia versión de un componente ya catalogado.

**Cómo mantener una arquitectura limpia:** flujo de datos en una sola dirección — MDX + frontmatter → Page (solo enrutamiento) → Layout (solo estructura) → Components (solo presentación de un concepto). Ningún Component conoce el enrutamiento ni el estado global de la aplicación más allá de lo que recibe como entrada — es lo que permite que el mismo `Badge` funcione idéntico dentro de una Card, dentro del Encabezado de un Documento o dentro del Sidebar, sin tres implementaciones distintas.

---

## 6. Checklist de Implementación

| # | Elemento | Criterio de aceptación | Referencia |
|---|---|---|---|
| 1 | Home | Header, Sidebar colapsado, Hero, 5 Tarjetas principales, Accesos rápidos, Últimas actualizaciones y Footer completo presentes y con las medidas ya especificadas | Fase Home |
| 2 | Sidebar | Los tres estados (colapsado en Home, expandido en Documento/Categoría, Drawer en mobile) implementados con el límite estructural de 3 niveles respetado | Fase Documento §2, Responsive §6 |
| 3 | Header | Idéntico en las tres plantillas, con el Toggle de Sidebar presente en Documento/Categoría | Fase Home §1, Documento §1 |
| 4 | Breadcrumbs | Formato, truncado y navegación por nivel funcionando según la regla de longitud máxima cerrada en Fase 6 §4 | Fase 6 §4 |
| 5 | Tabla de contenidos | Sticky, scroll-spy, divulgación progresiva de H3 activa únicamente | Fase Documento §5 |
| 6 | Responsive | Los cuatro breakpoints oficiales verificados en sus límites exactos, no solo en anchos intermedios | Fase Responsive §2, §11 |
| 7 | Dark Mode | Comportamiento base verificado — ver limitación registrada en "Notas de cierre" de este documento | PV-001 base (Dark Mode) |
| 8 | Buscador | Global y local funcionando, con búsquedas recientes y estados vacío/sin resultados implementados | Fase 6 §6 |
| 9 | Cards | Las tres variantes (estándar, destacada, ADR Card) con jerarquía y estados consistentes | Fase 7 §2, §19 |
| 10 | Alertas | Las tres variantes semánticas (info/warning/danger) sin una variante "success" de página completa | Fase 7 §3 |
| 11 | Tablas | Scroll horizontal, columna fija en tablas de referencia, sin ocultamiento de columnas | Fase 7 §6 |
| 12 | Diagramas | Nuevos diagramas en Mermaid/SVG, ninguno en PNG salvo la deuda ya identificada de HB-001 | Fase 7 §7 |
| 13 | Código | Encabezado, numeración condicional, selector de lenguaje vía Tabs cuando aplique | Fase 7 §5 |
| 14 | Componentes | Catálogo completo de Fase 7 implementado sin componentes "fantasma" fuera de él | Fase 7 §21 |
| 15 | Navegación | Los cinco planos y las cinco rutas de flujo de usuario verificados en las tres plantillas | WF-001 §5–6 |
| 16 | Accesibilidad | Matriz de la sección 2 de este documento auditada por completo, no solo revisada parcialmente | Fase Final §2 |
| 17 | UX | Los flujos de usuario nuevo, retorno y cambio de categoría probados con usuarios reales del equipo, no solo revisados en el documento | WF-001 §6 |
| 18 | Performance | Presupuesto de carga inicial cumplido, índice de búsqueda diferido verificado | Responsive §10 |
| 19 | Escalabilidad | Probado con el documento más extenso real disponible (HB-001), no solo con contenido de prueba corto | WF-001 §11, Responsive §11 |
| 20 | Consistencia visual | Cero valores de color, tipografía o espaciado fuera de los tokens de DS-001 en toda la implementación | DS-001 §4–§8 |

---

## 7. Riesgos

| Riesgo | Recomendación para evitarlo |
|---|---|
| Inconsistencias visuales entre desarrolladores distintos | Ningún componente se construye sin revisar primero si ya existe en el catálogo de Fase 7 — el checklist de la sección 6, ítem 14, es el control de este riesgo. |
| Duplicación de componentes (dos implementaciones del mismo concepto) | Revisión de PR obligatoria que verifique explícitamente contra el catálogo antes de aprobar cualquier componente nuevo (mismo estándar de revisión ya exigido para código, STD-001 §9–10). |
| Pérdida de consistencia con el paso del tiempo | Auditoría mensual ya establecida (STD-001 §6, Fase 7 §21) — el riesgo no se elimina de una vez, se contiene con revisión recurrente. |
| Cambios de diseño sin documentación | Ningún cambio visual se implementa sin una actualización correspondiente de PV-001 o un ADR — regla reforzada en la sección 9 de este documento. |
| Desviación del Design System durante la implementación (atajos por presión de tiempo) | El checklist de la sección 6 es una condición de aceptación de PR, no una sugerencia — un PR que no lo cumple no se aprueba, sin excepción por plazo. |
| **Implementación iniciada antes de ratificar las extensiones pendientes** *(riesgo nuevo, específico de este cierre)* | El Anexo de la Fase 7 registra 25 extensiones a DS-001 sin ratificación formal. Implementar sobre una base parcialmente no ratificada obliga a retrabajo si el Comité Técnico rechaza alguna. Recomendación: resolver esa sesión de ratificación antes de escribir la primera línea de código, no en paralelo. |

---

## 8. Criterios de Aprobación

El Handbook se considera correctamente implementado cuando se cumplen, en conjunto, los siguientes criterios medibles:

1. **100% de los ítems del Checklist de Implementación (sección 6) verificados**, no solo revisados — cada uno con evidencia concreta (captura, prueba, o auditoría según corresponda).
2. **Cero extensiones pendientes de ratificación** del Anexo de la Fase 7 al momento del lanzamiento — todas resueltas como aceptadas, rechazadas o reemplazadas.
3. **Auditoría de accesibilidad completa** contra la matriz de la sección 2, incluyendo una pasada manual de navegación por teclado de las tres plantillas, no solo una herramienta automatizada de contraste.
4. **Presupuesto de rendimiento cumplido** en la carga inicial de las tres plantillas, medido en condiciones reales, no solo en desarrollo local.
5. **Revisión visual página por página** por parte del Design System Architect, comparando la implementación contra PV-001 sección por sección — no una aprobación general de "se ve bien".
6. **Al menos un documento real de cada plantilla** (Home, un Documento largo tipo HB-001, una Categoría con múltiples documentos) probado de punta a punta antes de considerar el sistema listo para producción.

---

## 9. Conclusiones

PV-001 constituye la especificación visual oficial del THERS Engineering Handbook. Su propósito es servir como referencia para la implementación del Handbook utilizando React, Vite y Tailwind CSS, traduciendo cada decisión de arquitectura de información ya tomada en WF-001 y cada token del sistema de diseño ya definido en DS-001 en una composición visual completa, verificable y lista para desarrollo.

Ninguna modificación futura a lo aquí definido se realiza de forma informal. Todo cambio se canaliza mediante una nueva versión de este documento (siguiendo el esquema `MAJOR.MINOR` ya establecido) o mediante un Architecture Decision Record cuando el cambio afecte una decisión estructural — preservando la misma trazabilidad que el equipo ya exige para el código del producto THERS.

---

## 10. Estado del Documento

| Campo | Valor |
|---|---|
| Documento | PV-001 |
| Nombre | THERS Engineering Handbook Visual Prototype |
| Versión | 1.0 |
| Estado | Aprobado para Implementación |
| **Condición de vigencia** | Sujeto a que las 25 extensiones registradas en el Anexo de la Fase 7 se resuelvan formalmente (aceptadas, rechazadas o reemplazadas) antes del inicio del desarrollo — ver Riesgo específico en la sección 7. El estado "Aprobado" aplica al contenido de diseño; no exime de esa ratificación pendiente. |
| Tipo | Documento Oficial |
| Dependencias | HB-001 · STD-001 · ARC-001 · DS-001 · WF-001 |
| Uso | Referencia oficial para el desarrollo del Engineering Handbook |

---

*Fin de PV-001 — THERS Engineering Handbook Visual Prototype. Documento cerrado. No se ha generado código, imágenes ni mockups gráficos en ninguna de sus ocho fases.*
