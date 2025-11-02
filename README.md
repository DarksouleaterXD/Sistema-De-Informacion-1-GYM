# 🏋️ Sistema de Información Gym Spartan

Sistema completo de gestión para gimnasios desarrollado con **Django REST Framework** y **Next.js**.

---

## 🚀 Tecnologías

- **Backend**: Django 5.0 + Django REST Framework + PostgreSQL 15
- **Frontend**: Next.js 14.2 + TypeScript + React 18 + Tailwind CSS
- **Autenticación**: JWT + Sistema RBAC (51 permisos, 6 roles predeterminados)
- **Containerización**: Docker & Docker Compose
- **Documentación API**: OpenAPI (Swagger)

---

## 📚 Documentación para Colaboradores

**¿Primera vez en el proyecto?** Lee estos documentos en orden:

1. **[📖 SETUP_COLABORADORES.md](./SETUP_COLABORADORES.md)** - Guía completa de instalación (10 minutos)
2. **[🛠️ COMANDOS_UTILES.md](./COMANDOS_UTILES.md)** - Comandos frecuentes para desarrollo

---

## ⚡ Quick Start (Resumen)

```bash
# 1. Clonar y configurar
git clone --single-branch --branch feature/IDK https://github.com/DarksouleaterXD/Sistema-De-Informacion-1-GYM.git
cd Sistema-De-Informacion-1-GYM
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# 2. Levantar servicios
docker compose up -d --build

# 3. Configurar base de datos
docker compose exec backend python manage.py migrate

# 4. Cargar datos de prueba (usuarios, roles, permisos, clientes, etc.)
docker compose exec backend python seeders/init_system.py

# 5. Verificar que todo funcione
docker compose exec backend python seeders/verify_system.py
```

**✅ Listo!** Accede a http://localhost:3000 con `admin` / `admin123`

---

## 🌐 URLs de Acceso

| Servicio               | URL                             | Credenciales                  |
| ---------------------- | ------------------------------- | ----------------------------- |
| **Frontend**           | http://localhost:3000           | admin / admin123              |
| **Backend API**        | http://localhost:8000/api/      | -                             |
| **Django Admin**       | http://localhost:8000/admin/    | admin / admin123              |
| **API Docs (Swagger)** | http://localhost:8000/api/docs/ | -                             |
| **pgAdmin**            | http://localhost:5050           | admin@gym-spartan.com / admin |
| **MailHog**            | http://localhost:8025           | -                             |

---

## 🏗️ Estructura del Proyecto

```
Sistema-De-Informacion-1-GYM/
├── backend/                 # Django REST Framework
│   ├── apps/               # Aplicaciones Django
│   │   ├── audit/          # Auditoría (bitácora de acciones)
│   │   ├── clients/        # Gestión de clientes
│   │   ├── core/           # Lógica central, permisos, middleware
│   │   ├── membresias/     # Membresías y planes
│   │   ├── promociones/    # Promociones y descuentos
│   │   ├── roles/          # Sistema RBAC (roles y permisos)
│   │   └── users/          # Gestión de usuarios
│   ├── config/             # Configuración Django
│   ├── seeders/            # Scripts de datos de prueba
│   └── requirements.txt    # Dependencias Python
│
├── frontend/               # Next.js + TypeScript
│   ├── app/               # App Router
│   │   ├── dashboard/     # Páginas del dashboard
│   │   ├── login/         # Autenticación
│   │   └── layout.tsx     # Layout principal
│   ├── components/        # Componentes React
│   │   ├── auth/          # ProtectedRoute, permisos
│   │   ├── layout/        # Navbar, Sidebar, Dashboard
│   │   └── ui/            # Componentes reutilizables
│   ├── lib/               # Utilidades
│   │   ├── contexts/      # Context API (AuthContext)
│   │   ├── services/      # Servicios de API
│   │   ├── types/         # Tipos TypeScript
│   │   └── utils/         # Helpers
│   └── package.json       # Dependencias Node
│
├── docker-compose.yml      # Orquestación de servicios
├── SETUP_COLABORADORES.md  # Guía de instalación detallada
└── COMANDOS_UTILES.md      # Comandos frecuentes
```

---

## 🔐 Sistema de Permisos (RBAC)

