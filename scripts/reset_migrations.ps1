# Script para resetear las migraciones en PowerShell
# Ejecutar desde la raíz del proyecto: .\scripts\reset_migrations.ps1

Write-Host "🔄 RESETEO DE MIGRACIONES Y BASE DE DATOS" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Confirmar acción
$confirmation = Read-Host "⚠️  Esto eliminará la base de datos y las migraciones. ¿Continuar? (s/n)"
if ($confirmation -ne 's') {
    Write-Host "❌ Operación cancelada" -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "📦 Paso 1: Creando backup de la base de datos..." -ForegroundColor Yellow
if (Test-Path "backend\db.sqlite3") {
    Copy-Item "backend\db.sqlite3" "backend\db.sqlite3.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Write-Host "✅ Backup creado exitosamente" -ForegroundColor Green
}

Write-Host ""
Write-Host "🗑️  Paso 2: Eliminando base de datos actual..." -ForegroundColor Yellow
if (Test-Path "backend\db.sqlite3") {
    Remove-Item "backend\db.sqlite3" -Force
    Write-Host "✅ Base de datos eliminada" -ForegroundColor Green
}

Write-Host ""
Write-Host "🗑️  Paso 3: Eliminando archivos de migraciones..." -ForegroundColor Yellow

$apps = @("clients", "membresias", "users", "roles", "promociones", "audit", "core")

foreach ($app in $apps) {
    $migrationsPath = "backend\apps\$app\migrations"
    if (Test-Path $migrationsPath) {
        # Eliminar archivos de migración numerados (0*.py)
        Get-ChildItem -Path $migrationsPath -Filter "0*.py" | Remove-Item -Force
        Write-Host "  ✅ Migraciones de $app eliminadas" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "📝 Paso 4: Creando nuevas migraciones..." -ForegroundColor Yellow
Set-Location backend
python manage.py makemigrations
Write-Host "✅ Migraciones creadas" -ForegroundColor Green

Write-Host ""
Write-Host "🚀 Paso 5: Aplicando migraciones..." -ForegroundColor Yellow
python manage.py migrate
Write-Host "✅ Migraciones aplicadas" -ForegroundColor Green

Write-Host ""
Write-Host "👤 Paso 6: ¿Desea crear un superusuario? (s/n)" -ForegroundColor Yellow
$createSuperuser = Read-Host
if ($createSuperuser -eq 's') {
    python manage.py createsuperuser
}

Write-Host ""
Write-Host "🎉 ¡Reseteo completado exitosamente!" -ForegroundColor Green
Write-Host ""
Write-Host "Próximos pasos:" -ForegroundColor Cyan
Write-Host "1. Ejecutar seeders si desea datos de prueba: python seeders/run_all_seeders.py"
Write-Host "2. Iniciar el servidor: python manage.py runserver"
Write-Host ""

Set-Location ..
