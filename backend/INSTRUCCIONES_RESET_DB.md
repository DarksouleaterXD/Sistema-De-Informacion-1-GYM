# 🔄 INSTRUCCIONES PARA RESETEAR LA BASE DE DATOS

## ⚠️ IMPORTANTE: Hacer backup primero

Antes de continuar, si tienes datos importantes:

```bash
# Opcional: hacer backup de la BD
cp db.sqlite3 db.sqlite3.backup
```

## Pasos para resetear migraciones

### 1. Eliminar la base de datos actual

```bash
rm db.sqlite3
```

### 2. Eliminar archivos de migración (excepto **init**.py)

```bash
# En PowerShell
Remove-Item backend\apps\clients\migrations\0*.py
Remove-Item backend\apps\membresias\migrations\0*.py
Remove-Item backend\apps\users\migrations\0*.py
Remove-Item backend\apps\roles\migrations\0*.py
Remove-Item backend\apps\promociones\migrations\0*.py
Remove-Item backend\apps\audit\migrations\0*.py
Remove-Item backend\apps\core\migrations\0*.py
```

### 3. Crear nuevas migraciones

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

### 4. Crear superusuario y datos de prueba

```bash
python manage.py createsuperuser
# O usar los seeders
python seeders/run_all_seeders.py
```

## ✅ Verificar que todo funcione

```bash
python manage.py runserver
```

## 📝 Notas

- Los nuevos modelos incluyen todos los campos del diagrama UML
- Las relaciones están correctamente configuradas
- Se mantiene la auditoría automática (bitácora)
