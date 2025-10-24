# 🚀 Guía de Deployment - Azure Cloud vs Local

## 📋 Resumen de Entornos

### ☁️ SERVIDOR (Azure VM - 20.81.130.3)

**Infraestructura:**

- IP pública estática: `20.81.130.3`
- NSG (Network Security Group): Puertos 22 (SSH), 80 (HTTP)
- Nginx como reverse proxy en puerto 80
- Docker containers en loopback (127.0.0.1)

**Arquitectura de Red:**

```
Internet (20.81.130.3:80)
         ↓
    Nginx (:80)
         ↓
    ├─→ / → frontend (127.0.0.1:3000)
    └─→ /api/ → backend (127.0.0.1:8000)
```

**Docker Services (todos en 127.0.0.1):**

- Frontend: `127.0.0.1:3000`
- Backend: `127.0.0.1:8000`
- Database: `127.0.0.1:5432`
- MailHog: `127.0.0.1:8025`
- pgAdmin: `127.0.0.1:5050`

---

### 💻 LOCAL (Desarrollo)

**Infraestructura:**

- Localhost directo
- Sin Nginx
- Puertos expuestos al host

**Docker Services:**

- Frontend: `localhost:3000`
- Backend: `localhost:8000`
- Database: `localhost:5433` (mapeado desde 5432)
- MailHog: `localhost:8025`
- pgAdmin: `localhost:5050`

---

## 🔧 Configuración por Entorno

### ☁️ Configuración en Azure (Producción)

#### 1. Variables de Entorno Backend (`backend/.env`)

```bash
# Django
SECRET_KEY=<TU_SECRET_KEY_SEGURO>
DEBUG=False
ALLOWED_HOSTS=20.81.130.3,localhost,127.0.0.1,backend

# Database (PostgreSQL en Docker)
DATABASE_ENGINE=postgresql
DATABASE_NAME=spartan_db
DATABASE_USER=spartan_user
DATABASE_PASSWORD=<PASSWORD_SEGURO>
DATABASE_HOST=db
DATABASE_PORT=5432

# JWT
JWT_ACCESS_TOKEN_LIFETIME_HOURS=1
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

# Email (MailHog para testing)
EMAIL_BACKEND=smtp
EMAIL_HOST=mailhog
EMAIL_PORT=1025
EMAIL_USE_TLS=False
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=noreply@gym-spartan.com

# CORS - Importante: IP pública del servidor
CORS_ALLOWED_ORIGINS=http://20.81.130.3
```

#### 2. Variables de Entorno Frontend (`frontend/.env.local`)

```bash
# ✅ CRÍTICO: En producción con Nginx, usar ruta relativa
NEXT_PUBLIC_API_URL=/api
```

**¿Por qué `/api`?**

- Nginx hace proxy de `/api/` → `http://127.0.0.1:8000`
- El frontend llama a `/api/auth/login/` y Nginx lo reenvía al backend
- No hay CORS porque todo va por el mismo dominio

#### 3. Nginx Configuration (`/etc/nginx/sites-available/gym.conf`)

```nginx
server {
    listen 80;
    server_name 20.81.130.3;

    # Logs
    access_log /var/log/nginx/gym_access.log;
    error_log /var/log/nginx/gym_error.log;

    # Frontend (Next.js dev server)
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API (Django)
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # CORS headers (opcional, Django ya los maneja)
        add_header 'Access-Control-Allow-Origin' 'http://20.81.130.3' always;
        add_header 'Access-Control-Allow-Credentials' 'true' always;
    }

    # Django Admin static files
    location /static/ {
        alias /home/azureuser/Sistema-De-Informacion-1-GYM/backend/staticfiles/;
    }

    # Django Media files
    location /media/ {
        alias /home/azureuser/Sistema-De-Informacion-1-GYM/backend/media/;
    }
}
```

**Activar configuración:**

```bash
sudo ln -s /etc/nginx/sites-available/gym.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 4. Docker Compose en Azure

El `docker-compose.yml` actual **YA ESTÁ CONFIGURADO** para Azure:

✅ Puertos en loopback: `127.0.0.1:3000`, `127.0.0.1:8000`
✅ Healthcheck en PostgreSQL
✅ `depends_on: service_healthy` en backend
✅ `restart: unless-stopped` en todos los servicios

---

### 💻 Configuración Local (Desarrollo)

#### 1. Variables de Entorno Backend (`backend/.env`)

```bash
# Django
SECRET_KEY=django-insecure-dev-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,backend

