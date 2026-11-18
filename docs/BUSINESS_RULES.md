# Reglas de negocio y control

- Se rechazan archivos requeridos ausentes, columnas obligatorias ausentes, tipos incorrectos, nulos, números negativos, llaves duplicadas, descuentos fuera de 0–100, fechas inválidas o incompatibles con el nombre y referencias desconocidas.
- Se valida venta neta = unidades × precio × (1 − descuento/100), costo de venta contra maestro, costo de inventario contra maestro y saldo inicial + entradas − ventas = saldo final. Las unidades de ventas se concilian por fecha, tienda y producto; inventarios y presupuestos deben cubrir las combinaciones requeridas. Se comprueba continuidad entre días consecutivos disponibles.
- IQR (1,5 veces el rango intercuartílico) genera advertencias, no eliminación ni rechazo. Con IQR cero puede señalar numerosos casos válidos.
- Se registran claves transaccionales aprobadas y huellas del contenido. Si todas coinciden, se omite el lote; si hay solapamiento parcial o cambios en claves ya aprobadas se rechaza para revisión. Los maestros se validan en cada ejecución pero no se reservan como transacciones. El lote diario de demostración no se suma al histórico.
- Una excepción inesperada termina en FAILED y no reserva claves; se puede reintentar. Una ejecución terminada APPROVED reserva claves en la misma transacción que su resultado.

## Definiciones propuestas para fases futuras

Baja rotación: producto con inventario disponible y sin ventas durante los últimos 15 días, sujeto a historial suficiente. Agotado: inventario final igual a cero. Crecimiento: comparación diaria y semanal con periodos equivalentes disponibles; no calcular crecimiento mensual frente a septiembre sin datos. Las fórmulas implementadas están en [KPI_DEFINITIONS.md](KPI_DEFINITIONS.md).

La aprobación de validación y la persistencia son estados distintos. La segunda se realiza en transacción SQLite independiente; un lote omitido por validación puede incorporarse si aún no fue persistido. Las claves existentes con contenido diferente se rechazan, incluidos cambios en maestros.
