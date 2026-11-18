# Contratos de salida — versión 3.0

Cada ejecución exitosa crea un directorio UUID en `data/processed/`. `manifest.json` identifica ejecución, validación, periodo global persistido, corte y versión de fórmulas; acompaña a cada CSV. Los datos representan el acumulado persistido. Los CSV usan UTF-8 con BOM; campos vacíos representan indicador no disponible.

| Archivo | Granularidad y contenido |
|---|---|
| summary.json | Totales comerciales, periodo y conciliación de ventas, costos, presupuestos y filas. |
| daily.csv | Una fila por fecha con meta, métricas y crecimiento diario/semanal. |
| stores.csv | Una fila por tienda, métricas y presupuesto agregado. |
| cities.csv | Una fila por ciudad, métricas y presupuesto agregado por tienda y fecha. |
| categories.csv | Una fila por categoría con ventas; sin presupuesto. |
| ranking.csv | Producto y categoría, ventas, unidades y puestos independientes. |
| inventory.csv | Tienda-producto al corte, saldo, agotado, historial de 15 días y baja rotación nullable. |
| low_rotation.csv | Subconjunto de baja rotación; mantiene encabezados aunque esté vacío. |
| quality.json | Estado, errores y advertencias del último lote validado. |
| manifest.json | Identificadores, periodo, corte y versión 3.0. |

El manifiesto se escribe al final; no consumir directorios sin manifiesto. Sin historial completo no se evalúa baja rotación; sin periodos comparables o denominador distinto de cero, el crecimiento es nulo. Son salidas estructuradas, no reportes ejecutivos.
