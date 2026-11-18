# Diccionario de datos

Fuentes: CSV UTF-8 con BOM y comas, octubre de 2026. Tipos inferidos por Pandas: `str` e `int64`; fechas son texto ISO `AAAA-MM-DD`, interpretables como fecha. Los campos son obligatorios en este lote; restricciones y claves son las reglas de este conjunto, no garantías de fuentes futuras.

## tiendas — una fila por tienda

| Campo | Tipo | Descripción y restricción |
|---|---|---|
| tienda_id | str | Identificador único, clave primaria. |
| nombre | str | Nombre de tienda. |
| ciudad | str | Ciudad de la tienda. |

## productos — una fila por producto

| Campo | Tipo | Descripción y restricción |
|---|---|---|
| producto_id | str | Identificador único, clave primaria. |
| nombre | str | Nombre del producto. |
| categoria | str | Categoría comercial. |
| precio_lista_cop | int64 | Precio unitario de lista, COP, no negativo. |
| costo_unitario_cop | int64 | Costo unitario, COP, no negativo. |

## ventas — una fila por transacción simulada

| Campo | Tipo | Descripción y restricción |
|---|---|---|
| transaccion_id | str | Identificador único, clave primaria. |
| fecha | str (fecha) | Fecha de venta, octubre de 2026. |
| tienda_id | str | Clave foránea a tiendas.tienda_id. |
| producto_id | str | Clave foránea a productos.producto_id. |
| unidades | int64 | Unidades vendidas, no negativas. |
| precio_unitario_cop | int64 | Precio unitario antes de descuento, COP, no negativo. |
| descuento_pct | int64 | Descuento porcentual entre 0 y 100. |
| venta_neta_cop | int64 | Unidades × precio × (1 − descuento/100), COP. |
| costo_venta_cop | int64 | Unidades × costo unitario de producto, COP. |

## inventarios — una fila por fecha, tienda y producto

Clave primaria compuesta `(fecha, tienda_id, producto_id)`.

| Campo | Tipo | Descripción y restricción |
|---|---|---|
| fecha | str (fecha) | Fecha de inventario, octubre de 2026. |
| tienda_id | str | Clave foránea a tiendas.tienda_id. |
| producto_id | str | Clave foránea a productos.producto_id. |
| inventario_inicial | int64 | Existencia al inicio del día, unidades no negativas. |
| entradas | int64 | Unidades recibidas durante el día, no negativas. |
| unidades_vendidas | int64 | Unidades vendidas durante el día, no negativas; concilia con ventas agregadas. |
| inventario_final | int64 | Existencia al cierre, inicial + entradas − vendidas; no negativa. |
| costo_unitario_cop | int64 | Costo unitario de valoración, COP, no negativo. |

## presupuestos — una fila por fecha y tienda

Clave primaria compuesta `(fecha, tienda_id)`.

| Campo | Tipo | Descripción y restricción |
|---|---|---|
| fecha | str (fecha) | Fecha de la meta, octubre de 2026. |
| tienda_id | str | Clave foránea a tiendas.tienda_id. |
| meta_ventas_cop | int64 | Meta diaria de ventas, COP, no negativa. |
