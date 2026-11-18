# Definiciones de indicadores comerciales

## Actualización Fase 03 — versión 3.0

Esta sección sustituye las fórmulas propuestas previamente cuando difieren. Ventas = suma de venta neta; unidades = suma vendida; cumplimiento = 100 × ventas / presupuesto; ticket = ventas / transacciones únicas válidas; margen bruto = ventas − costo; margen porcentual = 100 × margen / ventas. Las sumas se agregan antes de dividir; denominador cero produce no disponible. Presupuesto solo se asigna a día, tienda o total, nunca categoría/producto.

Rotación = unidades vendidas / inventario promedio en unidades. El promedio es (existencia inicial del primer día + existencia final del último día)/2, agregadas al mismo nivel; es aproximación por extremos y requiere cobertura completa. Agotados = combinaciones tienda-producto con inventario final cero en el corte. Baja rotación = existencia positiva y cero ventas en los últimos 15 días incluidos, con 15 fechas completas; de lo contrario no disponible. Ranking ordena descendentemente por ventas y por unidades, con desempate por producto_id; incluye productos con ventas.

Crecimiento diario compara con el día anterior; semanal compara dos ventanas móviles consecutivas de siete días completos. No se calcula si falta un periodo o el denominador es cero. No se calcula crecimiento mensual frente a septiembre. No se redondean resultados intermedios ni se suman porcentajes.

## Referencia histórica de Fase 01

Las fórmulas son propuestas para este lote, no resultados calculados. Aplicar filtros y periodos coherentes; ante denominador cero o datos ausentes, informar «no disponible», nunca cero por defecto.

| Indicador | Fórmula y unidad | Fuentes y granularidad / reglas |
|---|---|---|
| Ventas | Σ venta_neta_cop, COP | Ventas por período, tienda o producto. |
| Unidades | Σ unidades, unidades | Ventas por período, tienda o producto. |
| Cumplimiento presupuestal | 100 × Σ venta_neta_cop / Σ meta_ventas_cop, % | Agregar ventas y metas separadamente por tienda y fecha antes de unir; luego agregar al período. No duplicar metas por producto; no hay presupuesto por producto. |
| Ticket promedio | Σ venta_neta_cop / número de transacciones distintas, COP/transacción | Ventas por período y tienda. El lote define una línea por transacción; no generalizar a datos futuros sin identificar tickets. |
| Rotación de inventario | Σ costo_venta_cop / [(valor inicial + valor final)/2], veces por período | Ventas e inventarios por tienda/producto; valorar existencias iniciales del primer día y finales del último al costo unitario. Agregar valores antes de dividir. Es aproximación basada en extremos, no promedio diario. |
| Agotados | Conteo de combinaciones tienda-producto con inventario_final = 0, unidades de combinaciones; opcional porcentaje sobre combinaciones observadas | Inventarios al cierre de una fecha. No sumar cierres diarios como si fueran productos únicos. |
| Productos más vendidos | Orden descendente por Σ unidades; desempatador producto_id | Ventas agrupadas por producto y período; expresar unidades, y aclarar si se usa venta neta en lugar de unidades. |
| Baja rotación | Orden ascendente por Σ unidades, incluyendo productos sin ventas mediante catálogo; umbral pendiente de aprobación | Catálogo y ventas por producto y período; no confundir con la rotación financiera. Sin umbral no clasificar automáticamente. |
| Crecimiento de ventas | 100 × (ventas período actual − ventas período comparable) / ventas período comparable, % | Ventas agregadas a igual alcance; solo comparar si existe período anterior y su valor es distinto de cero. Octubre permite comparación diaria desde el día 2; no permite crecimiento mensual frente a septiembre. |
