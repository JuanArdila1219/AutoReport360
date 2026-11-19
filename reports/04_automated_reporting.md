# Evidencia de reportes automáticos — Fase 04

Fuente: ejecución `82a5a72d-413e-432f-95f4-f17909613b4d`, datos ficticios de octubre de 2026. Generación `d3003f0c-e677-4c5b-a0a0-3b5a9ee8da6c`. Se generaron Excel (154.988 bytes) y PDF (8.777 bytes) en `reports/generated/e1445ef9be40dcf28ce531f27ab6a1f8fe331a340dfd9e357ff89eecdb13af48/`; el manifiesto local contiene las huellas y metadatos completos.

El tablero del Excel contiene ventas 8.001.670.200 COP, 89.126 unidades, cumplimiento 300,1453225 %, presupuesto 2.665.932.000 COP, ticket 205.582,195 COP, margen 3.367.158.450 COP, margen 42,080695 %, rotación 2,52428, seis agotados y cero combinaciones de baja rotación; coincide con las salidas oficiales. La hoja de baja rotación vacía conserva encabezados. El PDF muestra los mismos indicadores redondeados para lectura. El 300,15 % corresponde exclusivamente al conjunto ficticio.

La ejecución registrada tardó 5,688045 s en Excel, 0,350826 s en PDF y 6,104644 s en total; son tiempos del proceso, no intervención humana. Una segunda solicitud devolvió `SKIPPED` con el mismo ID y huellas.

La suite completa terminó con 30 pruebas aprobadas en 28,67 s, incluidas las 23 previas; `pip check` no encontró dependencias rotas. Se abrieron ambos archivos con OpenPyXL y pypdf: el Excel contiene seis gráficos nativos y el PDF cuatro páginas. El PDF definitivo se renderizó con PyMuPDF y sus cuatro páginas se revisaron visualmente. La inspección visual del Excel en una aplicación de escritorio queda pendiente; la comprobación realizada fue estructural y de valores.

La calidad del último lote y la calidad del histórico se identifican por separado; la segunda no está disponible en el contrato. El manifiesto de origen no contiene huellas para autenticar retrospectivamente todos sus archivos. Quedan pendientes las políticas de respaldo, retención e historización de maestros y pruebas reales de interrupción y concurrencia.
