# 🏋️ Guía de Setup para Colaboradores - Gym Spartan

Esta guía te ayudará a configurar el proyecto completo en tu máquina local en menos de 10 minutos.

---

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

- ✅ **Docker Desktop** (incluye Docker Compose)
- ✅ **Git**
- ✅ Un editor de código (VSCode recomendado)

---

## 🚀 Setup Rápido (5 Pasos)

### 1️⃣ Clonar el Repositorio

```bash
git clone --single-branch --branch feature/IDK https://github.com/DarksouleaterXD/Sistema-De-Informacion-1-GYM.git
cd Sistema-De-Informacion-1-GYM
```

### 2️⃣ Configurar Variables de Entorno

```bash
# Backend
cp backend/.env.example backend/.env

# Frontend
cp frontend/.env.example frontend/.env.local
```

**✨ No necesitas modificar nada** - Los valores por defecto funcionan perfectamente para desarrollo local.

### 3️⃣ Levantar Todos los Servicios

```bash
docker compose up -d --build
```

**Servicios que se levantarán automáticamente:**

- 🐘 PostgreSQL (base de datos)
- 🐍 Backend Django (API REST)
- ⚛️ Frontend Next.js (UI)
- 📧 MailHog (emails de prueba)
- 🔧 pgAdmin (gestor de BD)

**⏱️ Tiempo estimado:** 3-5 minutos la primera vez.

### 4️⃣ Ejecutar Migraciones

```bash
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
```

### 5️⃣ Cargar Datos de Prueba (IMPORTANTE)

```bash
# Opción A: Usar el script completo (RECOMENDADO)
docker compose exec backend python seeders/init_system.py

# Opción B: Solo seeders básicos
docker compose exec backend python manage.py seed
```

**✅ El script `init_system.py` hace TODO automáticamente:**

- ✅ Crea el superusuario `admin`
- ✅ Crea 51 permisos del sistema
- ✅ Crea 6 roles predeterminados (Administrador, Gerente, etc.)
- ✅ Asigna permisos a roles
- ✅ Crea 3 usuarios de prueba
- ✅ Crea 5 clientes de ejemplo
- ✅ Crea 7 planes de membresía
- ✅ Crea 5 promociones

---

## 🌐 URLs y Credenciales

### 🖥️ Acceso a la Aplicación

| Servicio               | URL                             | Descripción             |
| ---------------------- | ------------------------------- | ----------------------- |
| **Frontend (App)**     | http://localhost:3000           | Aplicación principal    |
| **Backend API**        | http://localhost:8000/api/      | API REST                |
| **Django Admin**       | http://localhost:8000/admin/    | Panel de administración |
| **API Docs (Swagger)** | http://localhost:8000/api/docs/ | Documentación API       |
| **pgAdmin**            | http://localhost:5050           | Gestor PostgreSQL       |
| **MailHog**            | http://localhost:8025           | Ver emails de prueba    |

### 🔐 Credenciales de Acceso

#### Usuario Administrador (Acceso Total)

```
URL: http://localhost:3000/login
Username: admin
Password: admin123
```

#### Usuarios de Prueba

```
Gerente:
  Username: gerente
  Password: gerente123

Recepcionista:
  Username: recepcionista
  Password: recep123
```

#### Django Admin

```
URL: http://localhost:8000/admin/
Username: admin
Password: admin123
```

#### pgAdmin

```
URL: http://localhost:5050
Email: admin@gym-spartan.com
Password: admin
```

**🔌 Conexión a PostgreSQL en pgAdmin:**

- Host: `db` (o `localhost` si conectas desde fuera de Docker)
- Port: `5432`
- Database: `spartan_db`
- Username: `spartan_user`
- Password: `spartan_pass`

---

## 📦 Comandos Útiles

### Ver Logs de los Servicios

```bash
# Todos los servicios
docker compose logs -f

# Solo backend
docker compose logs -f backend

# Solo frontend
docker compose logs -f frontend
```

### Reiniciar Servicios

```bash
# Reiniciar todo
docker compose restart

# Reiniciar solo backend
docker compose restart backend

# Reiniciar solo frontend
docker compose restart frontend
```

### Detener y Limpiar

```bash
# Detener servicios
docker compose down

# Detener y eliminar volúmenes (⚠️ BORRA LA BD)
docker compose down -v

# Limpiar todo y volver a empezar
docker compose down -v
docker compose up -d --build
docker compose exec backend python manage.py migrate
docker compose exec backend python seeders/init_system.py
```

### Acceder a la Shell de Django

```bash
docker compose exec backend python manage.py shell
```

### Crear un Superusuario Adicional

```bash
docker compose exec backend python manage.py createsuperuser
```

### Ejecutar Tests

```bash
# Backend
docker compose exec backend python manage.py test

# Frontend
docker compose exec frontend npm test
```

---

## 🗂️ Estructura del Proyecto

