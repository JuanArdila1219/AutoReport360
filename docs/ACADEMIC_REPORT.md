# AutoReport360: documento académico de cierre para revisión

## Resumen ejecutivo

AutoReport360 es un prototipo local para automatizar la consolidación, validación, análisis y preparación de información comercial de NovaRetail Colombia S.A.S., empresa ficticia de retail. Integra Python, reglas de calidad, indicadores, informes Excel y PDF, análisis local basado en evidencia, Power Automate Desktop (PAD) y un dashboard Streamlit. Una ejecución observada en PAD procesó 95.742 registros ficticios; el usuario confirmó la revisión mediante capturas de las seis secciones y una comprobación final. La evaluación económica es una proyección académica.

## Problema y objetivos

La preparación manual de información comercial puede dispersar archivos, repetir validaciones y retrasar decisiones. La pregunta es: ¿cómo automatizar la consolidación, validación, análisis y distribución de información comercial para reducir la carga operativa y mejorar la oportunidad en la toma de decisiones? El objetivo general es construir una solución modular que reciba información, verifique su calidad, consolide y calcule indicadores, prepare reportes y recomendaciones basadas en evidencia y facilite su consulta y distribución.

Objetivos específicos: definir y validar fuentes ficticias; construir extracción y controles de integridad; persistir y calcular indicadores coherentes; generar informes trazables; producir análisis local y soportar proveedores configurables sin llamadas reales; orquestar la recepción y preparar distribución local; habilitar consulta interactiva; y evaluar costos y beneficios bajo hipótesis explícitas.

## Contexto empresarial y datos

NovaRetail Colombia S.A.S. pertenece al sector retail; Inteligencia Comercial cuenta con cinco analistas, 30 tiendas y 60 productos en textil, calzado y accesorios. La moneda es COP. Las fuentes simuladas de octubre de 2026 incluyen 30 tiendas, 60 productos, 38.922 ventas, 55.800 inventarios y 930 presupuestos: 95.742 registros en total, incluidas las tablas maestras. No representan operaciones reales. Sus columnas y relaciones están en el [diccionario](DATA_DICTIONARY.md).

## Arquitectura y tecnologías

El flujo local comprende recepción de un lote con manifiesto y huellas, extracción, validación, persistencia, transformación e indicadores; después se generan análisis basado en evidencia e informes, se prepara un borrador local de distribución y se consultan salidas oficiales desde Streamlit. Los manifiestos aportan trazabilidad e integridad, pero no son firmas digitales. PAD invoca el orquestador Python y presenta los estados de procesamiento. El detalle y límites figuran en [arquitectura](ARCHITECTURE.md) y [automatización](AUTOMATION_DESIGN.md).

Python y Pandas gestionan los datos; OpenPyXL y el generador PDF construyen informes; Streamlit sirve la consulta local; Pytest verifica contratos y regresiones; Git y GitHub apoyan el control de versiones; PowerShell conecta PAD con Python. El análisis local es determinístico y no equivale a un proveedor generativo real. No hay envío real de correos ni integración activa con IA externa.

## Fases y flujo

| Fase | Resultado y estado |
|---|---|
| 00–01 | Estructura, fuentes ficticias, perfilamiento, calidad y diccionario. |
| 02–03 | Extracción, validación, persistencia y cálculos comerciales. |
| 04 | Reportes Excel/PDF y protección por huellas; revisión visual del Excel de escritorio pendiente. |
| 05–05.1 | Análisis local de hallazgos y recomendaciones, proveedor simulado y contingencia; activación generativa real pendiente. |
| 06–06.2 | Orquestación local y manejo de excepciones; PAD probado manualmente según la evidencia registrada. `PREPARED` no significa enviado. |
| 07 | Dashboard local y pruebas técnicas; revisión por capturas y comprobación final confirmadas por el usuario. |
| 08–09 | Evaluación económica proyectada y documentación académica preparadas para revisión. |

