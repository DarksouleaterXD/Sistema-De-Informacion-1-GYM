# 🎯 ACTUALIZACIÓN: MODELOS FUNCIONALES SEGÚN UML

## 📌 RESUMEN EJECUTIVO

Se han actualizado **todos los modelos** del backend para que sean completamente **funcionales** según el diagrama UML proporcionado.

### ✅ Cambios Principales:

1. **Cliente** - Agregados: `peso`, `altura`, `experiencia`
2. **Membresías** - Creado `PlanMembresia` y relación M2M con `Promocion`
3. **Promociones** - Actualizado según PUML: `meses`, `descuento`, `estado`
4. **Relaciones** - Todas las relaciones funcionales (Cliente→Membresía, Usuario→Roles→Permisos)

---

## 🚀 INICIO RÁPIDO

### 1. Resetear Base de Datos

```powershell
# Opción A - Automático (Recomendado)
.\scripts\reset_migrations.ps1

# Opción B - Manual (ver GUIA_COMPLETA_MODELOS.md)
```

### 2. Poblar con Datos de Prueba

```powershell
cd backend
python seeders/run_all_seeders.py
```

### 3. Iniciar Servidor

```powershell
python manage.py runserver
```

### 4. Acceder al Admin

```
URL: http://localhost:8000/admin
Usuario: admin@gym-spartan.com
Contraseña: admin123
```

---

## 📚 DOCUMENTACIÓN COMPLETA

### Archivos principales:

| Archivo                           | Descripción                         |
| --------------------------------- | ----------------------------------- |
| **📄 RESUMEN_CAMBIOS_MODELOS.md** | Resumen visual de todos los cambios |
| **📄 GUIA_COMPLETA_MODELOS.md**   | Guía paso a paso completa           |
| **📄 RELACIONES_FUNCIONALES.md**  | Diagramas y ejemplos de uso         |
| **📄 INSTRUCCIONES_RESET_DB.md**  | Guía para resetear la BD            |

---

## ✅ CHECKLIST DE FUNCIONALIDADES

- [x] ✅ Cliente puede tener múltiples membresías
- [x] ✅ Membresía se asocia a un plan específico
- [x] ✅ Membresía puede tener múltiples promociones
- [x] ✅ Usuario tiene múltiples roles
- [x] ✅ Rol tiene múltiples permisos
- [x] ✅ Bitácora registra todas las acciones
- [x] ✅ Validaciones completas
- [x] ✅ Admin configurado
- [x] ✅ Seeders funcionales

---

## 🔧 MODELOS ACTUALIZADOS

### 1. Cliente

```python
# Nuevos campos:
peso: Decimal(5,2)
altura: Decimal(3,2)
experiencia: PRINCIPIANTE | INTERMEDIO | AVANZADO
```

### 2. Membresías

```python
# Nuevo modelo:
PlanMembresia: nombre, duracion, precio_base, descripcion

# Actualizado:
Membresia.plan: FK → PlanMembresia
Membresia.promociones: M2M → Promocion

# Nueva relación M2M:
MembresiaPromocion: membresia, promocion
```

### 3. Promoción

```python
# Actualizados según PUML:
meses: INT
descuento: Decimal(5,2)
estado: ACTIVA | INACTIVA | VENCIDA
```

---

## 📊 DATOS DE PRUEBA

El sistema incluye:

- ✅ 5 Clientes (con datos completos)
- ✅ 7 Planes de Membresía
- ✅ 5 Promociones activas
- ✅ 3 Roles con permisos
- ✅ 4 Usuarios de prueba

---

## ⚠️ IMPORTANTE: SOBRE LAS MIGRACIONES

**¿Es necesario borrar las migraciones?**

✅ **SÍ**, porque:

1. Los modelos cambiaron estructuralmente
2. Se agregaron nuevos campos y relaciones
3. Evitamos conflictos entre migraciones antiguas y nuevas

**Solución:**
Usar el script `.\scripts\reset_migrations.ps1` que:

- Hace backup automático
- Elimina BD y migraciones antiguas
- Crea nuevas migraciones limpias
- Opción para crear superusuario

---

## 🎓 EJEMPLOS DE USO

### Crear cliente con membresía

```python
# 1. Crear cliente
cliente = Client.objects.create(
    nombre="Juan", apellido="Pérez", ci="12345678",
    peso=75.5, altura=1.75, experiencia="INTERMEDIO"
)

# 2. Seleccionar plan
plan = PlanMembresia.objects.get(nombre="Plan Mensual")

# 3. Registrar pago
inscripcion = InscripcionMembresia.objects.create(
    cliente=cliente, monto=plan.precio_base, metodo_de_pago="EFECTIVO"
)

# 4. Crear membresía
membresia = Membresia.objects.create(
    inscripcion=inscripcion, plan=plan,
    usuario_registro=usuario, estado="ACTIVA",
    fecha_inicio=date.today(),
    fecha_fin=date.today() + timedelta(days=plan.duracion)
)

# 5. Aplicar promoción (opcional)
promocion = Promocion.objects.get(nombre="Promoción Verano")
MembresiaPromocion.objects.create(membresia=membresia, promocion=promocion)
```

---

## 🔍 SOLUCIÓN DE PROBLEMAS

| Problema             | Solución                         |
| -------------------- | -------------------------------- |
| Error de migraciones | `.\scripts\reset_migrations.ps1` |
| Campos no aparecen   | Reiniciar servidor               |
| Error de FK          | Ejecutar seeders en orden        |
| BD corrupta          | Resetear con script              |

---

## 📞 CONTACTO Y SOPORTE

Para más detalles, revisar la documentación completa:

- `GUIA_COMPLETA_MODELOS.md` - Guía paso a paso
- `RELACIONES_FUNCIONALES.md` - Ejemplos y diagramas
- `RESUMEN_CAMBIOS_MODELOS.md` - Resumen visual

---

## 🎉 RESULTADO

```
┌─────────────────────────────────────────────┐
│  ✅ TODOS LOS MÓDULOS FUNCIONALES           │
│                                             │
│  Cliente ──► Membresía ──► Plan             │
│                        └──► Promociones     │
│                                             │
│  Usuario ──► Roles ──► Permisos             │
│                                             │
│  Bitácora automática activa                 │
└─────────────────────────────────────────────┘
```

**¡Sistema listo para usar! 🚀**