# Database (SQLite para desarrollo rápido, o PostgreSQL)
DATABASE_ENGINE=postgresql  # o sqlite3
DATABASE_NAME=spartan_db
DATABASE_USER=spartan_user
DATABASE_PASSWORD=spartan_pass
DATABASE_HOST=db
DATABASE_PORT=5432

# JWT
JWT_ACCESS_TOKEN_LIFETIME_HOURS=1
JWT_REFRESH_TOKEN_LIFETIME_DAYS=1

# Email (MailHog)
EMAIL_BACKEND=smtp
EMAIL_HOST=mailhog
EMAIL_PORT=1025
EMAIL_USE_TLS=False
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=noreply@gym-spartan.com

# CORS - Localhost para desarrollo
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

#### 2. Variables de Entorno Frontend (`frontend/.env.local`)

```bash
# ✅ En local: llamar directamente al backend sin Nginx
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**¿Por qué `http://localhost:8000`?**

- No hay Nginx en local
- El frontend llama directamente al backend en puerto 8000
- Django maneja CORS con `CORS_ALLOWED_ORIGINS=http://localhost:3000`

#### 3. Docker Compose Local

El mismo `docker-compose.yml` pero con ajustes menores:

**Opción 1: Mapear DB a puerto diferente para evitar conflictos**

```yaml
services:
  db:
    ports:
      - "5433:5432" # Puerto local 5433 para evitar conflicto
```

**Opción 2: Sin cambios** (usar puerto 5432 estándar)

---

## 📦 Comandos de Deployment

### ☁️ Azure VM (Producción)

#### Deploy Inicial

```bash
# Conectar a la VM
ssh azureuser@20.81.130.3

# Clonar el repositorio
cd ~
git clone https://github.com/DarksouleaterXD/Sistema-De-Informacion-1-GYM.git
cd Sistema-De-Informacion-1-GYM

# Configurar variables de entorno
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# Editar archivos .env con valores de producción
nano backend/.env
nano frontend/.env.local

# Levantar servicios
docker compose up -d --build

# Ejecutar migraciones
docker compose exec backend python manage.py migrate

# Crear superusuario
docker compose exec backend python manage.py createsuperuser

# Configurar Nginx (ver sección anterior)
sudo nano /etc/nginx/sites-available/gym.conf
sudo ln -s /etc/nginx/sites-available/gym.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### Actualizar Aplicación

```bash
# En la VM
cd ~/Sistema-De-Informacion-1-GYM
git pull

# Reconstruir contenedores
docker compose down
docker compose up -d --build

# Ejecutar nuevas migraciones
docker compose exec backend python manage.py migrate

# Recargar Nginx
sudo systemctl reload nginx
```

#### Ver Logs

```bash
# Docker logs
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f db

# Nginx logs
sudo tail -f /var/log/nginx/gym_error.log
sudo tail -f /var/log/nginx/gym_access.log
```

#### Verificar Servicios

```bash
# Desde la VM
curl -I http://127.0.0.1:3000  # Frontend
curl -I http://127.0.0.1:8000/api/  # Backend

# Estado de Docker
docker compose ps

# Estado de Nginx
sudo systemctl status nginx
```

---

### 💻 Local (Desarrollo)

#### Levantar Servicios

```bash
# Desde el directorio del proyecto
docker compose up -d --build

# Ejecutar migraciones
docker compose exec backend python manage.py migrate

# Crear superusuario (primera vez)
docker compose exec backend python manage.py createsuperuser

# Ejecutar seeders (opcional)
docker compose exec backend python manage.py shell < seeders/run_all_seeders.py
```

#### Ver Logs

```bash
docker compose logs -f backend
docker compose logs -f frontend
```

#### Acceder a URLs

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/
- Django Admin: http://localhost:8000/admin/
- pgAdmin: http://localhost:5050
- MailHog: http://localhost:8025

---

## 🔒 Seguridad en Azure

### NSG (Network Security Group)

**Reglas Recomendadas (PRODUCCIÓN):**

| Puerto | Protocolo | Origen   | Descripción       |
| ------ | --------- | -------- | ----------------- |
| 22     | TCP       | Tu IP    | SSH (restringido) |
| 80     | TCP       | Internet | HTTP              |
| 443    | TCP       | Internet | HTTPS (futuro)    |

**❌ CERRAR en Producción:**

- Puerto 3000 (frontend directo)
- Puerto 8000 (backend directo)
- Puerto 5432 (database)
- Puerto 5050 (pgAdmin)
- Puerto 8025 (MailHog)

**Comando para verificar:**

```bash
# Verificar que solo 80 está expuesto
sudo netstat -tlnp | grep LISTEN
```

### UFW (Firewall)

Actualmente **deshabilitado** porque NSG maneja la seguridad.

**Si quieres habilitarlo:**

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

---

## 🎯 Checklist de Verificación

### ☁️ Azure (Producción)

- [ ] Variables `.env` configuradas con valores de producción
- [ ] `DEBUG=False` en backend
- [ ] `SECRET_KEY` único y seguro
- [ ] `ALLOWED_HOSTS` incluye IP pública (20.81.130.3)
- [ ] `CORS_ALLOWED_ORIGINS=http://20.81.130.3`
- [ ] `NEXT_PUBLIC_API_URL=/api` en frontend
- [ ] Nginx configurado y funcionando
- [ ] Docker containers en loopback (127.0.0.1)
- [ ] NSG solo permite 22, 80, 443
- [ ] Migraciones ejecutadas
- [ ] Superusuario creado
- [ ] Acceso a http://20.81.130.3 funciona

