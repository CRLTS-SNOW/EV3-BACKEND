# Generated migration to make supplier fields required

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0007_alter_supplier_observaciones'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supplier',
            name='rut_nif',
            field=models.CharField(help_text='RUT/NIF del proveedor (único, requerido)', max_length=20, unique=True),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='razon_social',
            field=models.CharField(help_text='Razón social del proveedor (requerido)', max_length=255),
        ),
    ]

