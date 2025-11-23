# gestion/management/commands/seed_warehouses.py

from django.core.management.base import BaseCommand
from django.db import transaction
from ...models import Warehouse, Zone

class Command(BaseCommand):
    help = 'Crea diferentes bodegas y zonas para el proyecto'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('=== Creando bodegas y zonas ===')
        
        # Lista de bodegas con sus zonas
        warehouses_data = [
            {
                'name': 'Bodega Central',
                'address': 'Av. Principal 123, Santiago, Región Metropolitana',
                'zones': [
                    'Zona A - Refrigerados',
                    'Zona B - Secos',
                    'Zona C - Congelados',
                    'Zona D - Almacén General',
                    'Zona E - Productos Perecederos'
                ]
            },
            {
                'name': 'Bodega Norte',
                'address': 'Av. Industrial 456, Antofagasta, Región de Antofagasta',
                'zones': [
                    'Zona A - Almacén Principal',
                    'Zona B - Despacho',
                    'Zona C - Productos Fríos'
                ]
            },
            {
                'name': 'Bodega Sur',
                'address': 'Calle Los Almacenes 789, Concepción, Región del Bío Bío',
                'zones': [
                    'Zona A - Recepción',
                    'Zona B - Almacén',
                    'Zona C - Preparación de Pedidos',
                    'Zona D - Despacho'
                ]
            },
            {
                'name': 'Bodega Valparaíso',
                'address': 'Pasaje Los Puertos 321, Valparaíso, Región de Valparaíso',
                'zones': [
                    'Zona A - Almacén',
                    'Zona B - Despacho Rápido',
                    'Zona C - Productos Especiales'
                ]
            },
            {
                'name': 'Bodega Temuco',
                'address': 'Av. Los Almacenes 654, Temuco, Región de La Araucanía',
                'zones': [
                    'Zona A - Principal',
                    'Zona B - Secundaria',
                    'Zona C - Despacho'
                ]
            },
            {
                'name': 'Bodega Rancagua',
                'address': 'Calle Industrial 987, Rancagua, Región de O\'Higgins',
                'zones': [
                    'Zona A - Almacén',
                    'Zona B - Distribución'
                ]
            }
        ]
        
        created_count = 0
        zone_count = 0
        
        for warehouse_data in warehouses_data:
            # Verificar si la bodega ya existe
            warehouse, created = Warehouse.objects.get_or_create(
                name=warehouse_data['name'],
                defaults={
                    'address': warehouse_data['address'],
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'  OK: Creada bodega: {warehouse.name}')
            else:
                self.stdout.write(f'  -> Bodega ya existe: {warehouse.name}')
            
            # Crear zonas para esta bodega
            for zone_name in warehouse_data['zones']:
                zone, zone_created = Zone.objects.get_or_create(
                    warehouse=warehouse,
                    name=zone_name,
                    defaults={'is_active': True}
                )
                if zone_created:
                    zone_count += 1
                    self.stdout.write(f'    OK: Creada zona: {zone_name}')
        
        self.stdout.write(self.style.SUCCESS(
            f'\nProceso completado:'
            f'\n  - Bodegas creadas: {created_count}'
            f'\n  - Zonas creadas: {zone_count}'
            f'\n  - Total bodegas en sistema: {Warehouse.objects.count()}'
            f'\n  - Total zonas en sistema: {Zone.objects.count()}'
        ))

