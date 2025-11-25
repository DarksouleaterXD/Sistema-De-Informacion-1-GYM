# CU29 - Registrar Proveedor

## 📋 Descripción
Implementación completa del Caso de Uso 29: **Registrar Proveedor**. Permite a administradores y dueños registrar nuevos proveedores en el sistema con validaciones completas y registro en bitácora.

## 🎯 Requisitos Implementados

### Campos del Modelo
- ✅ **Obligatorios**: `razon_social`, `nit`
- ✅ **Opcionales**: `telefono`, `email`, `direccion`, `contacto_nombre`, `notas`
- ✅ **Estado inicial**: Activo (por defecto)

### Validaciones
- ✅ **Email**: Formato válido con `EmailValidator`
- ✅ **Teléfono**: 7-15 dígitos numéricos
- ✅ **Unicidad**: NIT y razón social únicos en BD
- ✅ **Normalización**: 
  - NIT a mayúsculas
  - Email a minúsculas
  - Teléfono solo dígitos

### Códigos de Respuesta HTTP
- ✅ **201**: Proveedor creado exitosamente
- ✅ **400**: Datos de entrada inválidos
- ✅ **403**: Permisos insuficientes (requiere autenticación)
- ✅ **409**: NIT o razón social duplicados (IntegrityError)
- ✅ **422**: Validación de formato fallida
- ✅ **500**: Error de persistencia/servidor

### Auditoría
- ✅ Registro en bitácora con:
  - Usuario que realiza la acción
  - IP del cliente
  - Fecha y hora
  - Datos del proveedor creado

## 🏗️ Arquitectura

### Estructura de Capas
```
apps/proveedores/
├── models.py          # Modelo de datos con validaciones
├── serializers.py     # DTOs de entrada/salida con validaciones
├── views.py           # Controllers (APIView)
├── admin.py           # Panel de administración Django
├── tests.py           # Tests unitarios (22 tests)
└── migrations/        # Migraciones de BD
```

### Separación de Responsabilidades
1. **Model** (`Proveedor`): Lógica de negocio y validaciones a nivel de BD
2. **Serializers**: 
   - `ProveedorCreateSerializer`: DTO de entrada con validaciones
   - `ProveedorResponseSerializer`: DTO de respuesta completo
   - `ProveedorListSerializer`: DTO simplificado para listados
   - `ProveedorUpdateSerializer`: DTO para actualizaciones
3. **Views**: 
   - `ProveedorListCreateView`: Lista y creación (GET/POST)
   - `ProveedorDetailView`: Detalle, actualización y eliminación (GET/PUT/PATCH/DELETE)

## 📊 Modelo de Datos

### Tabla: `proveedor`
```sql
CREATE TABLE proveedor (
    id BIGSERIAL PRIMARY KEY,
    razon_social VARCHAR(200) UNIQUE NOT NULL,
    nit VARCHAR(50) UNIQUE NOT NULL,
    telefono VARCHAR(15),
    email VARCHAR(254),
    direccion TEXT,
    contacto_nombre VARCHAR(100),
    notas TEXT,
    estado CHAR(1) DEFAULT 'A',
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- Índices
CREATE INDEX proveedor_nit_idx ON proveedor(nit);
CREATE INDEX proveedor_razon_idx ON proveedor(razon_social);
CREATE INDEX proveedor_estado_idx ON proveedor(estado);

-- Constraints
ALTER TABLE proveedor ADD CONSTRAINT unique_proveedor_nit UNIQUE (nit);
ALTER TABLE proveedor ADD CONSTRAINT unique_proveedor_razon_social UNIQUE (razon_social);
```

### Estados del Proveedor
- `A`: Activo
- `I`: Inactivo
- `S`: Suspendido

## 🔌 API Endpoints

### 1. Crear Proveedor (CU29)
```http
POST /api/proveedores/
Authorization: Bearer {token}
Content-Type: application/json

{
  "razon_social": "Distribuidora ABC S.A.",
  "nit": "1234567890",
  "telefono": "71234567",
  "email": "contacto@abc.com",
  "direccion": "Av. Principal #123",
  "contacto_nombre": "Juan Pérez",
  "notas": "Proveedor principal"
}
```

**Respuesta 201 Created:**
```json
{
  "id": 1,
  "razon_social": "Distribuidora ABC S.A.",
  "nit": "1234567890",
  "telefono": "71234567",
  "email": "contacto@abc.com",
  "direccion": "Av. Principal #123",
  "contacto_nombre": "Juan Pérez",
  "notas": "Proveedor principal",
  "estado": "A",
  "estado_display": "Activo",
  "esta_activo": true,
  "created_at": "2025-11-23T10:30:00Z",
  "updated_at": "2025-11-23T10:30:00Z"
}
```

**Errores Posibles:**

**422 Unprocessable Entity** (Validación):
```json
{
  "error": "Validación fallida",
  "detail": {
    "email": ["Ingrese un correo electrónico válido."],
    "telefono": ["El teléfono debe tener al menos 7 dígitos."]
  }
}
```

**422 Unprocessable Entity** (NIT duplicado):
```json
{
  "error": "Validación fallida",
  "detail": {
    "nit": ["Ya existe un proveedor con este NIT."]
  }
}
```

**403 Forbidden** (Sin autenticación):
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 2. Listar Proveedores
```http
GET /api/proveedores/?search=ABC&estado=A&page=1&page_size=10
Authorization: Bearer {token}
```

