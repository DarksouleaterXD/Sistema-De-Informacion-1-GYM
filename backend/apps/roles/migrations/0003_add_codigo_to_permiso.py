# Generated manually
from django.db import migrations, models


def populate_codigo(apps, schema_editor):
    """
    Migración de datos: copiar 'nombre' a 'codigo' para registros existentes
    """
    Permiso = apps.get_model('roles', 'Permiso')
    for permiso in Permiso.objects.all():
        # Usar el nombre como código temporal
        permiso.codigo = permiso.nombre.lower().replace(' ', '_')
        permiso.save()


class Migration(migrations.Migration):

    dependencies = [
        ('roles', '0002_initial'),
    ]

    operations = [
        # Agregar campo codigo como nullable temporalmente
        migrations.AddField(
            model_name='permiso',
            name='codigo',
            field=models.CharField(max_length=100, null=True, verbose_name='Código', help_text='Código único del permiso (ej: client.view, user.create)'),
        ),
        # Poblar el campo con datos
        migrations.RunPython(populate_codigo, reverse_code=migrations.RunPython.noop),
        # Hacer el campo NOT NULL y UNIQUE
        migrations.AlterField(
            model_name='permiso',
            name='codigo',
            field=models.CharField(max_length=100, unique=True, verbose_name='Código', help_text='Código único del permiso (ej: client.view, user.create)'),
        ),
        # Cambiar ordering del Meta
        migrations.AlterModelOptions(
            name='permiso',
            options={'ordering': ['codigo'], 'verbose_name': 'Permiso', 'verbose_name_plural': 'Permisos'},
        ),
    ]
