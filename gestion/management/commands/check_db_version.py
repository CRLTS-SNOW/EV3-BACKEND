# gestion/management/commands/check_db_version.py

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Verifica la versión de la base de datos MySQL'

    def handle(self, *args, **options):
        try:
            with connection.cursor() as cursor:
                # Ejecutar query para obtener la versión
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()[0]
                
                self.stdout.write(self.style.SUCCESS(f'✓ Versión de MySQL: {version}'))
                
                # También obtener información adicional
                cursor.execute("SELECT @@version_comment")
                version_comment = cursor.fetchone()[0]
                
                self.stdout.write(self.style.SUCCESS(f'✓ Comentario de versión: {version_comment}'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error al conectar con la base de datos: {e}'))
            self.stdout.write(self.style.WARNING('Asegúrate de que DATABASE_URL esté configurado correctamente'))