El sistema incluye **51 permisos** organizados en 9 módulos:

### Módulos de Permisos

- **Dashboard** (1 permiso): `dashboard.view`
- **Clientes** (5 permisos): view, create, edit, delete, export
- **Usuarios** (5 permisos): view, create, edit, delete, manage_permissions
- **Roles** (6 permisos): view, create, edit, delete, assign_to_user, assign_permissions
- **Membresías** (7 permisos): view, create, edit, delete, suspend, activate, renew
- **Inscripciones** (5 permisos): view, create, edit, delete, export
- **Planes** (5 permisos): view, create, edit, delete, toggle_active
- **Promociones** (7 permisos): view, create, edit, delete, activate, deactivate, assign
- **Auditoría** (3 permisos): view, export, delete_old

### Roles Predeterminados

| Rol                  | Permisos   | Descripción                               |
| -------------------- | ---------- | ----------------------------------------- |
| **Administrador**    | 51 (todos) | Acceso completo al sistema                |
| **Gerente**          | 36         | Gestión diaria sin eliminaciones críticas |
| **Administrativo**   | 25         | Operaciones administrativas básicas       |
| **Coach/Entrenador** | 13         | Solo lectura de clientes y membresías     |
| **Recepcionista**    | 10         | Gestión de inscripciones y clientes       |

---

## 📦 Comandos Útiles

### Desarrollo Diario

```bash
# Ver logs en tiempo real
docker compose logs -f backend
docker compose logs -f frontend

# Reiniciar servicios
docker compose restart backend
docker compose restart frontend

# Acceder a shell de Django
docker compose exec backend python manage.py shell

# Crear migraciones
docker compose exec backend python manage.py makemigrations

# Aplicar migraciones
docker compose exec backend python manage.py migrate
```

### Verificación y Testing

```bash
# Verificar sistema completo
docker compose exec backend python seeders/verify_system.py

# Verificar RBAC (roles y permisos)
docker compose exec backend python seeders/verify_rbac.py

# Ejecutar tests
docker compose exec backend python manage.py test
```

### Reset Completo

```bash
# ⚠️ ESTO BORRA TODOS LOS DATOS
docker compose down -v
docker compose up -d --build
docker compose exec backend python manage.py migrate
docker compose exec backend python seeders/init_system.py
```

**📖 Ver más comandos en [COMANDOS_UTILES.md](./COMANDOS_UTILES.md)**

---

## 🎯 Funcionalidades

### Gestión de Clientes

- ✅ CRUD completo de clientes
- ✅ Filtros y búsqueda avanzada
- ✅ Exportación a Excel/CSV
- ✅ Historial de actividad

### Gestión de Membresías

- ✅ Múltiples planes de membresía
- ✅ Estados: activo, inactivo, vencido, suspendido
- ✅ Cálculo automático de fechas
- ✅ Asignación de promociones

### Sistema de Promociones

- ✅ Descuentos por porcentaje o monto fijo
- ✅ Fecha de inicio y fin
- ✅ Estados: activa, inactiva, vencida
- ✅ Asignación a membresías

### Usuarios y Roles

- ✅ Sistema RBAC completo (51 permisos)
- ✅ 6 roles predeterminados personalizables
- ✅ Asignación dinámica de permisos
- ✅ Interfaz de gestión intuitiva

### Auditoría y Bitácora

- ✅ Registro automático de todas las acciones
- ✅ Información de IP y User-Agent
- ✅ Niveles: INFO, WARNING, ERROR, CRITICAL
- ✅ Búsqueda y filtros avanzados

---

## 🔧 Configuración de Variables de Entorno

### Backend (`backend/.env`)

```bash
# Django
SECRET_KEY=tu-clave-secreta-generada
DEBUG=True  # False en producción

# Base de Datos (valores por defecto para Docker)
DATABASE_ENGINE=postgresql
DATABASE_NAME=spartan_db
DATABASE_USER=spartan_user
DATABASE_PASSWORD=spartan_pass
DATABASE_HOST=db
DATABASE_PORT=5432

# JWT
JWT_SECRET_KEY=tu-jwt-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS (ajustar para producción)
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Frontend (`frontend/.env.local`)

```bash
# API URL
# Local: http://localhost:8000
# Azure con Nginx: /api
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🚨 Troubleshooting

