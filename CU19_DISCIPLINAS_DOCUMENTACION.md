# CU19: Gestionar Disciplinas - Documentación Completa

## 📋 Descripción
Implementación completa del Caso de Uso 19: **Gestionar Disciplinas**. Permite registrar, editar, eliminar y consultar las disciplinas (actividades) ofrecidas por el gimnasio.

## ✅ Funcionalidades Implementadas

### Backend (Django REST Framework)
1. **Modelo de Datos** (`apps/disciplinas/models.py`)
   - `Disciplina`: nombre (único), descripción, activa (boolean)
   - Hereda de `TimeStampedModel` (created_at, updated_at)
   - Validación de unicidad en nombre

2. **Serializers** (`apps/disciplinas/serializers.py`)
   - `DisciplinaSerializer`: Serialización completa con validación de duplicados
   - Validación case-insensitive para nombre único

3. **Views/API** (`apps/disciplinas/views.py`)
   - `DisciplinaListCreateView`: GET (listar) + POST (crear)
     - Paginación: 10 items por página
     - Búsqueda: por nombre o descripción
     - Filtro: por estado activa
   - `DisciplinaDetailView`: GET (detalle) + PUT/PATCH (editar) + DELETE (eliminar)
   - Auditoría: Todas las operaciones registran en bitácora

4. **URLs**
   - `GET/POST /api/disciplinas/`: Listar y crear disciplinas
   - `GET/PUT/PATCH/DELETE /api/disciplinas/<id>/`: Operaciones sobre disciplina específica

5. **Permisos**
   - `discipline.view`: Ver disciplinas
   - `discipline.create`: Crear disciplinas
   - `discipline.edit`: Editar disciplinas
   - `discipline.delete`: Eliminar disciplinas

### Frontend (Next.js + TypeScript + Tailwind)
1. **Servicio** (`lib/services/disciplina.service.ts`)
   - Interfaces TypeScript completas
   - Métodos CRUD: getDisciplinas, createDisciplina, updateDisciplina, deleteDisciplina

2. **Componentes**
   - `CreateEditDisciplinaModal.tsx`: Modal para crear/editar disciplinas
     - Formulario con validación
     - Modo crear y editar con mismo componente
     - Checkbox para estado activa/inactiva
   - `DeleteDisciplinaModal.tsx`: Confirmación de eliminación
     - Advertencia clara al usuario
     - Mensaje de confirmación

3. **Página Principal** (`app/dashboard/disciplinas/page.tsx`)
   - Tabla completa con todas las disciplinas
   - Búsqueda en tiempo real (nombre/descripción)
   - Filtros: Todas / Activas / Inactivas
   - Paginación (10 por página)
   - Botones de acción: Editar y Eliminar
   - Badge visual para estado (Activa/Inactiva)
   - Responsive design

4. **Integración con Sistema**
   - Agregada opción "Disciplinas" en sidebar con icono Dumbbell
   - Control de acceso basado en permisos (RBAC)
   - Ruta: `/dashboard/disciplinas`

## 🗄️ Migración de Base de Datos
```bash
# Crear migración
docker-compose exec backend python manage.py makemigrations disciplinas

# Aplicar migración
docker-compose exec backend python manage.py migrate
```

**Resultado**: Tabla `disciplina` creada con campos:
- id (PK, auto)
- nombre (VARCHAR 100, UNIQUE)
- descripcion (TEXT)
- activa (BOOLEAN, default=True)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

## 🌱 Seeders
### Disciplinas de Prueba (`seeders/disciplinas_seeder.py`)
10 disciplinas creadas:
1. ✅ Yoga (activa)
2. ✅ Spinning (activa)
3. ✅ CrossFit (activa)
4. ✅ Pilates (activa)
5. ✅ Zumba (activa)
6. ✅ Boxeo (activa)
7. ✅ Funcional (activa)
8. ✅ GAP (activa)
9. ✅ TRX (activa)
10. ❌ Natación (inactiva - piscina en mantenimiento)

**Ejecutar seeder:**
```bash
docker-compose exec backend python seeders/disciplinas_seeder.py
```

## 🔐 Permisos y RBAC
Los permisos de disciplinas se agregaron a:
- ✅ **Administrador**: Todos los permisos (50 total, incluyendo discipline.*)
- ✅ **Administrativo**: Permisos de gestión (25 total)
- ❌ **Instructor**: Sin permisos de disciplinas (solo lectura de clientes y membresías)

**Actualizar permisos:**
```bash
docker-compose exec backend python seeders/setup_rbac.py
```

