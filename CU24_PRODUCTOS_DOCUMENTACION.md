# CU24 - Registrar Producto - Documentación Completa

## 📋 Descripción General

Sistema completo de gestión de productos para el gimnasio, incluyendo suplementos, equipamiento, indumentaria y otros artículos de venta. Implementa un CRUD completo con validaciones de negocio, auditoría automática y gestión de inventario.

---

## 🎯 Características Implementadas

### ✅ Funcionalidades Principales

1. **CRUD Completo de Productos**
   - Crear producto con validaciones
   - Listar productos con filtros y búsqueda
   - Ver detalle completo de producto
   - Actualizar información de productos
   - Eliminar productos
   - Gestión de categorías

2. **Gestión de Inventario**
   - Control de stock actual y mínimo
   - Actualización de stock (entrada/salida)
   - Alertas de stock bajo
   - Múltiples unidades de medida

3. **Integración con Proveedores**
   - Relación con proveedores existentes
   - Trazabilidad del suministro

4. **Sistema de Promociones**
   - Aplicación de promociones vigentes
   - Cálculo automático de precios con descuento

5. **Auditoría Completa**
   - Registro de creación, modificación y eliminación
   - Rastreo de usuarios responsables

---

## 📊 Modelo de Datos

### CategoriaProducto

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer | ID único autoincremental |
| nombre | String (100) | Nombre de la categoría (único) |
| codigo | String (20) | Código único de categoría |
| descripcion | Text | Descripción opcional |
| activo | Boolean | Estado de la categoría |
| created_at | DateTime | Fecha de creación |
| updated_at | DateTime | Fecha de última actualización |

### Producto

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer | ID único autoincremental |
| nombre | String (200) | Nombre del producto |
| codigo | String (50) | Código/SKU único |
| descripcion | Text | Descripción detallada |
| categoria | ForeignKey | Categoría del producto |
| proveedor | ForeignKey | Proveedor que suministra |
| precio | Decimal (10,2) | Precio de venta (Bs.) |
| costo | Decimal (10,2) | Costo de adquisición (opcional) |
| stock | Integer | Cantidad en inventario |
| stock_minimo | Integer | Stock mínimo antes de reorden |
| unidad_medida | String (20) | Unidad (UNIDAD, KG, GR, LB, LITRO, ML, CAJA, PAQUETE) |
| promocion | ForeignKey | Promoción aplicable (opcional) |
| estado | String (20) | ACTIVO, INACTIVO, AGOTADO, DESCONTINUADO |
| creado_por | ForeignKey | Usuario que creó el registro |
| modificado_por | ForeignKey | Usuario que modificó el registro |
| created_at | DateTime | Fecha de creación |
| updated_at | DateTime | Fecha de última actualización |

**Índices:**
- `codigo` (índice único)
- `categoria + estado`
- `proveedor`
- `estado`

---

## 🔐 Estados del Producto

| Estado | Descripción |
|--------|-------------|
| `ACTIVO` | Producto disponible para venta |
| `INACTIVO` | Producto temporalmente no disponible |
| `AGOTADO` | Sin stock (automático cuando stock = 0) |
| `DESCONTINUADO` | Producto ya no se comercializará |

---

## 🔌 Endpoints API

### Categorías de Productos

#### Listar Categorías
```http
GET /api/categorias/
```

**Query Parameters:**
- `search`: Búsqueda por nombre, código o descripción
- `ordering`: Ordenamiento (nombre, codigo, created_at)

**Respuesta:**
```json
[
  {
    "id": 1,
    "nombre": "Suplementos Proteicos",
    "codigo": "SUP-PROT",
    "descripcion": "Proteínas, aminoácidos y ganadores de masa",
    "activo": true,
    "total_productos": 3,
    "created_at": "2025-11-24T10:00:00Z",
    "updated_at": "2025-11-24T10:00:00Z"
  }
]
```

#### Crear Categoría
```http
POST /api/categorias/
Content-Type: application/json
Authorization: Bearer {token}
```

