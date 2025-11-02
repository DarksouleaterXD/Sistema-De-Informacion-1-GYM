# 📝 Changelog - Sistema Gym Spartan

Todos los cambios notables del proyecto serán documentados en este archivo.

---

## [1.0.0] - 2024-11-02

### ✨ Funcionalidades Completas

#### Backend

- ✅ Sistema RBAC completo con 51 permisos granulares
- ✅ 6 roles predeterminados (Administrador, Gerente, Administrativo, Coach, Recepcionista)
- ✅ Gestión completa de Clientes (CRUD + búsqueda + paginación)
- ✅ Gestión de Membresías con estados (activo, inactivo, vencido, suspendido)
- ✅ Sistema de Promociones con descuentos
- ✅ Planes de Membresía personalizables
- ✅ Auditoría completa (bitácora de todas las acciones con IP y User-Agent)
- ✅ Autenticación JWT con refresh tokens
- ✅ Documentación API automática (Swagger/OpenAPI)
- ✅ Middleware de auditoría automático

#### Frontend

- ✅ Dashboard con estadísticas en tiempo real
- ✅ Gestión de Clientes con interfaz intuitiva
- ✅ Gestión de Membresías con asignación de promociones
- ✅ Gestión de Roles y Permisos con UI drag-and-drop
- ✅ Gestión de Usuarios con asignación de roles
- ✅ Bitácora de auditoría con filtros avanzados
- ✅ Sistema de autenticación con protección de rutas
- ✅ Componentes reutilizables (ProtectedRoute, Can, Cannot)
- ✅ Diseño responsive con Tailwind CSS

### 🔧 Mejoras Técnicas

#### Backend

- ✅ Respuestas paginadas en todos los endpoints de lista
- ✅ Manejo correcto de respuestas paginadas: `{count, next, previous, results}`
- ✅ Serializers optimizados con campos calculados
- ✅ Permisos granulares por endpoint
- ✅ Middleware de auditoría no invasivo
- ✅ Migraciones de base de datos organizadas
- ✅ Sistema de seeders modular y reutilizable

#### Frontend

- ✅ Validación defensiva de arrays en todas las vistas
- ✅ Manejo robusto de errores de API
- ✅ TypeScript estricto para mayor seguridad
- ✅ Context API para estado global (AuthContext)
- ✅ Servicios HTTP centralizados con interceptors
- ✅ Hot reload para desarrollo rápido

### 🐛 Correcciones

#### Roles y Permisos

- ✅ **FIXED**: Roles no aparecían en lista (respuesta paginada del backend)
- ✅ **FIXED**: Permisos no cargaban (endpoint incorrecto `/api/permisos/` → `/api/permissions/`)
- ✅ **FIXED**: Crash "permisos.map is not a function" (validación de arrays)
- ✅ **FIXED**: Backend bloqueaba acceso por permiso `HasRoleSuperUser` → cambio a `HasPermission`
- ✅ **FIXED**: Serializer de roles no aceptaba `permisos_ids` para asignación masiva

#### API y Servicios

- ✅ **FIXED**: Frontend no manejaba respuestas paginadas del backend
- ✅ **FIXED**: Service `getAll()` esperaba array pero recibía objeto con `results`
- ✅ **FIXED**: Service `getAllPermisos()` igual que anterior

#### Membresías

- ✅ **FIXED**: Error 400 al crear membresía (estado 'ACTIVO' vs 'activo')
- ✅ **FIXED**: Sincronización de estados backend/frontend (minúsculas vs MAYÚSCULAS)

### 📚 Documentación

- ✅ **NUEVO**: `SETUP_COLABORADORES.md` - Guía completa para nuevos colaboradores
- ✅ **NUEVO**: `COMANDOS_UTILES.md` - Referencia rápida de comandos frecuentes
- ✅ **NUEVO**: `README.md` actualizado y limpio con estructura clara
- ✅ **NUEVO**: Script `verify_system.py` para verificación automática
- ✅ **NUEVO**: Script `init_system.py` mejorado con output detallado
- ✅ **NUEVO**: Comando Django `python manage.py verify_system`

