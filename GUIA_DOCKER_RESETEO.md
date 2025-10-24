# 🐳 GUÍA DE RESETEO CON DOCKER

## 🚀 INICIO RÁPIDO

### Ejecutar el script automatizado:

```powershell
.\scripts\reset_migrations_docker.ps1
```

---

## 📋 PASOS DETALLADOS (MANUAL)

### 1. Detener los contenedores

```powershell
docker-compose down
```

### 2. Eliminar el volumen de la base de datos

```powershell
docker volume rm si1-spartan_postgres_data -f
```

### 3. Eliminar archivos de migraciones

```powershell
$apps = @("clients", "membresias", "users", "roles", "promociones", "audit", "core")
foreach ($app in $apps) {
    Get-ChildItem -Path "backend\apps\$app\migrations" -Filter "0*.py" | Remove-Item -Force
}
```

### 4. Iniciar los contenedores

```powershell
docker-compose up -d
```

### 5. Esperar a que PostgreSQL esté listo

```powershell
# Esperar ~10 segundos
Start-Sleep -Seconds 10

# O verificar logs
docker-compose logs db
```

### 6. Crear migraciones

```powershell
docker-compose exec backend python manage.py makemigrations
```

### 7. Aplicar migraciones

```powershell
docker-compose exec backend python manage.py migrate
```

### 8. Crear superusuario

```powershell
docker-compose exec backend python manage.py createsuperuser
```

**O usar valores por defecto:**

- Email: admin@gym-spartan.com
- Username: admin
- Password: admin123

### 9. Ejecutar seeders

```powershell
docker-compose exec backend python seeders/run_all_seeders.py
```

---

## 🔧 COMANDOS ÚTILES DE DOCKER

### Ver contenedores corriendo:

```powershell
docker-compose ps
```

### Ver logs del backend:

```powershell
docker-compose logs -f backend
```

### Ver logs de la base de datos:

```powershell
docker-compose logs -f db
```

### Entrar al contenedor del backend:

```powershell
docker-compose exec backend bash
```

### Entrar a la base de datos PostgreSQL:

```powershell
docker-compose exec db psql -U spartan_user -d spartan_db
```

### Reiniciar un servicio específico:

```powershell
docker-compose restart backend
```

### Reconstruir contenedores:

```powershell
docker-compose up -d --build
```

---

## 🌐 SERVICIOS DISPONIBLES

Después de ejecutar el reseteo, los servicios estarán disponibles en:

| Servicio         | URL                         | Descripción                  |
| ---------------- | --------------------------- | ---------------------------- |
| **Backend API**  | http://localhost:8000       | API REST de Django           |
| **Django Admin** | http://localhost:8000/admin | Panel de administración      |
| **Frontend**     | http://localhost:3000       | Aplicación Next.js           |
| **PgAdmin**      | http://localhost:5050       | Administrador de PostgreSQL  |
| **MailHog**      | http://localhost:8025       | Servidor de pruebas de email |
| **PostgreSQL**   | localhost:5432              | Base de datos                |

### Credenciales por defecto:

**Django Admin:**

- Email: admin@gym-spartan.com
- Password: admin123

**PgAdmin:**

- Email: admin@gym-spartan.com
- Password: admin

**PostgreSQL:**

- Database: spartan_db
- User: spartan_user
- Password: spartan_pass

---

## 🧪 VERIFICAR QUE TODO FUNCIONA

### 1. Verificar contenedores:

```powershell
docker-compose ps
```

Deberías ver todos los servicios "Up":

- spartan_db
- spartan_backend
- spartan_frontend
- spartan_mailhog
- spartan_pgadmin

### 2. Verificar logs del backend:

```powershell
docker-compose logs backend
```

No deberían haber errores.

### 3. Acceder al admin:

```
http://localhost:8000/admin
```

Login: admin@gym-spartan.com / admin123

### 4. Verificar modelos en admin:

Deberías ver:

- [x] Clientes (con peso, altura, experiencia)
- [x] Planes de Membresía
- [x] Inscripciones Membresía
- [x] Membresías
- [x] Promociones
- [x] Usuarios
- [x] Roles
- [x] Permisos
- [x] Bitácora

---

## 🐞 SOLUCIÓN DE PROBLEMAS

### Error: "database 'spartan_db' does not exist"

```powershell
# Recrear la base de datos
docker-compose down
docker volume rm si1-spartan_postgres_data -f
docker-compose up -d
```

### Error: "port is already allocated"

Otro servicio está usando el puerto. Cambiar en `docker-compose.yml` o detener el servicio conflictivo.

### Error: "Cannot connect to the Docker daemon"

Docker Desktop no está corriendo. Iniciar Docker Desktop.

### Los cambios en el código no se reflejan:

```powershell
# Reconstruir el contenedor
docker-compose up -d --build backend
```

### Ver todos los logs en tiempo real:

```powershell
docker-compose logs -f
```

---

## 📊 DATOS DE PRUEBA CREADOS

Después de ejecutar los seeders tendrás:

### Usuarios (4):

1. **admin** - admin@gym-spartan.com (Superusuario)
2. **entrenador1** - entrenador@gym-spartan.com (Rol: Entrenador)
3. **recepcion1** - recepcion@gym-spartan.com (Rol: Recepcionista)
4. **gerente1** - gerente@gym-spartan.com (Rol: Gerente)

### Clientes (5):

1. Pedro Ramírez - CI: 12345678
2. Ana Martínez - CI: 87654321
3. Luis Flores - CI: 11223344
4. Sofia Vargas - CI: 55667788
5. Brandon Cusicanqui - CI: 123145

### Planes de Membresía (7):

1. Plan Diario - Bs. 15
2. Plan Semanal - Bs. 80
3. Plan Quincenal - Bs. 140
4. Plan Mensual - Bs. 250
5. Plan Trimestral - Bs. 650
6. Plan Semestral - Bs. 1,200
7. Plan Anual - Bs. 2,200

### Promociones (5):

1. Promoción Año Nuevo - 15% desc.
2. Promoción Verano - 20% desc.
3. Black Friday Gym - 30% desc.
4. Estudiantes - 10% desc.
5. Referido - 25% desc.

---

## 🎯 COMANDOS RÁPIDOS

```powershell
# Reseteo completo (usar el script)
.\scripts\reset_migrations_docker.ps1

# Ver estado de servicios
docker-compose ps

# Ver logs
docker-compose logs -f backend

# Reiniciar backend
docker-compose restart backend

# Ejecutar comando en backend
docker-compose exec backend python manage.py <comando>

# Acceder a shell de Django
docker-compose exec backend python manage.py shell

# Crear superusuario
docker-compose exec backend python manage.py createsuperuser

# Ejecutar seeders
docker-compose exec backend python seeders/run_all_seeders.py

# Detener todo
docker-compose down

# Iniciar todo
docker-compose up -d

# Limpiar todo (incluyendo volúmenes)
docker-compose down -v
```

---

## ✅ CHECKLIST POST-RESETEO

- [ ] Contenedores corriendo (docker-compose ps)
- [ ] Backend responde (http://localhost:8000)
- [ ] Admin accesible (http://localhost:8000/admin)
- [ ] Frontend corriendo (http://localhost:3000)
- [ ] Seeders ejecutados
- [ ] Modelos visibles en admin
- [ ] Bitácora funcionando

---

**¡Listo para trabajar con Docker! 🐳**