### ❌ "Port already in use"

```bash
docker compose down
# Cambiar puerto en docker-compose.yml o matar proceso
```

### ❌ "Database connection error"

```bash
# Esperar a que PostgreSQL termine de iniciar (30 segundos)
docker compose logs db
docker compose ps
```

### ❌ Frontend muestra error 500

```bash
# Verificar variables de entorno
cat frontend/.env.local
# Debe contener: NEXT_PUBLIC_API_URL=http://localhost:8000

# Verificar que backend esté corriendo
curl http://localhost:8000/api/users/me/
```

### ❌ No aparecen datos de prueba

```bash
docker compose exec backend python seeders/init_system.py
```

**📖 Ver más soluciones en [SETUP_COLABORADORES.md](./SETUP_COLABORADORES.md)**

---

## 📊 API REST

### Endpoints Principales

```
POST   /api/auth/login/                    # Login (obtener JWT)
POST   /api/auth/logout/                   # Logout
GET    /api/users/me/                      # Usuario actual

GET    /api/clients/                       # Listar clientes
POST   /api/clients/                       # Crear cliente
GET    /api/clients/{id}/                  # Detalle cliente
PUT    /api/clients/{id}/                  # Actualizar cliente
DELETE /api/clients/{id}/                  # Eliminar cliente

GET    /api/membresias/                    # Listar membresías
POST   /api/membresias/                    # Crear membresía
GET    /api/membresias/stats/              # Estadísticas
GET    /api/planes-membresia/              # Planes disponibles

GET    /api/promociones/                   # Listar promociones
POST   /api/promociones/                   # Crear promoción

GET    /api/roles/                         # Listar roles
POST   /api/roles/                         # Crear rol
GET    /api/permissions/                   # Listar permisos

GET    /api/audit/logs/                    # Bitácora de auditoría
```

**📖 Documentación completa:** http://localhost:8000/api/docs/

---

## 🧪 Testing

```bash
# Backend
docker compose exec backend python manage.py test

# Tests de una app específica
docker compose exec backend python manage.py test apps.clients
docker compose exec backend python manage.py test apps.roles

# Frontend
docker compose exec frontend npm test
```

---

## 🤝 Contribuir

1. Fork el repositorio
2. Crea tu rama: `git checkout -b feature/nueva-funcionalidad`
3. Haz commits descriptivos: `git commit -m "feat: agregar funcionalidad X"`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Abre un Pull Request

### Convención de Commits

- `feat:` Nueva funcionalidad
- `fix:` Corrección de bug
- `docs:` Cambios en documentación
- `style:` Formateo, punto y coma faltante, etc.
- `refactor:` Refactorización de código
- `test:` Agregar tests
- `chore:` Actualizar dependencias, configuración, etc.

---

## 📄 Licencia

Este proyecto es privado y pertenece a Gym Spartan.

---

## 📞 Contacto y Soporte

- **Repositorio**: https://github.com/DarksouleaterXD/Sistema-De-Informacion-1-GYM
- **Branch activa**: feature/IDK
- **Documentación**: Ver carpeta `/docs` y archivos `.md` en la raíz

---

## ✅ Checklist para Nuevos Colaboradores

Antes de empezar a desarrollar:

- [ ] Docker Desktop instalado y corriendo
- [ ] Repositorio clonado (branch `feature/IDK`)
- [ ] Variables de entorno configuradas (`.env` y `.env.local`)
- [ ] Servicios levantados (`docker compose up -d`)
- [ ] Migraciones aplicadas (`python manage.py migrate`)
- [ ] Datos de prueba cargados (`python seeders/init_system.py`)
- [ ] Sistema verificado (`python seeders/verify_system.py`)
- [ ] Puedes hacer login en http://localhost:3000
- [ ] Leíste [SETUP_COLABORADORES.md](./SETUP_COLABORADORES.md)
- [ ] Leíste [COMANDOS_UTILES.md](./COMANDOS_UTILES.md)

**Si todos los items están ✅, ¡estás listo para desarrollar!** 🎉

---

**Última actualización:** Noviembre 2024  
**Versión:** 1.0.0
