# 📊 RELACIONES FUNCIONALES DE LOS MÓDULOS

Este documento explica cómo los módulos están interconectados según el diagrama UML y cómo funcionan en conjunto.

## 🎯 Resumen de Módulos Actualizados

### 1. **CLIENTES** ✅

**Modelo:** `Client`
**Ubicación:** `apps/clients/models.py`

**Campos actualizados:**

- ✅ `nombre` (VARCHAR 50)
- ✅ `apellido` (VARCHAR 50)
- ✅ `ci` (VARCHAR 20, unique)
- ✅ `telefono` (VARCHAR 20)
- ✅ `email` (EmailField)
- ✅ **NUEVO:** `peso` (Decimal 5,2)
- ✅ **NUEVO:** `altura` (Decimal 3,2)
- ✅ **NUEVO:** `experiencia` (VARCHAR 20 - choices: PRINCIPIANTE, INTERMEDIO, AVANZADO)
- ✅ `fecha_registro` (DateField)

**Relaciones:**

- 1 Cliente → N Inscripciones de Membresía
- 1 Cliente → N Rutinas (futuro)
- 1 Cliente → N Inscripciones de Clase (futuro)
- 1 Cliente → N Ventas (futuro)

---

### 2. **MEMBRESÍAS** ✅

**Modelos:** `PlanMembresia`, `InscripcionMembresia`, `Membresia`, `MembresiaPromocion`
**Ubicación:** `apps/membresias/models.py`

#### 2.1 **PlanMembresia** (NUEVO ✨)

```python
- nombre: VARCHAR(50)
- duracion: INT (días)
- precio_base: DECIMAL(10,2)
- descripcion: TEXT
```

**Propósito:** Define los planes de membresía disponibles (ej: "Plan Mensual", "Plan Trimestral")

#### 2.2 **InscripcionMembresia**

```python
- cliente: FK → Client
- monto: DECIMAL(10,2)
- metodo_de_pago: VARCHAR(30)
```

**Propósito:** Registra el pago inicial del cliente

#### 2.3 **Membresia**

```python
- inscripcion: OneToOne → InscripcionMembresia
- plan: FK → PlanMembresia  ← NUEVO
- usuario_registro: FK → User
- estado: VARCHAR(20)
- fecha_inicio: DATE
- fecha_fin: DATE
- promociones: M2M → Promocion (through MembresiaPromocion)  ← NUEVO
```

**Propósito:** Representa la membresía activa de un cliente

#### 2.4 **MembresiaPromocion** (NUEVO ✨)

```python
- membresia: FK → Membresia
- promocion: FK → Promocion
```

**Propósito:** Tabla intermedia que permite aplicar múltiples promociones a una membresía

**Flujo completo:**

```
1. Cliente se registra → Se crea Client
2. Cliente paga → Se crea InscripcionMembresia
3. Se asigna Plan → Se crea Membresia con plan específico
4. Se aplican promociones → Se crean registros en MembresiaPromocion
5. Usuario del sistema registra todo el proceso
```

---

### 3. **PROMOCIONES** ✅

**Modelo:** `Promocion`
**Ubicación:** `apps/promociones/models.py`

**Campos actualizados según PUML:**

- ✅ `nombre` (VARCHAR 100)
- ✅ **ACTUALIZADO:** `meses` (INT - cantidad de meses de duración)
- ✅ **ACTUALIZADO:** `descuento` (DECIMAL 5,2 - porcentaje)
- ✅ `fecha_inicio` (DATE)
- ✅ `fecha_fin` (DATE)
- ✅ **ACTUALIZADO:** `estado` (VARCHAR 20 - choices: ACTIVA, INACTIVA, VENCIDA)

**Relaciones:**

- N Promociones ↔ N Membresías (through MembresiaPromocion)

**Ejemplo de uso:**

```python
# Promoción "Verano 2025"
promocion = Promocion(
    nombre="Promoción Verano",
    meses=3,  # Dura 3 meses
    descuento=20.00,  # 20% de descuento
    fecha_inicio="2025-01-01",
    fecha_fin="2025-03-31",
    estado="ACTIVA"
)
```

---

### 4. **USUARIOS** ✅

**Modelo:** `User`
**Ubicación:** `apps/users/models.py`

**Campos:**

- ✅ Hereda de `AbstractUser` (username, password, email, etc.)
- ✅ `roles`: M2M → Role (through UserRole)

**Relaciones:**

- N Usuarios ↔ N Roles (through UserRole)
- 1 Usuario → N Membresías Registradas
- 1 Usuario → N Actividades en Historial (bitácora)
- 1 Usuario → N Movimientos de Inventario (futuro)

---

### 5. **ROLES Y PERMISOS** ✅

**Modelos:** `Role`, `Permiso`, `UserRole`, `RolPermiso`
**Ubicación:** `apps/roles/models.py`

#### 5.1 **Role**

```python
- nombre: VARCHAR(50)
- descripcion: TEXT
- permisos: M2M → Permiso (through RolPermiso)
```

#### 5.2 **Permiso**

```python
- nombre: VARCHAR(50)
- descripcion: TEXT
```

#### 5.3 **UserRole** (Tabla intermedia)

```python
- usuario: FK → User
- rol: FK → Role
```

#### 5.4 **RolPermiso** (Tabla intermedia)

```python
- rol: FK → Role
- permiso: FK → Permiso
```

**Flujo de permisos:**