### 🛠️ Scripts y Herramientas

#### Seeders

- ✅ `init_system.py` - Inicialización completa del sistema
- ✅ `permissions_seeder.py` - Crea 51 permisos
- ✅ `roles_default_seeder.py` - Crea 6 roles con permisos asignados
- ✅ `users_seeder.py` - Crea usuarios de prueba
- ✅ `clients_seeder.py` - Crea clientes de ejemplo
- ✅ `plan_membresia_seeder.py` - Crea planes de membresía
- ✅ `promocion_seeder.py` - Crea promociones

#### Verificación

- ✅ `verify_system.py` - Verifica estado completo del sistema
- ✅ `verify_rbac.py` - Verifica roles y permisos
- ✅ `test_api_me.py` - Prueba endpoint de usuario actual

### 📦 Dependencias

#### Backend

- Django 5.0
- Django REST Framework 3.14
- PostgreSQL 15
- djangorestframework-simplejwt
- drf-spectacular (OpenAPI)
- django-cors-headers

#### Frontend

- Next.js 14.2.33
- React 18
- TypeScript 5
- Tailwind CSS 3
- lucide-react (iconos)

### 🎯 Datos de Prueba Incluidos

- ✅ 1 Superusuario (admin)
- ✅ 3 Usuarios de prueba (gerente, recepcionista, coach)
- ✅ 6 Clientes de ejemplo
- ✅ 7 Planes de membresía
- ✅ 5 Promociones
- ✅ 51 Permisos del sistema
- ✅ 6 Roles con permisos asignados

### 🔐 Credenciales por Defecto

```
Usuario Administrador:
  Username: admin
  Password: admin123
  Email: admin@gym-spartan.com

Gerente:
  Username: gerente
  Password: gerente123

Recepcionista:
  Username: recepcionista
  Password: recep123
```

### 🐳 Docker

- ✅ PostgreSQL 15 con health checks
- ✅ Backend Django con auto-reload
- ✅ Frontend Next.js con hot reload
- ✅ MailHog para testing de emails
- ✅ pgAdmin para gestión de BD
- ✅ Volúmenes persistentes para datos

### 📊 Estadísticas del Proyecto

- **Líneas de código Backend**: ~15,000
- **Líneas de código Frontend**: ~8,000
- **Modelos Django**: 12
- **Endpoints API**: 35+
- **Permisos**: 51
- **Roles predeterminados**: 6
- **Páginas Frontend**: 8
- **Componentes reutilizables**: 20+

---

## [0.9.0] - 2024-10-24

### Versión Inicial

- Estructura básica del proyecto
- Modelos de datos definidos
- API REST inicial
- Frontend básico

---

## Próximas Funcionalidades

### v1.1.0 (Planificado)

- [ ] Gestión de Inscripciones completa
- [ ] Reportes y estadísticas avanzadas
- [ ] Exportación masiva a Excel/PDF
- [ ] Dashboard de coach con rutinas
- [ ] Sistema de notificaciones push
- [ ] Chat interno entre usuarios
- [ ] Calendario de clases/entrenamientos

### v1.2.0 (Planificado)

- [ ] App móvil React Native
- [ ] Pagos online integrados
- [ ] Sistema de facturación
- [ ] Integración con pasarelas de pago
- [ ] QR para check-in
- [ ] Biometría (opcional)

### v2.0.0 (Futuro)

- [ ] Microservicios
- [ ] GraphQL API
- [ ] AI para recomendaciones de entrenamiento
- [ ] Analytics avanzado con ML
- [ ] Multi-gimnasio (franquicias)

---

## Convenciones de Versionado

Este proyecto sigue [Semantic Versioning](https://semver.org/):

- **MAJOR**: Cambios incompatibles en la API
- **MINOR**: Nuevas funcionalidades compatibles
- **PATCH**: Correcciones de bugs

---

**Última actualización:** 2024-11-02  
**Versión actual:** 1.0.0  
**Branch activa:** feature/IDK