**Body:**
```json
{
  "nombre": "Nueva Categoría",
  "codigo": "NEW-CAT",
  "descripcion": "Descripción de la categoría",
  "activo": true
}
```

#### Actualizar Categoría
```http
PUT /api/categorias/{id}/
PATCH /api/categorias/{id}/
```

#### Eliminar Categoría
```http
DELETE /api/categorias/{id}/
```

---

### Productos

#### Listar Productos
```http
GET /api/productos/
```

**Query Parameters:**
- `search`: Búsqueda por nombre, código o descripción
- `categoria`: Filtrar por ID de categoría
- `proveedor`: Filtrar por ID de proveedor
- `estado`: Filtrar por estado (ACTIVO, INACTIVO, etc.)
- `precio_min`: Precio mínimo
- `precio_max`: Precio máximo
- `stock_bajo`: `true` para productos con stock ≤ stock_mínimo
- `ordering`: Ordenamiento (nombre, codigo, precio, stock, created_at)
- `page`: Número de página
- `page_size`: Tamaño de página

**Respuesta:**
```json
{
  "count": 16,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "nombre": "Proteína Whey Gold Standard",
      "codigo": "PROT-WGS-001",
      "categoria": 1,
      "categoria_nombre": "Suplementos Proteicos",
      "proveedor": 1,
      "proveedor_nombre": "Distribuidora Fitness Bolivia",
      "precio": "280.00",
      "precio_con_descuento": "280.00",
      "stock": 50,
      "stock_minimo": 10,
      "necesita_reposicion": false,
      "estado": "ACTIVO",
      "promocion": null,
      "promocion_nombre": null,
      "created_at": "2025-11-24T10:00:00Z"
    }
  ]
}
```

#### Ver Detalle de Producto
```http
GET /api/productos/{id}/
```

**Respuesta:**
```json
{
  "id": 1,
  "nombre": "Proteína Whey Gold Standard",
  "codigo": "PROT-WGS-001",
  "descripcion": "Proteína de suero de leche de alta calidad...",
  "categoria": 1,
  "categoria_info": {
    "id": 1,
    "nombre": "Suplementos Proteicos",
    "codigo": "SUP-PROT"
  },
  "proveedor": 1,
  "proveedor_info": {
    "id": 1,
    "razon_social": "Distribuidora Fitness Bolivia",
    "nit": "1234567890"
  },
  "precio": "280.00",
  "costo": "200.00",
  "precio_con_descuento": "280.00",
  "margen_ganancia": "40.00",
  "stock": 50,
  "stock_minimo": 10,
  "unidad_medida": "UNIDAD",
  "necesita_reposicion": false,
  "promocion": null,
  "promocion_info": null,
  "estado": "ACTIVO",
  "creado_por": 1,
  "creado_por_nombre": "Admin User",
  "modificado_por": 1,
  "modificado_por_nombre": "Admin User",
  "created_at": "2025-11-24T10:00:00Z",
  "updated_at": "2025-11-24T10:00:00Z"
}
```

#### Crear Producto
```http
POST /api/productos/
Content-Type: application/json
Authorization: Bearer {token}
```

**Body:**
```json
{
  "nombre": "Proteína Vegana",
  "codigo": "PROT-VEG-001",
  "descripcion": "Proteína vegetal de guisante y arroz",
  "categoria": 1,
  "proveedor": 1,
  "precio": "250.00",
  "costo": "180.00",
  "stock": 30,
  "stock_minimo": 5,
  "unidad_medida": "UNIDAD",
  "estado": "ACTIVO"
}
```

**Validaciones:**
- `codigo`: Debe ser único
- `precio`: Debe ser mayor que 0 y mayor o igual que el costo
- `costo`: Opcional, debe ser mayor o igual que 0
- `stock`: Debe ser mayor o igual que 0
- `stock_minimo`: Debe ser mayor o igual que 0

#### Actualizar Producto
```http
PUT /api/productos/{id}/
PATCH /api/productos/{id}/
```

#### Eliminar Producto
```http
DELETE /api/productos/{id}/
```

---

### Acciones Especiales

