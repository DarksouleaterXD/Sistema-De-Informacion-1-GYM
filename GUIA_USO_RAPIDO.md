# 🚀 GUÍA RÁPIDA DE USO - SISTEMA GYM SPARTAN

## 📋 Estado Actual del Sistema

**✅ Backend:** Completamente funcional con nuevos modelos  
**✅ Frontend:** Actualizado con nuevos campos y relaciones  
**✅ Base de Datos:** Poblada con datos de prueba  

---

## 🔑 Credenciales de Acceso

### Superusuario (Django Admin)
- **URL:** http://localhost:8000/admin
- **Email:** admin@gym-spartan.com
- **Password:** admin123

### Usuarios del Sistema (Frontend)

| Rol | Email | Password |
|-----|-------|----------|
| Gerente | gerente@gym-spartan.com | gerente123 |
| Recepcionista | recepcion@gym-spartan.com | recepcion123 |
| Entrenador | entrenador@gym-spartan.com | entrenador123 |

---

## 🌐 URLs del Sistema

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Frontend** | http://localhost:3000 | Aplicación Next.js |
| **Backend API** | http://localhost:8000/api | Django REST API |
| **Django Admin** | http://localhost:8000/admin | Panel de administración |
| **PgAdmin** | http://localhost:5050 | Gestión de PostgreSQL |
| **MailHog** | http://localhost:8025 | Testing de emails |

---

## 📊 Datos de Prueba Disponibles

### Clientes (5)
- Pedro Ramírez (CI: 12345678) - INTERMEDIO
- Ana Martínez (CI: 87654321) - PRINCIPIANTE
- Luis Flores (CI: 11223344) - AVANZADO
- Sofia Vargas (CI: 55667788) - INTERMEDIO
- Brandon Cusicanqui (CI: 123145) - PRINCIPIANTE

### Planes de Membresía (7)
| Plan | Duración | Precio |
|------|----------|--------|
| Diario | 1 día | Bs. 15 |
| Semanal | 7 días | Bs. 80 |
| Quincenal | 15 días | Bs. 140 |
| Mensual | 30 días | Bs. 250 |
| Trimestral | 90 días | Bs. 650 |
| Semestral | 180 días | Bs. 1,200 |
| Anual | 365 días | Bs. 2,200 |

### Promociones Activas (5)
- Promoción Año Nuevo: 15% descuento (1 mes)
- Promoción Verano: 20% descuento (3 meses)
- Black Friday Gym: 30% descuento (6 meses)
- Estudiantes: 10% descuento (1 mes)
- Referido: 25% descuento (1 mes)

---

## 🎯 Casos de Uso

### 1. Registrar un Nuevo Cliente

**Frontend:**
1. Ir a http://localhost:3000/dashboard/clients
2. Click en "Nuevo Cliente"
3. Llenar formulario con:
   - Nombre *
   - Apellido *
   - CI * (6-10 dígitos)
   - Teléfono (8 dígitos)
   - Email
   - **NUEVO:** Peso (kg) - Entre 20-300
   - **NUEVO:** Altura (m) - Entre 0.5-2.5
   - **NUEVO:** Experiencia - Principiante/Intermedio/Avanzado
4. Click en "Guardar"

**Django Admin:**
1. Ir a http://localhost:8000/admin
2. Login con admin@gym-spartan.com / admin123
3. Click en "Clientes" > "Agregar Cliente"
4. Llenar todos los campos
5. Guardar

### 2. Ver Datos de Clientes con Nuevos Campos

**Django Admin:**
```bash
# Acceder al shell
docker-compose exec backend python manage.py shell

# Ejecutar:
from apps.clients.models import Client

# Ver todos los clientes con nuevos campos
for cliente in Client.objects.all():
    print(f"{cliente.nombre_completo}")
    print(f"  - Peso: {cliente.peso} kg")
    print(f"  - Altura: {cliente.altura} m")
    print(f"  - Experiencia: {cliente.get_experiencia_display()}")
    print()
```

### 3. Crear una Membresía con Plan

**Django Admin:**
1. Ir a Membresías > Agregar Membresía
2. Seleccionar Cliente
3. **NUEVO:** Seleccionar Plan de Membresía (ej: Plan Mensual)
4. Seleccionar Estado (ACTIVO/INACTIVO/VENCIDO/SUSPENDIDO)
5. Fecha de inicio y fin
6. **NUEVO:** Seleccionar Promociones (opcional, multi-select)
7. Guardar

### 4. Aplicar Promoción a Membresía

**Django Admin:**
1. Ir a Membresía-Promoción > Agregar
2. Seleccionar Membresía
3. Seleccionar Promoción
4. El descuento se aplica automáticamente
5. Guardar

**API (Pendiente implementar endpoint):**
```bash
POST /api/membresias/{id}/aplicar-promocion/
{
  "promocion_id": 1
}
```

### 5. Ver Estadísticas de Membresías