## 🧪 Testing Manual
### Backend
```bash
# Listar disciplinas
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/disciplinas/

# Crear disciplina
curl -X POST -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Aerobics","descripcion":"Ejercicio aeróbico","activa":true}' \
  http://localhost:8000/api/disciplinas/

# Buscar disciplinas
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/disciplinas/?search=yoga"

# Filtrar por activas
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/disciplinas/?activa=true"
```

### Frontend
1. Login con usuario admin
2. Navegar a **Dashboard > Disciplinas**
3. **Crear**: Click en "Nueva Disciplina" → Llenar formulario → Guardar
4. **Editar**: Click en icono lápiz → Modificar datos → Guardar Cambios
5. **Eliminar**: Click en icono papelera → Confirmar eliminación
6. **Buscar**: Escribir en barra de búsqueda (actualiza en tiempo real)
7. **Filtrar**: Seleccionar "Activas" o "Inactivas" en dropdown

## 📝 Auditoría (Bitácora)
Todas las operaciones registran en la tabla `audit_log`:
- **CREATE**: `modulo="DISCIPLINAS"`, `actividad="CREAR"`
- **UPDATE**: `modulo="DISCIPLINAS"`, `actividad="ACTUALIZAR"`
- **DELETE**: `modulo="DISCIPLINAS"`, `actividad="ELIMINAR"`

Ver auditoría:
```python
from apps.audit.models import AuditLog
AuditLog.objects.filter(modulo="DISCIPLINAS").order_by('-created_at')
```

## 📂 Archivos Creados/Modificados

### Backend
**Creados:**
- `apps/disciplinas/__init__.py`
- `apps/disciplinas/apps.py`
- `apps/disciplinas/models.py`
- `apps/disciplinas/admin.py`
- `apps/disciplinas/serializers.py`
- `apps/disciplinas/views.py`
- `apps/disciplinas/tests.py`
- `apps/disciplinas/migrations/0001_initial.py`
- `seeders/disciplinas_seeder.py`

**Modificados:**
- `config/settings.py`: Agregada 'apps.disciplinas' a INSTALLED_APPS
- `config/urls.py`: Agregadas rutas /api/disciplinas/
- `apps/core/permissions.py`: Agregados 4 permisos de disciplinas
- `seeders/permissions_seeder.py`: Agregados permisos DISCIPLINE_*
- `seeders/roles_default_seeder.py`: Corregido uso de 'codigo' en lugar de 'nombre'

### Frontend
**Creados:**
- `lib/services/disciplina.service.ts`
- `components/disciplinas/CreateEditDisciplinaModal.tsx`
- `components/disciplinas/DeleteDisciplinaModal.tsx`
- `app/dashboard/disciplinas/page.tsx`

**Modificados:**
- `components/layout/sidebar.tsx`: Agregado link a Disciplinas
- `lib/utils/permissions.ts`: Agregados permisos DISCIPLINE_*

## 🔄 Dependencias con Otros CU
### Este CU es requerido por:
- **CU20: Programar Clase**: Necesita disciplinas para asignar a clases
- **CU21: Editar Clase**: Permite cambiar disciplina de una clase
- **CU22: Cancelar Clase**: Referencia a disciplina en clases canceladas

## 🎯 Criterios de Aceptación
- ✅ Registrar nueva disciplina con nombre único
- ✅ Editar información de disciplina existente
- ✅ Eliminar disciplina (con confirmación)
- ✅ Listar disciplinas con filtros
- ✅ Validar campos obligatorios (nombre, descripción)
- ✅ Verificar duplicidad de nombre (case-insensitive)
- ✅ Registrar auditoría de todas las operaciones
- ✅ Marcar disciplinas como activas/inactivas
- ✅ Búsqueda por nombre o descripción
- ✅ Paginación para grandes cantidades de datos

## 🚀 Comandos de Inicialización Completa
```bash
# 1. Crear y aplicar migraciones
docker-compose exec backend python manage.py makemigrations disciplinas
docker-compose exec backend python manage.py migrate

# 2. Crear permisos y roles
docker-compose exec backend python seeders/setup_rbac.py

# 3. Crear disciplinas de prueba
docker-compose exec backend python seeders/disciplinas_seeder.py

# 4. Reiniciar servicios
docker-compose restart backend frontend
```

## ✅ Estado: COMPLETADO
- Backend: 100% ✅
- Frontend: 100% ✅
- Permisos: 100% ✅
- Auditoría: 100% ✅
- Seeders: 100% ✅
- Testing: 100% ✅
- Documentación: 100% ✅

---
**Desarrollado por**: GitHub Copilot  
**Fecha**: 2024  
**Versión**: 1.0.0
