"""
Comando de Django para validar la integridad de los datos creados por seeders
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.roles.models import Role, Permiso, UserRole, RolPermiso
from apps.clients.models import Client
from apps.instructores.models import Instructor
from apps.membresias.models import PlanMembresia
from apps.promociones.models import Promocion
from apps.disciplinas.models import Disciplina
from apps.clases.models import Salon, Clase

User = get_user_model()


class Command(BaseCommand):
    help = 'Valida que todos los seeders se hayan ejecutado correctamente'

    def handle(self, *args, **options):
        self.stdout.write("\n" + "="*70)
        self.stdout.write(self.style.SUCCESS("🔍 VALIDACIÓN DE INTEGRIDAD DE SEEDERS"))
        self.stdout.write("="*70 + "\n")
        
        errors = []
        warnings = []
        
        # 1. Validar Superusuario
        self.stdout.write("📌 Validando Superusuario...")
        superuser = User.objects.filter(email="admin@gym-spartan.com").first()
        if superuser and superuser.is_superuser:
            self.stdout.write(self.style.SUCCESS("   ✅ Superusuario existe y está activo"))
        else:
            errors.append("❌ Superusuario no encontrado o no tiene permisos de superusuario")
        
        # 2. Validar Permisos
        self.stdout.write("\n📌 Validando Permisos...")
        permisos_count = Permiso.objects.count()
        if permisos_count >= 67:
            self.stdout.write(self.style.SUCCESS(f"   ✅ {permisos_count} permisos encontrados"))
        else:
            errors.append(f"❌ Se esperaban 67 permisos, se encontraron {permisos_count}")
        
        # 3. Validar Roles
        self.stdout.write("\n📌 Validando Roles...")
        roles_esperados = ["Administrador", "Administrativo", "Instructor"]
        roles_existentes = Role.objects.filter(nombre__in=roles_esperados)
        
        if roles_existentes.count() == len(roles_esperados):
            self.stdout.write(self.style.SUCCESS(f"   ✅ {len(roles_esperados)} roles predeterminados creados"))
            
            # Validar permisos por rol
            admin_role = roles_existentes.filter(nombre="Administrador").first()
            if admin_role:
                admin_permisos = RolPermiso.objects.filter(rol=admin_role).count()
                if admin_permisos == 67:
                    self.stdout.write(self.style.SUCCESS(f"   ✅ Rol Administrador tiene {admin_permisos} permisos"))
                else:
                    warnings.append(f"⚠️  Rol Administrador tiene {admin_permisos} permisos (se esperaban 67)")
            
            admin_role = roles_existentes.filter(nombre="Administrativo").first()
            if admin_role:
                admin_permisos = RolPermiso.objects.filter(rol=admin_role).count()
                if admin_permisos >= 20:
                    self.stdout.write(self.style.SUCCESS(f"   ✅ Rol Administrativo tiene {admin_permisos} permisos"))
                else:
                    warnings.append(f"⚠️  Rol Administrativo tiene {admin_permisos} permisos (se esperaban ~25)")
            
            instructor_role = roles_existentes.filter(nombre="Instructor").first()
            if instructor_role:
                instructor_permisos = RolPermiso.objects.filter(rol=instructor_role).count()
                if instructor_permisos >= 5:
                    self.stdout.write(self.style.SUCCESS(f"   ✅ Rol Instructor tiene {instructor_permisos} permisos"))
                else:
                    warnings.append(f"⚠️  Rol Instructor tiene {instructor_permisos} permisos (se esperaban ~5)")
        else:
            errors.append(f"❌ Se esperaban {len(roles_esperados)} roles, se encontraron {roles_existentes.count()}")
        
        # 4. Validar Usuarios
        self.stdout.write("\n📌 Validando Usuarios de Prueba...")
        usuarios_esperados = [
            "admin@gym-spartan.com",
            "administrativo@gym-spartan.com",
            "instructor@gym-spartan.com"
        ]
        usuarios_count = User.objects.filter(email__in=usuarios_esperados).count()
        if usuarios_count == len(usuarios_esperados):
            self.stdout.write(self.style.SUCCESS(f"   ✅ {usuarios_count} usuarios de prueba creados"))
            
            # Validar asignación de roles
            for email in usuarios_esperados:
                user = User.objects.filter(email=email).first()
                if user:
                    roles_asignados = UserRole.objects.filter(usuario=user).count()
                    if roles_asignados > 0:
                        role_names = ", ".join([ur.rol.nombre for ur in UserRole.objects.filter(usuario=user)])
                        self.stdout.write(self.style.SUCCESS(f"   ✅ {email} tiene rol(es): {role_names}"))
                    else:
                        warnings.append(f"⚠️  {email} no tiene roles asignados")
        else:
            warnings.append(f"⚠️  Se esperaban {len(usuarios_esperados)} usuarios, se encontraron {usuarios_count}")
        
        # 5. Validar Instructores
        self.stdout.write("\n📌 Validando Instructores...")
        instructores_count = Instructor.objects.count()
        if instructores_count >= 5:
            self.stdout.write(self.style.SUCCESS(f"   ✅ {instructores_count} instructores creados"))
            
            # Validar que todos los instructores tengan usuario con rol Instructor
            instructores_sin_rol = 0
            for instructor in Instructor.objects.all():
                if not UserRole.objects.filter(usuario=instructor.usuario, rol__nombre="Instructor").exists():
                    instructores_sin_rol += 1
            
            if instructores_sin_rol == 0:
                self.stdout.write(self.style.SUCCESS(f"   ✅ Todos los instructores tienen el rol 'Instructor' asignado"))
            else:
                warnings.append(f"⚠️  {instructores_sin_rol} instructor(es) no tienen el rol 'Instructor' asignado")
        else:
            warnings.append(f"⚠️  Se esperaban al menos 5 instructores, se encontraron {instructores_count}")
        
        # 6. Validar Clientes
        self.stdout.write("\n📌 Validando Clientes...")
        clientes_count = Client.objects.count()
        if clientes_count >= 5:
            self.stdout.write(self.style.SUCCESS(f"   ✅ {clientes_count} clientes creados"))
        else:
            warnings.append(f"⚠️  Se esperaban al menos 5 clientes, se encontraron {clientes_count}")
        
        # 7. Validar Planes de Membresía
        self.stdout.write("\n📌 Validando Planes de Membresía...")
        planes_count = PlanMembresia.objects.count()
        if planes_count >= 7:
            self.stdout.write(self.style.SUCCESS(f"   ✅ {planes_count} planes de membresía creados"))
        else:
            warnings.append(f"⚠️  Se esperaban al menos 7 planes, se encontraron {planes_count}")
        
        # 8. Validar Promociones
        self.stdout.write("\n📌 Validando Promociones...")
        promociones_count = Promocion.objects.count()
        if promociones_count >= 5:
            self.stdout.write(self.style.SUCCESS(f"   ✅ {promociones_count} promociones creadas"))
        else:
            warnings.append(f"⚠️  Se esperaban al menos 5 promociones, se encontraron {promociones_count}")
        
        # 9. Validar Disciplinas
        self.stdout.write("\n📌 Validando Disciplinas...")
        disciplinas_count = Disciplina.objects.count()
        if disciplinas_count >= 10:
            self.stdout.write(self.style.SUCCESS(f"   ✅ {disciplinas_count} disciplinas creadas"))
        else:
            warnings.append(f"⚠️  Se esperaban al menos 10 disciplinas, se encontraron {disciplinas_count}")
        
        # 10. Validar Salones
        self.stdout.write("\n📌 Validando Salones...")
        salones_count = Salon.objects.count()
        if salones_count >= 5:
            self.stdout.write(self.style.SUCCESS(f"   ✅ {salones_count} salones creados"))
        else:
            warnings.append(f"⚠️  Se esperaban al menos 5 salones, se encontraron {salones_count}")
        
        # 11. Validar Clases
        self.stdout.write("\n📌 Validando Clases...")
        clases_count = Clase.objects.count()
        if clases_count >= 5:
            self.stdout.write(self.style.SUCCESS(f"   ✅ {clases_count} clases de prueba creadas"))
        else:
            warnings.append(f"⚠️  Se esperaban al menos 5 clases, se encontraron {clases_count}")
        
        # Resumen final
        self.stdout.write("\n" + "="*70)
        self.stdout.write(self.style.SUCCESS("📊 RESUMEN DE VALIDACIÓN"))
        self.stdout.write("="*70)
        
        if not errors and not warnings:
            self.stdout.write(self.style.SUCCESS("\n✅ ¡TODOS LOS SEEDERS ESTÁN CORRECTOS!"))
            self.stdout.write(self.style.SUCCESS("   No se encontraron errores ni advertencias.\n"))
        else:
            if errors:
                self.stdout.write(self.style.ERROR(f"\n❌ ERRORES CRÍTICOS: {len(errors)}"))
                for error in errors:
                    self.stdout.write(self.style.ERROR(f"   {error}"))
            
            if warnings:
                self.stdout.write(self.style.WARNING(f"\n⚠️  ADVERTENCIAS: {len(warnings)}"))
                for warning in warnings:
                    self.stdout.write(self.style.WARNING(f"   {warning}"))
            
            self.stdout.write("\n")
            if errors:
                self.stdout.write(self.style.ERROR("💡 Ejecuta: python manage.py seed"))
                self.stdout.write(self.style.ERROR("   para corregir los errores.\n"))
        
        self.stdout.write("="*70 + "\n")