**Django Admin:**
```bash
docker-compose exec backend python manage.py shell

from apps.membresias.models import Membresia, PlanMembresia
from django.db.models import Count

# Membresías por plan
planes = PlanMembresia.objects.annotate(total=Count('membresia'))
for plan in planes:
    print(f"{plan.nombre}: {plan.total} membresías")

# Membresías por estado
estados = Membresia.objects.values('estado').annotate(total=Count('id'))
for estado in estados:
    print(f"{estado['estado']}: {estado['total']}")
```

---

## 🔧 Comandos Útiles

### Reiniciar Servicios
```bash
# Reiniciar todos
docker-compose restart

# Reiniciar solo backend
docker-compose restart backend

# Reiniciar solo frontend
docker-compose restart frontend
```

### Ver Logs
```bash
# Todos los servicios
docker-compose logs -f

# Solo backend
docker-compose logs -f backend

# Solo frontend
docker-compose logs -f frontend
```

### Acceder al Shell de Django
```bash
docker-compose exec backend python manage.py shell
```

### Ejecutar Migraciones
```bash
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
```

### Repoblar Base de Datos
```bash
docker-compose exec backend python manage.py seed
```

### Crear Superusuario Manual
```bash
docker-compose exec backend python manage.py createsuperuser
```

---

## 🧪 Pruebas de API

### Obtener Token de Autenticación
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@gym-spartan.com",
    "password": "admin123"
  }'
```

### Listar Clientes
```bash
curl -X GET http://localhost:8000/api/clients/ \
  -H "Authorization: Bearer {TOKEN}"
```

### Crear Cliente con Nuevos Campos
```bash
curl -X POST http://localhost:8000/api/clients/ \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Juan",
    "apellido": "Perez",
    "ci": "9876543",
    "telefono": "12345678",
    "email": "juan@example.com",
    "peso": "75.5",
    "altura": "1.75",
    "experiencia": "INTERMEDIO"
  }'
```

### Listar Planes de Membresía
```bash
curl -X GET http://localhost:8000/api/planes-membresia/ \
  -H "Authorization: Bearer {TOKEN}"
```

### Listar Promociones
```bash
curl -X GET http://localhost:8000/api/promociones/ \
  -H "Authorization: Bearer {TOKEN}"
```

---

## 📝 Verificación de Funcionalidades

### ✅ Checklist de Pruebas

#### Backend:
- [x] Crear cliente con peso, altura, experiencia
- [x] Ver clientes en Django Admin
- [x] Crear plan de membresía
- [x] Ver planes de membresía
- [x] Crear promoción con nuevo modelo
- [x] Ver promociones
- [x] Crear membresía con plan asignado
- [x] Aplicar promociones a membresía (M2M)
- [x] Ver bitácora de actividades

#### Frontend:
- [x] Página de clientes con nuevos campos
- [x] Formulario de creación con validaciones
- [x] Tipos TypeScript actualizados
- [x] Servicios API actualizados
- [ ] Página de membresías con selector de plan (pendiente)
- [ ] Página de promociones actualizada (pendiente)
- [ ] Página de planes de membresía (pendiente)

---

## 🐛 Solución de Problemas

### El frontend no muestra cambios
```bash
# Limpiar cache de Next.js
docker-compose exec frontend rm -rf .next
docker-compose restart frontend
```

### Error en migraciones
```bash
# Resetear migraciones (¡CUIDADO! Borra datos)
.\scripts\reset_migrations_docker.ps1
```

### Ver errores del backend
```bash
docker-compose logs backend --tail=100
```

### Base de datos sin datos
```bash
docker-compose exec backend python manage.py seed
```

---

## 📚 Recursos Adicionales

### Documentación Generada:
1. `SEEDERS_COMPLETADOS.md` - Estado de los seeders
2. `FRONTEND_ACTUALIZADO.md` - Cambios en frontend
3. `GUIA_COMPLETA_MODELOS.md` - Modelos del backend
4. `RELACIONES_FUNCIONALES.md` - Relaciones entre modelos

### Diagramas:
- UML del sistema (proporcionado por el usuario)

---

## 🎉 Resumen del Estado Actual

### ✅ Completado:
1. Modelos actualizados según UML
2. Migraciones aplicadas
3. Base de datos poblada con seeders
4. Frontend actualizado con nuevos campos
5. Servicios TypeScript sincronizados
6. Validaciones de formularios

### ⏳ Pendiente (Próximos pasos):
1. Actualizar página de membresías en frontend
2. Crear página de planes de membresía
3. Actualizar página de promociones
4. Implementar endpoints para aplicar/remover promociones
5. Dashboard con estadísticas
6. Reportes de ingresos
7. Sistema de notificaciones

---

## 🚀 ¡Listo para Usar!

El sistema está completamente funcional. Puedes empezar a:
- Registrar clientes con sus características físicas
- Asignar planes de membresía
- Aplicar promociones
- Gestionar usuarios y roles
- Ver bitácora de actividades

**¡Éxito con tu proyecto Gym Spartan! 💪**
