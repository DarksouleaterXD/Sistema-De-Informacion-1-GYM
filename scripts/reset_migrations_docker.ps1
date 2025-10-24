# Script para resetear las migraciones usando Docker
# Ejecutar desde la raiz del proyecto: .\scripts\reset_migrations_docker.ps1

Write-Host "RESETEO DE MIGRACIONES Y BASE DE DATOS (DOCKER)" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""

# Confirmar accion
$confirmation = Read-Host "Esto eliminara la base de datos y las migraciones. Continuar? (s/n)"
if ($confirmation -ne 's') {
    Write-Host "Operacion cancelada" -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "Verificando que los contenedores esten corriendo..." -ForegroundColor Yellow
docker-compose ps

Write-Host ""
Write-Host "Paso 1: Creando backup de la base de datos..." -ForegroundColor Yellow
if (Test-Path "backend\db.sqlite3") {
    Copy-Item "backend\db.sqlite3" "backend\db.sqlite3.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Write-Host "Backup creado exitosamente" -ForegroundColor Green
} else {
    Write-Host "No se encontro db.sqlite3 (probablemente usando PostgreSQL)" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Paso 2: Deteniendo contenedores..." -ForegroundColor Yellow
docker-compose down
Write-Host "Contenedores detenidos" -ForegroundColor Green

Write-Host ""
Write-Host "Paso 3: Eliminando volumen de base de datos..." -ForegroundColor Yellow
docker volume rm si1-spartan_postgres_data -f
Write-Host "Volumen eliminado" -ForegroundColor Green

Write-Host ""
Write-Host "Paso 4: Eliminando archivos de migraciones..." -ForegroundColor Yellow

$apps = @("clients", "membresias", "users", "roles", "promociones", "audit", "core")

foreach ($app in $apps) {
    $migrationsPath = "backend\apps\$app\migrations"
    if (Test-Path $migrationsPath) {
        # Eliminar archivos de migracion numerados (0*.py)
        Get-ChildItem -Path $migrationsPath -Filter "0*.py" | Remove-Item -Force
        Write-Host "  Migraciones de $app eliminadas" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Paso 5: Iniciando contenedores..." -ForegroundColor Yellow
docker-compose up -d
Write-Host "Contenedores iniciados" -ForegroundColor Green

Write-Host ""
Write-Host "Esperando a que la base de datos este lista..." -ForegroundColor Yellow
Start-Sleep -Seconds 10
Write-Host "Base de datos lista" -ForegroundColor Green

Write-Host ""
Write-Host "Paso 6: Creando nuevas migraciones..." -ForegroundColor Yellow
docker-compose exec backend python manage.py makemigrations
Write-Host "Migraciones creadas" -ForegroundColor Green

Write-Host ""
Write-Host "Paso 7: Aplicando migraciones..." -ForegroundColor Yellow
docker-compose exec backend python manage.py migrate
Write-Host "Migraciones aplicadas" -ForegroundColor Green

Write-Host ""
Write-Host "Paso 8: Desea crear un superusuario? (s/n)" -ForegroundColor Yellow
$createSuperuser = Read-Host
if ($createSuperuser -eq 's') {
    docker-compose exec backend python manage.py createsuperuser
}

Write-Host ""
Write-Host "Paso 9: Desea ejecutar los seeders? (s/n)" -ForegroundColor Yellow
$runSeeders = Read-Host
if ($runSeeders -eq 's') {
    Write-Host "Ejecutando seeders..." -ForegroundColor Yellow
    docker-compose exec backend python seeders/run_all_seeders.py
    Write-Host "Seeders ejecutados" -ForegroundColor Green
}

Write-Host ""
Write-Host "Reseteo completado exitosamente!" -ForegroundColor Green
Write-Host ""
Write-Host "Servicios disponibles:" -ForegroundColor Cyan
Write-Host "  Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "  Admin:    http://localhost:8000/admin" -ForegroundColor White
Write-Host "  PgAdmin:  http://localhost:5050" -ForegroundColor White
Write-Host "  MailHog:  http://localhost:8025" -ForegroundColor White
Write-Host ""
Write-Host "Ver logs: docker-compose logs -f backend" -ForegroundColor Yellow
Write-Host ""
