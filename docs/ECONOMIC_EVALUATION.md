# Evaluación económica académica

## Alcance y evidencia

NovaRetail Colombia S.A.S. es ficticia. La consolidación manual requiere recibir y validar archivos, reunir tablas, calcular indicadores y preparar informes; AutoReport360 automatiza esas etapas y prepara una distribución local. La persona sigue supervisando los resultados. No se ha implementado el envío real de correo ni se ha medido en campo el tiempo humano.

Una ejecución integral observada en Power Automate Desktop procesó 95.742 registros ficticios en **11,693733 segundos de robot**, con estado `SUCCESS` y distribución `PREPARED` ([evidencia](../reports/06_automation.md)). Esa duración pertenece a una ejecución específica, no es una media ni una medición del tiempo humano. La repetición `SKIPPED` es otro escenario y no debe emplearse como tiempo de procesamiento completo.

## Método y supuestos

El escenario base adopta las hipótesis originales: 60 minutos manuales y 5 minutos de intervención humana automatizada por ejecución, 22 ejecuciones mensuales, costo de 25.000 COP por hora e inversión inicial de 2.000.000 COP. Todas son hipótesis académicas; no se ha medido el ahorro humano ni se ha demostrado que pueda traducirse íntegramente en ahorro de caja. Se supone demanda estable durante 12 meses y que la hora liberada tiene valor económico completo. No se incluyen costos recurrentes de licencias, infraestructura, mantenimiento, soporte, capacitación, seguridad, impuestos, financiación ni reposición: se toman como cero **solo para esta proyección**. La inversión se reconoce una vez al inicio y no se descuentan flujos.

Fórmulas, con minutos expresados por ejecución:

1. Horas proyectadas liberadas al mes = (minutos manuales − minutos humanos automatizados) / 60 × ejecuciones mensuales.
2. Beneficio mensual bruto proyectado = horas liberadas × costo por hora.
3. Beneficio neto anual proyectado = 12 × beneficio mensual bruto − inversión inicial − costos recurrentes anuales.
4. ROI de primer año = beneficio neto anual / inversión inicial × 100.
5. Recuperación simple = inversión inicial / beneficio mensual neto recurrente; supone flujos uniformes y beneficio mensual positivo. No contempla valor del dinero en el tiempo.

## Escenarios de sensibilidad

Los tres escenarios son ilustrativos. La variación afecta tiempos humanos y frecuencia; costo hora, inversión, horizonte y costos recurrentes permanecen iguales. No son mediciones ni predicciones garantizadas.

| Escenario | Manual / humano automatizado, min | Ejecuciones/mes | Horas/mes | Beneficio mensual bruto, COP | Beneficio anual bruto, COP | ROI primer año | Recuperación simple |
|---|---:|---:|---:|---:|---:|---:|---:|
| Conservador | 45 / 10 | 16 | 9,33 | 233.333,33 | 2.800.000 | 40 % | 8,57 meses |
| Base | 60 / 5 | 22 | 20,17 | 504.166,67 | 6.050.000 | 202,5 % | 3,97 meses |
| Optimista | 75 / 5 | 22 | 25,67 | 641.666,67 | 7.700.000 | 285 % | 3,12 meses |

En el escenario base: 55/60 × 22 × 25.000 = 504.166,67 COP mensuales; 12 × el valor sin redondear = 6.050.000 COP; (6.050.000 − 2.000.000) / 2.000.000 × 100 = **202,5 %**. Por tanto, la cifra original es consistente únicamente con este horizonte y estos supuestos. El beneficio neto de primer año sería 4.050.000 COP; el retorno de la inversión no es igual al ahorro bruto. La recuperación continua estimada es 3,97 meses; con contabilización solo al cierre de cada mes completo, sería al final del cuarto mes. Se usan valores sin redondear en los cálculos y se redondean únicamente para presentación.

Con costos recurrentes positivos, réstelos del beneficio mensual para calcular recuperación y del anual para ROI. Si el beneficio mensual neto es cero o negativo, no existe recuperación bajo esas hipótesis. Para tomar decisiones reales se necesitan mediciones de múltiples ciclos, costos completos y validación de capacidad efectivamente aprovechable.

## Beneficios y limitaciones

La solución puede mejorar oportunidad, repetibilidad, trazabilidad y detección de errores; son beneficios cualitativos, no monetizados. El dato de duración del robot no demuestra productividad humana ni cumplimiento de una meta de cinco minutos. Los resultados comerciales proceden de datos simulados; no prueban utilidad real, aceptación operativa ni ahorro empresarial. No se incluye incremento de ventas, ingresos por mejores decisiones ni reducción de personal.
