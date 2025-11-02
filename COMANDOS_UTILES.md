# 🛠️ Scripts Útiles para Desarrollo

Este documento contiene comandos frecuentes para trabajar con el proyecto.

---

## 🚀 Inicialización del Proyecto

### Setup Completo (Primera vez)

```bash
# Clonar y configurar
git clone --single-branch --branch feature/IDK https://github.com/DarksouleaterXD/Sistema-De-Informacion-1-GYM.git
cd Sistema-De-Informacion-1-GYM
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# Levantar servicios
docker compose up -d --build

# Configurar base de datos
docker compose exec backend python manage.py migrate
docker compose exec backend python seeders/init_system.py

# Verificar que todo funcione
docker compose exec backend python seeders/verify_system.py
```

---

## 📦 Gestión de Servicios Docker

### Iniciar todos los servicios

```bash
docker compose up -d
```

### Iniciar con rebuild (si cambiaste Dockerfile o requirements)

```bash
docker compose up -d --build
```

### Ver estado de servicios

```bash
docker compose ps
```

### Ver logs en tiempo real

```bash
# Todos los servicios
docker compose logs -f

# Solo backend
docker compose logs -f backend

# Solo frontend
docker compose logs -f frontend

# Solo base de datos
docker compose logs -f db
```

### Detener servicios

```bash
docker compose down
```

### Detener y eliminar volúmenes (⚠️ BORRA LA BD)

```bash
docker compose down -v
```

### Reiniciar un servicio específico

```bash
docker compose restart backend
docker compose restart frontend
docker compose restart db
```

---

## 🗄️ Base de Datos

### Crear migraciones

```bash
docker compose exec backend python manage.py makemigrations
```

### Aplicar migraciones

```bash
docker compose exec backend python manage.py migrate
```

### Ver migraciones aplicadas

```bash
docker compose exec backend python manage.py showmigrations
```

### Revertir una migración

```bash
docker compose exec backend python manage.py migrate app_name migration_name
# Ejemplo: docker compose exec backend python manage.py migrate roles 0002
```

### Acceder a la shell de Django

```bash
docker compose exec backend python manage.py shell
```

### Acceder a psql (PostgreSQL)

```bash
docker compose exec db psql -U spartan_user -d spartan_db
```

---

## 🌱 Seeders (Datos de Prueba)

### Ejecutar inicialización completa (RECOMENDADO)

```bash
docker compose exec backend python seeders/init_system.py
```

Este script hace TODO:

- ✅ Ejecuta migraciones
- ✅ Crea superusuario
- ✅ Crea 51 permisos
- ✅ Crea 6 roles con permisos asignados
- ✅ Asigna rol Administrador al admin
- ✅ Crea usuarios de prueba
- ✅ Crea clientes de ejemplo
- ✅ Crea planes de membresía
- ✅ Crea promociones

### Ejecutar solo seeders de datos

```bash
docker compose exec backend python manage.py seed
```

### Ejecutar seeders individuales

```bash
# Solo permisos
docker compose exec backend python seeders/permissions_seeder.py

# Solo roles
docker compose exec backend python seeders/roles_default_seeder.py

# Solo usuarios
docker compose exec backend python seeders/users_seeder.py

# Solo clientes
docker compose exec backend python seeders/clients_seeder.py
```

---

## ✅ Verificación del Sistema

### Verificar que todo funcione correctamente

```bash
docker compose exec backend python seeders/verify_system.py
```

### Verificar RBAC (Roles y Permisos)

```bash
docker compose exec backend python seeders/verify_rbac.py
```

### Ver información del usuario admin

```bash
docker compose exec backend python seeders/test_api_me.py
```

---

## 👤 Gestión de Usuarios

### Crear un superusuario

```bash
docker compose exec backend python manage.py createsuperuser
```

### Cambiar contraseña de un usuario

```bash
docker compose exec backend python manage.py shell
>>> from apps.users.models import User
>>> user = User.objects.get(username='admin')
>>> user.set_password('nueva_password')
>>> user.save()
>>> exit()
```

### Listar todos los usuarios

```bash
docker compose exec backend python manage.py shell
>>> from apps.users.models import User
>>> for user in User.objects.all():
...     print(f"{user.username} - {user.email} - Superuser: {user.is_superuser}")
>>> exit()
```

---

## 🧪 Testing

### Ejecutar tests del backend

```bash
docker compose exec backend python manage.py test
```

### Ejecutar tests de una app específica

```bash
docker compose exec backend python manage.py test apps.clients
docker compose exec backend python manage.py test apps.roles
```

### Ejecutar tests del frontend

```bash
docker compose exec frontend npm test
```

---

## 🔄 Reset Completo del Proyecto

### Opción 1: Reset con datos de prueba

```bash
# Detener y eliminar todo
docker compose down -v

# Volver a levantar
docker compose up -d --build

# Esperar 30 segundos a que PostgreSQL inicie...

# Configurar base de datos
docker compose exec backend python manage.py migrate

# Cargar todos los datos
docker compose exec backend python seeders/init_system.py

# Verificar
docker compose exec backend python seeders/verify_system.py
```

