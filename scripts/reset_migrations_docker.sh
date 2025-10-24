#!/bin/bash
# Script para resetear las migraciones usando Docker (Linux/Mac)
# Ejecutar desde la raiz del proyecto: ./scripts/reset_migrations_docker.sh

echo -e "\033[0;36mRESETEO DE MIGRACIONES Y BASE DE DATOS (DOCKER)\033[0m"
echo -e "\033[0;36m====================================================\033[0m"
echo ""

# Confirmar accion
read -p "Esto eliminara la base de datos y las migraciones. Continuar? (s/n): " confirmation
if [ "$confirmation" != "s" ]; then
    echo -e "\033[0;31mOperacion cancelada\033[0m"
    exit 1
fi

echo ""
echo -e "\033[0;33mVerificando que los contenedores esten corriendo...\033[0m"
docker-compose ps

echo ""
echo -e "\033[0;33mPaso 1: Creando backup de la base de datos...\033[0m"
if [ -f "backend/db.sqlite3" ]; then
    backup_name="backend/db.sqlite3.backup_$(date +%Y%m%d_%H%M%S)"
    cp "backend/db.sqlite3" "$backup_name"
    echo -e "\033[0;32mBackup creado exitosamente: $backup_name\033[0m"
else
    echo -e "\033[0;36mNo se encontro db.sqlite3 (probablemente usando PostgreSQL)\033[0m"
fi

echo ""
echo -e "\033[0;33mPaso 2: Deteniendo contenedores...\033[0m"
docker-compose down
echo -e "\033[0;32mContenedores detenidos\033[0m"

echo ""
echo -e "\033[0;33mPaso 3: Eliminando volumen de base de datos...\033[0m"
docker volume rm si1-spartan_postgres_data -f 2>/dev/null || echo -e "\033[0;33mVolumen no existe o ya fue eliminado\033[0m"
echo -e "\033[0;32mVolumen eliminado\033[0m"

echo ""
echo -e "\033[0;33mPaso 4: Eliminando archivos de migraciones...\033[0m"

apps=("clients" "membresias" "users" "roles" "promociones" "audit" "core")

for app in "${apps[@]}"; do
    migrations_path="backend/apps/$app/migrations"
    if [ -d "$migrations_path" ]; then
        # Eliminar archivos de migracion numerados (0*.py)
        rm -f "$migrations_path"/0*.py
        echo -e "  \033[0;32mMigraciones de $app eliminadas\033[0m"
    fi
done

echo ""
echo -e "\033[0;33mPaso 5: Iniciando contenedores...\033[0m"
docker-compose up -d
echo -e "\033[0;32mContenedores iniciados\033[0m"

echo ""
echo -e "\033[0;33mEsperando a que la base de datos este lista...\033[0m"
sleep 10
echo -e "\033[0;32mBase de datos lista\033[0m"

echo ""
echo -e "\033[0;33mPaso 6: Creando nuevas migraciones...\033[0m"
docker-compose exec -T backend python manage.py makemigrations
echo -e "\033[0;32mMigraciones creadas\033[0m"

echo ""
echo -e "\033[0;33mPaso 7: Aplicando migraciones...\033[0m"
docker-compose exec -T backend python manage.py migrate
echo -e "\033[0;32mMigraciones aplicadas\033[0m"

echo ""
read -p "$(echo -e '\033[0;33mPaso 8: Desea crear un superusuario? (s/n): \033[0m')" create_superuser
if [ "$create_superuser" = "s" ]; then
    docker-compose exec backend python manage.py createsuperuser
fi

echo ""
read -p "$(echo -e '\033[0;33mPaso 9: Desea ejecutar los seeders? (s/n): \033[0m')" run_seeders
if [ "$run_seeders" = "s" ]; then
    echo -e "\033[0;33mEjecutando seeders...\033[0m"
    docker-compose exec -T backend python seeders/run_all_seeders.py
    echo -e "\033[0;32mSeeders ejecutados\033[0m"
fi

echo ""
echo -e "\033[0;32mReseteo completado exitosamente!\033[0m"
echo ""
echo -e "\033[0;36mServicios disponibles:\033[0m"
echo -e "  Backend:  http://localhost:8000"
echo -e "  Frontend: http://localhost:3000"
echo -e "  Admin:    http://localhost:8000/admin"
echo -e "  PgAdmin:  http://localhost:5050"
echo -e "  MailHog:  http://localhost:8025"
echo ""
echo -e "\033[0;33mVer logs: docker-compose logs -f backend\033[0m"
echo ""