```
1. Se crean Permisos básicos (ej: "crear_cliente", "editar_membresia")
2. Se crean Roles (ej: "Administrador", "Recepcionista")
3. Se asignan Permisos a Roles → RolPermiso
4. Se asignan Roles a Usuarios → UserRole
5. Usuario hereda permisos de sus roles
```

---

### 6. **BITÁCORA (AUDITORÍA)** ✅

**Modelo:** `HistorialActividad`
**Ubicación:** `apps/audit/models.py`

**Campos:**

- ✅ `user`: FK → User
- ✅ `accion`: VARCHAR(100)
- ✅ `descripcion`: TEXT
- ✅ `ip`: VARCHAR(45)
- ✅ `fecha`: DATE
- ✅ `hora`: TIME
- ✅ `nivel`: choices (INFO, WARNING, ERROR, CRITICAL)

**Propósito:** Registra automáticamente todas las acciones del sistema

---

## 🔗 DIAGRAMA DE RELACIONES FUNCIONALES

```
┌─────────────────┐
│     USUARIO     │
└────────┬────────┘
         │
         ├──── roles (M2M) ────► ROL ───── permisos (M2M) ────► PERMISO
         │
         └──── registra ────► MEMBRESÍA
                                   │
                                   ├─── inscripcion (1:1) ──► INSCRIPCIÓN ──► cliente ──► CLIENTE
                                   │                                                        │
                                   ├─── plan ──────────────► PLAN MEMBRESÍA                │
                                   │                                                        │
                                   └─── promociones (M2M) ─► PROMOCIÓN                     │
                                                                                            │
HISTORIAL_ACTIVIDAD ◄──── registra ──── todas las acciones ◄──────────────────────────────┘
```

---

## 💡 EJEMPLOS DE USO PRÁCTICO

### Ejemplo 1: Crear un cliente y asignarle una membresía

```python
# 1. Crear cliente
cliente = Client.objects.create(
    nombre="Juan",
    apellido="Pérez",
    ci="12345678",
    telefono="70123456",
    email="juan@example.com",
    peso=75.5,
    altura=1.75,
    experiencia="INTERMEDIO"
)

# 2. Crear plan de membresía (si no existe)
plan = PlanMembresia.objects.create(
    nombre="Plan Mensual",
    duracion=30,
    precio_base=200.00,
    descripcion="Acceso completo por 30 días"
)

# 3. Registrar inscripción (pago)
inscripcion = InscripcionMembresia.objects.create(
    cliente=cliente,
    monto=200.00,
    metodo_de_pago="EFECTIVO"
)

# 4. Crear membresía
membresia = Membresia.objects.create(
    inscripcion=inscripcion,
    plan=plan,
    usuario_registro=request.user,
    estado="ACTIVA",
    fecha_inicio=date.today(),
    fecha_fin=date.today() + timedelta(days=30)
)

# 5. Aplicar promoción (opcional)
promocion = Promocion.objects.get(nombre="Promoción Verano")
MembresiaPromocion.objects.create(
    membresia=membresia,
    promocion=promocion
)
```

### Ejemplo 2: Asignar rol a usuario

```python
# 1. Crear permisos
permiso_clientes = Permiso.objects.create(
    nombre="gestionar_clientes",
    descripcion="Puede crear, editar y eliminar clientes"
)

permiso_membresias = Permiso.objects.create(
    nombre="gestionar_membresias",
    descripcion="Puede gestionar membresías"
)

# 2. Crear rol
rol_recepcionista = Role.objects.create(
    nombre="Recepcionista",
    descripcion="Personal de recepción"
)

# 3. Asignar permisos al rol
RolPermiso.objects.create(rol=rol_recepcionista, permiso=permiso_clientes)
RolPermiso.objects.create(rol=rol_recepcionista, permiso=permiso_membresias)

# 4. Asignar rol a usuario
UserRole.objects.create(
    usuario=usuario,
    rol=rol_recepcionista
)

# 5. Verificar permisos
permisos_usuario = usuario.roles.all().values_list('permisos__nombre', flat=True)
```

---

## ✅ CHECKLIST DE FUNCIONALIDADES

- [x] Cliente puede tener múltiples inscripciones
- [x] Cada inscripción genera una membresía
- [x] Membresía se asocia a un plan específico
- [x] Membresía puede tener múltiples promociones
- [x] Usuario registra quien creó la membresía
- [x] Usuario puede tener múltiples roles
- [x] Rol puede tener múltiples permisos
- [x] Todas las acciones se registran en bitácora
- [x] Cliente tiene información física (peso, altura, experiencia)
- [x] Promociones tienen duración en meses y porcentaje de descuento

---

## 🚀 PRÓXIMOS PASOS

1. **Resetear la base de datos** usando el script `reset_migrations.ps1`
2. **Crear datos de prueba** con los seeders actualizados
3. **Probar las relaciones** desde Django Admin
4. **Implementar módulos faltantes** (Clases, Rutinas, Inventario, etc.)

---

## 📝 NOTAS IMPORTANTES

- ✅ Todos los modelos tienen auditoría automática (TimeStampedModel)
- ✅ Las relaciones Many-to-Many usan tablas intermedias explícitas
- ✅ Se mantiene integridad referencial con ForeignKey y protecciones adecuadas
- ✅ Los serializers están actualizados con los nuevos campos
- ✅ Los admins de Django están configurados para gestión visual
