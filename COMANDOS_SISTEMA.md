# 🛠️ Comandos Útiles del Sistema

Este documento lista todos los comandos personalizados disponibles en el sistema Gym Spartan.

## 📋 Tabla de Contenidos
- [Seeders](#seeders)
- [Validación](#validación)
- [Bitácora](#bitácora)
- [Migraciones](#migraciones)
- [Usuarios](#usuarios)

---

## 🌱 Seeders

### Ejecutar todos los seeders
```bash
docker-compose exec backend python manage.py seed
```
**Descripción**: Ejecuta todos los seeders en el orden correcto (Superusuario, Permisos, Roles, Usuarios, Instructores, Clientes, Planes, Promociones, Disciplinas, Salones, Clases).

**Resultado esperado**:
- ✅ 11 seeders exitosos
- 67 permisos creados
- 3 roles predeterminados (Administrador, Administrativo, Instructor)
- 5+ instructores
- 5+ clientes
- 7+ planes de membresía
- 5+ promociones
- 10+ disciplinas
- 5+ salones
- 5+ clases de prueba

---

## ✅ Validación

### Validar integridad de seeders
```bash
docker-compose exec backend python manage.py validate_seeders
```
**Descripción**: Verifica que todos los datos creados por los seeders estén correctos y completos.

**Qué valida**:
- ✅ Superusuario existe y está activo
- ✅ 67 permisos creados
- ✅ 3 roles con sus permisos correctos
- ✅ Usuarios de prueba creados
- ✅ Roles asignados correctamente
- ✅ Instructores con perfiles completos
- ✅ Clientes, planes, promociones, disciplinas, salones y clases

**Cuándo usar**: Después de ejecutar seeders o si sospechas que falta algún dato.

---

## 📋 Bitácora (Auditoría)

### Ver últimas entradas de bitácora
```bash
# Ver últimas 10 entradas
docker-compose exec backend python manage.py bitacora

# Ver últimas 20 entradas
docker-compose exec backend python manage.py bitacora --limit 20

# Ver solo logins
docker-compose exec backend python manage.py bitacora --tipo login

# Ver solo errores
docker-compose exec backend python manage.py bitacora --tipo error

# Ver creación de usuarios
docker-compose exec backend python manage.py bitacora --tipo create_user
```

**Descripción**: Muestra las últimas entradas del historial de actividades (bitácora) con formato amigable.

**Tipos de acción disponibles**:
- `login` - Inicio de sesión
- `logout` - Cierre de sesión
- `create` - Crear registro
- `update` - Actualizar registro
- `delete` - Eliminar registro
- `create_user` - Crear usuario
- `update_user` - Actualizar usuario
- `delete_user` - Eliminar usuario
- `create_role` - Crear rol
- `assign_role` - Asignar rol
- `create_client` - Crear cliente
- `error` - Error del sistema

**Salida incluye**:
- 🔐 Usuario que realizó la acción (o "Sistema" si no aplica)
- 📅 Fecha y hora
- 📝 Tipo y descripción de la acción
- 🌐 Dirección IP
- 📊 Datos adicionales en JSON

---

## 🗄️ Migraciones

### Crear migraciones
```bash
docker-compose exec backend python manage.py makemigrations
```

### Aplicar migraciones
```bash
docker-compose exec backend python manage.py migrate
```

### Ver estado de migraciones
```bash
docker-compose exec backend python manage.py showmigrations
```

### Resetear migraciones (⚠️ Peligroso - borra la BD)
```bash
# Windows PowerShell
.\scripts\reset_migrations_docker.ps1

# Linux/Mac
./scripts/reset_migrations_docker.sh
```

---

## 👤 Usuarios

### Crear superusuario manualmente
```bash
docker-compose exec backend python manage.py createsuperuser
```

### Acceder al shell de Django
```bash
docker-compose exec backend python manage.py shell
```

### Verificar usuarios en la base de datos
```bash
docker-compose exec backend python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(f'Usuarios: {User.objects.count()}'); [print(f'  - {u.email} ({u.get_full_name()})') for u in User.objects.all()[:10]]"
```

---

## 🔍 Base de Datos

### Acceder a psql (PostgreSQL)
```bash
docker-compose exec db psql -U spartan_user -d spartan_db
```

### Ver todas las tablas
```bash
docker-compose exec db psql -U spartan_user -d spartan_db -c "\dt"
```

### Contar registros en una tabla
```bash
# Ejemplo: contar instructores
docker-compose exec backend python manage.py shell -c "from apps.instructores.models import Instructor; print(f'Instructores: {Instructor.objects.count()}')"
```

---

## 🐳 Docker

### Ver logs del backend
```bash
docker-compose logs backend --tail=50
```

### Ver logs del frontend
```bash
docker-compose logs frontend --tail=50
```

### Reiniciar un servicio
```bash
# Reiniciar backend
docker-compose restart backend

# Reiniciar frontend
docker-compose restart frontend
```

### Reconstruir contenedores
```bash
docker-compose down
docker-compose up -d --build
```

### Limpiar todo y empezar de cero
```bash
docker-compose down -v  # ⚠️ Borra volúmenes (base de datos)
docker-compose up -d --build
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py seed
```

---

## 📊 Datos de Prueba

### Usuarios predeterminados
| Email | Contraseña | Rol |
|-------|-----------|-----|
| `admin@gym-spartan.com` | `admin123` | Administrador (Superusuario) |
| `administrativo@gym-spartan.com` | `admin123` | Administrativo |
| `instructor@gym-spartan.com` | `instructor123` | Instructor |

### Instructores de prueba
1. **Juan Pérez** - `jperez@gym-spartan.com` - CrossFit, Functional Training, HIIT
2. **María García** - `mgarcia@gym-spartan.com` - Yoga, Pilates, Stretching
3. **Carlos López** - `clopez@gym-spartan.com` - Spinning, Cardio, HIIT
4. **Ana Martínez** - `amartinez@gym-spartan.com` - Zumba, Dance Fitness, Aerobics
5. **Roberto Sánchez** - `rsanchez@gym-spartan.com` - Musculación, Powerlifting

---

## 🚀 Comandos Rápidos

### Desarrollo diario
```bash
# 1. Iniciar servicios
docker-compose up -d

# 2. Ver logs en tiempo real
docker-compose logs -f backend frontend

# 3. Ejecutar seeders si es necesario
docker-compose exec backend python manage.py seed

# 4. Validar que todo esté correcto
docker-compose exec backend python manage.py validate_seeders
```

### Solución de problemas
```bash
# Si el backend no responde
docker-compose restart backend
docker-compose logs backend --tail=50

# Si el frontend no carga
docker-compose restart frontend
docker-compose logs frontend --tail=50

# Si hay problemas con la base de datos
docker-compose restart db
docker-compose logs db --tail=50

# Ver bitácora de errores
docker-compose exec backend python manage.py bitacora --tipo error --limit 20
```

---

## 📝 Notas Importantes

1. **Seeders son idempotentes**: Puedes ejecutar `python manage.py seed` múltiples veces sin problemas. Creará solo lo que falta y actualizará lo existente.

2. **Bitácora automática**: Todas las acciones importantes se registran automáticamente en la bitácora con el usuario que las realizó (o "Sistema" si no aplica).

3. **Permisos granulares**: El sistema usa 67 permisos específicos que se verifican en cada acción. Los comandos de validación te ayudan a asegurarte de que estén correctos.

4. **Docker volumes**: Los datos de PostgreSQL se guardan en un volumen Docker. Si haces `docker-compose down -v`, **perderás todos los datos**.

5. **Orden de seeders**: Los seeders se ejecutan en un orden específico para respetar las dependencias. No cambies el orden sin revisar las dependencias.

---

## 🆘 Soporte

Si encuentras algún problema:

1. **Verifica los logs**: `docker-compose logs backend --tail=100`
2. **Valida los seeders**: `docker-compose exec backend python manage.py validate_seeders`
3. **Revisa la bitácora**: `docker-compose exec backend python manage.py bitacora --tipo error`
4. **Reinicia los servicios**: `docker-compose restart backend frontend`

---

**Última actualización**: Noviembre 7, 2025
**Versión del sistema**: 1.0.0
**Módulos activos**: Usuarios, Roles, Clientes, Instructores, Membresías, Promociones, Disciplinas, Clases, Bitácora
