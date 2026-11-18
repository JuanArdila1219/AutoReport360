# Datos simulados — AutoReport360
Empresa ficticia NovaRetail Colombia S.A.S. Semilla 42. Periodo 2026-10-01 a 2026-10-31. COP; fechas ISO; CSV UTF-8 con BOM, separador coma. No contienen datos reales ni personales.

- tiendas.csv: 30 filas de datos
- productos.csv: 60 filas de datos
- ventas.csv: 38,922 filas de datos
- inventarios.csv: 55,800 filas de datos
- presupuestos.csv: 930 filas de datos

## Granularidad y relaciones
- tiendas: tienda_id único; 30 tiendas.
- productos: producto_id único; 60 SKU, 20 por categoría.
- ventas: transaccion_id único; una transacción simulada contiene una línea de producto. Venta neta = unidades × precio × (1 − descuento/100); costo de venta = unidades × costo.
- inventarios: clave fecha + tienda_id + producto_id; cierre = apertura + entradas − ventas. Apertura siguiente = cierre anterior.
- presupuestos: clave fecha + tienda_id; meta de ventas en COP.
- lote_demo_2026-10-30: subconjunto de tres archivos diarios para simular adjuntos; no sumar al histórico. Catálogos permanecen como maestros.

## Uso y métricas
Cruzar por identificadores y fecha; agregar primero ventas e inventario a la misma granularidad, evitando duplicar metas. Ticket promedio = venta neta / transacciones distintas (en esta simulación cada transacción tiene una línea). Cumplimiento = ventas/meta; agotado = inventario final cero; rotación del periodo = costo de ventas / inventario promedio valorizado (apertura y cierre del periodo); no confundir con unidades vendidas. Crecimiento diario contra fecha anterior si existe.

Validaciones ejecutadas: unicidad de ventas, conciliación unidades ventas/inventarios, saldo no negativo y cobertura completa de inventarios y metas. Los archivos son datos limpios de referencia; las pruebas negativas se diseñarán después.