#### Actualizar Stock
```http
POST /api/productos/{id}/actualizar-stock/
Content-Type: application/json
Authorization: Bearer {token}
```

**Body:**
```json
{
  "cantidad": 20,
  "operacion": "sumar",  // o "restar"
  "motivo": "Compra a proveedor"
}
```

**Respuesta:**
```json
{
  "message": "Stock actualizado correctamente",
  "stock_anterior": 50,
  "stock_actual": 70,
  "operacion": "sumar",
  "cantidad": 20
}
```

**Notas:**
- Al restar, valida que haya stock suficiente
- Si el stock llega a 0, cambia automáticamente el estado a AGOTADO
- Si el stock vuelve a ser mayor que 0, cambia de AGOTADO a ACTIVO

#### Productos con Stock Bajo
```http
GET /api/productos/bajo-stock/
```

Retorna productos donde `stock ≤ stock_minimo` y estado = ACTIVO

#### Solo Productos Activos
```http
GET /api/productos/activos/
```

#### Estadísticas de Productos
```http
GET /api/productos/estadisticas/
```

**Respuesta:**
```json
{
  "total_productos": 16,
  "productos_activos": 15,
  "productos_agotados": 0,
  "productos_bajo_stock": 2,
  "valor_total_inventario": "45600.00",
  "stock_total": 1130,
  "precio_promedio": "105.50"
}
```

---

## 🧪 Pruebas y Testing

### Ejecutar Tests
```bash
# Todos los tests de productos
docker compose exec backend python manage.py test apps.productos

# Tests de modelos
docker compose exec backend python manage.py test apps.productos.tests.ProductoModelTest

# Tests de API
docker compose exec backend python manage.py test apps.productos.tests.ProductoAPITest
```

### Casos de Prueba Incluidos

1. ✅ Creación de producto
2. ✅ Validación de código único
3. ✅ Validación de precio > costo
4. ✅ Cálculo de margen de ganancia
5. ✅ Detección de stock bajo
6. ✅ Actualización de stock (suma y resta)
7. ✅ Cambio automático de estado al agotar stock
8. ✅ Precio con descuento (con promoción)
9. ✅ CRUD completo vía API
10. ✅ Filtros y búsquedas

---

## 📝 Ejemplos de Uso

### Ejemplo 1: Buscar productos de una categoría específica
```bash
curl -H "Authorization: Bearer {token}" \
  "http://localhost:8000/api/productos/?categoria=1&estado=ACTIVO"
```

### Ejemplo 2: Registrar entrada de mercancía
```bash
curl -X POST \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"cantidad": 50, "operacion": "sumar", "motivo": "Compra a proveedor"}' \
  "http://localhost:8000/api/productos/1/actualizar-stock/"
```

### Ejemplo 3: Registrar venta (salida de inventario)
```bash
curl -X POST \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"cantidad": 2, "operacion": "restar", "motivo": "Venta a cliente"}' \
  "http://localhost:8000/api/productos/1/actualizar-stock/"
```

### Ejemplo 4: Buscar productos con stock bajo
```bash
curl -H "Authorization: Bearer {token}" \
  "http://localhost:8000/api/productos/bajo-stock/"
```

### Ejemplo 5: Buscar productos por precio
```bash
curl -H "Authorization: Bearer {token}" \
  "http://localhost:8000/api/productos/?precio_min=100&precio_max=300"
```

---

## 🔒 Permisos Requeridos

| Acción | Permiso |
|--------|---------|
| Listar productos | `productos.view` |
| Ver detalle | `productos.view` |
| Crear producto | `productos.create` |
| Actualizar producto | `productos.edit` |
| Eliminar producto | `productos.delete` |
| Actualizar stock | `productos.edit` |

---

## 📊 Datos de Prueba Cargados

El seeder carga automáticamente:

- **7 categorías**: Suplementos Proteicos, Energéticos, Vitaminas, Equipamiento, Indumentaria, Bebidas, Snacks
- **16 productos** distribuidos en todas las categorías
- **1 proveedor** de ejemplo si no existe ninguno

