# 🚀 Guía de Despliegue en Azure Ubuntu

Esta guía te ayudará a desplegar correctamente el proyecto Sistema-De-Informacion-1-GYM en una máquina virtual de Azure Ubuntu.

---

## 📋 Requisitos Previos

- VM Ubuntu 24.04 LTS en Azure
- Puertos abiertos: 22 (SSH), 80 (HTTP), 443 (HTTPS), 3000 (Frontend), 8000 (Backend)
- Acceso SSH a la VM

---

## 🔧 Paso 1: Conectar por SSH

```bash
ssh -i ruta/a/tu/clave.pem azureuser@TU_IP_PUBLICA
```

**Ejemplo:**

```bash
ssh -i C:\Users\brahi\Downloads\gym_key.pem azureuser@51.57.78.32
```

---

## 🔄 Paso 2: Actualizar Sistema

```bash
sudo apt update && sudo apt upgrade -y
```

---

## 🐳 Paso 3: Instalar Docker y Docker Compose

```bash
# Instalar Docker
sudo apt install docker.io docker-compose -y

# Verificar instalación
docker --version
docker compose --version

# Iniciar y habilitar Docker
sudo systemctl start docker
sudo systemctl enable docker

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER

# ⚠️ IMPORTANTE: Cerrar sesión y volver a conectar
exit
```

**Vuelve a conectar por SSH después del exit:**

```bash
ssh -i ruta/a/tu/clave.pem azureuser@TU_IP_PUBLICA
```

---

## 📦 Paso 4: Instalar Git y Configurar

```bash
sudo apt install git -y

# Configurar Git (usa tu información)
git config --global user.name "Tu Nombre"
git config --global user.email "tu-email@ejemplo.com"
```

---

## 📥 Paso 5: Clonar el Repositorio

```bash
cd /home/azureuser/
git clone --single-branch --branch feature/Instructor https://github.com/DarksouleaterXD/Sistema-De-Informacion-1-GYM.git
cd Sistema-De-Informacion-1-GYM
```

---

## ⚙️ Paso 6: Configurar Variables de Entorno

### 6.1 Backend (.env)

```bash
cp backend/.env.example backend/.env
nano backend/.env
```

**Edita el archivo con estos valores (reemplaza TU_IP_PUBLICA):**

```bash
# ==== Django ====
SECRET_KEY=GENERA_UNA_CLAVE_SEGURA_AQUI
DEBUG=False
ALLOWED_HOSTS=TU_IP_PUBLICA,localhost,127.0.0.1,backend

# ==== Base de datos ====
DATABASE_ENGINE=postgresql
DATABASE_NAME=spartan_db
DATABASE_USER=spartan_user
DATABASE_PASSWORD=spartan_pass_CAMBIA_ESTO
DATABASE_HOST=db
DATABASE_PORT=5432

# ==== JWT ====
JWT_ACCESS_TOKEN_LIFETIME_HOURS=1
JWT_REFRESH_TOKEN_LIFETIME_DAYS=1

# ==== Email (MailHog) ====
EMAIL_BACKEND=smtp
EMAIL_HOST=mailhog
EMAIL_PORT=1025
EMAIL_USE_TLS=False
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=noreply@gym-spartan.com

# ==== CORS ====
CORS_ALLOWED_ORIGINS=http://TU_IP_PUBLICA:3000
```

**🔐 Generar SECRET_KEY segura:**

```bash
python3 -c "from secrets import token_urlsafe; print(token_urlsafe(50))"
```

Copia el resultado y pégalo en `SECRET_KEY=...`

**Para guardar en nano:**

- Presiona `Ctrl + X`
- Presiona `Y` para confirmar
- Presiona `Enter`

### 6.2 Frontend (.env.local)

```bash
cp frontend/.env.example frontend/.env.local
nano frontend/.env.local
```

**Edita con tu IP pública:**

```bash
NEXT_PUBLIC_API_URL=http://TU_IP_PUBLICA:8000
```

**Ejemplo:**

```bash
NEXT_PUBLIC_API_URL=http://51.57.78.32:8000
```

