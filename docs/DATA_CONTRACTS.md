# Contratos de entrada — Fase 02

La configuración ejecutable está en `config/data_contracts.json`; sus campos corresponden al [diccionario](DATA_DICTIONARY.md). Cada campo es obligatorio. Tipos: texto no vacío, entero no negativo o fecha ISO `AAAA-MM-DD`; descuento entre 0 y 100. CSV UTF-8 (BOM opcional), separado por comas; Excel `.xlsx`, primera hoja. Se permiten columnas adicionales. Una fila representa la granularidad indicada.

| Tabla | Clase | Archivo histórico | Clave primaria / granularidad | Relaciones |
|---|---|---|---|---|
| tiendas | maestra | tiendas.csv o .xlsx | tienda_id | — |
| productos | maestra | productos.csv o .xlsx | producto_id | — |
| ventas | transaccional | ventas.csv o .xlsx | transaccion_id | tienda_id y producto_id a sus maestros |
| inventarios | transaccional | inventarios.csv o .xlsx | fecha, tienda_id, producto_id | tienda_id y producto_id a sus maestros |
| presupuestos | transaccional | presupuestos.csv o .xlsx | fecha, tienda_id | tienda_id a tiendas |

El histórico requiere las cinco tablas. Un lote diario requiere `ventas_AAAA-MM-DD`, `inventarios_AAAA-MM-DD` y `presupuestos_AAAA-MM-DD` con extensión CSV o XLSX y la misma fecha; toma maestros sin sufijo de la entrada o del directorio maestro indicado. La fecha interna debe coincidir con el sufijo. Se exigen inventarios por cada fecha, tienda y producto del intervalo y presupuesto por tienda y fecha; se rechazan fechas intermedias sin cobertura. Los archivos con nombres de datos no reconocidos, formatos no admitidos o más de un archivo por tabla se rechazan. Otros documentos se ignoran.

La configuración define nombres, campos, tipos y llaves; relaciones y reglas comerciales están implementadas en código y no se generan automáticamente desde el JSON. La fecha identifica el periodo observado, no certifica que un histórico incluya periodos externos no entregados.
