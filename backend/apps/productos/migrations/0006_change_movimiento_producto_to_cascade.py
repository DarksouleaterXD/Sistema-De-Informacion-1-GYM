# Generated manually to change MovimientoInventario.producto from PROTECT to CASCADE

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0005_producto_fecha_vencimiento'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movimientoinventario',
            name='producto',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='movimientos',
                to='productos.producto',
                verbose_name='Producto'
            ),
        ),
    ]

