# Guía de usuario del dashboard local

Desde la raíz del proyecto en Windows, ejecute:

```powershell
.venv/Scripts/python.exe -m streamlit run app/dashboard.py
```

Abra la dirección local mostrada por Streamlit. Seleccione en la barra lateral una ejecución disponible y luego una de las seis secciones. La aplicación consulta salidas existentes y no ejecuta el procesamiento, regenera reportes ni envía correos. Si no existen datos disponibles o la ejecución no supera el contrato, siga el mensaje mostrado y consulte al responsable técnico; no modifique evidencias históricas para ocultar el aviso.

Si el navegador traduce la página automáticamente, seleccione el contenido original para la revisión: en una prueba Chrome expandió «M» a «millones» y alteró el encabezado al navegar. La relación con el error `removeChild` reportado aún no se ha demostrado.

- **Resumen ejecutivo:** revise periodo, tarjetas y tendencia diaria. Los importes grandes se muestran en millones de COP; la ayuda de cada tarjeta monetaria contiene el valor oficial completo. El detalle diario presenta formato colombiano. El 300,15 % observado corresponde exclusivamente a los datos ficticios.
- **Análisis comercial:** cambie la vista y filtre tiendas, ciudades, categorías o productos. El filtro afecta su tabla y gráfico; no cambia los indicadores generales ni asigna presupuesto a categorías o productos.
- **Inventarios:** consulte al corte los agotados, los casos identificados de baja rotación y las combinaciones con historial insuficiente. La ausencia de historial no equivale a cero.
- **Recomendaciones:** examine prioridad, acción sugerida, evidencia y responsable. Las acciones son propuestas sujetas a decisión humana; las oportunidades son potenciales.
- **Calidad y trazabilidad:** consulte validación, advertencias y referencias de ejecución. Los candidatos IQR merecen revisión estadística y no son automáticamente errores.
- **Informes:** seleccione una generación histórica verificada y descargue los formatos disponibles. Una generación no verificable se identifica con un motivo y no se ofrece; no debe concluirse corrupción sin evidencia adicional. `PREPARED` identifica un borrador local, no un correo enviado.

Las huellas no son firmas digitales y no garantizan protección frente a cambios coordinados del contenido y sus manifiestos. Use exclusivamente datos ficticios o autorizados. No exponga el servidor a internet sin una decisión y controles adicionales.
