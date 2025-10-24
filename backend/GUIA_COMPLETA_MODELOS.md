# 🎯 GUÍA COMPLETA: MODELOS FUNCIONALES SEGÚN UML

## ✅ CAMBIOS REALIZADOS

### 1. **Cliente** - Modelo actualizado

**Archivo:** `backend/apps/clients/models.py`

**Campos agregados:**

- ✅ `peso` (DECIMAL 5,2) - Peso en kilogramos
- ✅ `altura` (DECIMAL 3,2) - Altura en metros
- ✅ `experiencia` (VARCHAR 20) - Nivel: PRINCIPIANTE, INTERMEDIO, AVANZADO

### 2. **Membresías** - Modelos actualizados y nuevos

**Archivo:** `backend/apps/membresias/models.py`

**Modelo NUEVO: PlanMembresia**

```python
- nombre: Plan Mensual, Trimestral, etc.
- duracion: Días de duración
- precio_base: Precio del plan
- descripcion: Descripción del plan
```

**Modelo actualizado: Membresia**

- ✅ Agregado campo `plan` (FK a PlanMembresia)
- ✅ Agregada relación M2M con Promocion (through MembresiaPromocion)

**Modelo NUEVO: MembresiaPromocion**

- Tabla intermedia para aplicar promociones a membresías

### 3. **Promoción** - Modelo actualizado según PUML

**Archivo:** `backend/apps/promociones/models.py`

**Campos modificados:**

- ✅ `meses` (INT) - Duración en meses (antes: descripcion)
- ✅ `descuento` (DECIMAL 5,2) - Porcentaje de descuento (antes: valor_descuento)
- ✅ `estado` (VARCHAR 20) - ACTIVA, INACTIVA, VENCIDA (antes: activo boolean)
- ❌ Removido: `tipo_descuento`, `codigo`, `descripcion`

### 4. **Roles y Permisos** - Ya funcionales ✅

**Archivo:** `backend/apps/roles/models.py`

- ✅ Usuario → Roles (M2M through UserRole)
- ✅ Rol → Permisos (M2M through RolPermiso)
- ✅ Sistema de permisos completo

### 5. **Bitácora** - Ya funcional ✅

**Archivo:** `backend/apps/audit/models.py`

- ✅ Registro automático de actividades
- ✅ Middleware configurado
- ✅ Helpers disponibles

---

## 📋 INSTRUCCIONES PARA RESETEAR LA BASE DE DATOS

### ⚠️ IMPORTANTE: Sobre las migraciones

**SÍ, ES NECESARIO BORRAR LAS MIGRACIONES** porque:

1. Los modelos cambiaron estructuralmente (nuevos campos, nuevas relaciones)
2. Evitamos conflictos entre migraciones antiguas y nuevas
3. Partimos de cero con una base de datos limpia y consistente

### Opción 1: Usar el script PowerShell (RECOMENDADO)

```powershell
# Desde la raíz del proyecto
.\scripts\reset_migrations.ps1
```

Este script hace:

1. ✅ Backup automático de la BD actual
2. ✅ Elimina la base de datos
3. ✅ Elimina todas las migraciones (excepto **init**.py)
4. ✅ Crea nuevas migraciones
5. ✅ Aplica las migraciones
6. ✅ Opción para crear superusuario

### Opción 2: Manual (PowerShell)

```powershell
# 1. Hacer backup (opcional)
Copy-Item backend\db.sqlite3 backend\db.sqlite3.backup

# 2. Eliminar base de datos
Remove-Item backend\db.sqlite3

# 3. Eliminar migraciones
$apps = @("clients", "membresias", "users", "roles", "promociones", "audit", "core")
foreach ($app in $apps) {
    Get-ChildItem -Path "backend\apps\$app\migrations" -Filter "0*.py" | Remove-Item -Force
}

# 4. Ir a backend
cd backend

# 5. Crear migraciones
python manage.py makemigrations

# 6. Aplicar migraciones
python manage.py migrate

# 7. Crear superusuario
python manage.py createsuperuser

# 8. Ejecutar seeders (datos de prueba)
python seeders/run_all_seeders.py

# 9. Iniciar servidor
python manage.py runserver
```

---

## 🌱 SEEDERS ACTUALIZADOS

Se crearon/actualizaron los siguientes seeders:

