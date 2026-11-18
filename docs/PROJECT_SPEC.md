# Especificación del proyecto

## Problema y objetivo

¿Cómo automatizar la consolidación, validación, análisis y distribución de información comercial para reducir la carga operativa y mejorar la oportunidad en la toma de decisiones? AutoReport360 propone recibir archivos, validarlos, consolidar bases, calcular indicadores, generar reportes, producir resúmenes mediante IA configurable y distribuir resultados automáticamente.

## Contexto ficticio

NovaRetail Colombia S.A.S., sector retail, área Inteligencia Comercial: 30 tiendas, 60 productos en textil, calzado y accesorios, 5 analistas y moneda COP.

## Indicadores previstos

Ventas, unidades, cumplimiento presupuestal, ticket promedio, rotación, agotados, productos más vendidos, baja rotación y crecimiento de ventas. Los contratos de datos, granularidad, fórmulas, periodos, reglas de calidad y tratamiento de valores faltantes se definirán con los insumos disponibles; no se presupone que existan los campos necesarios.

## Supuestos económicos académicos

60 minutos manuales, 5 minutos de intervención humana objetivo, 22 ejecuciones mensuales, 25.000 COP por hora, inversión inicial de 2.000.000 COP y ROI proyectado de 202,5 %. Son supuestos y no resultados medidos. La duración del robot se medirá y registrará por separado. La evaluación debe verificar horizonte, fórmula y costos antes de sostener el ROI.

## Límites y criterios

Arquitectura modular, validación, prevención de duplicados, trazabilidad, registro sin secretos, pruebas unitarias y de integración, datos ficticios y autorización previa para servicios externos. La Fase 00 solo prepara estructura y documentación; no implementa el flujo ni el dashboard. Los formatos, canales y reglas detallados están pendientes de definir.

## Fase 01

Se incorporaron los cinco CSV originales simulados de octubre de 2026. Sus campos, reglas y limitaciones se describen en [DATA_DICTIONARY.md](DATA_DICTIONARY.md) y [KPI_DEFINITIONS.md](KPI_DEFINITIONS.md); las comprobaciones se documentan en `reports/01_data_quality.md`. La implementación del motor y las integraciones continúa fuera de alcance.

## Fase 02

Se implementan recepción local, lectura CSV/XLSX, contratos, validación y control persistente de lotes. Véanse [contratos](DATA_CONTRACTS.md) y [reglas](BUSINESS_RULES.md). Los indicadores, reportes comerciales e integraciones continúan fuera de alcance.
