# 🚀 COMANDOS PARA MIGRACIONES DE DJANGO

## 📝 Paso a Paso para Ejecutar Migraciones

### 1️⃣ Navegar al directorio del backend
```powershell
cd "d:\SI 1 Gym\Sistema-De-Informacion-1-GYM\backend"
```

### 2️⃣ Verificar la configuración (Opcional pero recomendado)
```powershell
python check_setup.py
```

### 3️⃣ Crear las migraciones
Este comando detecta cambios en los modelos y crea archivos de migración:
```powershell
python manage.py makemigrations
```

### 4️⃣ Aplicar las migraciones
Este comando ejecuta las migraciones y crea las tablas en la base de datos:
```powershell
python manage.py migrate
```

### 5️⃣ Crear un superusuario (Opcional)
Para acceder al admin de Django:
```powershell
python manage.py createsuperuser
```

### 6️⃣ Ejecutar el servidor
```powershell
python manage.py runserver
```

---

## 🔍 Comandos Útiles Adicionales

### Ver el estado de las migraciones
```powershell
python manage.py showmigrations
```

### Ver las migraciones de una app específica
```powershell
python manage.py showmigrations users
python manage.py showmigrations roles
python manage.py showmigrations clients
python manage.py showmigrations audit
```

### Ver el SQL que se ejecutará (sin aplicar cambios)
```powershell
python manage.py sqlmigrate users 0001
```

### Revertir una migración específica
```powershell
python manage.py migrate users 0001
```

### Revertir todas las migraciones de una app
```powershell
python manage.py migrate users zero
```

### Ejecutar migraciones de una app específica
```powershell
python manage.py migrate users
python manage.py migrate roles
python manage.py migrate clients
python manage.py migrate audit
```

---

## 🛠️ Comandos de Desarrollo

### Abrir shell de Django
```powershell
python manage.py shell
```

### Crear migraciones vacías (para datos personalizados)
```powershell
python manage.py makemigrations --empty users
```

### Ver todas las apps instaladas
```powershell
python manage.py diffsettings
```

### Verificar problemas en el proyecto
```powershell
python manage.py check
```

---

## ⚠️ Solución de Problemas

### Si hay errores de dependencias entre apps:
```powershell
# Hacer migraciones en orden
python manage.py makemigrations core
python manage.py makemigrations users
python manage.py makemigrations roles
python manage.py makemigrations clients
python manage.py makemigrations audit

# Aplicar en el mismo orden
python manage.py migrate core
python manage.py migrate users
python manage.py migrate roles
python manage.py migrate clients
python manage.py migrate audit
```

### Si la base de datos está vacía o corrupta:
```powershell
# Borrar db.sqlite3 y empezar de nuevo
Remove-Item db.sqlite3 -ErrorAction SilentlyContinue
python manage.py migrate
python manage.py createsuperuser
```

---

## 📊 Verificar que todo funciona

Después de las migraciones, verifica que:

1. **No hay errores en las migraciones**
   ```powershell
   python manage.py showmigrations
   ```

2. **Las tablas se crearon correctamente**
   ```powershell
   python manage.py dbshell
   .tables  # Para SQLite
   \dt      # Para PostgreSQL
   ```

3. **El servidor inicia sin problemas**
   ```powershell
   python manage.py runserver
   ```

4. **Puedes acceder al admin**
   - URL: http://localhost:8000/admin
   - Usuario y contraseña que creaste con `createsuperuser`

---

## 🎯 Secuencia Completa (Copy & Paste)

```powershell
# Navegar al backend
cd "d:\SI 1 Gym\Sistema-De-Informacion-1-GYM\backend"

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Iniciar servidor
python manage.py runserver
```

---

¡Listo! Ahora tu backend debería estar funcionando correctamente. 🚀
