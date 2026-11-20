# Evidencia de automatización local — Fase 06

## Fase 06.2: manejo de excepciones PAD

El usuario confirmó posteriormente pruebas manuales en PAD de SUCCESS, SKIPPED, REJECTED y FAILED, cuatro notificaciones, detención ante JSON inválido y captura de una excepción controlada. La regresión normal informada fue SKIPPED en 0,268634 segundos; un registro local conserva ese resultado. La auditoría inicial encontró que la plantilla local no incluía el `automation_id = 'NO_DISPONIBLE'` indicado para la excepción; la resolución consta a continuación y en la auditoría del Hito 04.

Corrección posterior: la plantilla local canónica ya incluye ese identificador de contingencia y se verificó con pruebas locales. Sin una exportación completa posterior a la última modificación manual no se puede confirmar igualdad exacta con el bloque de PAD.

Se ejecutaron **11 pruebas locales aprobadas en 39,42 segundos** con Windows PowerShell y procesos Python simulados. Cubrieron SUCCESS, SKIPPED, REJECTED y FAILED; salida vacía, JSON malformado, contrato inválido, salida de error nativa, código incompatible, Python ausente, excepción controlada y caracteres en español. La primera ejecución de pruebas detectó mensajes de progreso en el flujo de errores; se suprimieron y la repetición citada pasó. No se ejecutó la suite completa en esta fase.

El usuario confirmó la integración PAD y las notificaciones para SUCCESS, SKIPPED, REJECTED y FAILED, y observó que un `throw` fuera de un bloque controlado podía dejar sin salida a la acción de conversión JSON. La plantilla inline de Fase 06.2 invoca Python directamente, captura fallos durante el bloque y mantiene el código comercial en el JSON; las excepciones del anfitrión PAD requieren una rama propia. Las pruebas automatizadas de la plantilla usaron procesos locales simulados; posteriormente el usuario confirmó pruebas manuales en PAD. No se alteraron los espacios de trabajo ni se enviaron correos durante la auditoría.

## Primera ejecución desde Power Automate Desktop y corrección 06.1

La suite completa de Fase 06.1 terminó con **84 pruebas aprobadas en 161,59 segundos**, incluidas las 72 anteriores. `pip check` no encontró dependencias incompatibles y `git diff --check` no informó errores.

La ejecución real `2245f126-16f5-4417-9e0a-c34434f0abad` procesó 95.742 registros en 11,693733 segundos de robot, con `SUCCESS`, distribución local `PREPARED`, cero errores y cinco advertencias estadísticas. No se midió intervención humana. La segunda ejecución `ac81a5d3-da07-4270-9d1a-fc11a505c07b` terminó `FAILED` porque el lote ya estaba archivado; generó una alerta local, conservada como evidencia.

La auditoría en lectura cotejó lote archivado, manifiesto, fuente, análisis, informes y adjuntos del borrador. Las huellas de Excel y PDF coincidieron con sus manifiestos: `cd0807fc350df767920c65983333b6c771ece5b6b76c1cefb5710981ee519ad4` y `fe88bf69e0d6ae8f4aeb662f21e6a3d85451bcba6545f77e43c0015a9d4d9a08`, respectivamente. El borrador permanece `PREPARED`; no hay envío real. La repetición local por CLI `31a32a0a-7d7d-41e6-b2f1-09e78882d901` devolvió `SKIPPED`, `ALREADY_PROCESSED_VERIFIED` y `NOT_DUPLICATED` en 0,41662 segundos de robot, vinculada a la ejecución original y sin crear informes ni borradores nuevos. En ese momento la corrección aún no se había repetido en PAD; la validación manual posterior comunicada por el usuario se registra arriba.

La suite completa terminó con **72 pruebas aprobadas en 44,39 segundos**, incluidas las 63 existentes. `pip check` no encontró dependencias incompatibles y `git diff --check` no informó errores.

La demostración se ejecutó sobre copias aisladas de las cinco bases simuladas, en un espacio local separado. La recepción se completó mediante `READY.json` y huellas. La ejecución `d7a3170e-673a-458a-8c9b-5835fcce19aa` terminó `SUCCESS`: validación `APPROVED`, persistencia de 30 tiendas, 60 productos, 38.922 ventas, 55.800 inventarios y 930 presupuestos; análisis y dos reportes generados; distribución local `PREPARED`. Son 95.742 registros ficticios. El reporte reflejó ventas de 8.001.670.200 COP y cumplimiento de 300,15 % correspondientes a la simulación.

La ejecución integral midió 12,067450 segundos de robot y 12,076890 segundos transcurridos alrededor de la llamada de automatización, sin sumar ejecuciones independientes. La preparación de copias y la intervención humana no se midieron. La repetición idéntica devolvió `SKIPPED` y `NOT_DUPLICATED`. Un lote con estructura de ventas inválida terminó `REJECTED` y `NOT_PREPARED`; se preparó una alerta local, no un correo comercial. Los cinco CSV originales conservaron las huellas de Fase 01.

El borrador comercial propone asunto «AutoReport360 — informe comercial», resume las ventas, cumplimiento y seis agotados, incluye recomendaciones y referencia Excel y PDF por huella. Es un archivo local, no un envío. Los resultados y las rutas de la demostración están en `logs/demo_phase06_final/`, ignorado por Git.

En la demostración inicial de Fase 06, la prueba directa del lanzador PowerShell fue bloqueada porque la política de ejecución de scripts de esa máquina los deshabilitaba; no se modificó dicha política. En ese momento aún no se había creado el flujo en Power Automate. Posteriormente el usuario confirmó su creación y pruebas manuales, descritas arriba. No se utilizaron servicios externos de IA ni correo real en la demostración local.

La recuperación de reportes mediante cuarentena se prueba en un directorio temporal. Tras la recuperación se conserva el borrador histórico con un marcador separado de invalidación; requiere revisión humana. El bloqueo serializa un espacio de trabajo local y se probó mediante llamadas concurrentes en un proceso; faltan ensayos de procesos independientes, sistemas de archivos de red y cortes abruptos reales. Un corte entre la persistencia y la escritura del diario puede exigir intervención manual. El proveedor generativo real sigue desactivado.