**Guardar:** `Ctrl + X`, `Y`, `Enter`

---

## 🚀 Paso 7: Levantar Servicios con Docker

```bash
# Asegúrate de estar en el directorio raíz del proyecto
cd /home/azureuser/Sistema-De-Informacion-1-GYM

# Levantar servicios (usar "docker compose" con espacio, no "docker-compose")
docker compose up -d --build
```

**Ver progreso:**

```bash
# Ver estado de contenedores
docker compose ps

# Ver logs en tiempo real
docker compose logs -f
```

**Presiona `Ctrl + C` para salir de los logs**

---

## 🗄️ Paso 8: Configurar Base de Datos

**Espera ~30 segundos a que PostgreSQL inicie completamente**, luego:

```bash
# Aplicar migraciones
docker compose exec backend python manage.py migrate

# Cargar datos iniciales (usuarios, roles, permisos, clientes)
docker compose exec backend python seeders/init_system.py

# Verificar que todo funcione correctamente
docker compose exec backend python seeders/verify_system.py
```

**Deberías ver un mensaje de éxito similar a:**

```
✅ Sistema inicializado correctamente
✅ 51 permisos creados
✅ 6 roles creados con permisos asignados
✅ Usuario admin creado con rol Administrador
✅ 10 usuarios de prueba creados
✅ 20 clientes de ejemplo creados
```

---

## 🔓 Paso 9: Configurar Firewall de Azure

En el **Portal de Azure**, ve a:

1. **Tu VM → Configuración → Redes → Reglas de puerto de entrada**
2. **Agregar regla de puerto de entrada** para cada uno:

| Puerto | Servicio | Prioridad       |
| ------ | -------- | --------------- |
| 22     | SSH      | 1000            |
| 3000   | Frontend | 1010            |
| 8000   | Backend  | 1020            |
| 5050   | pgAdmin  | 1030 (opcional) |
| 8025   | MailHog  | 1040 (opcional) |

---

## 🌐 Paso 10: Acceder a la Aplicación

Abre tu navegador en:

| Servicio         | URL                                   | Credenciales                  |
| ---------------- | ------------------------------------- | ----------------------------- |
| **Frontend**     | `http://TU_IP_PUBLICA:3000`           | admin / admin123              |
| **Backend API**  | `http://TU_IP_PUBLICA:8000/api/`      | -                             |
| **Django Admin** | `http://TU_IP_PUBLICA:8000/admin/`    | admin / admin123              |
| **Swagger Docs** | `http://TU_IP_PUBLICA:8000/api/docs/` | -                             |
| **pgAdmin**      | `http://TU_IP_PUBLICA:5050`           | admin@gym-spartan.com / admin |

**Ejemplo con IP 51.57.78.32:**

- Frontend: `http://51.57.78.32:3000`
- Backend: `http://51.57.78.32:8000`

---

## 🐛 Solución de Problemas Comunes

### Error: `ERR_BLOCKED_BY_CLIENT`

**Causas:**

1. **Extensión del navegador bloqueando la petición**

   - Desactiva AdBlock, uBlock Origin, Privacy Badger temporalmente
   - Prueba en modo incógnito o con otro navegador

2. **CORS mal configurado**

   Verifica en Azure:

   ```bash
   # Ver variables de entorno del backend
   docker compose exec backend env | grep CORS

   # Debe mostrar:
   # CORS_ALLOWED_ORIGINS=http://TU_IP_PUBLICA:3000
   ```

   Si no es correcto, edita el archivo `.env`:

   ```bash
   nano backend/.env
   # Cambia CORS_ALLOWED_ORIGINS=http://TU_IP_PUBLICA:3000
   ```

   Luego reinicia el backend:

   ```bash
   docker compose restart backend
   ```

