# gestion/management/commands/seed_1000_products.py

import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction, connection, reset_queries
from django.utils import timezone
from django.db.models import Sum
import time

from ...models import (
    Supplier, Warehouse, Zone, Product, Inventory, ProductSupplier
)

class Command(BaseCommand):
    help = 'Genera 1000 productos de prueba y mide el rendimiento'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Limpiar productos existentes antes de crear nuevos',
        )
        parser.add_argument(
            '--test',
            action='store_true',
            help='Ejecutar pruebas de rendimiento después de crear productos',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('=== Generando 1000 productos de prueba ===\n')
        
        # Verificar que existan bodegas y zonas
        warehouses = Warehouse.objects.filter(is_active=True)
        zones = Zone.objects.filter(is_active=True)
        suppliers = Supplier.objects.filter(estado='ACTIVO')
        
        if not warehouses.exists():
            self.stdout.write(self.style.ERROR('ERROR: No hay bodegas activas. Ejecuta primero: python manage.py seed_data'))
            return
        
        if not zones.exists():
            self.stdout.write(self.style.ERROR('ERROR: No hay zonas activas. Ejecuta primero: python manage.py seed_data'))
            return
        
        if not suppliers.exists():
            self.stdout.write(self.style.ERROR('ERROR: No hay proveedores activos. Ejecuta primero: python manage.py seed_data'))
            return
        
        zones_list = list(zones)
        suppliers_list = list(suppliers)
        
        # Limpiar productos existentes si se solicita
        if options['clear']:
            self.stdout.write('Limpiando productos existentes...')
            ProductSupplier.objects.all().delete()
            Inventory.objects.all().delete()
            Product.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('OK: Productos eliminados\n'))
        
        # Categorías y productos base
        categorias = [
            'Chocolates', 'Alfajores', 'Tortas', 'Galletas', 'Helados',
            'Dulces', 'Caramelos', 'Chicles', 'Gomitas', 'Bombones',
            'Turrones', 'Mazapanes', 'Oreos', 'Chips', 'Snacks'
        ]
        
        nombres_base = {
            'Chocolates': ['Chocolate Blanco', 'Chocolate Negro', 'Chocolate con Leche', 'Chocolate Amargo', 'Chocolate con Almendras'],
            'Alfajores': ['Alfajor Manjar', 'Alfajor Maicena', 'Alfajor Chocolate', 'Alfajor Frutilla', 'Alfajor Vainilla'],
            'Tortas': ['Torta Mil Hojas', 'Torta de Zanahoria', 'Torta Tres Leches', 'Torta Selva Negra', 'Cheesecake'],
            'Galletas': ['Galletas de Vainilla', 'Galletas de Chocolate', 'Cookies', 'Brownie', 'Muffin'],
            'Helados': ['Helado Vainilla', 'Helado Chocolate', 'Helado Frutilla', 'Paletas Heladas'],
            'Dulces': ['Dulce de Leche', 'Mermelada', 'Miel', 'Miel de Abeja', 'Miel de Palma'],
            'Caramelos': ['Caramelo de Leche', 'Caramelo Ácido', 'Caramelo de Menta', 'Caramelo de Fruta'],
            'Chicles': ['Chicle de Menta', 'Chicle de Fruta', 'Chicle Burbuja', 'Chicle Sin Azúcar'],
            'Gomitas': ['Gomitas de Fruta', 'Gomitas Ácidas', 'Gomitas de Ositos', 'Gomitas de Gusanos'],
            'Bombones': ['Bombones Surtidos', 'Bombones de Chocolate', 'Bombones de Licor', 'Trufas'],
            'Turrones': ['Turrón de Alicante', 'Turrón de Jijona', 'Turrón de Chocolate', 'Turrón de Coco'],
            'Mazapanes': ['Mazapán de Almendra', 'Mazapán de Coco', 'Mazapán de Piñón'],
            'Oreos': ['Oreo Clásica', 'Oreo Doble Crema', 'Oreo de Chocolate', 'Oreo de Vainilla'],
            'Chips': ['Chips de Chocolate', 'Chips de Vainilla', 'Chips de Fresa'],
            'Snacks': ['Papas Fritas', 'Nachos', 'Palomitas', 'Mix de Frutos Secos']
        }
        
        # Generar productos
        self.stdout.write('Generando productos...')
        start_time = time.time()
        products_created = 0
        sku_counter = Product.objects.count() + 1
        
        for i in range(1000):
            categoria = random.choice(categorias)
            nombre_base = random.choice(nombres_base.get(categoria, ['Producto']))
            nombre = f"{nombre_base} {random.choice(['Premium', 'Clásico', 'Especial', 'Deluxe', 'Original', 'Tradicional'])} {random.randint(1, 999)}"
            
            # Generar SKU único
            sku = f'PROD-{str(sku_counter).zfill(6)}'
            sku_counter += 1
            
            # Generar EAN/UPC
            ean = f'789{random.randint(1000000000, 9999999999)}'
            
            # Precios aleatorios
            costo = Decimal(str(random.uniform(500, 5000))).quantize(Decimal('0.01'))
            precio = Decimal(str(costo * Decimal(random.uniform(1.5, 3.0)))).quantize(Decimal('0.01'))
            
            # Crear producto
            product = Product.objects.create(
                sku=sku,
                ean_upc=ean,
                name=nombre,
                categoria=categoria,
                uom_compra='UN',
                uom_venta='UN',
                factor_conversion=Decimal('1.0000'),
                costo_estandar=costo,
                precio_venta=precio,
                impuesto_iva=Decimal('19.00'),
                stock_minimo=Decimal(str(random.randint(10, 50))),
                stock_maximo=Decimal(str(random.randint(500, 2000))),
                punto_reorden=Decimal(str(random.randint(20, 100))),
                perishable=random.choice([True, False]),
                control_por_lote=random.choice([True, False]),
                control_por_serie=False,
                is_active=True
            )
            
            # Asignar a proveedores aleatorios
            num_suppliers = random.randint(1, 3)
            selected_suppliers = random.sample(suppliers_list, min(num_suppliers, len(suppliers_list)))
            
            for idx, supplier in enumerate(selected_suppliers):
                supplier_costo = round(costo * Decimal(str(random.uniform(0.90, 1.10))), 2)
                ProductSupplier.objects.create(
                    product=product,
                    supplier=supplier,
                    costo=supplier_costo,
                    lead_time_dias=random.randint(3, 15),
                    min_lote=Decimal('10.00'),
                    descuento_pct=Decimal('5.00') if idx == 0 else Decimal('0.00'),
                    preferente=(idx == 0)
                )
            
            # Crear inventario en zonas aleatorias
            num_zones = random.randint(2, min(4, len(zones_list)))
            selected_zones = random.sample(zones_list, num_zones)
            
            for zone in selected_zones:
                quantity = random.randint(20, 500)
                Inventory.objects.create(
                    product=product,
                    zone=zone,
                    quantity=quantity
                )
            
            products_created += 1
            
            if (i + 1) % 100 == 0:
                elapsed = time.time() - start_time
                self.stdout.write(f'  OK: {i + 1} productos creados ({elapsed:.2f}s)')
        
        elapsed_total = time.time() - start_time
        self.stdout.write(self.style.SUCCESS(f'\nOK: {products_created} productos creados en {elapsed_total:.2f} segundos'))
        self.stdout.write(f'  Promedio: {elapsed_total/products_created*1000:.2f}ms por producto\n')
        
        # Estadísticas
        total_inventory = Inventory.objects.count()
        total_supplier_relations = ProductSupplier.objects.count()
        
        self.stdout.write('=== Estadísticas ===')
        self.stdout.write(f'  Productos totales: {Product.objects.count()}')
        self.stdout.write(f'  Registros de inventario: {total_inventory}')
        self.stdout.write(f'  Relaciones producto-proveedor: {total_supplier_relations}')
        
        # Pruebas de rendimiento
        if options['test']:
            self.stdout.write('\n=== Pruebas de Rendimiento ===\n')
            self.run_performance_tests()
    
    def run_performance_tests(self):
        """Ejecuta pruebas de rendimiento"""
        from django.db.models import Q, Sum
        from django.db.models.functions import Coalesce
        from django.db.models import Prefetch
        from ...models import Inventory
        
        # Test 1: Listado básico (página 1)
        self.stdout.write('1. Test: Listado básico (primeros 20 productos)')
        reset_queries()
        start = time.time()
        
        queryset = Product.objects.filter(is_active=True)
        stock_prefetch = Prefetch(
            'stock',
            queryset=Inventory.objects.select_related('zone', 'zone__warehouse').only(
                'product_id', 'quantity', 'zone_id', 'zone__name', 'zone__warehouse__name'
            )
        )
        queryset = queryset.prefetch_related(stock_prefetch)
        queryset = queryset.annotate(total_stock=Coalesce(Sum('stock__quantity'), 0))
        queryset = queryset.order_by('name')[:20]
        list(queryset)  # Ejecutar consulta
        
        elapsed = (time.time() - start) * 1000
        queries = len(connection.queries)
        self.stdout.write(f'   Tiempo: {elapsed:.2f}ms')
        self.stdout.write(f'   Consultas SQL: {queries}')
        self.stdout.write(f'   Estado: {"OK" if elapsed < 200 else "LENTO"}\n')
        
        # Test 2: Búsqueda por nombre
        self.stdout.write('2. Test: Búsqueda por nombre ("chocolate")')
        reset_queries()
        start = time.time()
        
        queryset = Product.objects.filter(is_active=True)
        queryset = queryset.prefetch_related(stock_prefetch)
        queryset = queryset.annotate(total_stock=Coalesce(Sum('stock__quantity'), 0))
        queryset = queryset.filter(Q(name__icontains='chocolate'))[:20]
        list(queryset)
        
        elapsed = (time.time() - start) * 1000
        queries = len(connection.queries)
        self.stdout.write(f'   Tiempo: {elapsed:.2f}ms')
        self.stdout.write(f'   Consultas SQL: {queries}')
        self.stdout.write(f'   Estado: {"OK" if elapsed < 200 else "LENTO"}\n')
        
        # Test 3: Filtro por categoría
        self.stdout.write('3. Test: Filtro por categoría ("Chocolates")')
        reset_queries()
        start = time.time()
        
        queryset = Product.objects.filter(is_active=True, categoria='Chocolates')
        queryset = queryset.prefetch_related(stock_prefetch)
        queryset = queryset.annotate(total_stock=Coalesce(Sum('stock__quantity'), 0))
        queryset = queryset.order_by('name')[:20]
        list(queryset)
        
        elapsed = (time.time() - start) * 1000
        queries = len(connection.queries)
        self.stdout.write(f'   Tiempo: {elapsed:.2f}ms')
        self.stdout.write(f'   Consultas SQL: {queries}')
        self.stdout.write(f'   Estado: {"OK" if elapsed < 200 else "LENTO"}\n')
        
        # Test 4: Ordenamiento por precio
        self.stdout.write('4. Test: Ordenamiento por precio (descendente)')
        reset_queries()
        start = time.time()
        
        queryset = Product.objects.filter(is_active=True)
        queryset = queryset.prefetch_related(stock_prefetch)
        queryset = queryset.annotate(total_stock=Coalesce(Sum('stock__quantity'), 0))
        queryset = queryset.order_by('-precio_venta')[:20]
        list(queryset)
        
        elapsed = (time.time() - start) * 1000
        queries = len(connection.queries)
        self.stdout.write(f'   Tiempo: {elapsed:.2f}ms')
        self.stdout.write(f'   Consultas SQL: {queries}')
        self.stdout.write(f'   Estado: {"OK" if elapsed < 200 else "LENTO"}\n')
        
        # Test 5: Ordenamiento por stock
        self.stdout.write('5. Test: Ordenamiento por stock total (descendente)')
        reset_queries()
        start = time.time()
        
        queryset = Product.objects.filter(is_active=True)
        queryset = queryset.prefetch_related(stock_prefetch)
        queryset = queryset.annotate(total_stock=Coalesce(Sum('stock__quantity'), 0))
        queryset = queryset.order_by('-total_stock')[:20]
        list(queryset)
        
        elapsed = (time.time() - start) * 1000
        queries = len(connection.queries)
        self.stdout.write(f'   Tiempo: {elapsed:.2f}ms')
        self.stdout.write(f'   Consultas SQL: {queries}')
        self.stdout.write(f'   Estado: {"OK" if elapsed < 200 else "LENTO"}\n')
        
        # Resumen
        self.stdout.write('\n=== Resumen ===')
        self.stdout.write('OK: Todas las pruebas completadas')
        self.stdout.write('  Objetivo: < 200ms por operacion')
        self.stdout.write('\nTip: Usa Chrome DevTools Network tab para medir tiempos reales de API')

