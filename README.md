# AutoReport360

## Fase 06 — orquestación local

La integración con PAD fue probada manualmente según la evidencia comunicada por el usuario. La [plantilla local canónica](automation/pad_action_template.ps1) incluye `automation_id = 'NO_DISPONIBLE'` ante excepciones técnicas; no existe una exportación completa posterior a la última edición para verificar su igualdad exacta con el bloque de PAD. Ver [auditoría del Hito 04](reports/audit_hito04.md).

Fase 06.1 verifica las evidencias de lotes ya archivados antes de devolver `SKIPPED`; también permite consultar la bandeja sin procesarla. Ver [diseño](docs/AUTOMATION_DESIGN.md) y [condiciones para PAD](docs/POWER_AUTOMATE_DESKTOP_GUIDE.md).

La bandeja local, el marcador de recepción, la recuperación y la ejecución se describen en [diseño de automatización](docs/AUTOMATION_DESIGN.md); los resultados están en [evidencia de la fase](reports/06_automation.md). La integración de escritorio se documenta en la [guía de PAD](docs/POWER_AUTOMATE_DESKTOP_GUIDE.md); [Cloud](docs/POWER_AUTOMATE_CLOUD_DESIGN.md) es exclusivamente documental. No se envían correos.

## Fase 05.1 — recomendaciones comerciales

El análisis local 1.1 incorpora reglas configurables, recomendaciones sustentadas y oportunidades condicionadas. Los resultados están en [evidencia](reports/05_ai_analysis.md); las áreas y horizontes son propuestas académicas. La conexión generativa real continúa desactivada.

El cierre del Hito 03 se documenta en [auditoría](reports/audit_hito03.md) y [listado de publicación](reports/publication_hito03.txt). La revisión del Excel en escritorio y la activación real de proveedores permanecen pendientes.

## Fase 05 — análisis comercial

`.venv/Scripts/python.exe scripts/run_ai_analysis.py RUTA_ORIGEN --mode local` genera un JSON de reglas locales. Para enriquecer reportes: `.venv/Scripts/python.exe scripts/generate_reports.py RUTA_ORIGEN --analysis RUTA_ANALISIS.json --format both`. La CLI no conecta servicios y ante indisponibilidad usa contingencia local. Consultar [diseño](docs/AI_ANALYSIS_DESIGN.md), [contrato](docs/AI_OUTPUT_CONTRACT.md) y [evidencia](reports/05_ai_analysis.md).

Trabajo final de Automatizaciones de la Especialización en Analítica de Datos de UNAULA. El proyecto plantea automatizar la consolidación, validación, análisis y distribución de información comercial de la empresa ficticia NovaRetail Colombia S.A.S.

**Estado:** fases 00 a 06.2 implementadas; el Hito 04 consolida la integración local con PAD. El usuario confirmó pruebas manuales de PAD; la igualdad exacta del bloque requiere una exportación para compararse. No hay aplicación Streamlit ni envío de correo.

## Instalación local en Windows

Con Python 3.12 instalado, desde la raíz del proyecto: `python -m venv .venv`, seguido de `.venv\Scripts\python.exe -m pip install -r requirements.txt`. Para comprobar el entorno: `.venv\Scripts\python.exe -m pip check` y `.venv\Scripts\python.exe -m pytest -q`. La instalación requiere acceso a los paquetes y no se realizó durante esta auditoría.

## Contexto y alcance previsto

Inteligencia Comercial cuenta con 30 tiendas, 60 productos de textil, calzado y accesorios y 5 analistas; la moneda es COP. El flujo previsto recibe archivos, valida y consolida datos, calcula indicadores, genera reportes y resúmenes con IA configurable y distribuye resultados. La integración de servicios externos requiere autorización previa.

Indicadores previstos: ventas, unidades, cumplimiento presupuestal, ticket promedio, rotación, agotados, productos más vendidos, baja rotación y crecimiento de ventas. Sus fórmulas y datos necesarios se acordarán antes de implementarlos.

## Supuestos académicos

Se plantean 60 minutos manuales frente a 5 minutos de intervención humana por ejecución, 22 ejecuciones mensuales, costo de hora de 25.000 COP, inversión inicial de 2.000.000 COP y ROI proyectado de 202,5 %. **Son supuestos, no resultados medidos.** La duración del robot es independiente del tiempo de intervención humana. La fórmula, horizonte y costos incluidos en el ROI deben documentarse y verificarse en la evaluación económica.

## Organización y próximos pasos

Los documentos de trabajo se encuentran en [docs](docs/PROJECT_SPEC.md); el plan está en [docs/ROADMAP.md](docs/ROADMAP.md) y la arquitectura en [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). Los datos ficticios incorporados se conservan en `data/simulated/` sin sobrescritura ni regeneración.

Se emplean Python, Pandas, OpenPyXL y Pytest; el análisis local está implementado. Streamlit, Power Automate Cloud y las conexiones reales de IA siguen sujetos a autorización y trabajo posterior.

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
