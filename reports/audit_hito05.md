# Auditoría final de fases 07, 08 y 09

## Recomendación: APTO PARA PUBLICACIÓN

El usuario confirmó la revisión visual de las seis secciones y de las tarjetas y navegación posteriores al ajuste. En la auditoría original, esta recomendación técnica por sí sola no autorizaba la publicación. Posteriormente, el usuario autorizó expresamente publicar el Hito 05, incluidas las correcciones documentales necesarias. La accesibilidad completa y la apertura del Excel en escritorio siguen pendientes; no se afirman como aprobadas.

## Comprobación posterior de tarjetas y navegador

Las tarjetas se abreviaron a `$8.001,67 M` y `$3.367,16 M` para la ejecución histórica observada; la ayuda conserva los importes completos. En una ventana Chrome de escritorio de 1536 × 864 píxeles, sin traducción de la página, se observaron completas las tarjetas monetarias de ventas, margen y ticket. No se garantiza el ajuste en todos los tamaños, niveles de zoom o con traducción activa.

El usuario informó `NotFoundError` al navegar a Calidad y trazabilidad. En la prueba local Chrome anunció traducción automática: transformó `M` en `millones` y, durante una transición, se observó el encabezado anterior con contenido de calidad. Al volver a mostrar el texto original y navegar de Resumen a Calidad, aparecieron el encabezado y contenido correctos sin error visible. No se reprodujo el `NotFoundError` ni se demostró su causa; la interacción entre traducción y actualización del DOM es una hipótesis, no una conclusión. No se cambiaron componentes ni estado sin evidencia causal.

En la última revisión manual, el usuario confirmó en Chrome con contenido original ambas tarjetas sin recortes, encabezado correcto y datos visibles de Calidad, sin aparición de `removeChild`. Esta observación no demuestra la causa ni una corrección definitiva. Si reaparece, registrar navegador y versión, zoom, traducción, secuencia y mensaje de consola sin datos sensibles, y comparar con una sesión sin extensiones.

## Evidencia y pruebas

- El usuario confirmó mediante capturas la revisión humana de las seis secciones y la comprobación final de tarjetas y Calidad en Chrome con contenido original. Las capturas no fueron adjuntadas a esta auditoría ni inspeccionadas aquí; la revisión no equivale a una auditoría de accesibilidad.
- Tras las actualizaciones sustantivas de documentación para esta auditoría se ejecutó la suite completa con el Python de `.venv`: **106 pruebas aprobadas en 79,55 segundos**, en una única ejecución. Las pruebas incluyen la exclusión de reportes corruptos o faltantes. AppTest comprueba carga y navegación técnica, no toda la interacción del navegador ni accesibilidad integral. El registro de este resultado se agregó después de la ejecución.
- `pip check` no encontró dependencias incompatibles; `git diff --check` no informó errores. Git emitió avisos de conversión LF/CRLF para archivos modificados.
- Las cinco bases originales coinciden con las huellas de `reports/01_data_quality.json` y permanecen versionadas. No se modificaron archivos originales.
- Se comprobaron las reglas que excluyen `.env`, entorno virtual, los tres espacios PAD, bases SQLite, logs, informes generados y los dos Word. La búsqueda focalizada de patrones frecuentes de secretos y rutas de usuario en candidatos no encontró coincidencias; no garantiza por sí sola la ausencia de toda información sensible.

## Dashboard y reporte histórico no verificable

El encabezado usa la sección seleccionada; las tarjetas monetarias grandes muestran millones con el valor oficial completo en su ayuda. Las tablas se formatean sobre copias, se distinguen agotados, baja rotación identificada e historial insuficiente, y se presentan candidatos IQR como advertencias estadísticas. Los filtros conservan su granularidad y el dashboard no recalcula indicadores ni ejecuta el pipeline. Las gráficas tienen nombres comerciales y un detalle diario con importes colombianos. Las recomendaciones contienen prioridad, acción, evidencia y responsable cuando existe.

La advertencia observada corresponde en la ejecución `82a5a72d-413e-432f-95f4-f17909613b4d` a la generación `51d71ac6-3c31-47d6-8cd7-b5a96b7155f8`, con clave de directorio `bdf1c15227e5da9a403082847fffb6745dc649183b48c8ccc61a7455c9ed170b`. Los tamaños y SHA-256 de sus archivos Excel y PDF coinciden con su manifiesto. Se localizó el análisis cuya huella coincide con la registrada, pero el validador actual lo rechaza con `Analysis narrative inconsistent`. Por tanto, no se demuestra corrupción de Excel o PDF; la generación **no supera la verificación integral actual** y no se habilita su descarga. No se modificaron ni regeneraron el análisis ni los reportes.

El dashboard presenta generaciones históricas verificadas y el motivo de las no verificables; no ofrece una generación parcial. Se validan manifiesto, origen, formatos, tamaños y SHA-256; cuando hay análisis asociado también se exige su validación. Si no se puede leer un manifiesto, no se presupone que pertenece a la ejecución elegida. Las huellas no son firmas digitales y no previenen cambios coordinados de fuente y manifiesto.

## Evaluación económica y estado académico

Se verificaron independientemente los tres escenarios de [evaluación económica](../docs/ECONOMIC_EVALUATION.md): ROI de 40 %, 202,5 % y 285 %; recuperación simple de 8,57, 3,97 y 3,12 meses respectivamente. Son proyecciones de primer año con costos recurrentes supuestos en cero, monetización íntegra del tiempo y demás hipótesis explícitas; no son ahorros medidos. La ejecución PAD observada tardó 11,693733 segundos de robot y no midió tiempo humano.

Fase 07 está implementada y probada técnicamente, con revisión visual comunicada por el usuario. Fases 08 y 09 tienen documentación preparada para revisión académica. El [documento académico](../docs/ACADEMIC_REPORT.md), la [guía](../docs/USER_GUIDE.md), el [guion](../docs/PRESENTATION_SCRIPT.md) y la [lista de evidencias](../docs/EVIDENCE_CHECKLIST.md) describen el alcance actual sin presentar envío real ni IA externa como funcionalidad activa.

## Riesgos y límites pendientes

La causa de `removeChild` sigue sin confirmar. Revisar el Excel de escritorio; evaluar teclado, foco, contraste y accesibilidad con herramientas y personas; definir recuperación operativa de informes históricos no verificables, respaldo, retención e historización; y probar interrupciones abruptas y concurrencia entre procesos. La regeneración histórica debe ser una operación futura explícita, autorizada y auditable. `PREPARED` es un borrador local, no un correo enviado. Durante la auditoría no se ejecutó PAD, no se enviaron correos, no se activaron servicios externos y no se hizo commit ni push.

## Candidatos locales para revisión posterior

Son 17 archivos autorizados expresamente para la publicación del Hito 05, sujetos a las verificaciones finales:

1. `.gitignore`
2. `.streamlit/config.toml`
3. `README.md`
4. `app/catalog.py`
5. `app/dashboard.py`
6. `docs/ARCHITECTURE.md`
7. `docs/CHANGELOG.md`
8. `docs/ROADMAP.md`
9. `docs/ACADEMIC_REPORT.md`
10. `docs/DASHBOARD_DESIGN.md`
11. `docs/ECONOMIC_EVALUATION.md`
12. `docs/EVIDENCE_CHECKLIST.md`
13. `docs/PRESENTATION_SCRIPT.md`
14. `docs/USER_GUIDE.md`
15. `reports/07_dashboard.md`
16. `reports/audit_hito05.md`
17. `tests/test_dashboard.py`