### 💻 Local (Desarrollo)

- [ ] Variables `.env` con valores de desarrollo
- [ ] `DEBUG=True` en backend
- [ ] `ALLOWED_HOSTS=localhost,127.0.0.1`
- [ ] `CORS_ALLOWED_ORIGINS=http://localhost:3000`
- [ ] `NEXT_PUBLIC_API_URL=http://localhost:8000` en frontend
- [ ] Docker compose levantado
- [ ] Migraciones ejecutadas
- [ ] Acceso a http://localhost:3000 funciona

---

## 🚧 Próximos Pasos Recomendados

### 1. HTTPS con Certbot (SSL)

**Si tienes un dominio:**

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d tudominio.com
```

**Actualizar Nginx para SSL:**

```nginx
server {
    listen 443 ssl http2;
    server_name tudominio.com;

    ssl_certificate /etc/letsencrypt/live/tudominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tudominio.com/privkey.pem;

    # ... resto de configuración
}

server {
    listen 80;
    server_name tudominio.com;
    return 301 https://$server_name$request_uri;
}
```

### 2. Frontend Build Estático (Producción)

**Más performante que dev server:**

```dockerfile
# frontend/Dockerfile.prod
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
COPY --from=build /app/.next ./.next
COPY --from=build /app/public ./public
COPY --from=build /app/package*.json ./
RUN npm ci --production
EXPOSE 3000
CMD ["npm", "start"]
```

**Nginx para servir build estático:**

```nginx
location / {
    root /path/to/frontend/out;
    try_files $uri $uri/ /index.html;
}
```

### 3. Backup Automático de Database

```bash
# Script de backup
#!/bin/bash
docker compose exec -T db pg_dump -U spartan_user spartan_db > backup_$(date +%Y%m%d).sql
```

### 4. Monitoreo y Logs

- Configurar log rotation en Nginx
- Usar `docker compose logs` para debugging
- Considerar herramientas como Prometheus + Grafana

---

## 🆘 Troubleshooting

### Frontend no carga

**En Azure:**

```bash
# Verificar que el contenedor esté corriendo
docker compose ps

# Ver logs
docker compose logs frontend

# Verificar desde la VM
curl -I http://127.0.0.1:3000

# Verificar Nginx
sudo nginx -t
sudo systemctl status nginx
```

**En Local:**

```bash
docker compose logs frontend
curl -I http://localhost:3000
```

### Backend no responde

**Verificar:**

```bash
# ¿Está corriendo?
docker compose ps

# Logs
docker compose logs backend

# ¿Database está lista?
docker compose logs db

# ¿Migraciones aplicadas?
docker compose exec backend python manage.py showmigrations
```

### CORS Errors

**En Azure:**

- Verificar `CORS_ALLOWED_ORIGINS=http://20.81.130.3` en backend/.env
- Verificar `NEXT_PUBLIC_API_URL=/api` en frontend/.env.local

**En Local:**

- Verificar `CORS_ALLOWED_ORIGINS=http://localhost:3000` en backend/.env
- Verificar `NEXT_PUBLIC_API_URL=http://localhost:8000` en frontend/.env.local

### Connection Refused

**En Azure:**

```bash
# Verificar puertos en loopback
sudo netstat -tlnp | grep 127.0.0.1

# Verificar Nginx
curl -I http://127.0.0.1:8000/api/
```

---

## 📚 Recursos

- [Docker Compose Docs](https://docs.docker.com/compose/)
- [Nginx Reverse Proxy Guide](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Next.js Deployment](https://nextjs.org/docs/deployment)

---

**Última actualización**: Octubre 2024
**Proyecto**: SI1-Spartan - Sistema de Gestión de Gimnasio
