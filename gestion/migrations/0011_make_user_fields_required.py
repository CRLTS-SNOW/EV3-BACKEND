# Generated migration to make user fields required

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0010_update_product_supplier_fields'),
    ]

    operations = [
        # Primero establecer valores por defecto para campos null
        migrations.RunSQL(
            "UPDATE gestion_userprofile SET nombres = '' WHERE nombres IS NULL;",
            reverse_sql="UPDATE gestion_userprofile SET nombres = NULL WHERE nombres = '';"
        ),
        migrations.RunSQL(
            "UPDATE gestion_userprofile SET apellidos = '' WHERE apellidos IS NULL;",
            reverse_sql="UPDATE gestion_userprofile SET apellidos = NULL WHERE apellidos = '';"
        ),
        # Luego hacer los campos requeridos
        migrations.AlterField(
            model_name='userprofile',
            name='nombres',
            field=models.CharField(help_text='Nombres del usuario (requerido)', max_length=100),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='apellidos',
            field=models.CharField(help_text='Apellidos del usuario (requerido)', max_length=100),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='role',
            field=models.CharField(choices=[('admin', 'Administrador'), ('bodega', 'Operador de Bodega'), ('ventas', 'Operador de Ventas'), ('auditor', 'Auditor'), ('operador', 'Operador')], help_text='Rol del usuario en el sistema (requerido)', max_length=20),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='estado',
            field=models.CharField(choices=[('ACTIVO', 'Activo'), ('BLOQUEADO', 'Bloqueado'), ('INACTIVO', 'Inactivo')], default='ACTIVO', help_text='Estado del usuario (requerido, default: ACTIVO)', max_length=20),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='mfa_habilitado',
            field=models.BooleanField(default=False, help_text='Multi-factor authentication habilitado (requerido, default: False)'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='ultimo_acceso',
            field=models.DateTimeField(blank=True, editable=False, help_text='Última vez que el usuario accedió al sistema (solo lectura)', null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='sesiones_activas',
            field=models.IntegerField(default=0, editable=False, help_text='Número de sesiones activas (solo lectura)'),
        ),
    ]

