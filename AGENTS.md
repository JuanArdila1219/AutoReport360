# Instrucciones permanentes para AutoReport360

- Respetar el alcance y la fase autorizada; no desarrollar etapas futuras ni conectar servicios externos sin autorización.
- Mantener código, identificadores y docstrings en inglés; documentación de proyecto en español. Usar tipado, funciones reutilizables, excepciones claras y logging sin datos sensibles.
- Mantener arquitectura modular y responsabilidades separadas. Validar entradas, prevenir duplicados y conservar trazabilidad de origen, ejecución y resultados.
- Usar exclusivamente datos ficticios o autorizados; preservar los archivos recibidos y simulados existentes. No regenerar ni sobrescribir datos sin autorización.
- Proteger secretos: variables de entorno locales, nunca credenciales en código, repositorio, reportes o logs. No integrar servicios externos sin autorización.
- Añadir pruebas unitarias y de integración pertinentes a cada implementación; reportar únicamente pruebas realmente ejecutadas y resultados observados. No inventar métricas, datos ni resultados.
- Separar tiempo de intervención humana y duración del robot. Identificar los supuestos académicos como proyecciones, no como resultados medidos.
- Mantener dependencias necesarias únicamente y actualizar documentación y registro de cambios cuando corresponda. No hacer commit ni push sin autorización.
