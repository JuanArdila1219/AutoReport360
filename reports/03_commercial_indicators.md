# Indicadores comerciales — Fase 03

Resultados calculados sobre los datos ficticios de octubre de 2026, no sobre operación real. El histórico previamente aprobado se incorporó con validación SKIPPED y persistencia PERSISTED en la ejecución `e29e9774-b0a0-4e8c-b87b-c3118bbcab3b`; se insertaron 30 tiendas, 60 productos, 38.922 ventas, 55.800 inventarios y 930 presupuestos. Reejecución `82a5a72d-413e-432f-95f4-f17909613b4d`: SKIPPED / ALREADY_PERSISTED, cero filas insertadas.

| Indicador | Resultado |
|---|---:|
| Ventas netas | 8.001.670.200 COP |
| Unidades | 89.126 |
| Presupuesto | 2.665.932.000 COP |
| Cumplimiento | 300,15 % |
| Costo de ventas | 4.634.511.750 COP |
| Margen bruto | 3.367.158.450 COP |
| Margen porcentual | 42,08 % |
| Ticket promedio | 205.582,20 COP / transacción |
| Inventario promedio por extremos | 35.307,5 unidades |
| Rotación por unidades | 2,5243 veces |
| Agotados al 31 de octubre | 6 combinaciones tienda-producto |
| Baja rotación al 31 de octubre | 0 combinaciones con 15 días completos |

Mayor venta neta por producto: P049, 248.906.250 COP y 1.483 unidades. El ranking completo, desglose y manifiesto se encuentran en el directorio local `data/processed/82a5a72d-413e-432f-95f4-f17909613b4d/`. No se calcula crecimiento mensual frente a septiembre.

Conciliación: ventas origen y destino 8.001.670.200 COP y 38.922 filas; costo origen y destino 4.634.511.750 COP; presupuesto origen y destino 2.665.932.000 COP. Los cruces con maestros no aumentaron filas de ventas.

## Tiempos observados

Primera persistencia: validación 16,700223 s, persistencia y revalidación 9,501400 s, transformación 0,975826 s, indicadores 0,734473 s, salidas 0,099788 s, total 28,013020 s. Reejecución final: validación 16,506553 s, persistencia y revalidación 9,300740 s, transformación 1,032781 s, indicadores 1,016376 s, salidas 0,197617 s, total 28,058245 s. Son tiempos de robot de ejecuciones concretas; no se midió intervención humana.

## Límites operativos

La base comercial y el registro de validación son independientes y deben respaldarse juntos. Los maestros existentes no se actualizan: cualquier cambio de contenido para la misma clave se rechaza, por lo que se requiere política de historización. La recuperación automatizada cubre solo registros creados con el protocolo de bloqueo nuevo; registros antiguos sin marcador requieren revisión manual. El bloqueo de recuperación se implementa para Windows. El promedio de inventario usa extremos, no promedio diario. Los directorios sin manifiesto pueden ser residuos de una salida interrumpida y no deben consumirse.

## Verificación

La suite completa terminó con 23 pruebas aprobadas en 13,90 s. Las pruebas incluyen rollback, integridad referencial, reejecución, recuperación simulada y bloqueo de una ejecución activa, fórmulas, historial insuficiente y crecimiento comparable. La inspección de recuperación del registro real no encontró ejecuciones interrumpidas ni registros antiguos pendientes; la recuperación de un caso interrumpido se verificó mediante prueba aislada. Las cinco huellas de datos originales coinciden con el informe de Fase 01.