3. **Frontend apuntando a URL incorrecta**

   ```bash
   # Ver variable de entorno del frontend
   docker compose exec frontend env | grep NEXT_PUBLIC

   # Debe mostrar:
   # NEXT_PUBLIC_API_URL=http://TU_IP_PUBLICA:8000
   ```

   Si no es correcto:

   ```bash
   nano frontend/.env.local
   # Cambia NEXT_PUBLIC_API_URL=http://TU_IP_PUBLICA:8000

   # Reiniciar frontend
   docker compose down
   docker compose up -d --build
   ```

4. **Puertos no abiertos en Azure**

   Verifica en el Portal de Azure que los puertos 3000 y 8000 estén abiertos.

### Error: `Cannot connect to database`

```bash
# Ver logs de PostgreSQL
docker compose logs db

# Verificar que el contenedor esté corriendo
docker compose ps db

# Reiniciar base de datos
docker compose restart db

# Esperar 10 segundos y reintentar migraciones
docker compose exec backend python manage.py migrate
```

### Error: `Module not found`

```bash
# Reinstalar dependencias del backend
docker compose exec backend pip install -r requirements.txt
docker compose restart backend

# Para el frontend
docker compose exec frontend npm install
docker compose restart frontend
```

### Frontend muestra página en blanco

```bash
# Limpiar caché y reconstruir
docker compose down
docker compose up -d --build

# Ver logs del frontend
docker compose logs -f frontend
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

---

## 🔄 Actualizar la Aplicación

Cuando hagas cambios en GitHub:

```bash
cd /home/azureuser/Sistema-De-Informacion-1-GYM

# Obtener últimos cambios
git pull origin feature/Instructor

# Reconstruir contenedores
docker compose up -d --build

# Aplicar nuevas migraciones (si hay)
docker compose exec backend python manage.py migrate

# Verificar
docker compose ps
```

---

## 🛑 Detener la Aplicación

```bash
# Detener servicios (mantiene datos)
docker compose down

# Detener y eliminar volúmenes (⚠️ BORRA LA BASE DE DATOS)
docker compose down -v
```

---

## 📊 Comandos Útiles de Monitoreo

```bash
# Ver estado de contenedores
docker compose ps

# Ver uso de recursos
docker stats

# Ver logs recientes
docker compose logs --tail=100

# Ver solo errores
docker compose logs | grep -i error

# Entrar a un contenedor
docker compose exec backend bash
docker compose exec frontend sh
docker compose exec db psql -U spartan_user -d spartan_db
```

---

## 🔐 Seguridad en Producción

**⚠️ IMPORTANTE antes de ir a producción:**

1. **Cambiar todas las contraseñas por defecto:**

   - Base de datos (`DATABASE_PASSWORD` en `.env`)
   - Usuario admin (`admin123` → contraseña fuerte)
   - pgAdmin (`admin`)

2. **Usar HTTPS con SSL/TLS:**

   - Instalar Nginx como proxy reverso
   - Obtener certificado SSL con Let's Encrypt (Certbot)

3. **Cambiar `DEBUG=False`** en `backend/.env`

4. **Configurar backups automáticos** de PostgreSQL

5. **Restringir acceso SSH** solo a IPs conocidas

---

## 📞 Soporte

Si tienes problemas:

1. **Ver logs:** `docker compose logs -f`
2. **Verificar estado:** `docker compose ps`
3. **Revisar variables de entorno:**
   ```bash
   docker compose exec backend env
   docker compose exec frontend env
   ```

---

## 📝 Checklist de Despliegue

- [ ] VM Ubuntu creada en Azure
- [ ] Puertos 22, 3000, 8000 abiertos en Azure
- [ ] Docker y Docker Compose instalados
- [ ] Repositorio clonado
- [ ] `backend/.env` configurado con IP pública
- [ ] `frontend/.env.local` configurado con IP pública
- [ ] Contenedores levantados (`docker compose up -d --build`)
- [ ] Migraciones aplicadas
- [ ] Datos iniciales cargados (`init_system.py`)
- [ ] Sistema verificado (`verify_system.py`)
- [ ] Acceso al frontend desde navegador
- [ ] Login funcionando correctamente

---

**✅ ¡Listo! Tu aplicación debería estar corriendo en Azure.**

**Última actualización:** Noviembre 2025
