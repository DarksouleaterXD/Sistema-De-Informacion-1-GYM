# 🔧 Reporte de Corrección de Seeders

**Fecha:** 6 de Noviembre, 2025  
**Rama:** feature/Instructor  
**Estado:** ✅ RESUELTO

## 📋 Resumen Ejecutivo

Después de pullear los cambios de un colaborador, los seeders del sistema fallaban. Se realizó una inspección completa y se identificaron 3 errores críticos en los imports y nombres de funciones.

---

## 🐛 Problemas Encontrados

### 1. Error en `setup_rbac.py` - Imports Incorrectos

**Archivo:** `backend/seeders/setup_rbac.py`

**Líneas afectadas:** 21-22

**Problema:**

```python
# ❌ INCORRECTO
from permissions_seeder import PermissionSeeder
from roles_default_seeder import create_default_roles
```

**Error generado:**

```
ModuleNotFoundError: No module named 'permissions_seeder'
```

**Causa:** Los imports no incluían el prefijo `seeders.` necesario para la estructura del proyecto.

**Solución aplicada:**

```python
# ✅ CORRECTO
from seeders.permissions_seeder import PermissionSeeder
from seeders.roles_default_seeder import create_default_roles
```

---

### 2. Error en `init_system.py` - Función Inexistente

**Archivo:** `backend/seeders/init_system.py`

**Líneas afectadas:** 95, 97

**Problema:**

```python
# ❌ INCORRECTO
from seeders.setup_rbac import setup_complete_rbac
setup_complete_rbac()
```

**Error generado:**

```
ImportError: cannot import name 'setup_complete_rbac' from 'seeders.setup_rbac'
```

**Causa:** La función en `setup_rbac.py` se llama `setup_rbac()`, no `setup_complete_rbac()`.

**Solución aplicada:**

```python
# ✅ CORRECTO
from seeders.setup_rbac import setup_rbac
setup_rbac()
```

---

### 3. Error en `users_seeder.py` - Roles Inexistentes

**Archivo:** `backend/seeders/users_seeder.py`

**Líneas afectadas:** 22-24

**Problema:**

```python
# ❌ INCORRECTO - Buscaba roles que no existen
rol_gerente = Role.objects.get(nombre='Gerente')
rol_recepcionista = Role.objects.get(nombre='Recepcionista')
rol_entrenador = Role.objects.get(nombre='Entrenador')
```

**Error generado:**

```
Role matching query does not exist.
```

**Causa:** Los roles creados en `roles_default_seeder.py` son diferentes:

- ✅ Administrador
- ✅ Administrativo
- ✅ Instructor

Pero el seeder buscaba:

- ❌ Gerente
- ❌ Recepcionista
- ❌ Entrenador

**Solución aplicada:**

```python
# ✅ CORRECTO
rol_administrativo = Role.objects.get(nombre='Administrativo')
rol_instructor = Role.objects.get(nombre='Instructor')
```

---

### 4. Error en `users_seeder.py` - Campos del Modelo User

**Problema adicional:**

```python
# ❌ INCORRECTO - El modelo User no tiene estos campos
'nombre': 'María',
'apellido': 'González',
```

**Causa:** El modelo `User` hereda de `AbstractUser` que usa `first_name` y `last_name`, no `nombre` y `apellido`.

**Solución aplicada:**

```python
# ✅ CORRECTO
'first_name': 'María',
'last_name': 'González',
```

---

### 5. Error en `users_seeder.py` - Asignación de Roles

**Problema:**

```python
# ❌ INCORRECTO - Método no funciona correctamente
user.roles.set(roles)
```

**Solución aplicada:**

```python
# ✅ CORRECTO - Usar el modelo intermedio UserRole
from apps.roles.models import UserRole
for role in roles:
    UserRole.objects.create(usuario=user, rol=role)
```

---

## ✅ Resultado Final

### Antes de las correcciones:

```
❌ Configurar RBAC: ERROR
❌ Asignar Rol Admin: ERROR
⚠️  Usuarios de prueba: 0 creados
```

### Después de las correcciones:

```
✅ Configurar RBAC: OK
✅ Asignar Rol Admin: OK
✅ Usuarios de prueba: 3 creados
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 ¡SISTEMA INICIALIZADO COMPLETAMENTE!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 📊 Estado del Sistema

### ✅ Datos Creados Correctamente:

- **Usuarios:** 4 (1 admin + 3 usuarios de prueba)

  - `admin@gym-spartan.com` → Rol: Administrador
  - `administrativo@gym-spartan.com` → Rol: Administrativo
  - `instructor@gym-spartan.com` → Rol: Instructor
  - `instructor2@gym-spartan.com` → Rol: Instructor

- **Roles:** 3

  - Administrador (62 permisos)
  - Administrativo (25 permisos)
  - Instructor (5 permisos)

- **Permisos:** 62 permisos personalizados

- **Clientes:** 5 clientes de prueba

- **Planes de Membresía:** 7 planes

- **Promociones:** 5 promociones

---

## 🔑 Credenciales de Prueba

### Usuario Administrador:

```
Email: admin@gym-spartan.com
Username: admin
Password: admin123
Rol: Administrador (acceso completo)
```

### Usuario Administrativo:

```
Email: administrativo@gym-spartan.com
Username: administrativo1
Password: admin123
Rol: Administrativo (gestión diaria)
```

### Usuarios Instructores:

```
Email: instructor@gym-spartan.com
Username: instructor1
Password: instructor123
Rol: Instructor (solo lectura para clases)

Email: instructor2@gym-spartan.com
Username: instructor2
Password: instructor123
Rol: Instructor (solo lectura para clases)
```

---

## 🚀 Comandos para Ejecutar Seeders

### Dentro del contenedor Docker:

```bash
docker exec -it spartan_backend python -c "import sys; sys.path.append('/app'); from seeders.init_system import main; main()"
```

### Localmente (con entorno virtual activado):

```bash
cd backend
python -c "import sys; sys.path.append('.'); from seeders.init_system import main; main()"
```

---

## 📝 Archivos Modificados

1. ✅ `backend/seeders/setup_rbac.py` - Corrección de imports
2. ✅ `backend/seeders/init_system.py` - Corrección del nombre de función
3. ✅ `backend/seeders/users_seeder.py` - Corrección completa:
   - Nombres de roles actualizados
   - Campos del modelo User corregidos
   - Asignación de roles mediante UserRole

---

## 🧪 Verificación del Sistema

Todos los pasos de inicialización ahora pasan correctamente:

- [x] Verificar Base de Datos
- [x] Ejecutar Migraciones
- [x] Crear Superusuario
- [x] Configurar RBAC (Permisos y Roles)
- [x] Asignar Rol Administrador
- [x] Cargar Datos de Prueba
- [x] Verificar Sistema

**Exitosos: 7/7** ✅

---

## 💡 Recomendaciones

1. **Testing:** Ejecutar los seeders después de cada pull para verificar integridad
2. **Documentación:** Mantener actualizada la lista de roles en el README
3. **Validación:** Agregar tests unitarios para los seeders
4. **CI/CD:** Considerar agregar los seeders al pipeline de CI/CD

---

## 🔗 Referencias

- Documentación RBAC: `RBAC_CONFIRMACION_COMPLETA.md`
- Roles implementados: `ROLES_USUARIOS_IMPLEMENTACION.md`
- Configuración Docker: `docker-compose.yml`

---

**Autor de las correcciones:** GitHub Copilot  
**Revisado por:** [Tu nombre]  
**Estado:** ✅ COMPLETADO Y VERIFICADO
