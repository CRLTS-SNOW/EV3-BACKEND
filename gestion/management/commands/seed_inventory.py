# gestion/management/commands/seed_inventory.py

import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Sum
from gestion.models import Product, Zone, Inventory

class Command(BaseCommand):
    help = 'Rellena el inventario con datos de prueba para productos y zonas existentes'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('=== Rellenando inventario con datos de prueba ===')
        
        # Obtener productos y zonas activos
        products = Product.objects.filter(is_active=True)
        zones = Zone.objects.filter(is_active=True)
        
        if not products.exists():
            self.stdout.write(self.style.ERROR('ERROR: No hay productos activos en la base de datos.'))
            self.stdout.write('  Ejecuta primero: python manage.py seed_data')
            return
        
        if not zones.exists():
            self.stdout.write(self.style.ERROR('ERROR: No hay zonas activas en la base de datos.'))
            self.stdout.write('  Ejecuta primero: python manage.py seed_data')
            return
        
        # Limpiar inventario existente (opcional, comentar si quieres mantener el existente)
        existing_count = Inventory.objects.count()
        if existing_count > 0:
            self.stdout.write(f'\nLimpiando {existing_count} registros de inventario existentes...')
            Inventory.objects.all().delete()
        
        self.stdout.write(f'\nProductos disponibles: {products.count()}')
        self.stdout.write(f'Zonas disponibles: {zones.count()}')
        
        # Crear inventario
        self.stdout.write('\nCreando registros de inventario...')
        inventory_count = 0
        zones_list = list(zones)
        
        for product in products:
            # Asignar stock a 2-4 zonas aleatorias (o todas si hay menos de 4)
            num_zones = min(random.randint(2, 4), len(zones_list))
            selected_zones = random.sample(zones_list, num_zones)
            
            for zone in selected_zones:
                # Cantidad aleatoria entre 20 y 500 unidades
                quantity = random.randint(20, 500)
                
                Inventory.objects.create(
                    product=product,
                    zone=zone,
                    quantity=quantity
                )
                inventory_count += 1
                self.stdout.write(f'  ✓ {product.name[:40]:<40} en {zone.name[:30]:<30} - Stock: {quantity}')
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Creados {inventory_count} registros de inventario'))
        
        # Resumen por zona
        self.stdout.write('\n=== Resumen por zona ===')
        for zone in zones_list:
            total_stock = Inventory.objects.filter(zone=zone).aggregate(
                total=Sum('quantity')
            )['total'] or 0
            products_count = Inventory.objects.filter(zone=zone).count()
            self.stdout.write(f'  {zone.name}: {products_count} productos, {total_stock} unidades totales')
        
        # Resumen por producto
        self.stdout.write('\n=== Top 10 productos con más stock ===')
        top_products = Inventory.objects.values('product__name').annotate(
            total_stock=Sum('quantity')
        ).order_by('-total_stock')[:10]
        
        for idx, item in enumerate(top_products, 1):
            self.stdout.write(f'  {idx}. {item["product__name"][:40]:<40} - Stock total: {item["total_stock"]}')
        
        self.stdout.write(self.style.SUCCESS('\n=== Inventario rellenado exitosamente! ==='))

