# Auditoría del Hito 01 — fases 00 a 03

Fecha de auditoría: 18 de noviembre de 2026. Alcance: código, pruebas, documentación, archivos simulados, controles locales y candidatos de Git. El listado autorizado está en `reports/publication_hito01.txt`.

## Resultado y restricciones de publicación

La suite y las conciliaciones revisadas son satisfactorias para el conjunto simulado, con las limitaciones descritas aquí. La plantilla académica original contiene nombres personales en metadatos de autor y última modificación. La especificación Word se inspeccionó en cuerpo, metadatos, relaciones, XML personalizado y miniatura; no se identificaron datos personales o credenciales en los componentes examinados. Esta inspección no constituye una garantía absoluta de ausencia de información sensible. Por decisión del usuario se excluyen ambos documentos Word de la publicación y se conservan intactos localmente.

Se inspeccionaron los archivos candidatos mediante búsqueda de patrones de credenciales, correo y rutas locales; no se identificaron coincidencias sensibles en el texto examinado. La búsqueda por patrones no garantiza detectar todos los secretos. `.env.example` es una plantilla sin credenciales; `.env` y variantes privadas, cachés, `.venv`, logs, datos procesados y SQLite quedan excluidos. Se añadieron patrones genéricos para SQLite y `.db`. Los cinco CSV ficticios y su README están incluidos explícitamente en el listado autorizado.

## Fuentes e integridad

Los cinco CSV de `data/simulated/` coinciden por SHA-256 tanto con los originales del Hito 1 como con el informe de Fase 01. Los dos Word copiados coinciden con sus originales. No se modificaron los datos originales. La base comercial SQLite existente pasó `integrity_check`, tiene cero violaciones de `foreign_key_check` y contiene 30 tiendas, 60 productos, 38.922 ventas, 55.800 inventarios y 930 presupuestos; `row_lineage` contiene 95.742 filas. El SQLite de validación también pasó `integrity_check`.

Antes del commit se detectó que Git normalizaba los finales de línea de los CSV. `.gitattributes` desactiva esa conversión para conservar en el repositorio los bytes de las fuentes autorizadas.

## Pruebas y dependencias

Ejecutado con `.venv/Scripts/python.exe` en la auditoría: `pytest -q`, **23 pruebas aprobadas en 35,52 s**; `pip check`, sin dependencias rotas. Las pruebas cubren casos válidos y negativos, integridad, rollback, reejecución y recuperación simulada. No se ha efectuado una prueba de recuperación mediante terminación real de proceso; la cobertura automatizada no demuestra todos los fallos posibles del sistema de archivos.

En la comprobación previa de publicación se repitió la suite: **23 pruebas aprobadas en 8,42 s**, y `pip check` volvió a indicar que no hay dependencias rotas.

## Auditoría de indicadores

- **Ticket:** 8.001.670.200 COP / 38.922 transacciones distintas = 205.582,19515955 COP. Hay 38.922 filas, 38.922 identificadores distintos y ninguno nulo. El material de origen afirma una línea por transacción para esta simulación; la comprobación de unicidad no demuestra por sí sola esa semántica para datos futuros. El código requiere identificadores no vacíos y únicos. No extrapolar la fórmula a fuentes con varias líneas por ticket sin adaptar el contrato y la lógica.
- **Cumplimiento:** 8.001.670.200 / 2.665.932.000 × 100 = 300,1453225 %, redondeado 300,15 %. Ventas y metas abarcan octubre de 2026 y se compararon a nivel tienda-fecha sin multiplicar metas. Los 930 presupuestos son únicos, ninguno es cero y los 930 días-tienda superan 100 % individualmente (rango aproximado 136,21 %–572,96 %). El valor elevado refleja la relación observada en estas bases simuladas; no se dispone del generador ni de evidencia para afirmar la intención o causa de esa relación. No es un resultado empresarial real.
- **Rotación:** 89.126 unidades / ((45.437 iniciales + 25.178 finales)/2) = 2,52427954 veces. Es rotación en unidades al nivel global, con promedio por extremos, no promedio diario ni rotación valorizada a costo. La especificación académica original propone una fórmula valorizada distinta: es un documento histórico; prevalece la definición explícita de Fase 03 en `docs/KPI_DEFINITIONS.md`. Comparar periodos o niveles requiere igual cobertura y unidades coherentes.
- **Baja rotación:** comprobación independiente en el histórico al 31 de octubre: 0 combinaciones con stock positivo y cero ventas en 15 días completos; 0 combinaciones con historial insuficiente y 6 agotadas. Escenarios aislados en memoria: 15 días sin ventas y stock positivo → verdadero; una venta → falso; stock final cero → falso y agotado; un día faltante → no disponible. Los escenarios no modificaron las fuentes.

## Recuperación y duplicados

La validación serializa las ejecuciones actuales con bloqueo de archivo Windows; recuperación solo cambia registros con el protocolo nuevo y tras adquirirlo, dejando intactos registros heredados sin marcador. El mecanismo no es multiplataforma y no recupera automáticamente ejecuciones antiguas. La persistencia usa transacciones SQLite, claves únicas y foráneas; los conflictos se rechazan y un lote previamente aprobado puede persistirse. La deduplicación depende de conservar los registros de estado y los respaldos coherentes; cambiar de directorio de estado crea un historial independiente. El resultado APPROVED de validación no demuestra persistencia exitosa. Los cambios de maestros se rechazan y requieren política futura de historización. Se recomienda probar interrupciones abruptas y concurrencia entre procesos en una siguiente revisión.

## Decisiones pendientes

Ambos Word quedan fuera del listado autorizado y permanecen localmente sin modificar. La fórmula de rotación valorizada de la especificación histórica difiere de la versión implementada; se conserva esta aclaración en Markdown. Los CSV representan datos ficticios autorizados, no datos operacionales. El usuario autorizó expresamente el primer commit y push sujetos a comprobaciones satisfactorias.
