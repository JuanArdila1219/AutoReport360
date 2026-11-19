# Diseño del análisis comercial — Fase 05

## Ampliación 05.1

El motor 1.1 construye una narrativa dinámica, hechos y recomendaciones priorizadas. Presupuesto inferior a 100 %: alta; igual o superior a 200 %: media y revisión de calibración, sin afirmar error. Un agotado o más: alta. Margen inferior a 20 %, baja rotación presente, advertencias del último lote o variación diaria/semanal absoluta igual o superior a 10 %: media. Los valores de `config/ai_analysis.json` son supuestos académicos, no umbrales validados de operación. El crecimiento semanal compara dos ventanas consecutivas de siete días completos.

Las candidatas de redistribución tienen saldo positivo del mismo producto en otra tienda al corte; no se conoce su excedente ni inventario mínimo. No se proponen cantidades. El ranking carece de costo y no permite calcular rentabilidad por producto. La diferencia entre máximos y mínimos de tiendas o ciudades no controla tamaño ni explica causas. Las oportunidades son potenciales; no se generan hipótesis causales ni impactos económicos.

El proveedor simulado solo selecciona IDs: el sistema reconstruye y verifica hechos, prioridades y recomendaciones. El resumen usa el catálogo local completo aun cuando el proveedor seleccione un subconjunto. La versión 1.0.0 sigue admitida; las reglas nuevas producen una huella distinta sin sobrescribir históricos.

El módulo reutiliza la validación de `src/reporting/source.py` y construye un catálogo compacto de hechos a partir de indicadores oficiales. No transmite filas originales, rutas ni credenciales. Los identificadores de tienda/producto solo se incluyen si cumplen un patrón restringido; los nombres de ciudad y categoría se omiten del contexto. El texto de entrada se trata como datos. Los resultados locales usan reglas, no IA generativa.

El proveedor puede seleccionar exclusivamente identificadores del catálogo; no puede aportar texto libre, cifras o referencias nuevas. Las respuestas fuera de esa estructura, IDs inexistentes o duplicados y uso de tokens inválido activan contingencia local. La representación final se construye con hechos, acciones y limitaciones del catálogo. La identidad considera huellas de origen y componentes, versión, instrucciones, configuración, proveedor y modelo. Una contingencia se guarda con nombre independiente y no bloquea un reintento. Un resultado existente incompatible se rechaza.

`OpenAIAdapter` prepara una solicitud Responses con Structured Outputs, `store=False`, tiempo límite y reintentos acotados para excepciones de tiempo/conexión. La CLI no proporciona cliente ni autorización y nunca realiza solicitudes externas; se probaron exclusivamente clientes en memoria. Para una futura activación se requiere autorización explícita, seleccionar un modelo compatible, instalar/configurar el SDK por separado, suministrar un cliente con credenciales mediante variables de entorno sin compartirlas en el chat, controlar reintentos internos del SDK y realizar pruebas aprobadas de seguridad, costo y conectividad. La integración real, sus excepciones específicas, el tiempo límite efectivo y la facturación no se han probado. La estructura se fundamenta en la [documentación oficial de salidas estructuradas de OpenAI](https://developers.openai.com/api/docs/guides/structured-outputs).

Las reglas y umbrales vigentes se detallan en la ampliación 05.1. No hay pronósticos ni evaluación del histórico de calidad. La redistribución se condiciona a disponibilidad confirmada en otras tiendas. Oportunidades queda vacío cuando las reglas no identifican ninguna.

```powershell
.venv/Scripts/python.exe scripts/run_ai_analysis.py RUTA_ORIGEN --mode local
.venv/Scripts/python.exe scripts/generate_reports.py RUTA_ORIGEN --analysis RUTA_ANALISIS.json --format both
```

`--mode generative` sin cliente autorizado devuelve contingencia local; no constituye llamada real. Los informes enriquecidos verifican huellas y evidencia y añaden la huella del análisis a su identidad. Los reportes sin `--analysis` siguen disponibles.
