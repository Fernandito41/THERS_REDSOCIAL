# Seguridad infantil y Google Play — qué cubre THERS hoy (2026-10-02)

> **No declara cumplimiento total.** Documenta qué parte del requisito *Child Safety Standards* de
> Google Play queda cubierta por la implementación (`ADR-038-child-safety-reports.md`) y qué sigue
> pendiente. **Play Console no se modificó.** Fuente de los requisitos: ayuda de Play Console,
> «Learning more about our Child Safety Standards policy» (consultada el 2026-10-02; **reverificar al
> enviar la app**: las políticas cambian y no encontré una fecha límite explícita).
>
> La política aplica a las apps de **redes sociales y citas** y, según la propia ayuda, **la presencia
> o ausencia de menores en la app es irrelevante**: THERS, aunque sea 18+, queda dentro.

## Los cinco elementos y su estado

| # | Requisito de Play | Estado | Qué hay |
|---|---|---|---|
| 1 | **Estándares publicados** contra la explotación y el abuso sexual infantil, en un recurso web accesible, con el nombre de la app o del desarrollador | **Hecho en código, no desplegado** | Página pública `/child-safety` en español e inglés, sin sesión, con el nombre «THERS Social Network». Verificada abierta en un navegador real. **Falta desplegar la web** en `thersweb.com` |
| 2 | **Mecanismo de comentarios dentro de la app** (sin salir de ella) | **Hecho en código, sin fusionar** | Categoría de reporte «Explotación o abuso de menores» en la app móvil, para publicaciones, comentarios, mensajes recibidos y cuentas, con prioridad máxima asignada por el servidor. Depende de fusionar el backend de reportes (`ADR-032`, fase 1). **La web no tiene interfaz de reporte** |
| 3 | **Retirar el material cuando se tiene conocimiento real**, conforme a la ley y a lo declarado | **❌ Pendiente** | No hay herramienta para retirar contenido ni suspender cuentas. La página lo presenta como capacidad de THERS; hoy solo sería posible tocando la base de datos |
| 4 | **Persona de contacto designada**, con nombre y datos, **registrada en Play Console** | **Parcial** | La página y la política nombran a Diego Medina (Administrador) y `seguridadinfantil@thersweb.com`. **Falta registrarlo en Play Console** (paso manual del equipo) |
| 5 | **Cumplir las leyes de seguridad infantil** de cada jurisdicción | **No verificado** | La página lo declara. No se revisaron las obligaciones concretas de El Salvador (por ejemplo, de denuncia ante autoridades) ni la LEPINA. **Requiere abogado** |

## Qué quedó cubierto con este cambio
- Estándares públicos (redactados y probados; falta desplegarlos).
- Categoría de reporte específica, en el mismo sistema de reportes, para los cuatro tipos de objetivo existentes.
- Prioridad máxima decidida por el servidor, no por el cliente, con escalada de reportes previos y límite propio.
- Contacto de seguridad infantil publicado.
- Diferencia explícita entre contenido sensible permitido y contenido de explotación infantil (prohibido).

## Qué sigue pendiente (no marcar como terminado)
1. **Panel mínimo de moderación:** nadie lee todavía la cola; un reporte crítico solo se ve consultando la base. **Sin esto, la prioridad máxima es una promesa que el sistema no puede cumplir en la práctica.**
2. **Retirada administrativa de contenido** y **suspensión administrativa de cuentas** (`ADR-032`, fases 2 a 4).
3. **Aviso al equipo** (correo o notificación) cuando entre un reporte crítico.
4. **Flujo operativo interno:** quién revisa, en cuánto tiempo, qué se conserva como evidencia, a quién se comunica y cómo se atiende la solicitud de una autoridad. Hoy solo existe la intención.
5. **Interfaz de reporte en la web.**
6. **Registrar el contacto en Play Console** y declarar la URL **cuando exista el panel mínimo y un proceso de guardia** (ver riesgo 1 del ADR-038).
7. **Revisión jurídica** de la página y de las obligaciones de denuncia en El Salvador.
8. **Plazo de conservación** de reportes y evidencia (propuesta: 12 meses; sin decidir).
9. **Fusionar y desplegar:** la rama de reportes, este cambio y la web.

## Lo que la página NO afirma (a propósito)
Detección automática, comparación de huellas (hash), IA, reconocimiento de imágenes, acuerdos con autoridades u organizaciones, ni horarios de atención. Nada de eso existe.
