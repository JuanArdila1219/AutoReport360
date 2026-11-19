# Auditoría Hito 03 — analista comercial virtual

Fecha: 19 de noviembre de 2026. Alcance: cambios posteriores al Hito 02 en las fases 05 y 05.1; no se modificaron los indicadores ni las fuentes originales durante el cierre.

## Resultados

- `.venv/Scripts/python.exe -m pytest -q`: **63 pruebas aprobadas en 40,35 s**. `pip check`: sin dependencias rotas. `git diff --check`: sin errores; Git advirtió conversiones futuras de finales de línea.
- Los cinco CSV coincidieron con las huellas SHA-256 registradas en el perfilamiento de Fase 01. Los dos Word locales coincidieron con sus originales; ambos siguen excluidos.
- Los análisis de versiones 1.0 y 1.1 se validaron contra la fuente. Los archivos de las generaciones enriquecidas anterior y actual coincidieron con sus manifiestos; el manifiesto actual contiene la huella del análisis.
- La repetición del análisis y de los reportes actuales devolvió `SKIPPED`. Se ejercitaron en memoria el proveedor simulado y su contingencia ante respuesta inválida; no hubo llamadas a proveedores externos.
- Los indicadores de las hojas anteriores, salvo la hoja de conclusiones enriquecida, coincidieron en la comparación previa; solo cambió la fecha de generación de la portada. El PDF se renderizó; la revisión visual del Excel en escritorio sigue pendiente.
- La búsqueda por patrones en candidatos no encontró correos, rutas personales ni claves con los formatos revisados. Esta búsqueda no garantiza ausencia absoluta de secretos o datos personales. La plantilla `.env.example` no contiene credenciales.
- Los artefactos generados, `.env` privado, SQLite, logs, cachés, entorno virtual, Word y carpeta de originales permanecen excluidos por `.gitignore`. Los cinco CSV ficticios autorizados están versionados. El listado exacto de cambios se encuentra en `reports/publication_hito03.txt`.
- La rama local `main` y el remoto autorizado coincidían en el commit del Hito 02 `4f63e014b2abf6622b1498004750d5bd3708bbf3` antes de la publicación.

## Pendientes

Revisión visual del Excel en una aplicación de escritorio; autorización y pruebas reales antes de activar un proveedor generativo; política para recuperación de reportes corruptos; respaldo, retención e historización de maestros; pruebas reales de interrupción y concurrencia. Como mejoras menores se registran la localización de cifras en español colombiano y la identificación explícita de segmentos destacados. El contrato de Fase 03 no autentica retrospectivamente los archivos de origen; las recomendaciones y umbrales son académicos y requieren revisión humana.
