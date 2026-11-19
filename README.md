# AutoReport360

Trabajo final de Automatizaciones de la Especialización en Analítica de Datos de UNAULA. El proyecto plantea automatizar la consolidación, validación, análisis y distribución de información comercial de la empresa ficticia NovaRetail Colombia S.A.S.

**Estado:** Fase 04: validación, persistencia, indicadores y reportes locales Excel/PDF. No hay aplicación Streamlit ni integraciones externas.

## Contexto y alcance previsto

Inteligencia Comercial cuenta con 30 tiendas, 60 productos de textil, calzado y accesorios y 5 analistas; la moneda es COP. El flujo previsto recibe archivos, valida y consolida datos, calcula indicadores, genera reportes y resúmenes con IA configurable y distribuye resultados. La integración de servicios externos requiere autorización previa.

Indicadores previstos: ventas, unidades, cumplimiento presupuestal, ticket promedio, rotación, agotados, productos más vendidos, baja rotación y crecimiento de ventas. Sus fórmulas y datos necesarios se acordarán antes de implementarlos.

## Supuestos académicos

Se plantean 60 minutos manuales frente a 5 minutos de intervención humana por ejecución, 22 ejecuciones mensuales, costo de hora de 25.000 COP, inversión inicial de 2.000.000 COP y ROI proyectado de 202,5 %. **Son supuestos, no resultados medidos.** La duración del robot es independiente del tiempo de intervención humana. La fórmula, horizonte y costos incluidos en el ROI deben documentarse y verificarse en la evaluación económica.

## Organización y próximos pasos

Los documentos de trabajo se encuentran en [docs](docs/PROJECT_SPEC.md); el plan está en [docs/ROADMAP.md](docs/ROADMAP.md) y la arquitectura preliminar en [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). Los archivos recibidos se preservarán en `data/raw/` y los datos ficticios existentes en `data/simulated/`, sin sobrescritura ni regeneración. No se incluyen datos en esta inicialización.

Se emplean Python, Pandas, OpenPyXL y Pytest para el perfilamiento y sus pruebas. Streamlit, Power Automate e IA configurable se contemplan para etapas posteriores, sujetos a diseño y autorización.

## Fase 01 — datos simulados

Se incorporaron cinco fuentes de octubre de 2026 y dos documentos académicos; sus resultados se encuentran en [calidad de datos](reports/01_data_quality.md), [diccionario](docs/DATA_DICTIONARY.md) y [definiciones de indicadores](docs/KPI_DEFINITIONS.md). Ejecutar `.venv/Scripts/python.exe scripts/profile_data.py` para regenerar los informes y `.venv/Scripts/python.exe -m pytest -q` para las pruebas. El script lee los CSV sin modificarlos y sobrescribe los informes generados.

Entorno comprobado: Python 3.12.7, Pandas 3.1.1, NumPy 2.5.5, OpenPyXL 3.1.5, Streamlit 1.67.0 y Pytest 9.2.0; `pip check` satisfactorio. Las versiones directas están fijadas en requirements, no las transitivas; para reproducibilidad completa se requiere un bloqueo de dependencias específico de plataforma.

Solo los cinco CSV y su README de origen están habilitados explícitamente para versionarse en `data/simulated/`; los demás datos siguen ignorados. La carpeta original del Hito 1 está ignorada para evitar duplicación, pero permanece intacta. El lote diario es un subconjunto y no debe sumarse al histórico.

## Fase 02 — validación local

Ejecutar `.venv/Scripts/python.exe scripts/run_validation.py data/simulated`. Para un lote diario, pasar su directorio; opcionalmente usar `--master-dir RUTA` y `--state-dir RUTA`. La salida JSON incluye el estado y el proceso devuelve 0 para APPROVED/SKIPPED y 1 para REJECTED/FAILED. El registro predeterminado en `logs/validation/` contiene SQLite, JSON por ejecución y log; conservarlo para mantener la deduplicación. El comando no mueve ni modifica los archivos de entrada.

Consultar [contratos](docs/DATA_CONTRACTS.md), [reglas](docs/BUSINESS_RULES.md) y [evidencia de la fase](reports/02_validation_engine.md). El CLI puede invocarse en una integración futura, sin servicios conectados actualmente.

## Fase 03 — pipeline local

Ejecutar `.venv/Scripts/python.exe scripts/run_pipeline.py data/simulated`. Opciones: `--state-dir`, `--output-dir` y `--master-dir`. Código de salida: 0 éxito (incluye reejecución idempotente), 2 rechazo y 1 fallo. La validación puede ser SKIPPED y la persistencia PERSISTED cuando el lote se aprobó antes sin persistirse. Las salidas por ejecución se describen en [contratos de salida](docs/DATA_OUTPUT_CONTRACTS.md) y [KPI](docs/KPI_DEFINITIONS.md).

Para recuperar ejecuciones interrumpidas del protocolo nuevo: `.venv/Scripts/python.exe scripts/recover_validation.py logs/validation`. El comando requiere el bloqueo de validación libre y no altera registros antiguos sin marcador. No borrar las bases de estado: SQLite comercial y de validación, evidencia y originales deben respaldarse juntos.

## Auditoría y publicación inicial

La [auditoría del Hito 01](reports/audit_hito01.md) documenta validaciones, resultados y riesgos. El [listado autorizado](reports/publication_hito01.txt) excluye ambos Word académicos, que permanecen locales; la plantilla contiene metadatos personales. El 300,15 % de cumplimiento es una característica observada en los datos ficticios, no un resultado real. La rotación implementada usa unidades y promedio de inventario por extremos, distinta de la propuesta valorizada del documento histórico.

## Fase 04 — reportes locales

Ejecutar `.venv/Scripts/python.exe scripts/generate_reports.py RUTA_DE_LA_EJECUCION --output-dir reports/generated --format both`. También se admite `excel` o `pdf`. El destino contiene un directorio por combinación de origen, formato y versión, con manifiesto y huellas; las solicitudes idénticas se omiten tras verificar los archivos. La ejecución del pipeline sigue igual. Los resultados generados no se incluyen en Git. Consultar [diseño](docs/REPORTING_DESIGN.md) y [evidencia](reports/04_automated_reporting.md).

**Auditoría Hito 02:** se corrigió la reutilización de informes anteriores mediante versión y huella del generador en la clave de idempotencia. Véase [audit_hito02.md](reports/audit_hito02.md). Permanecen pendientes la revisión visual del Excel en escritorio, la política de recuperación de reportes corruptos y las pruebas reales de concurrencia e interrupción.