### Productos Incluidos:
1. Proteína Whey Gold Standard - Bs. 280.00
2. Proteína Isolate Premium - Bs. 350.00
3. Creatina Monohidrato 300g - Bs. 120.00
4. Pre-Entreno Explosive - Bs. 150.00
5. Quemador de Grasa Thermo - Bs. 180.00
6. Multivitamínico Daily - Bs. 90.00
7. Omega 3 1000mg - Bs. 110.00
8. Guantes de Entrenamiento Pro - Bs. 65.00
9. Shaker Mezclador 700ml - Bs. 35.00
10. Cinta para Muñecas - Bs. 45.00
11. Camiseta Deportiva Dry-Fit - Bs. 85.00
12. Short de Entrenamiento - Bs. 75.00
13. Bebida Isotónica 500ml - Bs. 12.00
14. Energético Sport 250ml - Bs. 15.00
15. Barra Proteica Chocolate - Bs. 18.00
16. Mix de Frutos Secos 200g - Bs. 35.00

---

## 🎨 Propiedades Calculadas

### precio_con_descuento
Calcula automáticamente el precio con descuento si hay una promoción vigente:
- Tipo `porcentaje`: `precio - (precio * valor / 100)`
- Tipo `monto_fijo`: `precio - valor`

### necesita_reposicion
Retorna `True` si `stock ≤ stock_minimo`

### margen_ganancia
Calcula el porcentaje de ganancia: `((precio - costo) / costo) * 100`

---

## 🔄 Flujo de Trabajo Recomendado

1. **Configuración Inicial**
   ```bash
   # Crear categorías
   POST /api/categorias/
   ```

2. **Registro de Producto**
   ```bash
   # Seleccionar categoría
   # Seleccionar proveedor
   # Ingresar datos del producto
   # Registrar precio y stock inicial
   POST /api/productos/
   ```

3. **Gestión de Inventario**
   ```bash
   # Al recibir mercancía
   POST /api/productos/{id}/actualizar-stock/
   {cantidad: X, operacion: "sumar"}
   
   # Al vender
   POST /api/productos/{id}/actualizar-stock/
   {cantidad: X, operacion: "restar"}
   ```

4. **Monitoreo**
   ```bash
   # Revisar stock bajo
   GET /api/productos/bajo-stock/
   
   # Ver estadísticas
   GET /api/productos/estadisticas/
   ```

5. **Aplicar Promociones** (opcional)
   ```bash
   # Asignar promoción a producto
   PATCH /api/productos/{id}/
   {promocion: {id_promocion}}
   ```

---

## ✅ Checklist de Implementación

- [x] Modelos (CategoriaProducto, Producto)
- [x] Migraciones de base de datos
- [x] Serializers (List, Detail, CreateUpdate)
- [x] ViewSets con CRUD completo
- [x] Filtros y búsqueda
- [x] Paginación
- [x] Validaciones de negocio
- [x] Auditoría automática
- [x] Gestión de stock
- [x] Cálculo de precios con descuento
- [x] Propiedades calculadas
- [x] Tests unitarios
- [x] Tests de API
- [x] Seeder de datos de prueba
- [x] Documentación completa
- [x] Endpoints RESTful
- [x] Permisos y seguridad
- [x] Admin de Django

---

## 🚀 Próximas Mejoras Sugeridas

1. **Historial de Movimientos de Stock**
   - Tabla para registrar cada entrada/salida
   - Reporte de movimientos por período

2. **Códigos de Barras**
   - Generación automática de códigos EAN-13
   - Escaneo con dispositivos móviles

3. **Fotos de Productos**
   - Campo ImageField
   - Galería de imágenes

4. **Alertas Automáticas**
   - Notificaciones por email de stock bajo
   - Alertas de productos por vencer

5. **Reportes Avanzados**
   - Productos más vendidos
   - Análisis de rotación de inventario
   - Productos con menor margen

6. **Ventas y Facturación**
   - Módulo de ventas integrado
   - Generación de facturas
   - Registro de transacciones

---

**Última actualización:** 24 de Noviembre, 2025  
**Versión:** 1.0.0  
**Caso de Uso:** CU24 - Registrar Producto
