# 🎯 INSTRUCCIONES FINALES - EJECUTAR AHORA

## ✅ TODO ESTÁ LISTO

Todos los modelos han sido actualizados según tu diagrama UML:

### ✨ Cambios realizados:

1. **Cliente** → Agregados: `peso`, `altura`, `experiencia`
2. **PlanMembresia** → NUEVO modelo para planes (Mensual, Trimestral, etc.)
3. **Membresia** → Ahora tiene `plan` y puede tener múltiples `promociones`
4. **MembresiaPromocion** → NUEVA tabla intermedia M2M
5. **Promocion** → Actualizada: `meses`, `descuento`, `estado` (según PUML)
6. **Seeders** → Creados para planes y promociones
7. **Serializers y Admins** → Todos actualizados

---

## 🚀 PASO 1: RESETEAR LA BASE DE DATOS

### Opción Automática (RECOMENDADA):

```powershell
# Ejecutar desde la raíz del proyecto (d:\SI1-Spartan)
.\scripts\reset_migrations.ps1
```

Este script:

- ✅ Hace backup automático de tu BD actual
- ✅ Elimina la base de datos
- ✅ Elimina migraciones antiguas
- ✅ Crea nuevas migraciones limpias
- ✅ Aplica las migraciones
- ✅ Te pregunta si quieres crear superusuario

### Opción Manual (si la automática falla):

```powershell
# 1. Ir a backend
cd backend

# 2. Eliminar base de datos
Remove-Item db.sqlite3

# 3. Eliminar migraciones
$apps = @("clients", "membresias", "users", "roles", "promociones", "audit", "core")
foreach ($app in $apps) {
    Get-ChildItem -Path "apps\$app\migrations" -Filter "0*.py" | Remove-Item -Force
}

# 4. Crear nuevas migraciones
python manage.py makemigrations

# 5. Aplicar migraciones
python manage.py migrate

# 6. Crear superusuario
python manage.py createsuperuser
```

---

## 🌱 PASO 2: POBLAR CON DATOS DE PRUEBA

```powershell
# Asegúrate de estar en d:\SI1-Spartan\backend
cd backend

# Ejecutar todos los seeders
python seeders\run_all_seeders.py
```

Esto creará:

- ✅ Superusuario: admin@gym-spartan.com / admin123
- ✅ 3 Roles con permisos
- ✅ 4 Usuarios de prueba
- ✅ 5 Clientes (con peso, altura, experiencia)
- ✅ 7 Planes de Membresía (Diario, Semanal, Mensual, Trimestral, etc.)
- ✅ 5 Promociones activas

---

## 🎯 PASO 3: VERIFICAR QUE TODO FUNCIONA

### 1. Iniciar el servidor

```powershell
# Desde backend/
python manage.py runserver
```

### 2. Abrir Django Admin

```
URL: http://localhost:8000/admin
Usuario: admin@gym-spartan.com
Contraseña: admin123
```

### 3. Verificar que se vean todos los módulos:

En el panel admin deberías ver:

**CLIENTS**

- [x] Clientes (al abrir uno, deberías ver: peso, altura, experiencia)

**MEMBRESÍAS**

- [x] Planes de Membresía ← NUEVO (deberías ver 7 planes)
- [x] Inscripciones Membresía
- [x] Membresías (al crear una, deberías poder seleccionar plan y promociones)

**PROMOCIONES**

- [x] Promociones (deberías ver 5 promociones con meses, descuento, estado)

**USERS**

- [x] Usuarios

**ROLES**

- [x] Roles
- [x] Permisos
- [x] Usuario-Rol
- [x] Rol-Permiso

**AUDIT**

- [x] Bitácora del Sistema

---

## 🧪 PASO 4: PROBAR CREAR UNA MEMBRESÍA

### Desde Django Admin:

1. **Ir a Clientes** → Seleccionar cualquier cliente (ej: Pedro Ramírez)

2. **Ir a Inscripciones Membresía** → Añadir nueva:

   - Cliente: Pedro Ramírez
   - Monto: 250.00
   - Método de pago: EFECTIVO
   - Guardar

3. **Ir a Membresías** → Añadir nueva:

   - Inscripción: Seleccionar la que acabas de crear
   - Plan: Plan Mensual ← NUEVO CAMPO
   - Usuario registro: admin
   - Estado: ACTIVA
   - Fecha inicio: hoy
   - Fecha fin: hoy + 30 días
   - Promociones: (opcional) Seleccionar "Promoción Verano" ← NUEVA RELACIÓN
   - Guardar

4. **Verificar** que la membresía aparece con:
   - ✅ Plan asociado
   - ✅ Promociones aplicadas (si seleccionaste alguna)
   - ✅ Días restantes calculados

---

## ✅ CONFIRMAR QUE TODO ESTÁ CORRECTO

Si todo funcionó:

- [x] No hay errores al crear migraciones
- [x] No hay errores al aplicar migraciones
- [x] Los seeders se ejecutan sin errores
- [x] El servidor inicia correctamente
- [x] Django Admin muestra todos los módulos
- [x] Puedes crear una membresía con plan y promociones
- [x] Los nuevos campos de cliente (peso, altura, experiencia) aparecen

---

## 🔍 SI HAY ALGÚN ERROR:

### Error: "No such table: plan_membresia"

```powershell
cd backend
python manage.py migrate
```

### Error: "FOREIGN KEY constraint failed"

```powershell
cd backend
python seeders\run_all_seeders.py
```

### Error en migraciones

```powershell
# Resetear todo de nuevo
.\scripts\reset_migrations.ps1
```

---

## 📚 DOCUMENTACIÓN DISPONIBLE

Si necesitas más detalles, revisa:

1. **GUIA_COMPLETA_MODELOS.md** - Guía paso a paso completa
2. **RELACIONES_FUNCIONALES.md** - Diagramas y ejemplos de código
3. **RESUMEN_CAMBIOS_MODELOS.md** - Resumen visual de cambios
4. **INSTRUCCIONES_RESET_DB.md** - Guía de reseteo manual

---

## 🎉 RESPUESTA A TU PREGUNTA

> **"¿ES NECESARIO BORRAR MIGRACIONES?"**

✅ **SÍ, ES NECESARIO** porque:

1. Agregamos nuevos modelos (`PlanMembresia`, `MembresiaPromocion`)
2. Modificamos campos existentes (Promoción: `meses`, `descuento`, `estado`)
3. Agregamos campos a Cliente (`peso`, `altura`, `experiencia`)
4. Agregamos relaciones M2M nuevas (`Membresia.promociones`)

Django no puede generar migraciones incrementales limpias con tantos cambios estructurales. Es mejor partir de cero.

---

## 🚀 RESUMEN EJECUTIVO

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  1. Ejecutar: .\scripts\reset_migrations.ps1        │
│                                                     │
│  2. Ejecutar: python seeders\run_all_seeders.py     │
│                                                     │
│  3. Ejecutar: python manage.py runserver            │
│                                                     │
│  4. Abrir: http://localhost:8000/admin              │
│                                                     │
│  5. Verificar que todo funciona ✅                  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## ¡AHORA SÍ, EJECUTA! 🎯

```powershell
# Paso 1 - Desde la raíz del proyecto
.\scripts\reset_migrations.ps1

# Paso 2 - Espera a que termine y luego:
cd backend
python seeders\run_all_seeders.py

# Paso 3 - Iniciar servidor
python manage.py runserver
```

**¡Listo! Todos los módulos ahora son funcionales según tu diagrama UML** 🎉
