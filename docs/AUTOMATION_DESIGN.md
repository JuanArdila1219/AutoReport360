# Orquestación local — Fase 06

## Fase 06.1: lotes archivados y consulta

**Política conservadora del Hito 04:** no regenerar automáticamente informes de lotes archivados por cambios del generador. Conservar la ejecución original, sus artefactos y huellas. Una futura regeneración requerirá una operación explícita, autorizada y auditable, que todavía no está implementada. No se debe reingresar un lote archivado con el propósito de regenerarlo: el mecanismo existente de reingreso puede crear informes cuando cambian componentes y no constituye dicha operación autorizada.

Al solicitar un lote ausente de `pending` y `processing`, el orquestador busca una ejecución exitosa previa del mismo nombre y verifica recepción archivada, diario, fuente, análisis, manifiesto y huellas de reportes, además del borrador y su estado de invalidación. Solo entonces devuelve `SKIPPED`, `reason: ALREADY_PROCESSED_VERIFIED` y `distribution_status: NOT_DUPLICATED`, sin ejecutar el pipeline ni regenerar o preparar otra distribución. Los registros se cotejan por integridad y consistencia; no son firmas criptográficas. Un historial ambiguo o alterado devuelve `FAILED` con `AMBIGUOUS_HISTORY` o `HISTORY_UNVERIFIED`.

Un nombre sin recepción comprobable devuelve `FAILED` y `BATCH_NOT_RECEIVED`; si se recibió pero fue rechazado o falló, el motivo es `BATCH_PREVIOUSLY_REJECTED` o `BATCH_PREVIOUSLY_FAILED`. Un lote sin marcador devuelve `FAILED` y `BATCH_INCOMPLETE`; un lote inválido usa `INVALID_BATCH` (su estado puede ser `REJECTED` o `FAILED` según la etapa); otros errores usan `TECHNICAL_ERROR`. `inbox_status` indica `EMPTY` o `PENDING` cuando la consulta no procesa un lote. Los códigos de salida existentes se conservan.

Para consultar carpetas pendientes sin ejecutar ni crear estado: `.venv/Scripts/python.exe scripts/run_automation.py --workspace RUTA --list-pending`. El JSON devuelve `EMPTY`/`INBOX_EMPTY` o `PENDING`/`PENDING_BATCHES` con nombres y presencia del marcador; no certifica todavía sus huellas. Esta consulta por CLI no modifica el lanzador PowerShell existente.

`scripts/run_automation.py` reutiliza el pipeline de Fase 03, el análisis local y el generador de reportes. Un espacio de trabajo independiente contiene `pending`, `processing`, `processed`, `rejected`, `failed`, `state`, `runs`, `outbox`, `analysis`, `reports`, `processed_data` y `quarantine`. No configure ese espacio dentro de los datos originales. El lote permanece en estas carpetas como copia: sus archivos no se editan. Los originales externos siguen bajo responsabilidad de quien prepara la recepción.

## Recepción

Copie los archivos del lote a `pending/NOMBRE/`. Solo cuando estén completos, cree `READY.json` con `batch_id`, `received_at` y `files`: mapa de cada ruta relativa a su SHA-256 hexadecimal. Ejemplo de forma (el valor debe ser el hash real):

```json
{"batch_id":"lote-01","received_at":"2026-10-01T00:00:00Z","files":{"ventas.csv":"SHA256_REAL"}}
```

El ejemplo ilustra el formato, no constituye un lote completo. Deben declararse todos los archivos y no puede haber archivos adicionales. Los maestros pueden estar en la raíz de un histórico o en `masters/` para un lote diario; deben figurar en el manifiesto. Los nombres y coberturas siguen [contratos de entrada](DATA_CONTRACTS.md). Un marcador ausente no mueve ni procesa el lote. Un hash incorrecto falla y se registra una alerta local. El productor debe escribir el marcador únicamente al terminar la descarga y cerrar los archivos; idealmente crear el marcador mediante renombrado atómico.

```powershell
.venv/Scripts/python.exe scripts/run_automation.py NOMBRE --workspace "C:\ruta\espacio local"
```

La CLI admite solo `--mode local`, emite un único JSON y devuelve 0 para `SUCCESS`/`SKIPPED`, 2 para `REJECTED`, 1 para `FAILED`. La ruta anterior es ilustrativa. Los archivos `runs/*.json` registran etapas, duraciones, identificadores, inserciones, advertencias y estado de preparación; las subetapas del pipeline están en `stages.pipeline.details.times_seconds`. `robot_seconds` mide el proceso local; no mide intervención humana ni espera previa a la invocación.

## Idempotencia y recuperación

La clave del lote deriva del contenido y nombres relativos declarados, incluidos maestros. Se serializa todo el espacio mediante creación atómica de `.automation.lock`. El diario conserva la salida del pipeline tras éxito; las repeticiones reutilizan esa salida y las huellas de análisis y reporte determinan si se regeneran. Un lote ya persistido fuera de este diario no crea un borrador automáticamente. El borrador comercial tiene identidad determinística por lote; un cambio de diseño puede producir informes nuevos sin crear otro borrador ni enviar nada. Se verifica la integridad y la relación con el análisis antes de prepararlo.

Ante fallo se mueve la copia a `failed` y se prepara solo una alerta local. Para reintentar, copie el lote preservado a `pending` con el mismo nombre y manifiesto; no reinicialice las bases. Un proceso interrumpido puede dejar un lote en `processing` o el bloqueo: verificar primero que no hay proceso activo y respaldar el espacio antes de intervenir. Un aborto abrupto inmediatamente después de persistir y antes de escribir el diario puede requerir revisión manual; no se considera automáticamente distribuido. La escritura interrumpida de un borrador se rechaza para revisión en lugar de sobrescribirla.

Si el generador detecta un reporte anterior alterado, falla sin reemplazarlo. Solo con `--recover-corrupt` se comprueba la generación registrada, se mueve íntegra a `quarantine` con nombre único y se intenta regenerar; no se crea una nueva distribución si ya existía. Si había un borrador comercial, se crea un marcador `invalidated-ID.json`: el borrador histórico queda conservado pero no debe utilizarse, aunque apunte a una ruta regenerada; requiere revisión manual y nuevas huellas. No utilizar esta opción para un daño no verificado o una generación diferente. Conservar y respaldar cuarentena, diarios, SQLite y fuentes conjuntamente. No se ha validado la recuperación ante cortes reales del sistema ni el bloqueo en recursos de red.

`PREPARED` significa borrador local, nunca envío. `NOT_DUPLICATED` indica que no se preparó otro borrador. Los borradores se guardan en `outbox` y pueden incluir rutas locales; no publicarlos. No hay correo real ni proveedor IA externo.