### Opción 2: Reset sin datos (BD vacía)

```bash
docker compose down -v
docker compose up -d --build
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
```

---

## 📝 Django Admin

### Acceder al panel de administración

```
URL: http://localhost:8000/admin/
Usuario: admin
Password: admin123
```

### Registrar un modelo en el admin

Edita `apps/tu_app/admin.py`:

```python
from django.contrib import admin
from .models import TuModelo

@admin.register(TuModelo)
class TuModeloAdmin(admin.ModelAdmin):
    list_display = ['campo1', 'campo2', 'created_at']
    list_filter = ['campo1', 'created_at']
    search_fields = ['campo1', 'campo2']
```

---

## 🌐 Frontend (Next.js)

### Instalar dependencias nuevas

```bash
docker compose exec frontend npm install nombre-paquete
```

### Limpiar caché de Next.js

```bash
docker compose exec frontend rm -rf .next
docker compose restart frontend
```

### Ver errores en tiempo real

```bash
docker compose logs -f frontend
```

---

## 🐛 Debugging

### Ver variables de entorno del backend

```bash
docker compose exec backend env | grep -E '(DATABASE|SECRET|DEBUG)'
```

### Ver variables de entorno del frontend

```bash
docker compose exec frontend env | grep NEXT_PUBLIC
```

### Inspeccionar contenedor

```bash
# Abrir bash en el contenedor
docker compose exec backend bash
docker compose exec frontend sh

# Ver archivos
docker compose exec backend ls -la
docker compose exec backend cat config/settings.py
```

### Ver uso de recursos

```bash
docker stats
```

---

## 🔐 Seguridad

### Generar nueva SECRET_KEY para Django

```bash
docker compose exec backend python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copia el resultado y actualiza `backend/.env`:

```bash
SECRET_KEY=tu-nueva-clave-generada
```

---

## 📚 Documentación API

### Ver documentación Swagger

```
http://localhost:8000/api/docs/
```

### Ver documentación ReDoc

```
http://localhost:8000/api/redoc/
```

### Descargar schema OpenAPI

```bash
curl http://localhost:8000/api/schema/ > api-schema.yaml
```

---

## 🚨 Solución de Problemas Comunes

### Puerto ya en uso

```bash
# Ver qué proceso usa el puerto 3000
netstat -ano | findstr :3000

# Matar el proceso (Windows)
taskkill /PID <numero-pid> /F

# En Linux/Mac
lsof -ti:3000 | xargs kill -9
```

### Backend no conecta a la BD

```bash
# Verificar que PostgreSQL esté levantado
docker compose ps db

# Ver logs de PostgreSQL
docker compose logs db

# Reiniciar base de datos
docker compose restart db
```

### "ModuleNotFoundError" en backend

```bash
# Reinstalar dependencias
docker compose exec backend pip install -r requirements.txt
docker compose restart backend
```

### Frontend muestra página en blanco

```bash
# Limpiar y reiniciar
docker compose exec frontend rm -rf .next node_modules
docker compose exec frontend npm install
docker compose restart frontend
```

### Permisos de archivos (Linux/Mac)

```bash
# Dar permisos a tu usuario
sudo chown -R $USER:$USER .
```

---

## 🎯 Workflow de Desarrollo

### 1. Crear una rama nueva

```bash
git checkout -b feature/nombre-funcionalidad
```

### 2. Hacer cambios y verificar

```bash
# Backend
docker compose logs -f backend

# Frontend
docker compose logs -f frontend
```

### 3. Commit y push

```bash
git add .
git commit -m "feat: descripción del cambio"
git push origin feature/nombre-funcionalidad
```

### 4. Antes de hacer merge

```bash
# Verificar que todo funcione
docker compose exec backend python manage.py test
docker compose exec backend python seeders/verify_system.py
```

---

## 📊 Monitoreo

### Ver estado de la base de datos

```bash
docker compose exec db psql -U spartan_user -d spartan_db -c "\dt"
```

### Ver tamaño de la base de datos

```bash
docker compose exec db psql -U spartan_user -d spartan_db -c "\l+"
```

### Ver conexiones activas

```bash
docker compose exec db psql -U spartan_user -d spartan_db -c "SELECT * FROM pg_stat_activity;"
```

---

## 🔗 URLs Importantes

| Servicio     | URL                             | Credenciales                  |
| ------------ | ------------------------------- | ----------------------------- |
| Frontend     | http://localhost:3000           | admin / admin123              |
| Backend API  | http://localhost:8000/api/      | -                             |
| Django Admin | http://localhost:8000/admin/    | admin / admin123              |
| Swagger Docs | http://localhost:8000/api/docs/ | -                             |
| pgAdmin      | http://localhost:5050           | admin@gym-spartan.com / admin |
| MailHog      | http://localhost:8025           | -                             |

---

**💡 Tip:** Guarda este archivo en tus favoritos para acceso rápido a los comandos más usados.

**Última actualización:** Noviembre 2024
