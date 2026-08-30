# THERS Handbook Design System v1.0

**Estándar oficial y obligatorio para toda página nueva del THERS Engineering Handbook**

| Campo | Valor |
|---|---|
| Documento | Design System — Especificación Técnica (sin código) |
| Versión | 1.0 |
| Estado | Oficial — vinculante |
| Depende de | *Arquitectura UX del Handbook v0.1* (sitemap, navegación, arquitectura del portal) — **este documento no modifica ninguna de esas decisiones**, las formaliza a nivel de sistema visual |
| Elaborado por | Principal Product Designer · Senior UX Designer · Senior UI Designer · Design System Architect · Frontend Architect · Technical Writer · Especialista en Accesibilidad (WCAG 2.2 AA) · Especialista Bootstrap/Tailwind · Especialista en Documentación Técnica · Especialista en Developer Experience |
| Gobernanza | Ver sección 16 |

---

## Índice

1. [Introducción](#1-introducción)
2. [Principios de Diseño](#2-principios-de-diseño)
3. [Identidad Visual](#3-identidad-visual)
4. [Sistema de Colores](#4-sistema-de-colores)
5. [Tipografía](#5-tipografía)
6. [Iconografía](#6-iconografía)
7. [Espaciados](#7-espaciados)
8. [Grid](#8-grid)
9. [Componentes Oficiales](#9-componentes-oficiales)
10. [Navegación](#10-navegación)
11. [Responsive](#11-responsive)
12. [Accesibilidad](#12-accesibilidad)
13. [Animaciones](#13-animaciones)
14. [Convenciones](#14-convenciones)
15. [Escalabilidad](#15-escalabilidad)
16. [Gobernanza](#16-gobernanza)
17. [Checklist de cumplimiento](#17-checklist-de-cumplimiento)

---

## 1. Introducción

### 1.1 Objetivo del Design System

Este documento define el **sistema visual único y obligatorio** con el que debe construirse cualquier página, componente o extensión del THERS Engineering Handbook. Su propósito es que, sin importar quién escriba o desarrolle una página nueva, el resultado sea indistinguible en calidad y consistencia del resto del Handbook.

No es una guía de estilo opcional: es un **contrato de diseño**. Un Pull Request que introduce un color, espaciado, tipografía o componente fuera de este sistema no cumple el checklist de revisión (sección 17) y no debe aprobarse.

### 1.2 Alcance

Aplica a **todo el THERS Engineering Handbook**: las 8 categorías raíz definidas en el Sitemap (Organización, Estrategia, Arquitectura, Ingeniería, Academy, Playbooks, Roadmap, Meta) y cualquier categoría futura que se agregue siguiendo el proceso de la sección 15.

No aplica al producto THERS en sí (la app React/Flask que el equipo desarrolla como proyecto). Ambos sistemas pueden evolucionar de forma independiente; si en el futuro se decide unificarlos, eso es una decisión de gobernanza (sección 16), no una consecuencia automática de este documento.

### 1.3 Filosofía de diseño

El Handbook es una **herramienta de trabajo diario**, no un producto de marketing. Se usa bajo presión (buscando cómo revertir un commit a las 11pm) tanto como en momentos de aprendizaje pausado (onboarding de un nuevo integrante). El diseño debe servir a ambos modos de uso:

> **"Aburrido a propósito."** La interfaz no compite por atención con el contenido. Cada decisión visual existe para reducir el tiempo entre "tengo una pregunta" y "encontré la respuesta correcta". Inspirado en la claridad de GitHub Docs, la jerarquía de Stripe Docs, la organización de Microsoft Learn y la disciplina de tokens de Material Design — sin copiar ninguno de sus lenguajes visuales.

---

## 2. Principios de Diseño

| Principio | Significa en la práctica |
|---|---|
| **Claridad** | Cada página responde una pregunta identificable en su título. Ninguna decisión visual debe requerir explicación para entenderse. Si un componente necesita una leyenda para ser comprendido, el componente está mal diseñado. |
| **Consistencia** | Un mismo tipo de contenido (una advertencia, una tabla, un paso a paso) se ve y se comporta *exactamente igual* en cualquier parte del Handbook. La consistencia es lo que permite que un usuario recurrente navegue sin leer, solo reconociendo patrones. |
| **Simplicidad** | Se prefiere el componente más simple que resuelva el problema. Un componente nuevo solo se justifica si ninguno de los existentes (sección 9) puede adaptarse. |
| **Escalabilidad** | Todo patrón debe funcionar igual de bien con 12 páginas que con 1,200. Ninguna decisión de diseño puede depender del volumen actual de contenido (ver sección 15). |
| **Accesibilidad** | No es una capa final ni un checklist post-lanzamiento: es un requisito de diseño desde el primer boceto. Cumplimiento WCAG 2.2 AA como piso mínimo, no como aspiración (sección 12). |
| **Legibilidad** | El Handbook se lee, no se hojea como una landing page. Tipografía, longitud de línea, contraste y espaciado se optimizan para sesiones de lectura de 5 a 20 minutos, no para scroll rápido de 5 segundos. |
| **Mantenibilidad** | Todo valor visual (color, tamaño, espaciado) existe como **token**, nunca como valor suelto. Cambiar un token debe propagar el cambio a todo el sistema sin tocar página por página. |

---

## 3. Identidad Visual

### 3.1 Nombre oficial

El nombre oficial de la plataforma es **THERS Engineering Handbook**. En contextos de espacio reducido (tabs del navegador, breadcrumbs raíz, badges) se permite abreviar a **THERS Handbook**. No se permite "Handbook" a secas fuera de contexto, ni acrónimos adicionales no aprobados.

### 3.2 Uso del logo / wordmark

Mientras no exista un isotipo gráfico aprobado, la identidad visual del Handbook es un **wordmark tipográfico**: "THERS" en Inter Bold (peso 700), tracking neutro, acompañado opcionalmente del sufijo "Handbook" en Inter Regular de menor tamaño, alineado a la base del wordmark.

- **Espacio de seguridad**: margen mínimo alrededor del wordmark equivalente a la altura de la letra "T" del propio wordmark, libre de otros elementos (iconos, texto, bordes).
- **Tamaño mínimo digital**: 20px de altura de caja para el wordmark en el TopNav; nunca por debajo de eso en ninguna superficie digital.
- **Buenas prácticas**: usar siempre el color de texto primario (`--color-text-primary`) o blanco puro sobre superficies oscuras de marca; nunca sobre fondos con bajo contraste (< 4.5:1); nunca dentro de una tarjeta con otros logos de igual jerarquía visual.
- **Prohibido**: estirar, rotar, aplicar sombra o efectos 3D, recolorear con colores fuera de la paleta (sección 4), usar una fuente distinta a Inter para el wordmark.
- **Versionado del logo**: si en el futuro se introduce un isotipo gráfico, este pasa a ser un cambio de **Identidad Visual mayor** y sigue el proceso de gobernanza (sección 16), incluyendo actualización obligatoria de este documento a v2.0.

---

## 4. Sistema de Colores

Todo color se consume exclusivamente como **Design Token**, nunca como valor hexadecimal directo en un componente. Esta sección es la fuente de verdad de dichos tokens (formaliza y expande los valores ya introducidos en el documento de Arquitectura UX v0.1, sin modificarlos).

### 4.1 Tokens semánticos — Light / Dark

| Token | Rol | Light | Dark | Contraste sobre fondo (AA) |
|---|---|---|---|---|
| `color-primary` | Acento de marca, links, foco, estado activo | `#4F46E5` | `#818CF8` | ✅ 4.5:1+ sobre `color-bg` |
| `color-primary-hover` | Hover/press de elementos primarios | `#4338CA` | `#A5B4FC` | ✅ |
| `color-secondary` | Acento complementario (tags "Beta", enlaces secundarios, gráficos) | `#0D9488` | `#2DD4BF` | ✅ |
| `color-bg` | Fondo base de la aplicación | `#FFFFFF` | `#0F1115` | — |
| `color-surface` | Fondo de tarjetas, sidebar, modales | `#F7F8FA` | `#181B21` | — |
| `color-surface-raised` | Popovers, tooltips, dropdowns (por encima de `surface`) | `#FFFFFF` | `#20242C` | — |
| `color-border` | Bordes, separadores, líneas de tabla | `#E5E7EB` | `#2A2E37` | — |
| `color-border-strong` | Bordes con énfasis (inputs en foco, tarjetas seleccionadas) | `#C7CBD3` | `#3A3F4B` | — |
| `color-text-primary` | Texto de cuerpo y headings | `#1A1D23` | `#E6E8EB` | ✅ 4.5:1+ |
| `color-text-secondary` | Metadatos, captions, texto de apoyo | `#6B7280` | `#9CA3AF` | ✅ 4.5:1 sobre `bg`/`surface` |
| `color-text-disabled` | Texto/iconos deshabilitados | `#AEB2BB` | `#565B66` | — (no requiere AA: no es contenido activo) |
| `color-info` | Callouts/alertas informativas | `#0284C7` | `#38BDF8` | ✅ |
| `color-success` | Confirmaciones, badge "Estable" | `#16A34A` | `#4ADE80` | ✅ |
| `color-warning` | Advertencias, badge "Draft" | `#B45309` | `#FBBF24` | ✅ (nota: el tono light se oscurece respecto al de UI Arquitectura v0.1 para asegurar 4.5:1 sobre fondo blanco en texto) |
| `color-danger` | Errores, badge "Deprecado" | `#DC2626` | `#F87171` | ✅ |
| `color-code-bg` | Fondo de bloques de código | `#F4F4F5` | `#14161B` | — |
| `color-overlay` | Fondo de modales/backdrop | `rgba(15,17,21,0.5)` | `rgba(0,0,0,0.7)` | — |

### 4.2 Cuándo usar cada color

- **`primary`**: exclusivamente para acciones/enlaces principales y estado activo de navegación. Nunca se usa como color decorativo.
- **`secondary`**: refuerzo visual de baja frecuencia — un badge "Beta", un acento en un gráfico. Si `secondary` empieza a aparecer en más del 10% de una página, es señal de mal uso.
- **`info` / `success` / `warning` / `danger`**: exclusivamente semánticos. Nunca se usan por preferencia estética; su presencia siempre comunica un estado (ver Callouts y Alertas, sección 9).
- **`text-secondary`**: cualquier texto que no sea el contenido principal que el usuario vino a leer (fechas, autores, breadcrumbs, captions).
- Un color semántico (`success`, `warning`, `danger`, `info`) **nunca se usa como fondo sólido de un bloque grande de texto**; se usa como acento (borde izquierdo, icono, texto del badge) para no fatigar la lectura.

### 4.3 Tema claro y oscuro

- El cambio de tema es un cambio de un único atributo raíz; ningún componente implementa lógica de color propia — todos consumen los tokens de la tabla 4.1.
- Todo color semántico debe cumplir **mínimo 4.5:1** de contraste para texto normal y **3:1** para texto grande (≥ 24px o ≥ 19px bold) y para elementos gráficos/UI, en ambos temas — verificado en la tabla 4.1.
- Ningún componente puede tener una versión que "solo funcione" en un tema; todo diseño se valida en ambos antes de aprobarse (checklist, sección 17).

---

## 5. Tipografía

### 5.1 Familias tipográficas

| Uso | Familia | Fallback |
|---|---|---|
| UI, texto de cuerpo, headings | **Inter** | `system-ui, -apple-system, sans-serif` |
| Código (inline y bloques) | **JetBrains Mono** | `ui-monospace, Menlo, monospace` |

No se introduce una tercera familia tipográfica bajo ninguna circunstancia. Si un componente "necesita" otra fuente, el componente no cumple el sistema.

### 5.2 Jerarquía y escala

| Token | Tamaño | Line-height | Peso | Tracking | Uso |
|---|---|---|---|---|---|
| `text-display` | 36px | 44px (1.22) | 700 | -0.02em | Título de Home únicamente |
| `text-h1` | 30px | 38px (1.27) | 700 | -0.01em | Título de página (uno solo por página) |
| `text-h2` | 24px | 32px (1.33) | 600 | normal | Secciones principales |
| `text-h3` | 20px | 28px (1.4) | 600 | normal | Subsecciones |
| `text-h4` | 16px | 24px (1.5) | 600 | normal | Sub-subsecciones, títulos de card |
| `text-body` | 16px | 27px (1.7) | 400 | normal | Texto de cuerpo — line-height amplio, optimizado para lectura larga |
| `text-body-sm` | 14px | 22px (1.6) | 400 | normal | Texto secundario dentro de contenido |
| `text-caption` | 13px | 18px (1.4) | 400–500 | 0.01em | Metadatos, timestamps, labels de formulario |
| `text-code` | 14px | 21px (1.5) | 400 | normal | Inline code y bloques de código |

### 5.3 Reglas de uso

- Nunca se salta un nivel de heading por razones estéticas (un H3 nunca precede a un H1 sin H2 intermedio) — esto también es un requisito de accesibilidad (sección 12).
- El peso `700` se reserva para `display` y `h1`; el resto de headings usa `600` como techo, para evitar una jerarquía visual "gritada".
- Longitud de línea objetivo en `text-body`: 65–75 caracteres — controla el `max-width` del contenedor de contenido, no el tamaño de fuente.

---

## 6. Iconografía

### 6.1 Biblioteca oficial

**Lucide** es la única biblioteca de iconos aprobada. No se mezclan sets de iconos (ni siquiera "solo por esta vez"); un icono fuera de Lucide requiere aprobación del Design System Architect y, de aprobarse, se redibuja siguiendo la retícula de Lucide antes de integrarse.

### 6.2 Tamaños

| Token | Tamaño | Uso |
|---|---|---|
| `icon-xs` | 14px | Inline dentro de texto (ej. junto a un link externo) |
| `icon-sm` | 16px | Badges, botones pequeños, metadatos |
| `icon-md` | 20px | Sidebar, botones estándar, inputs |
| `icon-lg` | 24px | Headers de sección, tarjetas de categoría en Home |

### 6.3 Uso correcto

- Grosor de trazo (`stroke-width`) fijo en **1.5px** en todos los tamaños salvo `icon-lg`, que usa **2px** para mantener peso visual consistente al escalar.
- El icono hereda el color del texto que lo acompaña (`currentColor`), salvo cuando es semántico (ver 6.4).
- Todo icono decorativo (que acompaña texto ya descriptivo) se marca como decorativo para lectores de pantalla (sección 12); un icono que es el único indicador de una acción **debe** tener texto accesible alternativo.

### 6.4 Uso incorrecto

- ❌ Combinar iconos "outline" y "filled" en la misma vista.
- ❌ Usar un icono semántico (alerta, error) con un color que no corresponda a su token semántico.
- ❌ Iconos como único medio de comunicar una acción destructiva sin confirmación textual adicional.
- ❌ Redimensionar un icono a un tamaño fuera de la escala 6.2 (rompe la nitidez en pantallas no-retina).

---

## 7. Espaciados

Escala en base 4px. Todo margin, padding y gap del Handbook se expresa en uno de estos tokens — valores intermedios no están permitidos.

| Token | Valor | Cuándo usarlo |
|---|---|---|
| **XS** (`space-1`) | 4px | Separación entre un icono y su texto adyacente; padding interno de un badge |
| **SM** (`space-2`) | 8px | Padding interno de elementos pequeños (chips, botones compactos); gap entre ítems de una lista densa |
| **MD** (`space-4`) | 16px | Padding estándar de cards, inputs y botones; separación entre elementos relacionados dentro de un componente |
| **LG** (`space-6`) | 24px | Separación entre bloques dentro de una misma sección (ej. entre un párrafo y la tabla que le sigue) |
| **XL** (`space-8`) | 32px | Separación entre secciones (`h2`) de una página |
| **2XL** (`space-12`) | 48px | Separación entre bloques mayores de una página (ej. entre el header de la página y el primer contenido) |
| **3XL** (`space-16`, extensión reservada) | 64px | Uso exclusivo en el Home (espaciado entre hero y grid de categorías) — no usar dentro de páginas de contenido |

**Regla de oro**: si dos elementos parecen necesitar un espaciado "a medio camino" entre dos tokens, se elige el token mayor. Nunca se introduce un valor de espaciado nuevo para "que se vea mejor" en un caso puntual.

---

## 8. Grid

### 8.1 Contenedores

| Contenedor | Ancho | Aplica a |
|---|---|---|
| `container-content` | max-width 760px | Columna de lectura (texto, párrafos, listas) — protege la longitud de línea (sección 5.3) |
| `container-wide` | max-width 1120px | Tablas anchas, diagramas, grids de tarjetas dentro del contenido |
| `container-app` | max-width 1440px | Layout completo de 3 columnas (Sidebar + Contenido + TOC) |
| `sidebar` | fijo 260px | Panel de navegación izquierdo |
| `toc-rail` | fijo 220px | Panel de tabla de contenidos derecho |

### 8.2 Breakpoints

Formaliza, sin modificar, los rangos ya definidos en la Arquitectura UX v0.1:

| Token | Rango | Alineado a convención |
|---|---|---|
| `bp-mobile` | < 640px | equivalente a `sm` de Tailwind/Bootstrap |
| `bp-tablet` | 640px – 1023px | equivalente a `md`/`lg` |
| `bp-desktop` | 1024px – 1439px | equivalente a `xl` |
| `bp-wide` | ≥ 1440px | equivalente a `2xl` |

### 8.3 Grid interno de contenido

Dentro de `container-content`/`container-wide`, cualquier composición en columnas (ej. una grilla de tarjetas de categorías) usa una **grid de 12 columnas** con gutter `space-6` (24px) en desktop y `space-4` (16px) en mobile. No se usan grids de 16 o 24 columnas: mantiene la lógica compatible tanto con utilidades Tailwind como con el sistema de grid de Bootstrap, en caso de que un colaborador provenga de cualquiera de los dos ecosistemas.

---

## 9. Componentes Oficiales

Especificación de comportamiento y estilo. **No se define implementación**, solo el contrato visual y funcional que cualquier implementación debe cumplir.

### 9.1 Header (TopNav)

Altura fija 64px, `color-surface` de fondo, `color-border` como borde inferior de 1px. Contiene: wordmark (izquierda) · buscador (centro, colapsa a icono en mobile) · toggle de tema + link a GitHub (derecha). Permanece fijo (`sticky top-0`) con z-index por encima del contenido pero por debajo de modales.

### 9.2 Sidebar

Ancho fijo `260px` en desktop (token `sidebar`, sección 8.1), fondo `color-surface`, scroll propio independiente del contenido. Item de navegación: padding vertical `space-2`, horizontal `space-4`, radio de esquina `6px`. Estado activo: fondo `color-primary` al 8% de opacidad + barra de acento izquierda de 2px en `color-primary` + texto en `color-primary`. Ver especificación completa de estados en sección 10.

### 9.3 Footer

Solo en Home y páginas índice de categoría (no en páginas de contenido largas, donde el Footer añadiría scroll innecesario). Contiene: versión del Handbook, link a "Cómo contribuir", copyright del equipo. Altura auto, padding `space-8` vertical, tipografía `text-caption`, color `text-secondary`.

### 9.4 Breadcrumbs

Tipografía `text-body-sm`, separador `/` en `color-text-secondary`. Cada nivel intermedio es un link en `color-text-secondary` que pasa a `color-primary` en hover; el último nivel (página actual) en `color-text-primary`, sin subrayado, no interactivo. En mobile, colapsa niveles intermedios en un elemento `…` expandible (ver Arquitectura UX v0.1, sección 12).

### 9.5 Cards

Fondo `color-surface`, borde 1px `color-border`, radio `8px`, padding `space-4`. Hover (si es interactiva/clicable): eleva `color-border` a `color-border-strong` + sombra sutil de 1 nivel; nunca cambia de color de fondo completo. Anatomía estándar: icono/badge opcional (arriba) → título `text-h4` → descripción `text-body-sm` en `text-secondary` → metadato opcional al pie.

### 9.6 Botones

| Variante | Uso | Fondo | Texto | Borde |
|---|---|---|---|---|
| `primary` | Acción principal de la página (máx. 1 por vista) | `color-primary` | blanco | ninguno |
| `secondary` | Acción alternativa | transparente | `color-primary` | 1px `color-primary` |
| `ghost` | Acción terciaria, de bajo énfasis | transparente | `color-text-primary` | ninguno |
| `danger` | Acción destructiva | `color-danger` | blanco | ninguno |

Tamaños: `sm` (32px alto), `md` (40px alto, default), `lg` (48px alto). Padding horizontal siempre `space-4` mínimo. Estados obligatorios: `default`, `hover`, `active/pressed`, `focus-visible` (anillo de foco, sección 12), `disabled` (opacidad 40%, cursor not-allowed).

### 9.7 Tablas

Encabezado con fondo `color-surface`, texto `text-caption` en mayúsculas, `color-text-secondary`. Filas separadas por `color-border` (1px, solo horizontal — no se usan bordes verticales). Padding de celda `space-2` vertical / `space-4` horizontal. Fila con hover sutil (`color-surface` al 100% sobre `color-bg`). En mobile, la tabla nunca se comprime: se envuelve en un contenedor con scroll horizontal propio y una sombra lateral leve que indica contenido adicional.

### 9.8 Timeline

Uso: Roadmap, historial de decisiones (ADR), Changelog. Línea vertical `2px` en `color-border`, con nodos circulares de `12px` en `color-primary` (hito completado), `color-border-strong` (pendiente) o `color-warning` (en progreso). Cada entrada: fecha en `text-caption`, título en `text-h4`, descripción en `text-body-sm`.

### 9.9 FAQ

Lista de `Accordion` (ver 9.19) con la pregunta como `text-h4` siempre visible y la respuesta en `text-body` revelada al expandir. Solo un ítem puede permanecer expandido a la vez por defecto en secciones FAQ (comportamiento distinto al Accordion genérico, donde pueden coexistir varios abiertos).

### 9.10 Alertas (banners de página)

Ocupan el ancho completo de `container-content`, se ubican inmediatamente debajo del H1. Variantes `info` / `warning` / `danger`, cada una con: icono semántico + texto + borde izquierdo de 3px en el color semántico + fondo del color semántico al 8% de opacidad. Uso típico: "Esta página está desactualizada" (`warning`/`danger`, persistente) — distinta de un Callout (9.13), que vive **dentro** del cuerpo del contenido, no como banner de la página completa.

### 9.11 Badges

Altura fija `20px`, padding horizontal `space-2`, radio `4px`, tipografía `text-caption` peso 500. Variantes semánticas obligatorias: `Estable` (`success`), `Draft` (`warning`), `Deprecado` (`danger`), `Beta` (`secondary`, sección 4.1). Un badge nunca lleva icono salvo los de estado de PR/build (excepción documentada, no un patrón general).

### 9.12 Buscador

Input de `40px` de alto en el Header, expandido a modal centrado (`max-width 640px`) al activarse (click o `Ctrl/Cmd+K`). Resultados agrupados por categoría con encabezado `text-caption` en mayúsculas por grupo. Ítem de resultado: título coincidente resaltado en `color-primary` sobre fondo transparente (nunca resaltado con fondo de color, para no interferir con el resaltado de scroll/foco). Ver comportamiento funcional completo en Arquitectura UX v0.1, sección 11 — este documento solo define su estilo.

### 9.13 Tabla de contenidos (TOC)

Riel derecho `toc-rail` (220px), tipografía `text-body-sm`, indentado por nivel (`H2` sin indent, `H3` con `space-4` de indent). Ítem activo (scroll-spy): texto en `color-primary` + barra de acento izquierda de 2px, igual lenguaje visual que el ítem activo del Sidebar (9.2), para reforzar que ambos son "dónde estoy".

### 9.14 Bloques de código

Fondo `color-code-bg`, radio `8px`, padding `space-4`, tipografía `text-code`. Header opcional del bloque: nombre de archivo/lenguaje a la izquierda, botón "Copiar" a la derecha (icono `icon-sm`, cambia a icono de check por 2 segundos tras copiar). Resaltado de sintaxis con paleta propia por tema (no es una simple inversión de colores del tema base). Line-numbers opcionales, activados solo cuando el bloque supera 6 líneas.

### 9.15 Callouts

Viven **dentro** del flujo de contenido (a diferencia de la Alerta 9.10, que es un banner de página). Estructura: icono semántico + título en negrita opcional + cuerpo en `text-body`. Borde izquierdo 3px en el color semántico + fondo al 6% de opacidad del mismo color. Cuatro variantes obligatorias: `Nota` (info), `Tip` (success), `Advertencia` (warning), `Peligro` (danger) — mismo mapeo ya usado en el Manual de Organización con `>` de Markdown.

### 9.16 Listas

Viñeta estándar: círculo sólido de 4px en `color-text-secondary`, indent `space-4`. Listas numeradas: número en `text-body` peso 500, color `color-text-secondary`. Listas de tareas (`- [ ]`): checkbox cuadrado de 16px, borde `color-border-strong`, relleno `color-primary` + check blanco cuando está marcado. Espaciado entre ítems: `space-2`; si un ítem contiene múltiples líneas/párrafos, `space-4`.

### 9.17 Formularios

Uso limitado en el Handbook (no es una app transaccional): campo de búsqueda (9.12) y widget de feedback ("¿Te sirvió esta página?" + textarea opcional). Input estándar: 40px alto, borde 1px `color-border`, radio `6px`, `color-border-strong` + anillo de foco en estado focus (sección 12). Label siempre visible arriba del campo (nunca solo placeholder).

### 9.18 Modales

`color-overlay` de fondo, contenedor centrado `color-surface-raised`, radio `12px`, sombra elevada. Ancho según contenido: `sm` (400px, confirmaciones) / `md` (640px, buscador) / `lg` (960px, visor de imagen ampliada de diagramas). Cierre por: botón "X" (esquina superior derecha), tecla `Esc`, click en el overlay. Foco atrapado dentro del modal mientras está abierto (sección 12).

### 9.19 Tooltips

Fondo `color-text-primary` invertido (es decir, oscuro en tema claro y viceversa) para máximo contraste, texto en el color de fondo base, `text-caption`, padding `space-2`/`space-1`, radio `4px`. Aparecen tras 400ms de hover **o** al recibir foco por teclado (nunca solo hover — requisito de accesibilidad, sección 12). Máximo ancho 240px; texto largo se envuelve, nunca se trunca con "...".

*(Accordion, referenciado en 9.9 y en TOC mobile de la Arquitectura UX v0.1: cabecera clicable con icono chevron que rota 180° al expandir, contenido con altura animada — ver reglas de animación en sección 13.)*

---

## 10. Navegación

- **Sidebar (desktop)**: siempre visible, ancho fijo. Un solo nivel expandido por defecto — la rama que contiene la página actual; el resto colapsado. Click en categoría expande/colapsa; click en página navega.
- **Estados de ítem de navegación**: `default` (texto `text-primary`) → `hover` (fondo `surface` +4%, sin cambio de texto) → `active` (fondo `primary` 8%, texto y barra de acento `primary`) → `focus-visible` (anillo de foco adicional al estado que corresponda, nunca lo reemplaza).
- **Menús desplegables** (si se requieren, ej. selector de versión futuro): mismo lenguaje visual que el Sidebar — fondo `surface-raised`, sombra, radio `8px`.
- **Colapsado**: en desktop, el usuario puede colapsar el Sidebar completo a una franja de solo iconos (`icon-md` centrados, tooltip con el nombre de la categoría al hover/foco). En mobile, el Sidebar no tiene estado "colapsado a iconos": es binario, oculto o en drawer completo.
- **Mobile**: Sidebar se convierte en `Drawer` deslizable desde la izquierda, activado por icono de menú en el Header, con overlay (`color-overlay`) sobre el contenido y cierre por swipe, tap fuera o `Esc` (si hay teclado conectado).
- **Desktop**: además del Sidebar, el TOC (9.13) actúa como "navegación secundaria" de la página actual — ambos coexisten sin competir porque responden preguntas distintas ("¿en qué documento estoy?" vs. "¿en qué parte del documento estoy?").

---

## 11. Responsive

| Componente | Mobile (< 640px) | Tablet (640–1023px) | Desktop (≥ 1024px) |
|---|---|---|---|
| Header | Wordmark + icono de buscador + icono de menú | Igual que mobile, buscador puede expandirse inline | Wordmark + buscador completo + toggle tema + GitHub |
| Sidebar | Oculto, en Drawer | Colapsable manual, overlay | Visible fijo, colapsable a iconos |
| TOC | Oculto, reemplazado por acordeón "En esta página" al inicio del contenido | Igual que mobile o modal opcional | Riel fijo a la derecha |
| Contenido | Ancho completo menos padding `space-4` | `container-content` centrado | `container-content` centrado, con Sidebar y TOC a los lados |
| Cards (grid) | 1 columna | 2 columnas | 3–4 columnas según `container-wide` |
| Tablas | Scroll horizontal propio | Igual que mobile si excede ancho | Ancho completo dentro de `container-wide` |
| Botones | Ancho completo si son la única acción de un bloque | Ancho de contenido (`hug`) | Ancho de contenido (`hug`) |
| Breadcrumbs | Truncado a 2 niveles | Truncado a 3 niveles | Completo |

Principio transversal: ningún componente puede **desaparecer contenido** al reducir el viewport, solo puede **reorganizar** cómo se accede a él (colapsar, mover a acordeón, requerir un tap adicional).

---

## 12. Accesibilidad

Cumplimiento **WCAG 2.2 nivel AA** como piso obligatorio, no como objetivo aspiracional.

- **Contraste**: mínimo 4.5:1 para texto normal, 3:1 para texto grande (≥ 24px, o ≥ 19px bold) y para componentes de interfaz (bordes de input, iconos funcionales) — ya verificado por token en la sección 4.1.
- **Navegación por teclado**: el 100% de la interfaz debe ser operable sin mouse. Orden de tabulación lógico (sigue el orden visual: Header → Sidebar → Contenido → TOC). Link "Saltar al contenido" (`skip-to-content`) visible al primer `Tab` desde cualquier página.
- **Foco visible**: todo elemento interactivo tiene un anillo de foco propio (`focus-visible`), 2px, en `color-primary`, con 2px de separación del elemento — nunca se remueve el outline sin reemplazarlo por una alternativa igual o más visible.
- **Lectores de pantalla**: landmarks semánticos (`header`, `nav`, `main`, `aside`, `footer`) obligatorios en cada página; el ítem activo de navegación se marca con `aria-current="page"`; resultados de búsqueda anuncian su cantidad mediante región `aria-live="polite"`; toda imagen/diagrama requiere texto alternativo obligatorio en el frontmatter (no opcional, ver Arquitectura UX v0.1, sección 15).
- **Tamaño mínimo de objetivo (WCAG 2.2 — 2.5.8)**: todo elemento clicable/tocable mide al menos **24×24px**, o cuenta con un área de toque invisible que complete ese mínimo, incluso si el ícono visual es más pequeño (`icon-sm`, 16px).
- **Movimiento reducido**: toda animación no esencial se desactiva automáticamente si el sistema operativo indica preferencia de movimiento reducido (ver sección 13).

---

## 13. Animaciones

### 13.1 Cuándo usar

Únicamente para **comunicar un cambio de estado**, nunca por razones decorativas:

| Token de duración | Valor | Uso |
|---|---|---|
| `motion-fast` | 120ms | Hover, cambios de color, toggles pequeños |
| `motion-base` | 200ms | Apertura/cierre de Accordion, Dropdown, Tooltip |
| `motion-slow` | 300ms | Entrada/salida de Modal, Drawer mobile |

Easing: `ease-out` para elementos que **entran** (aparecen más rápido al inicio, se asientan suave), `ease-in` para elementos que **salen**.

### 13.2 Cuándo evitar

- Ninguna animación de entrada de página o de contenido al hacer scroll (fade-in de párrafos, etc.) — en un contexto de lectura técnica, retrasa la disponibilidad de la información.
- Sin autoplay de ningún tipo (carruseles, videos, transiciones automáticas).
- Sin animaciones que dupliquen el propósito de una que ya existe (ej. el Sidebar no necesita "rebote" además de su transición de expansión).
- **`prefers-reduced-motion: reduce`** activo → todas las transiciones no esenciales (13.1) se reducen a `0ms` o se reemplazan por un cambio instantáneo de estado; solo se preserva la animación estrictamente necesaria para no perder contexto (ej. el Drawer mobile sigue apareciendo, pero sin deslizamiento).

---

## 14. Convenciones

Reglas de aplicación obligatoria, sin excepción salvo aprobación explícita del Design System Architect:

- Todos los **botones** usan una de las 4 variantes de la sección 9.6; no existen botones "custom" por página.
- Todas las **cards** de una misma vista comparten exactamente la misma altura cuando están en grid (se define por el contenido más largo, con truncado de descripción si es necesario — nunca alturas dispares en una misma fila).
- Todas las **tablas** con más de 8 filas incluyen un `sticky header` al hacer scroll vertical dentro del bloque.
- Toda **página** tiene exactamente un `H1`, generado desde el campo `title` del frontmatter — nunca escrito a mano en el cuerpo del MDX.
- Toda **sección** (`H2`) que supere ~400 palabras evalúa si debería ser su propia página, no una sección larga.
- Todo **título** (H1–H4) es una frase nominal clara, nunca una pregunta retórica ni un título "creativo" que oculte el tema real de la sección.
- Todo **enlace** interno usa el texto real del destino como texto del link (nunca "click aquí" o "ver más").
- Toda **imagen o diagrama** incluye `alt` descriptivo y, si es un diagrama técnico, un caption con el número de figura (mismo patrón ya usado en el Manual de Organización).
- Todo **badge de estado** (`Estable`/`Draft`/`Deprecado`) es obligatorio en el frontmatter de cada página — no puede quedar ambiguo si un contenido es confiable.
- Todo **bloque de código** declara su lenguaje explícitamente (para el resaltado de sintaxis); nunca se deja como texto plano si es código real.
- Toda **Alerta** de tipo `Deprecado`/`warning` de página incluye un link directo a la página que la reemplaza, cuando exista.

---

## 15. Escalabilidad

El sistema está diseñado para que agregar contenido nunca requiera "inventar" diseño nuevo:

- **Nuevas páginas dentro de una categoría existente** (ej. una nueva guía dentro de Ingeniería/Backend): se construyen exclusivamente combinando los 19 componentes de la sección 9 y los tokens de las secciones 4–8. Ningún nuevo manual necesita, por diseño, un componente nuevo.
- **Nuevas categorías raíz**: heredan automáticamente Header, Sidebar, Breadcrumbs, TOC y el resto del sistema sin cambios — lo único que aporta una categoría nueva es un ítem más en el árbol de navegación (gobernado por el proceso de decisión de alto impacto ya definido en el Manual de Organización, sección 11, y referenciado en Arquitectura UX v0.1, sección 14).
- **Volumen**: la escala tipográfica, de espaciado y de color no cambia si el Handbook pasa de 20 a 2,000 páginas — lo único que crece es el índice de búsqueda (aspecto técnico, no de diseño) y potencialmente la profundidad del Sidebar (que ya soporta colapsado, sección 10).
- **Regla de expansión de componentes**: si un caso de uso nuevo genuinamente no encaja en ninguno de los 19 componentes oficiales, no se improvisa una solución ad-hoc en esa página — se levanta como propuesta de componente nuevo siguiendo el proceso de gobernanza (sección 16).

---

## 16. Gobernanza

- **Rol responsable**: el **Design System Architect** es el dueño de este documento y el único con autoridad para aprobar cambios estructurales (nuevo componente, nuevo token de color, cambio de tipografía). El resto del equipo puede *proponer*, no aprobar unilateralmente.
- **Cambios menores** (ajustar un valor dentro de una escala ya existente, ej. un tamaño de icono): PR directo, con aprobación de una revisión estándar (mismo flujo de código, Manual de Organización sección 9-10).
- **Cambios mayores** (nuevo componente, nuevo color semántico, cambio de familia tipográfica): siguen el mismo proceso de decisión de alto impacto ya definido para el equipo — propuesta breve, discusión, consenso del Comité Técnico, y se documenta como **ADR** (Manual de Organización, sección 12), enlazado desde este documento.
- **Versionado**: esquema `MAJOR.MINOR`.
  - `MINOR` (ej. 1.0 → 1.1): adición de un token o componente sin romper nada existente (ej. un nuevo tipo de Badge).
  - `MAJOR` (ej. 1.0 → 2.0): cualquier cambio que altere visualmente páginas ya existentes sin acción del autor (ej. cambiar la paleta primaria, la tipografía base, o remover un componente).
- **Registro de cambios**: todo cambio a este documento, sin importar el tamaño, se anota en `meta/changelog-del-handbook` (definido en Arquitectura UX v0.1, sección 2), con referencia al ADR correspondiente si aplica.
- **Auditoría periódica**: este Design System se revisa en la misma cadencia mensual ya establecida para la documentación del equipo (Manual de Organización, sección 6), verificando que ningún componente nuevo se haya introducido fuera de proceso.

---

## 17. Checklist de cumplimiento

Verificación obligatoria antes de aprobar cualquier Pull Request que agregue o modifique una página del Handbook.

- [ ] El frontmatter incluye `title`, `category`, `order`, `status`, `owner` (Arquitectura UX v0.1, sección 14).
- [ ] La página tiene exactamente un `H1`, sin saltos de nivel de heading.
- [ ] Todos los colores usados provienen de los tokens de la sección 4 — cero valores hexadecimal sueltos.
- [ ] Toda la tipografía usa Inter/JetBrains Mono y los tokens de la sección 5 — sin tamaños de fuente arbitrarios.
- [ ] Todos los iconos son de Lucide, en uno de los 4 tamaños de la sección 6.2.
- [ ] Todo espaciado corresponde a un token de la sección 7 — sin valores intermedios inventados.
- [ ] Los componentes usados son exclusivamente los 19 de la sección 9; cualquier componente nuevo tiene un ADR de gobernanza aprobado (sección 16).
- [ ] La página se probó visualmente en tema claro **y** oscuro.
- [ ] La página se probó en los 4 breakpoints de la sección 8.2 (mobile, tablet, desktop, wide).
- [ ] Contraste de texto verificado ≥ 4.5:1 (o 3:1 para texto grande/UI) en ambos temas.
- [ ] Navegación completa por teclado probada: Tab, Shift+Tab, Enter/Espacio, Esc en modales.
- [ ] Todo elemento interactivo tiene un anillo de foco visible.
- [ ] Toda imagen/diagrama tiene `alt` descriptivo.
- [ ] Ningún target clicable mide menos de 24×24px.
- [ ] Las animaciones usadas están dentro de los tokens de la sección 13 y respetan `prefers-reduced-motion`.
- [ ] Todos los enlaces internos usan texto descriptivo del destino (no "click aquí").
- [ ] La página aparece correctamente en el Sidebar y en el Sitemap — no es una página huérfana.
- [ ] Se ejecutó el link-checker y el validador de frontmatter en CI sin errores (Arquitectura UX v0.1, sección 17).

---

*Fin de THERS Handbook Design System v1.0. Este documento es vinculante para toda página del Handbook a partir de su aprobación por el Comité Técnico. Cambios futuros siguen el proceso de la sección 16.*
