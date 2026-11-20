# Auditoría del Hito 04 — automatización y Power Automate Desktop

Fecha: 19 de noviembre de 2026. Alcance: cambios locales de las fases 06, 06.1 y 06.2 posteriores al Hito 03. La auditoría inicial recomendó correcciones; su resolución y la recomendación actual se registran al comienzo de este informe. No se ha realizado commit ni push de este hito.

## Resolución del hallazgo

**Recomendación técnica actual: APTO PARA PUBLICACIÓN**, con las limitaciones y pendientes señalados en este informe. La publicación requiere autorización independiente del usuario; no se han realizado commit ni push.

En la revisión previa a la publicación autorizada se corrigieron afirmaciones históricas de arquitectura, roadmap y evidencia que no reflejaban las pruebas manuales posteriores de PAD. La suite se repitió con **96 pruebas aprobadas en 230,02 segundos**; `pip check` y `git diff --check` no encontraron errores y los cinco CSV originales conservaron sus huellas. La comprobación por patrones de los candidatos no encontró rutas personales, correos ni formatos habituales de credenciales; no garantiza detectar todos los posibles secretos. La equivalencia exacta del bloque de PAD sigue sin poder comprobarse sin una exportación completa.

La plantilla local canónica ahora incluye `automation_id = 'NO_DISPONIBLE'` dentro de `result` ante una excepción técnica. La prueba ejecuta una excepción controlada en un bloque temporal y verifica el valor; otra prueba lo verifica cuando falta Python. No existe una instrucción temporal de prueba en la plantilla. Se conserva la diferencia entre las pruebas automatizadas locales y las pruebas manuales en PAD informadas por el usuario: no se ejecutó PAD ni se alteró su configuración en esta corrección, y sin una exportación completa posterior a la última edición no puede afirmarse igualdad exacta entre ambos bloques.

La política acordada es no regenerar automáticamente los lotes archivados por cambios en el generador y preservar los artefactos y huellas originales. Una regeneración futura requiere una operación explícita, autorizada y auditable, que aún no existe. El reingreso de un lote puede generar informes si cambian componentes y no debe utilizarse como sustituto de esa operación.

Validación de la corrección: **96 pruebas aprobadas en 204,45 segundos**, `pip check` sin incompatibilidades y `git diff --check` sin errores. Las cinco huellas originales coinciden con el perfil de Fase 01. La búsqueda por patrones en los 17 candidatos no identificó rutas personales, correos ni formatos habituales de credenciales; es una comprobación limitada. Los tres espacios PAD, `.env`, `.venv`, cachés, documentos Word, logs y reportes generados se comprobaron como ignorados. El área de staging está vacía.

## Hallazgo inicial — corregido

En la auditoría inicial la respuesta de excepción de `automation/pad_action_template.ps1` no contenía `automation_id = 'NO_DISPONIBLE'`, campo indicado por el usuario. La corrección posterior se describe arriba; el bloque completo de PAD sigue sin estar disponible para comparación exacta.

La cadena de prueba controlada no aparece en la plantilla PowerShell definitiva local; sí aparece intencionalmente en `tests/test_pad_action_template.py` como parte de una prueba aislada. No debe confundirse esa prueba con una excepción activa en el bloque.

## Comprobaciones ejecutadas

- `.venv/Scripts/python.exe -m pytest -q`: **95 pruebas aprobadas en 315,35 s**. `pip check`: sin dependencias incompatibles. `git diff --check`: sin errores; Git advirtió posibles conversiones de finales de línea.
- Las cinco bases ficticias originales coincidieron con los SHA-256 documentados en `reports/01_data_quality.json`.
- Se revisaron los registros locales de las tres bandejas PAD: existen ejecuciones con `SUCCESS`, `SKIPPED`, `REJECTED` y `FAILED`. Para las dos ejecuciones exitosas se cotejaron recepción, fuente, análisis, manifiestos, huellas de los dos reportes y correspondencia de los adjuntos del borrador. Los borradores figuran `PREPARED`, no enviados.
- La ejecución integral `2245f126-16f5-4417-9e0a-c34434f0abad` registra 95.742 filas insertadas, `SUCCESS`, `PREPARED`, cinco advertencias y 11,693733 segundos de robot. El registro `3d319371-e351-4cca-b826-4ca6939787f8` registra `SKIPPED` y 0,268634 segundos. No se midió tiempo de intervención humana.
- El usuario confirmó además pruebas manuales en PAD de cuatro notificaciones, detención con JSON inválido y captura de excepción PowerShell. Estas observaciones provienen de su confirmación; no se ejecutaron nuevamente en esta auditoría ni hay aquí una copia verificable del flujo visual completo.
- Las pruebas automatizadas cubren duplicados, recuperación de etapas, verificación de reportes, cuarentena y excepciones con procesos simulados. La ejecución concurrente comprobada se limita a hilos en un proceso; no constituye una prueba de interrupción real o de concurrencia entre procesos y máquinas.
- La búsqueda por patrones de credenciales, correos y rutas personales en los candidatos revisados no produjo coincidencias. Esta búsqueda no garantiza ausencia absoluta de datos sensibles. `.env`, entorno virtual, cachés, Word, SQLite, registros, reportes generados y los tres espacios PAD inspeccionados permanecen ignorados. Los cinco CSV ficticios autorizados ya están versionados.
- La plantilla local usa sustitución textual de variables PAD: las entradas deben ser de confianza; el bloque no captura fallos anteriores al inicio de PowerShell ni tiempos de espera impuestos por PAD. El stderr del proceso Python se descarta; la investigación de fallos depende de los registros locales disponibles. No se encontraron credenciales incrustadas mediante la búsqueda realizada.

## Riesgos y límites

El contrato de origen de Fase 03 no autentica retrospectivamente sus archivos. Se requieren políticas de respaldo y retención, historización de maestros, revisión visual del Excel en escritorio y pruebas de concurrencia multiproceso, red e interrupción abrupta. La recuperación de un reporte corrupto conserva cuarentena e invalida el borrador, pero requiere revisión humana; también falta un procedimiento operativo probado de recuperación tras interrupciones, bloqueos y pérdida de estado. No se han conectado proveedores reales de IA, correo ni Power Automate Cloud.

La búsqueda de un lote ya archivado verifica el reporte y el análisis registrados, y no fuerza regeneración por cambios de presentación. Conforme a la política conservadora, se conservan los resultados originales; una eventual operación explícita de regeneración está pendiente y no se implementó en esta corrección.

## Inventario exacto de candidatos

Modificados:

```text
.gitignore
README.md
docs/ARCHITECTURE.md
docs/BUSINESS_RULES.md
docs/CHANGELOG.md
docs/ROADMAP.md
```

Nuevos:

```text
automation/pad_action_template.ps1
automation/run_automation.ps1
docs/AUTOMATION_DESIGN.md
docs/POWER_AUTOMATE_CLOUD_DESIGN.md
docs/POWER_AUTOMATE_DESKTOP_GUIDE.md
reports/06_automation.md
reports/audit_hito04.md
scripts/run_automation.py
tests/test_automation.py
tests/test_automation_exceptions.py
tests/test_pad_action_template.py
```

Estos 17 archivos son candidatos para revisión y no están preparados en staging. La recomendación técnica no sustituye la autorización de commit y push. Los directorios de trabajo PAD y sus evidencias, reportes generados, datos procesados, bases de estado, registros, documentos Word, entorno virtual y `.env` privado no están incluidos. Los datos ficticios autorizados ya forman parte del repositorio y no se modificaron en esta auditoría.
