# Evidencia de validación — Fase 02

Ejecuciones locales del 18 de noviembre de 2026, con `.venv/Scripts/python.exe`. Las duraciones son tiempo del proceso medido en esa ejecución, no tiempo de intervención humana ni estimación de ahorro.

| Caso | ID | Estado | Duración del proceso |
|---|---|---|---:|
| Histórico completo, 95.742 filas incluidas maestras | cfa71922-89a6-48bb-983d-ef3bd2d4d985 | APPROVED | 19,964893 s |
| Lote del 30 de octubre posterior al histórico | c3406447-0aba-4cd9-96f0-dc0b74d8c419 | SKIPPED | 2,553598 s |
| Directorio sin los cinco archivos obligatorios | fecc87d7-dd8e-4cc8-b9e8-e2fd014c8188 | REJECTED | 0,085264 s |

El lote diario tuvo 3.063 claves transaccionales coincidentes y ninguna con contenido distinto. El histórico tuvo cinco advertencias agregadas IQR, sin errores críticos. El rechazo identificó los cinco archivos faltantes. Los JSON completos y SQLite se conservan localmente bajo `logs/phase02_final/` y `logs/phase02_invalid/`; están ignorados por Git por contener rutas locales. El tiempo de intervención humana no se midió.

## Límites

El control depende de conservar el mismo SQLite: usar otro directorio de estado inicia un historial independiente. Las aprobaciones guardan claves y huellas, no una copia consolidada ni datos listos para el siguiente motor. Las columnas y llaves son configurables, pero las reglas y relaciones comerciales están codificadas. La validación usa maestros actuales y cobertura completa de combinaciones; no contempla tiendas o productos activos solo durante una parte del periodo. CSV requiere UTF-8 y coma; XLSX usa la primera hoja. Una interrupción abrupta puede dejar una ejecución en VALIDATING; requiere inspección operativa. La persistencia no puede garantizar evidencia si el almacenamiento falla. El sistema no mide intervención humana.
