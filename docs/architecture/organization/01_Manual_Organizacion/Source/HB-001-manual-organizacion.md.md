# THERS

**MANUAL OFICIAL DE ORGANIZACIÓN DEL PROYECTO**

*Documento interno de equipo · Estándares de trabajo profesional*

**Versión 1.0**

Julio 2026

**Equipo:** 4 integrantes

**Stack tecnológico:** React · Vite · Tailwind CSS · Flask · PostgreSQL · JWT

**Repositorio:** GitHub (privado/organización del equipo)

---

## Índice

- [0. Propósito y alcance del documento](#0-propósito-y-alcance-del-documento)
- [1. Organigrama](#1-organigrama)
- [2. Roles](#2-roles)
- [3. Responsabilidades](#3-responsabilidades)
  - [3.1 Responsabilidades individuales por rol](#31-responsabilidades-individuales-por-rol)
  - [3.2 Responsabilidades compartidas por todo el equipo](#32-responsabilidades-compartidas-por-todo-el-equipo)
- [4. Responsabilidades diarias](#4-responsabilidades-diarias)
  - [4.1 Checklist diario individual](#41-checklist-diario-individual)
- [5. Responsabilidades semanales](#5-responsabilidades-semanales)
- [6. Responsabilidades mensuales](#6-responsabilidades-mensuales)
- [7. Flujo de trabajo](#7-flujo-de-trabajo)
  - [7.1 Flujo de ramas en Git](#71-flujo-de-ramas-en-git)
- [8. Cómo trabajar en GitHub](#8-cómo-trabajar-en-github)
  - [8.1 Ramas protegidas](#81-ramas-protegidas)
  - [8.2 Convención de nombres de ramas](#82-convención-de-nombres-de-ramas)
  - [8.3 Convención de commits (Conventional Commits)](#83-convención-de-commits-conventional-commits)
  - [8.4 Tablero de GitHub Projects](#84-tablero-de-github-projects)
- [9. Cómo trabajar con Pull Requests](#9-cómo-trabajar-con-pull-requests)
  - [9.1 Reglas generales](#91-reglas-generales)
  - [9.2 Plantilla de descripción de PR](#92-plantilla-de-descripción-de-pr)
  - [9.3 Checklist antes de solicitar revisión](#93-checklist-antes-de-solicitar-revisión)
- [10. Cómo revisar código](#10-cómo-revisar-código)
  - [10.1 Checklist del revisor](#101-checklist-del-revisor)
  - [10.2 Tiempos de revisión](#102-tiempos-de-revisión)
- [11. Cómo tomar decisiones técnicas](#11-cómo-tomar-decisiones-técnicas)
  - [11.1 Proceso para decisiones de alto impacto](#111-proceso-para-decisiones-de-alto-impacto)
- [12. Cómo registrar decisiones importantes](#12-cómo-registrar-decisiones-importantes)
  - [12.1 Plantilla de ADR](#121-plantilla-de-adr)
- [13. Cómo organizar reuniones](#13-cómo-organizar-reuniones)
  - [13.1 Reglas para reuniones efectivas](#131-reglas-para-reuniones-efectivas)
- [14. Cómo organizar Notion](#14-cómo-organizar-notion)
- [15. Cómo documentar el proyecto](#15-cómo-documentar-el-proyecto)
  - [15.1 Reglas mínimas de documentación](#151-reglas-mínimas-de-documentación)
- [16. Cómo organizar tareas](#16-cómo-organizar-tareas)
  - [16.1 Columnas del tablero](#161-columnas-del-tablero)
  - [16.2 Plantilla mínima de una tarea/Issue](#162-plantilla-mínima-de-una-tareaissue)
- [17. Cómo repartir el trabajo](#17-cómo-repartir-el-trabajo)
- [18. Cómo evitar trabajo duplicado](#18-cómo-evitar-trabajo-duplicado)
- [19. Cómo trabajar usando IA](#19-cómo-trabajar-usando-ia)
  - [19.1 Reglas de uso](#191-reglas-de-uso)
- [20. Reglas oficiales del equipo](#20-reglas-oficiales-del-equipo)

---

## 0. Propósito y alcance del documento

Este Manual de Organización establece las reglas de funcionamiento del equipo THERS: cómo estamos organizados, cómo tomamos decisiones, cómo trabajamos en GitHub, cómo documentamos y cómo colaboramos día a día. El objetivo es que THERS deje de operar como un proyecto universitario informal y adopte procesos de una empresa de software real, sin necesidad de reiniciar el trabajo ya avanzado (backend, frontend y módulo de autenticación ya existen y se mantienen).

Este documento cubre exclusivamente organización de equipo, procesos y gobernanza. No define arquitectura técnica profunda, infraestructura ni Docker; esos temas se documentarán en manuales técnicos separados (p. ej. Manual de Arquitectura, Manual de Despliegue).

> **Nota:** Este manual es un documento vivo. Cualquier integrante puede proponer cambios siguiendo el proceso descrito en la sección 12 (Registro de decisiones importantes).

## 1. Organigrama

THERS es un equipo autogestionado de 4 integrantes. No existe una jerarquía de mando vertical: la Dirección Técnica (funciones tipo CTO) se ejerce de forma colegiada a través del Comité Técnico, formado por los 4 integrantes. El rol de Project Owner / Scrum Master coordina el proceso pero no tiene autoridad unilateral sobre decisiones técnicas.

![Organigrama del equipo THERS](media/organigrama-thers.png)

*Figura 1. Organigrama del equipo THERS.*

> **Nota:** Los nombres 'Integrante 1-4' deben reemplazarse por los nombres reales del equipo en la versión final del documento (Notion / GitHub).

## 2. Roles

Cada integrante tiene un rol principal (área de mayor responsabilidad) pero todos participan en revisión de código, testing y documentación. Los roles rotan al inicio de cada semestre académico o cada 3 meses de desarrollo, salvo acuerdo distinto del equipo.

| Rol | Enfoque principal | Responsable de |
|---|---|---|
| Project Owner / Scrum Master | Gestión ágil y producto | Backlog, sprints, reuniones, seguimiento de avance |
| Tech Lead Backend | Flask, PostgreSQL, JWT, API | Arquitectura de backend, endpoints, seguridad, migraciones |
| Tech Lead Frontend | React, Vite, Tailwind | UI/UX, componentes, consumo de API, estado de la app |
| QA / Documentación / DevOps de apoyo | Calidad y soporte técnico | Pruebas, documentación técnica, CI básico, GitHub |

## 3. Responsabilidades

### 3.1 Responsabilidades individuales por rol

| Rol | Responsabilidades |
|---|---|
| Project Owner / Scrum Master | Mantener el backlog priorizado y actualizado<br>Convocar y moderar reuniones (daily, planning, review, retro)<br>Dar seguimiento al avance del sprint<br>Comunicar bloqueos al resto del equipo |
| Tech Lead Backend | Diseñar y mantener endpoints de la API (Flask)<br>Administrar el esquema de base de datos (PostgreSQL) y migraciones<br>Garantizar buenas prácticas de autenticación (JWT)<br>Revisar PRs relacionados a backend |
| Tech Lead Frontend | Mantener la arquitectura de componentes React<br>Garantizar consistencia visual con Tailwind<br>Optimizar el build con Vite<br>Revisar PRs relacionados a frontend |
| QA / Documentación / DevOps de apoyo | Probar manualmente funcionalidades antes de aceptar un PR<br>Mantener actualizado README, CONTRIBUTING y changelog<br>Configurar y mantener automatizaciones simples (lint, tests)<br>Apoyar en la gestión del repositorio (issues, labels, board) |

### 3.2 Responsabilidades compartidas por todo el equipo

- Escribir código legible, comentado cuando sea necesario y alineado a los estándares del proyecto.
- Revisar al menos un Pull Request ajeno por semana.
- Reportar bloqueos apenas ocurran, no esperar a la siguiente reunión.
- Actualizar el estado de sus tareas en el tablero (Notion/GitHub Projects) diariamente.
- Proteger credenciales y variables sensibles (no subir archivos .env al repositorio).

## 4. Responsabilidades diarias

Cada integrante, todos los días de trabajo activo, debe cumplir el siguiente checklist mínimo:

| Momento | Actividad | Responsable |
|---|---|---|
| Inicio de sesión de trabajo | Revisar mensajes/canal del equipo y el tablero de tareas | Todos |
| Inicio de sesión de trabajo | Hacer pull de la rama develop antes de empezar a codear | Todos |
| Durante el día | Hacer commits pequeños y descriptivos (Conventional Commits) | Todos |
| Durante el día | Mover la tarjeta de la tarea en el tablero al cambiar de estado | Todos |
| Fin de sesión de trabajo | Hacer push del trabajo, aunque no esté terminado (rama propia) | Todos |
| Fin de sesión de trabajo | Actualizar el Daily Log en Notion (2-3 líneas: qué hice, qué sigue, bloqueos) | Todos |

### 4.1 Checklist diario individual

- [ ] Pull de develop antes de empezar.
- [ ] Trabajo registrado en el tablero (tarjeta movida a 'En progreso').
- [ ] Commits con mensajes claros durante el día.
- [ ] Push al final del día, aunque el trabajo esté incompleto.
- [ ] Bloqueos reportados en el canal del equipo, sin esperar al daily.

## 5. Responsabilidades semanales

| Día sugerido | Actividad | Responsable |
|---|---|---|
| Lunes | Sprint Planning: definir tareas de la semana | Project Owner + equipo |
| Lunes a viernes | Daily standup breve (sync o async) | Todos |
| Miércoles | Revisión cruzada de código pendiente (PRs abiertos) | Todos |
| Viernes | Sprint Review: demo de lo completado | Todos |
| Viernes | Retrospectiva breve: qué mejorar la próxima semana | Todos |
| Viernes | Actualizar changelog y documentación de la semana | QA/Docs |

## 6. Responsabilidades mensuales

| Actividad | Detalle | Responsable |
|---|---|---|
| Revisión de roadmap | Ajustar prioridades del backlog según avance real | Project Owner + Comité Técnico |
| Revisión de arquitectura | Evaluar deuda técnica y necesidades de refactor | Tech Leads |
| Auditoría de dependencias | Revisar versiones de librerías (React, Flask, etc.) | Tech Leads |
| Revisión de documentación | Verificar que README y manuales sigan vigentes | QA/Docs |
| Retrospectiva mensual | Evaluación general de procesos del equipo | Todos |
| Rotación de roles (si aplica) | Evaluar si corresponde rotar responsabilidades | Todos |

## 7. Flujo de trabajo

Toda unidad de trabajo (funcionalidad, corrección o mejora) sigue el mismo ciclo de vida, desde su creación como idea hasta su integración en la rama principal:

| # | Etapa | Descripción |
|---|---|---|
| 1 | Idea / necesidad | Se identifica una necesidad (feature, bug, mejora). |
| 2 | Issue en GitHub | Se crea un Issue con descripción, criterios de aceptación y etiquetas. |
| 3 | Backlog | El Issue entra al backlog priorizado en el tablero. |
| 4 | Sprint / asignación | En el Planning, se asigna a un integrante y entra a 'To Do'. |
| 5 | Desarrollo | Se crea una rama feature/ desde develop; tarjeta pasa a 'En progreso'. |
| 6 | Pull Request | Al terminar, se abre un PR hacia develop vinculado al Issue. |
| 7 | Revisión de código | Al menos un integrante revisa el PR (ver sección 10). |
| 8 | Merge | Aprobado el PR, se integra a develop; tarjeta pasa a 'Done'. |
| 9 | Release | Periódicamente, develop se integra a main mediante PR de release. |

### 7.1 Flujo de ramas en Git

![Flujo de ramas: main, develop y features integradas vía Pull Request](media/flujo-ramas-git.png)

*Figura 2. Flujo de ramas: main, develop y features integradas vía Pull Request.*

## 8. Cómo trabajar en GitHub

### 8.1 Ramas protegidas

- **main:** código en producción / entregable estable. Nadie hace push directo.
- **develop:** rama de integración. Nadie hace push directo; todo entra por PR.
- Ambas ramas requieren Pull Request y al menos 1 revisión aprobada para recibir cambios.

### 8.2 Convención de nombres de ramas

| Tipo | Prefijo | Ejemplo |
|---|---|---|
| Nueva funcionalidad | `feature/` | `feature/perfil-usuario` |
| Corrección de error | `fix/` | `fix/token-refresh` |
| Tareas técnicas / refactor | `chore/` | `chore/actualizar-dependencias` |
| Documentación | `docs/` | `docs/manual-organizacion` |
| Urgencia en producción | `hotfix/` | `hotfix/login-caido` |

### 8.3 Convención de commits (Conventional Commits)

| Prefijo | Uso |
|---|---|
| `feat:` | Nueva funcionalidad |
| `fix:` | Corrección de error |
| `docs:` | Cambios de documentación |
| `style:` | Formato, sin cambios de lógica |
| `refactor:` | Cambio de código sin alterar comportamiento |
| `test:` | Agregar o corregir pruebas |
| `chore:` | Tareas de mantenimiento (dependencias, config) |

Ejemplo: `feat: agregar validacion de formulario de registro`

### 8.4 Tablero de GitHub Projects

Columnas del tablero: Backlog → To Do → En progreso → En revisión (PR) → Done.

- Cada tarjeta corresponde a un Issue.
- Toda tarjeta debe tener: etiqueta de tipo, responsable asignado y sprint/milestone.

## 9. Cómo trabajar con Pull Requests

### 9.1 Reglas generales

- Un PR debe resolver una sola cosa (un Issue, una funcionalidad concreta).
- Título del PR en el mismo formato que los commits: `feat: ...`, `fix: ...`
- Todo PR debe vincularse a su Issue (`Closes #12`).
- Ningún PR se fusiona sin al menos 1 aprobación.
- El autor del PR no se autoaprueba.

### 9.2 Plantilla de descripción de PR

| Campo | Contenido esperado |
|---|---|
| Resumen | Qué hace este PR en 1-2 líneas |
| Issue relacionado | `Closes #___` |
| Cambios principales | Lista breve de cambios |
| Cómo probarlo | Pasos para que el revisor lo pruebe localmente |
| Capturas (si aplica) | Imágenes de UI si hay cambios visuales |
| Checklist | Ver 9.3 |

### 9.3 Checklist antes de solicitar revisión

- [ ] El código compila/corre sin errores localmente.
- [ ] No se incluyen archivos .env, credenciales o datos sensibles.
- [ ] Se probó manualmente el flujo afectado.
- [ ] El PR está vinculado a su Issue correspondiente.
- [ ] No hay código comentado o de prueba (console.log, prints) olvidado.

## 10. Cómo revisar código

La revisión de código busca calidad y aprendizaje compartido, no señalar errores de forma negativa. Todo comentario debe ser específico y constructivo.

### 10.1 Checklist del revisor

- [ ] ¿El código resuelve lo que dice el Issue/PR?
- [ ] ¿Sigue las convenciones de nombres y estilo del proyecto?
- [ ] ¿Hay lógica duplicada que podría reutilizarse?
- [ ] ¿Se manejan errores y casos límite (inputs vacíos, fallos de red, etc.)?
- [ ] ¿Existe algún riesgo de seguridad (validación de datos, exposición de JWT, SQL injection)?
- [ ] ¿El PR es entendible sin tener que preguntar al autor?

### 10.2 Tiempos de revisión

| Tipo de PR | Tiempo máximo de respuesta |
|---|---|
| Hotfix / urgente | Menos de 4 horas |
| Feature normal | Menos de 24 horas hábiles |
| Documentación / chore | Menos de 48 horas |

> **Nota:** Si un PR no recibe revisión en el tiempo esperado, el autor debe avisar directamente en el canal del equipo, no solo esperar.

## 11. Cómo tomar decisiones técnicas

Las decisiones técnicas se clasifican por impacto, para no burocratizar cambios pequeños ni improvisar cambios grandes.

| Nivel | Ejemplo | Cómo se decide |
|---|---|---|
| Bajo impacto | Nombrar una variable, estilo de un componente | El autor decide y avanza |
| Impacto medio | Elegir una librería nueva, cambiar estructura de carpetas | Se discute en daily/canal; basta acuerdo de 2+ integrantes |
| Alto impacto | Cambiar el modelo de datos, la autenticación, el stack | Se lleva al Comité Técnico completo (los 4); requiere consenso |

### 11.1 Proceso para decisiones de alto impacto

1. Se redacta una propuesta breve (problema, opciones, recomendación).
2. Se comparte en Notion (ver sección 12) con al menos 24h de anticipación.
3. Se discute en reunión o async en el canal del equipo.
4. Se decide por consenso; si no hay consenso, se vota (mayoría simple, 4 integrantes).
5. La decisión final se documenta como ADR (sección 12).

## 12. Cómo registrar decisiones importantes

Toda decisión de impacto medio o alto se registra como un ADR (Architecture Decision Record) en Notion, en la página 'Registro de Decisiones'. Esto evita perder el contexto de por qué se tomó una decisión.

### 12.1 Plantilla de ADR

| Campo | Contenido |
|---|---|
| ID | ADR-001, ADR-002, ... |
| Título | Nombre corto de la decisión |
| Fecha | dd/mm/aaaa |
| Estado | Propuesta / Aceptada / Reemplazada |
| Contexto | Qué problema se está resolviendo |
| Opciones consideradas | Alternativas evaluadas |
| Decisión | Qué se decidió y por qué |
| Consecuencias | Qué implica esta decisión a futuro |

## 13. Cómo organizar reuniones

| Reunión | Frecuencia | Duración | Objetivo |
|---|---|---|---|
| Daily standup | Diaria (L-V) | 10-15 min | Qué hice, qué haré, bloqueos |
| Sprint Planning | Semanal (lunes) | 30-45 min | Definir tareas de la semana |
| Sprint Review | Semanal (viernes) | 20-30 min | Mostrar avances completados |
| Retrospectiva | Semanal (viernes) | 15-20 min | Qué mejorar en el proceso |
| Revisión de roadmap | Mensual | 45-60 min | Ajustar prioridades y arquitectura |

### 13.1 Reglas para reuniones efectivas

- Toda reunión tiene una agenda mínima compartida antes de empezar.
- Se registran acuerdos y pendientes en Notion (minuta breve, no acta extensa).
- Si un integrante no puede asistir, revisa la minuta y reporta su estado por escrito.
- Reuniones que no sean daily se agendan con al menos 24h de anticipación.

## 14. Cómo organizar Notion

Notion es el centro de gestión del proyecto (no reemplaza a GitHub para código, pero sí organiza planificación, documentación y decisiones).

| Página | Contenido |
|---|---|
| Inicio | Resumen del proyecto, enlaces rápidos, estado general |
| Roadmap | Visión de mediano plazo, próximos hitos |
| Backlog | Lista priorizada de Issues/tareas pendientes |
| Sprints | Tablero o registro de cada sprint (semana) con objetivos |
| Daily Log | Registro breve diario de cada integrante |
| Registro de Decisiones (ADR) | Historial de decisiones técnicas importantes |
| Minutas de reuniones | Acuerdos y pendientes de cada reunión |
| Documentación técnica | Enlace o copia de README, guías, diagramas |
| Roles y responsabilidades | Versión viva de este manual |

## 15. Cómo documentar el proyecto

| Documento | Ubicación | Actualiza |
|---|---|---|
| README.md | Raíz del repositorio | Cómo instalar y correr el proyecto (frontend + backend) |
| CONTRIBUTING.md | Raíz del repositorio | Reglas de este manual resumidas para nuevos colaboradores |
| CHANGELOG.md | Raíz del repositorio | Cambios relevantes por versión/sprint |
| Documentación de API | /docs o Notion | Endpoints, parámetros, respuestas (backend Flask) |
| Manual de Organización (este documento) | Notion + repositorio | Roles, procesos y reglas del equipo |
| ADR (decisiones) | Notion | Historial de decisiones técnicas |

### 15.1 Reglas mínimas de documentación

- Todo endpoint nuevo del backend se documenta el mismo día que se crea el PR.
- Todo componente reutilizable del frontend lleva un comentario breve explicando su propósito y props.
- El README se revisa y actualiza al final de cada sprint si hubo cambios en instalación o configuración.

## 16. Cómo organizar tareas

### 16.1 Columnas del tablero

| Columna | Significado |
|---|---|
| Backlog | Tarea identificada, sin priorizar aún |
| To Do | Priorizada para el sprint actual |
| En progreso | Alguien está trabajando activamente en ella |
| En revisión | PR abierto, esperando revisión |
| Done | Fusionada a develop y verificada |

### 16.2 Plantilla mínima de una tarea/Issue

| Campo | Ejemplo |
|---|---|
| Título | Agregar recuperación de contraseña |
| Descripción | Como usuario quiero recuperar mi contraseña por correo |
| Criterios de aceptación | El usuario recibe un enlace válido por 15 minutos |
| Etiqueta | feature / bug / docs / chore |
| Prioridad | Alta / Media / Baja |
| Responsable | Nombre del integrante asignado |
| Estimación | Horas o talla (S/M/L) |

## 17. Cómo repartir el trabajo

- Las tareas se reparten en el Sprint Planning semanal, no de forma improvisada durante la semana.
- Se prioriza que cada integrante trabaje dentro de su área principal (backend, frontend, QA/docs), pero cualquiera puede tomar tareas de otra área si tiene disponibilidad y conocimiento.
- Ninguna tarea se asigna sin responsable claro; 'lo vemos entre todos' no es una asignación válida.
- La carga se reparte de forma pareja: se busca que los 4 integrantes tengan una cantidad similar de tareas activas por sprint.
- Si una tarea es muy grande, se divide en subtareas más pequeñas antes de asignarla.

## 18. Cómo evitar trabajo duplicado

- [ ] Antes de empezar una tarea, verificar que su tarjeta esté en 'En progreso' y asignada a ti.
- [ ] Nunca tomar una tarea que ya tiene responsable asignado sin coordinar primero.
- [ ] Revisar issues y PRs abiertos antes de crear uno nuevo similar.
- [ ] Comunicar en el canal del equipo cuando se empieza algo que podría solaparse con otra área (ej. cambios en modelos de datos).
- [ ] Hacer pull de develop frecuentemente para reducir conflictos de código.

> **Nota:** Si dos integrantes detectan que están trabajando en algo parecido, se resuelve en el momento (no se espera al daily): uno continúa y el otro reasigna su tiempo a otra tarea del backlog.

## 19. Cómo trabajar usando IA

El uso de herramientas de IA (asistentes de código, generación de texto, etc.) está permitido y se fomenta como apoyo a la productividad, siempre que el resultado sea revisado y comprendido por quien lo integra al proyecto.

| Permitido | No permitido |
|---|---|
| Generar código base o boilerplate que luego se revisa y ajusta | Copiar y pegar código generado por IA sin entenderlo ni probarlo |
| Pedir ayuda para depurar errores o explicar mensajes de error | Compartir credenciales, JWT secrets o datos de la base de datos con la IA |
| Redactar o mejorar documentación (README, comentarios, este manual) | Subir código con licencias restrictivas generado o copiado sin verificar |
| Generar casos de prueba o sugerencias de refactor | Usar IA como único revisor de un PR (siempre debe haber revisión humana) |
| Usar IA para investigar librerías o comparar enfoques técnicos | Delegar decisiones de arquitectura de alto impacto únicamente a la IA |

### 19.1 Reglas de uso

- Todo código relevante generado con IA pasa por el mismo proceso de PR y revisión que cualquier otro código.
- No se pega información sensible del proyecto (contraseñas, JWT secret, datos reales de usuarios) en herramientas de IA externas.
- Si una parte importante de una funcionalidad fue generada con IA, se puede mencionar brevemente en la descripción del PR, sin que esto sea obligatorio para cambios menores.

## 20. Reglas oficiales del equipo

Estas reglas resumen los acuerdos innegociables de THERS. Todo integrante nuevo debe leerlas antes de contribuir.

- [ ] Nunca se hace push directo a main ni a develop: todo entra por Pull Request.
- [ ] Ningún PR se fusiona sin al menos 1 revisión aprobada.
- [ ] Nunca se sube el archivo .env ni credenciales al repositorio.
- [ ] Toda tarea tiene un responsable único y visible en el tablero.
- [ ] Toda decisión de alto impacto se documenta como ADR antes de implementarse.
- [ ] Los bloqueos se comunican de inmediato, no se guardan para la siguiente reunión.
- [ ] El código generado con IA se revisa y se entiende antes de integrarse.
- [ ] La documentación (README, changelog) se actualiza el mismo sprint en que cambia el código relacionado.
- [ ] El respeto y la comunicación clara son obligatorios en revisiones de código y reuniones.
- [ ] Este manual se revisa y puede actualizarse en la retrospectiva mensual.
