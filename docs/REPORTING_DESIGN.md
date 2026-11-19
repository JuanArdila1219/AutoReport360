# Diseño de reportes — Fase 04

Fase 05.1: el Excel incorpora resumen dinámico, hallazgos, oportunidades, recomendaciones, responsables sugeridos y combinaciones agotadas. El PDF presenta hasta cinco recomendaciones priorizadas y evidencia. La huella del análisis sigue formando parte de la identidad; los indicadores proceden del contrato de Fase 03 sin recalcularse. Se conserva compatibilidad con análisis 1.0.0.

En Fase 05 `--analysis` incorpora opcionalmente hallazgos validados y recomendaciones en Excel y PDF. El SHA-256 del análisis interviene en la clave de generación. Sin ese argumento se conserva el flujo anterior. La modalidad local no se presenta como IA generativa.

El generador independiente consume los diez archivos del contrato 3.0. Comprueba manifiesto, identificadores, periodo, versión, presencia de archivos, claves y granularidad, fechas, ventas agregadas y presupuesto diario frente al resumen, y consistencia de las marcas de baja rotación. Reutiliza los indicadores oficiales; cuenta las marcas de agotado y baja rotación ya calculadas para presentarlas. El manifiesto de Fase 03 no incluye huellas de sus archivos, por lo que no puede autenticarse su procedencia retrospectivamente: las comprobaciones detectan inconsistencias, no toda manipulación coordinada.

La identidad visual centralizada en `src/reporting/theme.py` usa la paleta solicitada. El Excel incluye portada, tablero con diez indicadores, seis gráficos nativos, navegación y hojas de detalle, calidad y metodología. Las tablas vacías conservan encabezados; los valores ausentes permanecen vacíos o como «No disponible». El PDF usa ReportLab y gráficos vectoriales locales. Las conclusiones son descriptivas y no atribuyen causas.

## Ejecución

```powershell
.venv/Scripts/python.exe scripts/generate_reports.py RUTA_DE_LA_EJECUCION --output-dir reports/generated --format both
```

`--format` acepta `excel`, `pdf` o `both`. La generación es independiente y no cambia el comportamiento del pipeline. Cada combinación de archivos de origen, formato, versión y huella del generador tiene una clave SHA-256; si ya existe, se comprueban sus tamaños y huellas antes de devolver `SKIPPED`. El trabajo se escribe en un directorio temporal y se publica mediante renombrado al finalizar ambos formatos y su manifiesto. Una falla genera evidencia JSON local en `.failures/`, siempre que el destino sea escribible. No se reemplazan salidas alteradas o incompletas. Un bloqueo `.lock-*` remanente tras una interrupción abrupta requiere comprobar que no exista un proceso activo antes de retirarlo manualmente.

Cada manifiesto de generación registra ID, origen, fecha UTC, archivos, tamaños, huellas, duraciones, estado y advertencias. La calidad presentada corresponde al último lote; el contrato no informa calidad acumulada. Los reportes generados y evidencias locales permanecen ignorados por Git. No hay integración de IA, Power Automate ni envío.

## Límites y operación

La rotación se basa en unidades y promedio por extremos; el ticket supone una línea por transacción en la simulación; la baja rotación requiere 15 días completos. Septiembre no está disponible y el 300,15 % corresponde a datos ficticios. La revisión visual del PDF utiliza un renderizador de control; la apertura estructural de Excel no sustituye una revisión en Excel o LibreOffice. Faltan políticas de respaldo, retención y cambios históricos de maestros, y ensayos reales de interrupción y concurrencia.

## Auditoría del Hito 02

El Excel recibió una portada nueva, tarjetas y una hoja final de conclusiones; el PDF incorpora portada, tarjetas y acciones sugeridas. Las comparaciones registradas conservaron KPI y valores numéricos; las cuatro páginas del PDF revisado se inspeccionaron visualmente. La revisión visual del Excel en una aplicación de escritorio sigue pendiente.

**Corrección preventiva:** la versión se centralizó en `4.0.5` y la clave incluye además una huella del contenido. Se incluyen todos los `.py` directamente en `src/reporting/`, cualquier archivo no oculto de `assets/`, `resources/` y `templates/` bajo ese directorio, y las versiones instaladas de OpenPyXL, Pandas, pypdf y ReportLab. Se excluyen cachés y archivos compilados. Los nombres incluidos son relativos y no se emplean fechas ni rutas absolutas. Si se añaden dependencias de contenido fuera de esos módulos o carpetas, debe ampliarse explícitamente este alcance. El manifiesto registra versión y huella; los informes antiguos no se modifican.

El cierre del Hito 02 verificó 41 pruebas, la omisión de una repetición idéntica y la conservación de los reportes anteriores. La revisión visual del Excel en escritorio sigue pendiente. Ante un archivo de salida faltante o corrupto, el generador rechaza la reutilización y no sobrescribe; falta acordar una política de recuperación. Las pruebas reales de concurrencia e interrupción también siguen pendientes.