Una persona dispone un lote completo y su manifiesto; el orquestador valida y procesa las fuentes, o informa `REJECTED`/`FAILED`. Un lote ya procesado y verificable produce `SKIPPED`, sin repetir el envío ni la generación. La salida `SUCCESS` puede preparar borradores locales; el dashboard consulta ejecuciones existentes sin iniciar el pipeline ni regenerar históricos archivados.

## Indicadores y hallazgos

Las definiciones oficiales están en [KPI_DEFINITIONS.md](KPI_DEFINITIONS.md). Ventas son la suma neta; cumplimiento es ventas sobre presupuesto, agregado por tienda y fecha; ticket es venta neta sobre transacciones distintas; margen es venta menos costo; rotación en unidades divide unidades vendidas entre inventario promedio por extremos. Agotados cuenta combinaciones tienda-producto al corte. Baja rotación exige existencia positiva, cero ventas y 15 días completos de historial. Un indicador sin historial no se convierte en cero. No hay crecimiento mensual frente a septiembre por ausencia de ese periodo.

En la simulación documentada, ventas netas fueron 8.001.670.200 COP, unidades 89.126 y cumplimiento 300,15 %. Este último es la relación observada entre ventas y presupuesto de los datos ficticios, no un resultado real ni prueba de la causa de dicha relación. La aproximación de rotación no utiliza promedio diario y el ticket de este lote se basa en una línea por transacción; no deben generalizarse sin revisar la estructura de otras fuentes.

## Reportes, dashboard y pruebas

Excel y PDF presentan los indicadores existentes; los informes enriquecidos incorporan análisis local validado. El dashboard consulta ejecuciones locales controladas y ofrece informes solo después de comprobar sus huellas; no ejecuta el procesamiento al abrirse. Las secciones son resumen, análisis comercial, inventarios, recomendaciones, calidad/trazabilidad e informes. Sus filtros operan en la granularidad de cada vista, sin recalcular metas por producto o categoría. La evidencia técnica y los resultados reales más recientes se registran en [auditoría Hito 05](../reports/audit_hito05.md). El usuario comunicó la revisión mediante capturas y la comprobación final; no equivalen a una auditoría completa de accesibilidad. La causa del `removeChild` observado anteriormente sigue sin confirmar.

PAD fue probado manualmente para `SUCCESS`, `SKIPPED`, `REJECTED`, `FAILED`, notificaciones, JSON inválido y excepción controlada, según [auditoría Hito 04](../reports/audit_hito04.md). Una ejecución integral procesó 95.742 registros en 11,693733 segundos de robot; no se midió el tiempo humano.

## Evaluación económica

La [evaluación detallada](ECONOMIC_EVALUATION.md) calcula, para el escenario base supuesto, 504.166,67 COP de beneficio bruto mensual, 6.050.000 COP anual, ROI de primer año de 202,5 % y recuperación simple de 3,97 meses. Supone 60 minutos manuales, 5 de intervención automatizada, 22 ejecuciones mensuales, 25.000 COP/hora, inversión de 2.000.000 COP y cero costos recurrentes. Son proyecciones, no ahorro medido; la duración del robot es otra magnitud.

## Riesgos, trabajo futuro y conclusiones

Persisten revisión visual del Excel en escritorio; pruebas reales de interrupción abrupta y concurrencia; políticas de respaldo, retención, recuperación e historización; autenticación y despliegue seguro si se ampliara el alcance; y evaluación real de proveedores externos y costos, previa autorización. La recuperación y regeneración de históricos debe ser explícita y auditable, no automática. Las recomendaciones requieren decisión humana.

El prototipo demuestra la integración técnica de fuentes ficticias con controles y entregables trazables. No demuestra ahorro económico real ni operación empresarial desatendida. Su eventual adopción requiere validar interfaz, seguridad operativa, costos y tiempos humanos en condiciones reales.
