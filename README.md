# 🏋️ SI1-Spartan - Sistema de Gestión de Gimnasio# SI1-Spartan



Sistema completo de gestión para gimnasios desarrollado con Django REST Framework y Next.js.Proyecto Full Stack con Django, Next.js y PostgreSQL usando Docker.



## 🚀 Instalación Rápida## 🚀 Tecnologías



### Requisitos- **Backend**: Django 5.0 + Django REST Framework

- Docker y Docker Compose- **Frontend**: Next.js 14.2

- Git- **Base de datos**: PostgreSQL 15

- **Containerización**: Docker & Docker Compose

### Pasos de Instalación

## 📋 Prerequisitos

```bash

# 1. Clonar repositorio- Docker Desktop instalado

git clone --single-branch --branch feature/IDK https://github.com/DarksouleaterXD/Sistema-De-Informacion-1-GYM.git- Docker Compose

cd Sistema-De-Informacion-1-GYM

## � Variables de Entorno

# 2. Configurar variables de entorno

cp backend/.env.example backend/.env### Configuración Inicial (IMPORTANTE)

cp frontend/.env.example frontend/.env.local

Antes de iniciar el proyecto, debes copiar los archivos de ejemplo y configurar tus variables de entorno:

# 3. Editar archivos .env según tu entorno:

# - Local: dejar como está```bash

# - Azure/Nube: editar backend/.env (CORS, ALLOWED_HOSTS) y frontend/.env.local (NEXT_PUBLIC_API_URL=/api)# Backend

cp backend/.env.example backend/.env

# 4. Levantar servicios

docker compose up -d --build# Frontend

cp frontend/.env.example frontend/.env.local

# 5. Ejecutar migraciones y seeders```

docker compose exec backend python manage.py makemigrations

docker compose exec backend python manage.py migrate### Backend (.env)

docker compose exec backend python manage.py seed

```Edita `backend/.env` y configura:



## 🌐 Acceso a la Aplicación```bash

# Genera una clave secreta segura para producción

### LocalSECRET_KEY=tu-clave-secreta-generada

- **Frontend**: http://localhost:3000

- **Backend API**: http://localhost:8000/api/# En desarrollo usa DEBUG=True, en producción DEBUG=False

- **Django Admin**: http://localhost:8000/admin/DEBUG=True

- **API Docs (Swagger)**: http://localhost:8000/api/docs/

- **pgAdmin**: http://localhost:5050# Base de datos (los valores por defecto funcionan con Docker)

- **MailHog**: http://localhost:8025DATABASE_ENGINE=postgresql

DATABASE_NAME=spartan_db

### Azure/Nube (con Nginx)DATABASE_USER=spartan_user

- **App**: http://TU_IP/DATABASE_PASSWORD=spartan_pass  # ⚠️ Cambiar en producción

- **API**: http://TU_IP/api/DATABASE_HOST=db

- **Admin**: http://TU_IP/admin/DATABASE_PORT=5432

```

## ⚙️ Configuración por Entorno

### Frontend (.env.local)

### 🖥️ Local (Desarrollo)

El archivo `frontend/.env.local` ya tiene la configuración correcta:

**backend/.env**

```env```bash

ALLOWED_HOSTS=localhost,127.0.0.1,backendNEXT_PUBLIC_API_URL=http://localhost:8000

CORS_ALLOWED_ORIGINS=http://localhost:3000```

```

> ⚠️ **IMPORTANTE**: Los archivos `.env` y `.env.local` están en `.gitignore` y NO se suben al repositorio por seguridad.

**frontend/.env.local**

```env## �🛠️ Configuración inicial

NEXT_PUBLIC_API_URL=http://localhost:8000

```### 1. Inicializar el proyecto Django



### ☁️ Azure/Nube (Producción)Primero, construye y ejecuta los contenedores:



**backend/.env**```bash

```envdocker-compose up -d db

DEBUG=False```

