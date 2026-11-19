# Auditoría Hito 02 — reportes automáticos

Fecha: 19 de noviembre de 2026. **Resultado: hallazgo de idempotencia corregido y verificado para el cierre del Hito 02.** La publicación se realiza únicamente según la autorización expresa del usuario.

## Bloqueo comprobado

`src/reporting/generator.py` construye la clave a partir de las huellas de origen, formato y la versión fija `4.0.4`. Esa versión no cambió después del rediseño de Excel y PDF. Al ejecutar de nuevo la misma entrada con `--output-dir reports/generated --format both`, se obtuvo `SKIPPED` y se devolvió la generación anterior del 18 de noviembre, con los reportes anteriores a las mejoras visuales. Por tanto, una instalación con resultados previos puede no recibir el diseño aprobado. Los archivos anteriores no se sobrescribieron.

Se requiere corregir la invalidación o versionado y probar tanto la actualización de reportes tras un cambio de presentación como la omisión de una repetición realmente idéntica. Cambiar de directorio sirve para visualizar el diseño nuevo, pero no soluciona el problema. La restricción de este hito exige detener la publicación ante errores críticos.

## Corrección y nueva evidencia

La versión centralizada `4.0.5` y una huella SHA-256 de módulos, recursos declarados y versiones de bibliotecas relevantes forman ahora parte de la identidad y del manifiesto. La demostración en el destino habitual generó `ec013ff2-a3ff-4689-b726-2e64165c1756` con estado `SUCCESS`; una repetición devolvió `SKIPPED` con el mismo ID. Las huellas de los archivos de la generación previa continuaron coincidiendo con su manifiesto, y KPI y hojas de detalle del Excel coincidieron entre versiones. La suite de corrección terminó con **41 pruebas aprobadas en 30,54 s**, incluidas las 30 previas. La corrección no sustituye la revisión visual pendiente del Excel.

Se contrastaron además 26 importes e indicadores del PDF anterior y el nuevo frente a la salida oficial, con coincidencia en ambos. Los cinco CSV de origen conservaron sus huellas y `pip check` volvió a pasar. La huella cubre las carpetas de recursos declaradas; cualquier futuro recurso ubicado fuera de ellas debe incorporarse explícitamente al mecanismo.

## Comprobaciones realizadas

- `.venv/Scripts/python.exe -m pytest -q`: **30 pruebas aprobadas en 15,39 s**. La suite actual no detecta el escenario de versión obsoleta descrito arriba.
- `.venv/Scripts/python.exe -m pip check`: sin dependencias rotas. `git diff --check` no informó errores.
- Los cinco CSV conservan sus SHA-256 frente al informe de Fase 01 y a los originales del Hito 1; los dos Word locales también coinciden con sus copias originales.
- El remoto configurado para fetch y push corresponde a `https://github.com/JuanArdila1219/AutoReport360.git`; `refs/heads/main` coincidió con el commit local del Hito 01 `40d550902fac2cfdee47ce5be2a8bad663a40407` en la consulta.
- `.env` privado, `.venv`, caché, SQLite, reportes generados, carpeta original y ambos Word se comprobaron como ignorados. La búsqueda por patrones en los candidatos examinados no identificó correos, rutas locales ni credenciales; no garantiza ausencia absoluta de secretos.
- El PDF rediseñado de cuatro páginas se revisó visualmente. Sus 26 valores de resumen y desgloses comparados aparecieron en ambos PDF. El Excel nuevo preservó KPI, celdas de detalle, fórmulas y seis gráficos en comparación estructural; **su revisión visual en una aplicación de escritorio está pendiente**.

## Archivos candidatos revisados

Cambios existentes desde el Hito 01: `.gitignore`, `README.md`, `docs/ARCHITECTURE.md`, `docs/CHANGELOG.md`, `docs/ROADMAP.md`, `requirements.txt`, `docs/REPORTING_DESIGN.md`, `reports/04_automated_reporting.md`, `scripts/generate_reports.py`, `src/reporting/{excel,generator,pdf,source,theme}.py` y `tests/test_reporting.py`. A esta auditoría se añade `reports/audit_hito02.md`. No se prepararon archivos en staging debido al bloqueo.

## Riesgos adicionales

El manifiesto de Fase 03 no incorpora huellas para autenticar retrospectivamente sus insumos; las comprobaciones del generador detectan algunas inconsistencias, pero no una alteración coordinada. Quedan pendientes políticas de respaldo, retención e historización de maestros, y pruebas reales de interrupción y concurrencia. El tiempo del robot no representa tiempo de intervención humana.

## Auditoría final de cierre

La suite completa se repitió: **41 pruebas aprobadas en 29,58 s**; `pip check` no encontró dependencias rotas y `git diff --check` no encontró errores. La repetición de la generación 4.0.5 devolvió `SKIPPED`, y las huellas de los reportes anteriores continuaron intactas. Los cinco CSV coincidieron con sus originales y las huellas de Fase 01; ambos Word locales coincidieron con sus originales. El listado de publicación autorizado se encuentra en `reports/publication_hito02.txt`.

Permanecen pendientes la revisión visual del Excel en escritorio, una política para recuperar reportes faltantes o corruptos y pruebas reales de concurrencia e interrupción. El generador rechaza actualmente las salidas dañadas sin sobrescribirlas.