```
Sistema-De-Informacion-1-GYM/
├── backend/                 # Django REST Framework
│   ├── apps/               # Aplicaciones Django
│   │   ├── audit/          # Auditoría y bitácora
│   │   ├── clients/        # Gestión de clientes
│   │   ├── core/           # Lógica central y permisos
│   │   ├── membresias/     # Membresías y planes
│   │   ├── promociones/    # Promociones
│   │   ├── roles/          # Roles y permisos RBAC
│   │   └── users/          # Usuarios
│   ├── config/             # Configuración Django
│   ├── seeders/            # Scripts de datos de prueba
│   └── requirements.txt
│
├── frontend/               # Next.js + TypeScript
│   ├── app/               # App Router de Next.js
│   │   ├── dashboard/     # Páginas del dashboard
│   │   └── login/         # Página de login
│   ├── components/        # Componentes React
│   │   ├── auth/          # Autenticación y permisos
│   │   ├── layout/        # Layouts
│   │   └── ui/            # Componentes UI reutilizables
│   └── lib/               # Utilidades y servicios
│       ├── contexts/      # Context API
│       ├── services/      # Servicios API
│       └── types/         # Tipos TypeScript
│
└── docker-compose.yml     # Orquestación de servicios
```

---

## 🔥 Troubleshooting

### ❌ "Port 3000 is already allocated"

```bash
# Detener el servicio que usa el puerto
docker compose down
# Cambiar el puerto en docker-compose.yml o matar el proceso
```

### ❌ "Database connection error"

```bash
# Esperar a que PostgreSQL termine de iniciar
docker compose logs db

# Verificar que el servicio de BD esté saludable
docker compose ps
```

### ❌ "Module not found" en Backend

```bash
# Reinstalar dependencias
docker compose exec backend pip install -r requirements.txt
docker compose restart backend
```

### ❌ "Module not found" en Frontend

```bash
# Reinstalar dependencias
docker compose exec frontend npm install
docker compose restart frontend
```

### ❌ Frontend no carga o muestra error 500

```bash
# Verificar que el backend esté corriendo
curl http://localhost:8000/api/

# Verificar variables de entorno
cat frontend/.env.local
# Debe contener: NEXT_PUBLIC_API_URL=http://localhost:8000
```

### ❌ No aparecen los datos de prueba

```bash
# Ejecutar el script de inicialización
docker compose exec backend python seeders/init_system.py
```

### 🔄 Resetear Todo (Base de datos limpia)

```bash
# ⚠️ ESTO BORRA TODOS LOS DATOS
docker compose down -v
docker compose up -d --build
docker compose exec backend python manage.py migrate
docker compose exec backend python seeders/init_system.py
```

---

## 🧪 Verificar que Todo Funciona

### 1. Backend API funcionando

```bash
curl http://localhost:8000/api/
# Debe responder con lista de endpoints
```

### 2. Login en Frontend

1. Ir a http://localhost:3000/login
2. Usar: `admin` / `admin123`
3. Debe redirigir a http://localhost:3000/dashboard

### 3. Ver datos en el Dashboard

- **Clientes**: 5 clientes de prueba
- **Roles**: 6 roles creados
- **Usuarios**: 4 usuarios (admin + 3 de prueba)
- **Planes**: 7 planes de membresía

---

## 🎯 Próximos Pasos

Una vez que tengas todo funcionando:

1. **Explora el código**: Revisa la estructura de carpetas
2. **Lee la documentación API**: http://localhost:8000/api/docs/
3. **Prueba los endpoints**: Usa Postman o Thunder Client
4. **Revisa los permisos**: El sistema tiene RBAC completo
5. **Crea tu rama**: `git checkout -b feature/tu-funcionalidad`

---

## 📚 Recursos Adicionales

- **Django REST Framework**: https://www.django-rest-framework.org/
- **Next.js 14 Docs**: https://nextjs.org/docs
- **Docker Docs**: https://docs.docker.com/
- **TypeScript**: https://www.typescriptlang.org/docs/

---

## 💬 ¿Necesitas Ayuda?

Si tienes problemas:

1. Revisa la sección **Troubleshooting** arriba
2. Verifica los logs: `docker compose logs -f`
3. Contacta al equipo en Slack/Discord
4. Abre un issue en GitHub

---

## ✅ Checklist de Verificación

Antes de empezar a desarrollar, asegúrate de que:

- [ ] Todos los servicios están corriendo (`docker compose ps`)
- [ ] El backend responde en http://localhost:8000/api/
- [ ] El frontend carga en http://localhost:3000
- [ ] Puedes hacer login con `admin` / `admin123`
- [ ] Ves datos de prueba en el dashboard (clientes, roles, etc.)
- [ ] Los logs no muestran errores críticos
- [ ] pgAdmin conecta correctamente a la BD

**Si todos los items están ✅, ¡estás listo para desarrollar!** 🎉

---

**Última actualización:** Noviembre 2024  
**Versión del proyecto:** 1.0.0  
**Branch activa:** feature/IDK