ALLOWED_HOSTS=TU_IP_PUBLICA,localhost,127.0.0.1,backend

CORS_ALLOWED_ORIGINS=http://TU_IP_PUBLICALuego, crea el proyecto Django:

SECRET_KEY=<generar-clave-segura>

``````bash

docker-compose run --rm backend django-admin startproject config .

**frontend/.env.local**```

```env

NEXT_PUBLIC_API_URL=/api### 2. Configurar Django para PostgreSQL

```

Edita el archivo `backend/config/settings.py` y reemplaza la configuración de DATABASES con:

## 📦 Stack Tecnológico

```python

- **Backend**: Django 5.0 + Django REST Frameworkimport os

- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS

- **Database**: PostgreSQL 15DATABASES = {

- **Authentication**: JWT    'default': {

- **Containerization**: Docker + Docker Compose        'ENGINE': 'django.db.backends.postgresql',

        'NAME': os.environ.get('DATABASE_NAME', 'spartan_db'),

## 🔧 Comandos Útiles        'USER': os.environ.get('DATABASE_USER', 'spartan_user'),

        'PASSWORD': os.environ.get('DATABASE_PASSWORD', 'spartan_pass'),

```bash        'HOST': os.environ.get('DATABASE_HOST', 'db'),

# Ver logs        'PORT': os.environ.get('DATABASE_PORT', '5432'),

docker compose logs -f backend    }

docker compose logs -f frontend}



# Crear superusuario# Agregar CORS

docker compose exec backend python manage.py createsuperuserINSTALLED_APPS = [

    # ... apps existentes

# Shell de Django    'rest_framework',

docker compose exec backend python manage.py shell    'corsheaders',

]

# Conectar a PostgreSQL

docker compose exec db psql -U spartan_user -d spartan_dbMIDDLEWARE = [

    'corsheaders.middleware.CorsMiddleware',

# Detener servicios    # ... middleware existentes

docker compose down]



# Reiniciar servicio específicoCORS_ALLOWED_ORIGINS = [

docker compose restart backend    "http://localhost:3000",

```]



## 📚 API DocumentationALLOWED_HOSTS = ['*']

```

La documentación de la API está disponible en:

- **Swagger UI**: http://localhost:8000/api/docs/### 3. Inicializar Next.js

- **ReDoc**: http://localhost:8000/api/redoc/

```bash

## 🔐 Credenciales por Defectodocker-compose run --rm frontend npx create-next-app@latest . --typescript --tailwind --app --no-src-dir --import-alias "@/*"

```

Después de ejecutar `python manage.py seed`:

- **Superusuario**: admin / admin123### 4. Ejecutar migraciones de Django

- **Usuarios de prueba**: Consultar logs del seeder

```bash

## 📝 Estructura del Proyectodocker-compose run --rm backend python manage.py migrate

```

```

SI1-Spartan/### 5. Crear superusuario de Django (opcional)

├── backend/              # Django REST API

│   ├── apps/            # Aplicaciones Django```bash

│   ├── config/          # Configuracióndocker-compose run --rm backend python manage.py createsuperuser

│   └── seeders/         # Datos de prueba```

├── frontend/            # Next.js App

│   ├── app/            # App Router## 🏃 Ejecutar el proyecto

│   ├── components/     # Componentes React

│   └── lib/            # Servicios y utilidades### Iniciar todos los servicios

└── docker-compose.yml  # Configuración Docker

``````bash

docker-compose up

## 🤝 Contribución```



1. Fork el proyectoO en modo detached:

2. Crea tu feature branch (`git checkout -b feature/AmazingFeature`)

3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)```bash

4. Push a la branch (`git push origin feature/AmazingFeature`)docker-compose up -d

5. Abre un Pull Request```



---### Acceder a los servicios



**Desarrollado con ❤️ para Gym Spartan**- **Frontend**: http://localhost:3000

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