**Respuesta 200 OK:**
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/proveedores/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "razon_social": "Distribuidora ABC S.A.",
      "nit": "1234567890",
      "telefono": "71234567",
      "email": "contacto@abc.com",
      "estado": "A",
      "estado_display": "Activo",
      "created_at": "2025-11-23T10:30:00Z"
    }
  ]
}
```

### 3. Obtener Detalle
```http
GET /api/proveedores/{id}/
Authorization: Bearer {token}
```

### 4. Actualizar Proveedor
```http
PUT /api/proveedores/{id}/
PATCH /api/proveedores/{id}/
Authorization: Bearer {token}
```

### 5. Eliminar (Desactivar) Proveedor
```http
DELETE /api/proveedores/{id}/
Authorization: Bearer {token}
```

## ✅ Tests

### Ejecutar Tests
```bash
# En Docker
docker exec spartan_backend python manage.py test apps.proveedores.tests

# Local
python manage.py test apps.proveedores.tests
```

### Cobertura de Tests (22 tests)

#### Tests del Modelo
- ✅ Crear proveedor exitoso
- ✅ Representación string
- ✅ Unicidad de NIT
- ✅ Unicidad de razón social
- ✅ Cambios de estado (activar, desactivar, suspender)

#### Tests de API
- ✅ Crear proveedor exitoso (201)
- ✅ Crear con datos mínimos
- ✅ NIT duplicado (422)
- ✅ Razón social duplicada (422)
- ✅ Sin razón social (422)
- ✅ Sin NIT (422)
- ✅ Email inválido (422)
- ✅ Teléfono muy corto (422)
- ✅ Teléfono muy largo (422)
- ✅ Teléfonos válidos (7-15 dígitos)
- ✅ Listar proveedores
- ✅ Obtener detalle
- ✅ Sin autenticación (401/403)
- ✅ Registro en bitácora

#### Tests de Validación
- ✅ Normalizar NIT a mayúsculas
- ✅ Normalizar teléfono a solo dígitos
- ✅ Normalizar email a minúsculas

## 🧪 Pruebas Manuales

### Script de Pruebas
```bash
# Ejecutar script de pruebas manuales
cd backend
python test_cu29.py
```

El script `test_cu29.py` incluye:
1. Autenticación
2. Crear proveedor exitoso
3. NIT duplicado
4. Email inválido
5. Teléfono inválido
6. Listar proveedores
7. Obtener detalle

### Con cURL

**Crear proveedor:**
```bash
curl -X POST http://localhost:8000/api/proveedores/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "razon_social": "Test Proveedor",
    "nit": "TEST123",
    "telefono": "71234567",
    "email": "test@proveedor.com"
  }'
```

## 📝 Registro en Bitácora

Cada operación se registra en `HistorialActividad`:

```python
{
  "usuario": "admin",
  "accion": "Proveedor creado",
  "descripcion": "Proveedor 'Distribuidora ABC S.A.' (NIT: 1234567890) creado exitosamente",
  "modulo": "PROVEEDORES",
  "tipo_accion": "create",
  "nivel": "info",
  "ip_address": "192.168.1.100",
  "fecha_hora": "2025-11-23T10:30:00Z",
  "datos_adicionales": {
    "proveedor_id": 1,
    "nit": "1234567890",
    "razon_social": "Distribuidora ABC S.A.",
    "estado": "A"
  }
}
```

## 🔒 Seguridad

- ✅ Autenticación requerida (`IsAuthenticated`)
- ✅ Validación de entrada en múltiples capas
- ✅ Prevención de SQL injection (ORM Django)
- ✅ Sanitización de datos (normalización)
- ✅ Auditoría completa de operaciones

## 📚 Integración con Otros CU

### Preparado para:
- **CU30**: Gestionar Órdenes de Compra (FK a Proveedor)
- **Productos**: Vincular productos con proveedores
- **Inventario**: Relacionar compras con proveedores

## 🚀 Deployment

### Migraciones
```bash
# Crear migraciones
docker exec spartan_backend python manage.py makemigrations proveedores

# Aplicar migraciones
docker exec spartan_backend python manage.py migrate proveedores
```

### Configuración
1. App registrada en `INSTALLED_APPS`
2. URLs registradas en `config/urls.py`
3. Modelos registrados en Django Admin
4. Middleware de auditoría activo

## 📖 Documentación API

La API está documentada con:
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **Schema OpenAPI**: http://localhost:8000/api/schema/

## 🎨 Convenciones de Código

- ✅ PEP 8 compliance
- ✅ Type hints en funciones críticas
- ✅ Docstrings en español
- ✅ Nombres descriptivos
- ✅ Separación de capas (Model-Serializer-View)
- ✅ DRY (Don't Repeat Yourself)
- ✅ SOLID principles

## 🔧 Mantenimiento

### Agregar Validación Nueva
1. Actualizar `models.py` (método `clean()`)
2. Actualizar serializers (método `validate_campo()`)
3. Agregar tests
4. Documentar en este README

### Agregar Campo Nuevo
1. Modificar modelo
2. Crear migración
3. Actualizar serializers
4. Actualizar tests
5. Actualizar documentación

## 📞 Soporte

Para dudas o problemas:
1. Revisar tests en `apps/proveedores/tests.py`
2. Revisar logs de auditoría
3. Consultar documentación de Django REST Framework
4. Revisar código de otros módulos (clientes, disciplinas) como referencia
