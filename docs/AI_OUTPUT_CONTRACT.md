# Contrato de salida del análisis

## Versión 1.1.0

Cada recomendación contiene `id`, `finding_id`, `descripcion`, `evidencia`, `fuente`, `justificacion`, `action`, `priority`, `responsable_sugerido`, `horizonte_sugerido`, `impacto_esperado`, `indicador_seguimiento` y `condiciones_limitaciones`. Las oportunidades contienen `finding_id`, `tipo` y `descripcion`; los riesgos referencian hallazgos. La evidencia de agotados puede incluir combinaciones y tiendas con saldo positivo. Las propuestas no asignan responsabilidades reales. Los campos se reconstruyen y contrastan antes de generar reportes. Los análisis 1.0.0 usan su contrato anterior.

JSON UTF-8: `analysis_id`, `pipeline_run_id`, `period`, `provider`, `model`, `mode`, `engine_version`, `instruction_version`, `request_key`, `source_hashes`, `component_fingerprint`, `business_config`, `executive_summary`, `findings`, `risks`, `opportunities`, `recommendations`, `evidence`, `limitations`, `generated_at`, `duration_seconds`, `tokens`, `cost`, `status` y `fallback_reason`. El resultado de la CLI agrega `execution_status` y `path` para uso local; no se guardan como contenido del análisis.

Cada hallazgo contiene ID, tipo, descripción, evidencia con valor/unidad/fuente, prioridad, acción, limitación y naturaleza. Los IDs, hechos y evidencias se reconstruyen desde la fuente antes de aceptar una salida en reportes; las recomendaciones y riesgos deben coincidir. El modo puede ser `local`, `local_fallback` o `generative` para proveedor inyectado. En esta fase todos los proveedores generativos ejercitados son simulados. `tokens` y `cost` son nulos cuando no hay información confiable; no se estiman tarifas.

Las hipótesis causales no se producen actualmente. Las recomendaciones son acciones sugeridas y no se ejecutan. El catálogo cerrado limita la capacidad expresiva generativa y reduce el riesgo de afirmar datos sin evidencia; no constituye una garantía general contra toda inyección.