### 1. **plan_membresia_seeder.py** (NUEVO)

Crea planes predefinidos:

- Plan Diario (1 día - Bs. 15)
- Plan Semanal (7 días - Bs. 80)
- Plan Quincenal (15 días - Bs. 140)
- Plan Mensual (30 días - Bs. 250)
- Plan Trimestral (90 días - Bs. 650)
- Plan Semestral (180 días - Bs. 1200)
- Plan Anual (365 días - Bs. 2200)

### 2. **promocion_seeder.py** (NUEVO)

Crea promociones predefinidas:

- Promoción Año Nuevo (1 mes - 15% desc.)
- Promoción Verano (3 meses - 20% desc.)
- Black Friday Gym (6 meses - 30% desc.)
- Estudiantes (1 mes - 10% desc.)
- Referido (1 mes - 25% desc.)

### 3. **clients_seeder.py** (ACTUALIZADO)

Ahora incluye: peso, altura, experiencia

### 4. **run_all_seeders.py** (ACTUALIZADO)

Ejecuta todos los seeders en orden:

1. SuperUser
2. Roles y Permisos
3. Usuarios
4. Clientes
5. Planes de Membresía ← NUEVO
6. Promociones ← NUEVO

---

## 🔗 RELACIONES FUNCIONALES

### Flujo completo: Cliente → Membresía

```python
# 1. Cliente se registra
cliente = Client.objects.create(
    nombre="Juan",
    apellido="Pérez",
    ci="12345678",
    telefono="70123456",
    peso=75.5,
    altura=1.75,
    experiencia="INTERMEDIO"
)

# 2. Se elige un plan
plan = PlanMembresia.objects.get(nombre="Plan Mensual")

# 3. Cliente paga
inscripcion = InscripcionMembresia.objects.create(
    cliente=cliente,
    monto=plan.precio_base,
    metodo_de_pago="EFECTIVO"
)

# 4. Se crea la membresía
membresia = Membresia.objects.create(
    inscripcion=inscripcion,
    plan=plan,
    usuario_registro=usuario_logueado,
    estado="ACTIVA",
    fecha_inicio=date.today(),
    fecha_fin=date.today() + timedelta(days=plan.duracion)
)

# 5. (Opcional) Aplicar promoción
promocion = Promocion.objects.get(nombre="Promoción Verano")
MembresiaPromocion.objects.create(
    membresia=membresia,
    promocion=promocion
)
```

### Flujo completo: Usuario → Roles → Permisos

```python
# 1. Crear permisos
permiso = Permiso.objects.create(
    nombre="gestionar_clientes",
    descripcion="Puede crear, editar y eliminar clientes"
)

# 2. Crear rol
rol = Role.objects.create(
    nombre="Recepcionista",
    descripcion="Personal de recepción"
)

# 3. Asignar permiso al rol
RolPermiso.objects.create(rol=rol, permiso=permiso)

# 4. Asignar rol a usuario
UserRole.objects.create(usuario=usuario, rol=rol)

# 5. Usuario ahora tiene el permiso
usuario.roles.all()  # [<Role: Recepcionista>]
usuario.roles.first().permisos.all()  # [<Permiso: gestionar_clientes>]
```

---

## ✅ VERIFICACIÓN POST-MIGRACIÓN

### 1. Verificar que las tablas se crearon correctamente

```powershell
cd backend
python manage.py dbshell
```

En SQLite:

```sql
.tables
-- Deberías ver:
-- cliente
-- plan_membresia (NUEVO)
-- inscripcion_membresia
-- membresia
-- membresia_promocion (NUEVO)
-- promocion
-- usuario
-- roles
-- permiso
-- usuario_rol
-- rol_permiso
-- historial_actividad

.exit
```

### 2. Verificar desde Django Admin

```powershell
python manage.py runserver
```

Ir a: http://localhost:8000/admin

**Login:**

- Usuario: admin@gym-spartan.com
- Contraseña: admin123

**Verificar que aparezcan:**

- ✅ Clientes (con campos: peso, altura, experiencia)
- ✅ Planes de Membresía (NUEVO)
- ✅ Inscripciones Membresía
- ✅ Membresías (con plan y promociones)
- ✅ Promociones (con meses, descuento, estado)
- ✅ Usuarios
- ✅ Roles
- ✅ Permisos
- ✅ Bitácora del Sistema

