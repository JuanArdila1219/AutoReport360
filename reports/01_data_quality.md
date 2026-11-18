# Calidad de datos — octubre de 2026

Perfil generado a partir de los cinco CSV originales. IQR señala candidatos, no errores; ceros de ventas, entradas o inventario pueden ser válidos comercialmente.

| Tabla | Filas | Columnas | Duplicados de llave | Nulos |
|---|---:|---:|---:|---:|
| tiendas | 30 | 3 | 0 | 0 |
| productos | 60 | 5 | 0 | 0 |
| ventas | 38922 | 9 | 0 | 0 |
| inventarios | 55800 | 8 | 0 | 0 |
| presupuestos | 930 | 3 | 0 | 0 |

Total: 95742 registros.

## Comprobaciones

Los recuentos son incidencias observadas; diferencias de precio frente a lista pueden reflejar políticas comerciales y requieren interpretación.

- `ventas_unknown_store`: 0
- `ventas_unknown_product`: 0
- `ventas_outside_october`: 0
- `inventarios_unknown_store`: 0
- `inventarios_unknown_product`: 0
- `inventarios_outside_october`: 0
- `presupuestos_unknown_store`: 0
- `presupuestos_outside_october`: 0
- `inventory_balance_errors`: 0
- `inventory_continuity_errors`: 0
- `sales_inventory_mismatches`: 0
- `sales_value_errors`: 0
- `sales_cost_errors`: 0
- `sales_price_differs_from_list`: 0
- `inventory_cost_differs_from_catalog`: 0
- `invalid_discounts`: 0
- `missing_store_day_budgets`: 0
- `missing_inventory_combinations`: 0
- `sales_without_budget`: 0

El JSON complementario contiene columnas, tipos, nulos, negativos, duplicados, fechas, huellas SHA-256 y candidatos IQR por campo. IQR con rango intercuartílico cero puede señalar numerosos valores válidos.
