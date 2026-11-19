"""Shared visual identity and wording for commercial reports."""
COLORS = {"navy": "101E33", "petrol": "168C91", "turquoise": "2DD4BF", "light": "F1F5F9", "yellow": "EAB54C", "red": "DC2626", "white": "FFFFFF"}
BRAND = "AutoReport360"
SLOGAN = "Menos tareas operativas. Más decisiones estratégicas."
COMPANY = "NovaRetail Colombia S.A.S."
AREA = "Inteligencia Comercial"
METHODOLOGY = [
    "Empresa y datos ficticios con fines académicos. Todos los importes están expresados en COP.",
    "Cumplimiento presupuestal: ventas netas / presupuesto. El resultado de 300,15 % corresponde a la simulación de octubre de 2026.",
    "Rotación: unidades vendidas / promedio de inventario en unidades calculado con los extremos del periodo.",
    "Baja rotación: inventario positivo y cero ventas en los últimos 15 días completos; sin historial completo no está disponible.",
    "Ticket promedio: ventas netas / transacciones únicas; válido para la simulación con una línea por transacción.",
    "No existe información de septiembre para calcular crecimiento mensual. Un valor no disponible no equivale a cero.",
    "Las advertencias de calidad corresponden únicamente al último lote validado; la calidad del histórico acumulado no está disponible.",
]


def quality_status(value: str) -> str:
    """Translate the supported validation statuses for report readers."""
    return {"APPROVED": "Aprobado", "SKIPPED": "Omitido por duplicado"}.get(value, value)


def quality_warning(value: str) -> str:
    """Translate known phase-03 warning language without changing the count."""
    return value.replace("IQR candidates", "valores candidatos por IQR")