### 3. Probar creación desde Admin

1. **Crear un cliente:**

   - Dashboard → Clientes → Añadir cliente
   - Llenar: nombre, apellido, CI, teléfono, peso, altura, experiencia

2. **Crear una membresía:**

   - Dashboard → Membresías → Añadir membresía
   - Primero crear inscripción (cliente + monto + método pago)
   - Luego crear membresía (inscripción + plan + fechas)

3. **Asignar rol a usuario:**

   - Dashboard → Usuarios → Editar usuario
   - En "Roles" seleccionar el rol

4. **Aplicar promoción:**
   - Dashboard → Membresías → Editar membresía
   - En "Promociones aplicadas" agregar promoción

---

## 🚀 PRÓXIMOS PASOS

### 1. Actualizar el frontend

Los endpoints del backend ahora incluyen más campos. Actualizar:

**Cliente:**

```typescript
interface Client {
  id: number;
  nombre: string;
  apellido: string;
  ci: string;
  telefono: string;
  email: string;
  peso?: number; // NUEVO
  altura?: number; // NUEVO
  experiencia: string; // NUEVO
  fecha_registro: string;
}
```

**Membresía:**

```typescript
interface Membresia {
  id: number;
  inscripcion: InscripcionMembresia;
  plan: PlanMembresia; // NUEVO
  promociones_aplicadas: Promocion[]; // NUEVO
  estado: string;
  fecha_inicio: string;
  fecha_fin: string;
  // ... demás campos
}
```

### 2. Crear servicios para nuevos modelos

Crear en `frontend/lib/services/`:

- `plan-membresia.service.ts`
- Actualizar `membresia.service.ts`
- Actualizar `client.service.ts`
- Actualizar `promocion.service.ts`

### 3. Actualizar formularios

- Formulario de cliente: agregar peso, altura, experiencia
- Formulario de membresía: agregar selector de plan
- Formulario de membresía: agregar selector de promociones

---

## 📝 ARCHIVOS IMPORTANTES CREADOS

1. ✅ `INSTRUCCIONES_RESET_DB.md` - Instrucciones de reseteo
2. ✅ `RELACIONES_FUNCIONALES.md` - Diagrama de relaciones y ejemplos
3. ✅ `scripts/reset_migrations.ps1` - Script automatizado
4. ✅ `seeders/plan_membresia_seeder.py` - Seeder de planes
5. ✅ `seeders/promocion_seeder.py` - Seeder de promociones

---

## 🔍 SOLUCIÓN DE PROBLEMAS

### Error: "No such table: plan_membresia"

**Solución:** Ejecutar migraciones

```powershell
cd backend
python manage.py migrate
```

### Error: "FOREIGN KEY constraint failed"

**Solución:** Ejecutar seeders en orden

```powershell
python seeders/run_all_seeders.py
```

### Error: Campos no aparecen en Admin

**Solución:** Reiniciar servidor

```powershell
# Ctrl+C para detener
python manage.py runserver
```

---

## 📞 RESUMEN EJECUTIVO

### ¿Qué se hizo?

✅ Actualizados todos los modelos según diagrama UML  
✅ Agregados campos faltantes a Cliente  
✅ Creado modelo PlanMembresia  
✅ Actualizado modelo Promoción  
✅ Creada relación M2M Membresía-Promoción  
✅ Actualizados serializers y admins  
✅ Creados seeders nuevos  
✅ Creado script de reseteo automático

### ¿Es necesario borrar migraciones?

✅ **SÍ** - Los cambios estructurales requieren reseteo completo

### ¿Cómo resetear?

```powershell
.\scripts\reset_migrations.ps1
```

### ¿Cómo poblar con datos?

```powershell
cd backend
python seeders/run_all_seeders.py
```

### ¿Cómo verificar?

```powershell
python manage.py runserver
# Ir a http://localhost:8000/admin
```

---

## 🎉 ¡LISTO!

Ahora todos los módulos están funcionales según el diagrama UML:

- ✅ Cliente puede tener membresías
- ✅ Membresía tiene plan y puede tener promociones
- ✅ Usuario tiene roles
- ✅ Rol tiene permisos
- ✅ Todo se registra en bitácora
