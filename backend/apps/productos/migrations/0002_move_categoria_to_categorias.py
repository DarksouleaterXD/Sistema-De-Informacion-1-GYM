# Generated manually - Mover CategoriaProducto de productos a categorias
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0001_initial'),
        ('categorias', '0001_initial'),  # Depende de que categorias ya tenga el modelo registrado
    ]

    operations = [
        # Separar el estado de Django de la base de datos
        # La tabla física no cambia, solo actualizamos las referencias en Django
        migrations.SeparateDatabaseAndState(
            database_operations=[
                # No hacemos cambios en la BD, la tabla y la ForeignKey ya existen correctamente
            ],
            state_operations=[
                # Eliminar CategoriaProducto del estado de productos
                migrations.DeleteModel(
                    name='CategoriaProducto',
                ),
                # Actualizar la ForeignKey en Producto para que apunte a categorias.categoriaproducto
                migrations.AlterField(
                    model_name='producto',
                    name='categoria',
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='productos',
                        to='categorias.categoriaproducto',
                        verbose_name='Categoría'
                    ),
                ),
            ],
        ),
    ]

