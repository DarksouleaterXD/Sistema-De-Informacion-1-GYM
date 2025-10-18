# SI1-Spartan

Proyecto Full Stack con Django, Next.js y PostgreSQL usando Docker.

## 🚀 Tecnologías

- **Backend**: Django 5.0 + Django REST Framework
- **Frontend**: Next.js 14.2
- **Base de datos**: PostgreSQL 15
- **Containerización**: Docker & Docker Compose

## 📋 Prerequisitos

- Docker Desktop instalado
- Docker Compose

## 🛠️ Configuración inicial

### 1. Inicializar el proyecto Django

Primero, construye y ejecuta los contenedores:

```bash
docker-compose up -d db
```

Luego, crea el proyecto Django:

```bash
docker-compose run --rm backend django-admin startproject config .
```

### 2. Configurar Django para PostgreSQL

Edita el archivo `backend/config/settings.py` y reemplaza la configuración de DATABASES con:

```python
import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DATABASE_NAME', 'spartan_db'),
        'USER': os.environ.get('DATABASE_USER', 'spartan_user'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD', 'spartan_pass'),
        'HOST': os.environ.get('DATABASE_HOST', 'db'),
        'PORT': os.environ.get('DATABASE_PORT', '5432'),
    }
}

# Agregar CORS
INSTALLED_APPS = [
    # ... apps existentes
    'rest_framework',
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    # ... middleware existentes
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]

ALLOWED_HOSTS = ['*']
```

### 3. Inicializar Next.js

```bash
docker-compose run --rm frontend npx create-next-app@latest . --typescript --tailwind --app --no-src-dir --import-alias "@/*"
```

### 4. Ejecutar migraciones de Django

```bash
docker-compose run --rm backend python manage.py migrate
```

### 5. Crear superusuario de Django (opcional)

```bash
docker-compose run --rm backend python manage.py createsuperuser
```

## 🏃 Ejecutar el proyecto

### Iniciar todos los servicios

```bash
docker-compose up
```

O en modo detached:

```bash
docker-compose up -d
```

### Acceder a los servicios

- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **Admin Django**: http://localhost:8000/admin
- **PostgreSQL**: localhost:5432

### Ver logs

```bash
docker-compose logs -f
```

### Detener los servicios

```bash
docker-compose down
```

### Detener y eliminar volúmenes (⚠️ elimina la base de datos)

```bash
docker-compose down -v
```

## 📝 Comandos útiles

### Backend (Django)

```bash
# Crear una nueva app
docker-compose run --rm backend python manage.py startapp nombre_app

# Hacer migraciones
docker-compose run --rm backend python manage.py makemigrations

# Aplicar migraciones
docker-compose run --rm backend python manage.py migrate

# Shell de Django
docker-compose run --rm backend python manage.py shell

# Crear superusuario
docker-compose run --rm backend python manage.py createsuperuser
```

### Frontend (Next.js)

```bash
# Instalar dependencias
docker-compose run --rm frontend npm install nombre-paquete

# Acceder al contenedor
docker-compose exec frontend sh
```

### Base de datos

```bash
# Acceder a PostgreSQL
docker-compose exec db psql -U spartan_user -d spartan_db

# Backup de la base de datos
docker-compose exec db pg_dump -U spartan_user spartan_db > backup.sql

# Restaurar backup
docker-compose exec -T db psql -U spartan_user spartan_db < backup.sql
```

## 🔧 Desarrollo

### Reconstruir contenedores después de cambios en Dockerfile

```bash
docker-compose up --build
```

### Reconstruir un servicio específico

```bash
docker-compose up --build backend
```

## 📦 Estructura del proyecto

```
SI1-Spartan/
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── (archivos Django)
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   └── (archivos Next.js)
├── docker-compose.yml
├── .gitignore
└── README.md
```

## 🐛 Solución de problemas

### El backend no se conecta a la base de datos

Asegúrate de que el contenedor de PostgreSQL esté funcionando:

```bash
docker-compose ps
```

### Errores de permisos en Windows

Ejecuta Docker Desktop como administrador.

### Los cambios no se reflejan

Los volúmenes están configurados para desarrollo en vivo, pero si hay problemas:

```bash
docker-compose restart backend
# o
docker-compose restart frontend
```
