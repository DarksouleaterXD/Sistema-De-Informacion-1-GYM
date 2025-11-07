# 📘 Guía Rápida: Trabajar con Seeders

## 🎯 Propósito

Este documento proporciona instrucciones claras sobre cómo ejecutar los seeders después de hacer pull de cambios del repositorio.

---

## ⚡ Comando Rápido

Para ejecutar todos los seeders y configurar el sistema completo:

```bash
docker exec -it spartan_backend python -c "import sys; sys.path.append('/app'); from seeders.init_system import main; main()"
```

---

## 📋 ¿Cuándo ejecutar los seeders?

Ejecuta los seeders en las siguientes situaciones:

1. ✅ **Después de hacer pull** de cambios de un colaborador
2. ✅ **Después de resetear** la base de datos
3. ✅ **Al configurar el proyecto** por primera vez
4. ✅ **Cuando los roles o permisos** cambien en el código
5. ✅ **Si notas que faltan** usuarios de prueba o datos iniciales

---

## 🔍 Verificar que todo está OK

Después de ejecutar los seeders, deberías ver este mensaje:

```
🎉 ¡SISTEMA INICIALIZADO COMPLETAMENTE!

📝 Credenciales de acceso:
   URL: http://localhost:3000
   Username: admin
   Password: admin123
```

Y el resumen debe mostrar:

```
✅ Verificar Base de Datos
✅ Ejecutar Migraciones
✅ Crear Superusuario
✅ Configurar RBAC
✅ Asignar Rol Admin
✅ Cargar Datos
✅ Verificar Sistema

Exitosos: 7/7
```

---

## 👥 Usuarios Disponibles después de Seeders

### 1. Administrador (Acceso Total)

```
Email: admin@gym-spartan.com
Username: admin
Password: admin123
Permisos: 62 permisos (acceso completo)
```

### 2. Administrativo (Gestión Diaria)

```
Email: administrativo@gym-spartan.com
Username: administrativo1
Password: admin123
Permisos: 25 permisos (sin eliminar usuarios/roles)
```

### 3. Instructor 1 (Solo Lectura)

```
Email: instructor@gym-spartan.com
Username: instructor1
Password: instructor123
Permisos: 5 permisos (solo consulta)
```

### 4. Instructor 2 (Solo Lectura)

```
Email: instructor2@gym-spartan.com
Username: instructor2
Password: instructor123
Permisos: 5 permisos (solo consulta)
```

---

## 🛠️ Comandos Útiles

### Ver usuarios en la BD:

```bash
docker exec -it spartan_backend python manage.py shell -c "from apps.users.models import User; [print(f'{u.username} - {u.email}') for u in User.objects.all()]"
```

### Ver roles en la BD:

```bash
docker exec -it spartan_backend python manage.py shell -c "from apps.roles.models import Role; [print(f'{r.nombre}: {r.descripcion}') for r in Role.objects.all()]"
```

### Ver permisos totales:

```bash
docker exec -it spartan_backend python manage.py shell -c "from apps.roles.models import Permiso; print(f'Total permisos: {Permiso.objects.count()}')"
```

### Verificar sistema RBAC:

```bash
docker exec -it spartan_backend python -c "import sys; sys.path.append('/app'); from seeders.verify_system import verify_rbac_system; verify_rbac_system()"
```

---

## 🚨 Solución de Problemas

### Problema: "Role matching query does not exist"

**Causa:** Los roles no se crearon correctamente.

**Solución:**

```bash
# 1. Verificar que los contenedores estén corriendo
docker-compose ps

# 2. Ejecutar seeders nuevamente
docker exec -it spartan_backend python -c "import sys; sys.path.append('/app'); from seeders.init_system import main; main()"
```

### Problema: "ModuleNotFoundError: No module named 'seeders'"

**Causa:** Estás ejecutando el comando fuera del contenedor Docker.

**Solución:** Asegúrate de usar `docker exec -it spartan_backend` al inicio del comando.

### Problema: "Usuario ya existe"

**Causa:** Los seeders ya se ejecutaron antes.

**Solución:** Esto es normal. Los seeders son idempotentes (pueden ejecutarse múltiples veces sin problemas).

---

## 🔄 Resetear Base de Datos (Solo si es necesario)

Si necesitas empezar de cero:

### En Windows (PowerShell):

```powershell
# 1. Detener contenedores
docker-compose down

# 2. Eliminar volumen de base de datos
docker volume rm sistema-de-informacion-1-gym_postgres_data

# 3. Levantar contenedores
docker-compose up -d

# 4. Esperar que la BD esté lista (15 segundos)
Start-Sleep -Seconds 15

# 5. Ejecutar migraciones
docker exec -it spartan_backend python manage.py migrate

# 6. Ejecutar seeders
docker exec -it spartan_backend python -c "import sys; sys.path.append('/app'); from seeders.init_system import main; main()"
```

### En Linux/Mac (Bash):

```bash
# 1. Detener contenedores
docker-compose down

# 2. Eliminar volumen de base de datos
docker volume rm sistema-de-informacion-1-gym_postgres_data

# 3. Levantar contenedores
docker-compose up -d

# 4. Esperar que la BD esté lista (15 segundos)
sleep 15

# 5. Ejecutar migraciones
docker exec -it spartan_backend python manage.py migrate

# 6. Ejecutar seeders
docker exec -it spartan_backend python -c "import sys; sys.path.append('/app'); from seeders.init_system import main; main()"
```

---

## 📚 Archivos Importantes de Seeders

| Archivo                    | Descripción                                                 |
| -------------------------- | ----------------------------------------------------------- |
| `init_system.py`           | Script maestro que ejecuta todos los seeders en orden       |
| `setup_rbac.py`            | Configura el sistema RBAC (permisos y roles)                |
| `permissions_seeder.py`    | Crea los 62 permisos del sistema                            |
| `roles_default_seeder.py`  | Crea los 3 roles: Administrador, Administrativo, Instructor |
| `users_seeder.py`          | Crea usuarios de prueba                                     |
| `clients_seeder.py`        | Crea clientes de prueba                                     |
| `plan_membresia_seeder.py` | Crea planes de membresía                                    |
| `promocion_seeder.py`      | Crea promociones                                            |

---

## ✅ Checklist Post-Pull

Después de hacer pull de cambios, verifica:

- [ ] Contenedores corriendo: `docker-compose ps`
- [ ] Migraciones aplicadas: `docker exec -it spartan_backend python manage.py migrate`
- [ ] Seeders ejecutados: Ver comando rápido arriba
- [ ] Login funciona con: `admin@gym-spartan.com` / `admin123`
- [ ] Frontend accesible en: `http://localhost:3000`
- [ ] Backend accesible en: `http://localhost:8000`

---

## 🆘 Ayuda Adicional

Si encuentras problemas después de seguir esta guía:

1. Revisa el archivo `SEEDERS_FIX_REPORT.md` para más detalles técnicos
2. Verifica los logs del backend: `docker logs spartan_backend`
3. Consulta con el equipo en el canal de desarrollo

---

## 📞 Contacto

Si necesitas ayuda con los seeders:

- Crea un issue en GitHub
- Contacta al líder técnico del proyecto
- Revisa la documentación en `/docs`

---

**Última actualización:** 6 de Noviembre, 2025  
**Versión:** 1.0  
**Mantenido por:** Equipo de Desarrollo Spartan GYM
