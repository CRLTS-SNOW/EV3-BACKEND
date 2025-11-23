# gestion/management/commands/seed_data.py

import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User
from django.utils import timezone

# Importa todos tus modelos
from ...models import (
    Supplier, Warehouse, Zone, Product, Inventory, UserProfile,
    ProductSupplier, Client
)
from ...firebase_service import sync_django_user_to_firebase, initialize_firebase

class Command(BaseCommand):
    help = 'Carga la BD con datos de prueba completos (proveedores, productos, inventario, etc.)'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('=== Iniciando carga de datos de prueba ===')
        
        # Limpiar datos existentes (excepto usuarios)
        self.stdout.write('Limpiando datos existentes...')
        ProductSupplier.objects.all().delete()
        Inventory.objects.all().delete()
        Product.objects.all().delete()
        Client.objects.all().delete()
        Supplier.objects.all().delete()
        Zone.objects.all().delete()
        Warehouse.objects.all().delete()

        # Inicializar Firebase
        self.stdout.write('Inicializando Firebase...')
        initialize_firebase()

        # --- 1. Crear Bodegas y Zonas ---
        self.stdout.write('\n1. Creando bodegas y zonas...')
        warehouse1 = Warehouse.objects.create(
            name='Bodega Central',
            address='Av. Principal 123, Santiago',
            is_active=True
        )
        zone1A = Zone.objects.create(warehouse=warehouse1, name='Zona A - Refrigerados', is_active=True)
        zone1B = Zone.objects.create(warehouse=warehouse1, name='Zona B - Secos', is_active=True)
        zone1C = Zone.objects.create(warehouse=warehouse1, name='Zona C - Congelados', is_active=True)
        
        warehouse2 = Warehouse.objects.create(
            name='Bodega Despacho',
            address='Av. Industrial 456, Valparaíso',
            is_active=True
        )
        zone2A = Zone.objects.create(warehouse=warehouse2, name='Zona A - Despacho', is_active=True)
        zone2B = Zone.objects.create(warehouse=warehouse2, name='Zona B - Almacén', is_active=True)

        self.stdout.write(self.style.SUCCESS(f'  OK: Creadas {Warehouse.objects.count()} bodegas y {Zone.objects.count()} zonas'))

        # --- 2. Crear Proveedores ---
        self.stdout.write('\n2. Creando proveedores...')
        suppliers_data = [
            {
                'rut_nif': '76.123.456-7',
                'razon_social': 'Chocolates del Sur S.A.',
                'nombre_fantasia': 'ChocoSur',
                'email': 'contacto@chocosur.cl',
                'telefono': '+56 9 1234 5678',
                'direccion': 'Av. Los Chocolates 100, Temuco',
                'ciudad': 'Temuco',
                'pais': 'Chile',
                'condiciones_pago': '30 días',
                'moneda': 'CLP',
                'contacto_principal_nombre': 'Juan Pérez',
                'contacto_principal_email': 'juan.perez@chocosur.cl',
                'contacto_principal_telefono': '+56 9 1234 5679',
                'estado': 'ACTIVO'
            },
            {
                'rut_nif': '77.234.567-8',
                'razon_social': 'Alfajores de la Montaña Ltda.',
                'nombre_fantasia': 'Alfajores Montaña',
                'email': 'ventas@alfajores.cl',
                'telefono': '+56 9 2345 6789',
                'direccion': 'Calle Los Alfajores 200, Valparaíso',
                'ciudad': 'Valparaíso',
                'pais': 'Chile',
                'condiciones_pago': '15 días',
                'moneda': 'CLP',
                'contacto_principal_nombre': 'María González',
                'contacto_principal_email': 'maria.gonzalez@alfajores.cl',
                'contacto_principal_telefono': '+56 9 2345 6790',
                'estado': 'ACTIVO'
            },
            {
                'rut_nif': '78.345.678-9',
                'razon_social': 'Dulces Artesanales SpA',
                'nombre_fantasia': 'Dulces Artesanales',
                'email': 'info@dulcesartesanales.cl',
                'telefono': '+56 9 3456 7890',
                'direccion': 'Pasaje Los Dulces 300, Concepción',
                'ciudad': 'Concepción',
                'pais': 'Chile',
                'condiciones_pago': '45 días',
                'moneda': 'CLP',
                'contacto_principal_nombre': 'Carlos Rodríguez',
                'contacto_principal_email': 'carlos.rodriguez@dulcesartesanales.cl',
                'contacto_principal_telefono': '+56 9 3456 7891',
                'estado': 'ACTIVO'
            },
            {
                'rut_nif': '79.456.789-0',
                'razon_social': 'Helados Premium S.A.',
                'nombre_fantasia': 'Helados Premium',
                'email': 'ventas@heladospremium.cl',
                'telefono': '+56 9 4567 8901',
                'direccion': 'Av. Los Helados 400, La Serena',
                'ciudad': 'La Serena',
                'pais': 'Chile',
                'condiciones_pago': '30 días',
                'moneda': 'CLP',
                'contacto_principal_nombre': 'Ana Martínez',
                'contacto_principal_email': 'ana.martinez@heladospremium.cl',
                'contacto_principal_telefono': '+56 9 4567 8902',
                'estado': 'ACTIVO'
            },
            {
                'rut_nif': '80.567.890-1',
                'razon_social': 'Tortas y Pasteles del Valle Ltda.',
                'nombre_fantasia': 'Tortas del Valle',
                'email': 'pedidos@tortasdelvalle.cl',
                'telefono': '+56 9 5678 9012',
                'direccion': 'Calle Las Tortas 500, Rancagua',
                'ciudad': 'Rancagua',
                'pais': 'Chile',
                'condiciones_pago': '20 días',
                'moneda': 'CLP',
                'contacto_principal_nombre': 'Luis Fernández',
                'contacto_principal_email': 'luis.fernandez@tortasdelvalle.cl',
                'contacto_principal_telefono': '+56 9 5678 9013',
                'estado': 'ACTIVO'
            }
        ]
        
        suppliers = []
        for sup_data in suppliers_data:
            supplier = Supplier.objects.create(**sup_data)
            suppliers.append(supplier)
            self.stdout.write(f'  OK: {supplier.razon_social}')

        # --- 3. Crear Productos ---
        self.stdout.write('\n3. Creando productos...')
        product_categories = {
            'Chocolates': [
                ('Chocolate Blanco 100g', '7891234567890', 'UN', Decimal('2500.00'), Decimal('3500.00')),
                ('Chocolate Negro 70%', '7891234567891', 'UN', Decimal('2800.00'), Decimal('4200.00')),
                ('Chocolate con Leche', '7891234567892', 'UN', Decimal('2400.00'), Decimal('3800.00')),
                ('Chocolate Amargo 85%', '7891234567893', 'UN', Decimal('3000.00'), Decimal('4500.00')),
                ('Bombones Surtidos 200g', '7891234567894', 'UN', Decimal('3500.00'), Decimal('5500.00')),
                ('Trufas de Chocolate', '7891234567895', 'UN', Decimal('3200.00'), Decimal('4800.00')),
                ('Barra Chocolate Almendras', '7891234567896', 'UN', Decimal('2600.00'), Decimal('4000.00')),
            ],
            'Alfajores': [
                ('Alfajor Manjar Nuez', '7891234567900', 'UN', Decimal('800.00'), Decimal('1200.00')),
                ('Alfajor Maicena', '7891234567901', 'UN', Decimal('700.00'), Decimal('1100.00')),
                ('Alfajor Chocolate', '7891234567902', 'UN', Decimal('750.00'), Decimal('1150.00')),
                ('Alfajor Frutilla', '7891234567903', 'UN', Decimal('780.00'), Decimal('1180.00')),
                ('Alfajor Doble Crema', '7891234567904', 'UN', Decimal('900.00'), Decimal('1300.00')),
                ('Alfajor Vainilla', '7891234567905', 'UN', Decimal('720.00'), Decimal('1120.00')),
            ],
            'Tortas': [
                ('Torta Mil Hojas', '7891234567910', 'UN', Decimal('8500.00'), Decimal('12000.00')),
                ('Torta de Zanahoria', '7891234567911', 'UN', Decimal('7500.00'), Decimal('11000.00')),
                ('Torta Tres Leches', '7891234567912', 'UN', Decimal('8000.00'), Decimal('11500.00')),
                ('Torta Selva Negra', '7891234567913', 'UN', Decimal('9000.00'), Decimal('13000.00')),
                ('Cheesecake Maracuyá', '7891234567914', 'UN', Decimal('8800.00'), Decimal('12500.00')),
                ('Pie de Limón', '7891234567915', 'UN', Decimal('6500.00'), Decimal('9500.00')),
            ],
            'Galletas': [
                ('Galletas de Vainilla', '7891234567920', 'CAJA', Decimal('3500.00'), Decimal('5500.00')),
                ('Galletas de Chocolate', '7891234567921', 'CAJA', Decimal('3800.00'), Decimal('5800.00')),
                ('Cookies Chocolate Chip', '7891234567922', 'CAJA', Decimal('4000.00'), Decimal('6000.00')),
                ('Brownie Cacao 80%', '7891234567923', 'UN', Decimal('2200.00'), Decimal('3500.00')),
                ('Muffin de Chocolate', '7891234567924', 'UN', Decimal('1800.00'), Decimal('2800.00')),
            ],
            'Helados': [
                ('Helado Vainilla 1L', '7891234567930', 'UN', Decimal('4500.00'), Decimal('6500.00')),
                ('Helado Chocolate 1L', '7891234567931', 'UN', Decimal('4800.00'), Decimal('6800.00')),
                ('Helado Frutilla 1L', '7891234567932', 'UN', Decimal('4700.00'), Decimal('6700.00')),
                ('Paletas Heladas x6', '7891234567933', 'UN', Decimal('3500.00'), Decimal('5500.00')),
            ]
        }
        
        products = []
        sku_counter = 1
        for category, items in product_categories.items():
            for name, ean, uom, costo, precio in items:
                product = Product.objects.create(
                    sku=f'PROD-{str(sku_counter).zfill(4)}',
                    ean_upc=ean,
                    name=name,
                    categoria=category,
                    uom_compra=uom,
                    uom_venta=uom,
                    factor_conversion=Decimal('1.0000'),
                    costo_estandar=costo,
                    precio_venta=precio,
                    impuesto_iva=Decimal('19.00'),
                    stock_minimo=Decimal('10.0000'),
                    stock_maximo=Decimal('500.0000'),
                    punto_reorden=Decimal('20.0000'),
                    perishable=(category == 'Helados'),
                    control_por_lote=(category in ['Helados', 'Tortas']),
                    control_por_serie=False,
                    is_active=True
                )
                products.append(product)
                sku_counter += 1
                
                # Asignar a proveedores aleatorios (cada producto a 1-3 proveedores)
                num_suppliers = random.randint(1, 3)
                selected_suppliers = random.sample(suppliers, num_suppliers)
                
                for idx, supplier in enumerate(selected_suppliers):
                    # El primer proveedor es preferente
                    # Calcular costo con máximo 2 decimales para evitar errores de validación
                    if idx == 0:
                        supplier_costo = round(costo * Decimal('0.95'), 2)
                    else:
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
        
        self.stdout.write(self.style.SUCCESS(f'  OK: Creados {len(products)} productos'))

        # --- 4. Crear Inventario ---
        self.stdout.write('\n4. Creando inventario...')
        zones = [zone1A, zone1B, zone1C, zone2A, zone2B]
        inventory_count = 0
        
        for product in products:
            # Asignar stock a 2-3 zonas aleatorias
            num_zones = random.randint(2, 3)
            selected_zones = random.sample(zones, num_zones)
            
            for zone in selected_zones:
                quantity = Decimal(str(random.randint(20, 200)))
                Inventory.objects.create(
                    product=product,
                    zone=zone,
                    quantity=quantity
                )
                inventory_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  OK: Creados {inventory_count} registros de inventario'))

        # --- 5. Crear Clientes ---
        self.stdout.write('\n5. Creando clientes...')
        clients_data = [
            {'name': 'Café Central', 'email': 'pedidos@cafecentral.cl', 'phone': '+56 9 1111 1111'},
            {'name': 'Panadería El Buen Pan', 'email': 'compras@elbuenpan.cl', 'phone': '+56 9 2222 2222'},
            {'name': 'Restaurante La Cocina', 'email': 'proveedores@lacocina.cl', 'phone': '+56 9 3333 3333'},
            {'name': 'Tienda de Regalos', 'email': 'pedidos@tiendaregalos.cl', 'phone': '+56 9 4444 4444'},
            {'name': 'Supermercado Local', 'email': 'compras@superlocal.cl', 'phone': '+56 9 5555 5555'},
        ]
        
        for client_data in clients_data:
            Client.objects.create(**client_data)
        
        self.stdout.write(self.style.SUCCESS(f'  OK: Creados {len(clients_data)} clientes'))

        # --- 6. Verificar/Crear Usuarios Demo ---
        self.stdout.write('\n6. Verificando usuarios demo...')
        password = '123456'
        
        # Admin
        admin, _ = User.objects.get_or_create(username='admin', defaults={'email': 'admin@lilis.com'})
        admin.email = 'admin@lilis.com'
        admin.first_name = 'Administrador'
        admin.last_name = 'Sistema'
        admin.is_staff = True
        admin.is_superuser = True
        admin.is_active = True
        admin.save()
        
        profile, _ = UserProfile.objects.get_or_create(user=admin)
        profile.role = 'admin'
        profile.nombres = 'Administrador'
        profile.apellidos = 'Sistema'
        profile.estado = 'ACTIVO'
        profile.area = 'Administracion'
        profile.save()
        
        sync_django_user_to_firebase(admin, password=password)
        self.stdout.write(self.style.SUCCESS('  OK: Usuario admin verificado'))
        
        # Bodeguero
        bodeguero, _ = User.objects.get_or_create(username='bodeguero', defaults={'email': 'bodeguero@lilis.com'})
        bodeguero.email = 'bodeguero@lilis.com'
        bodeguero.first_name = 'Operador'
        bodeguero.last_name = 'Bodega'
        bodeguero.is_active = True
        bodeguero.save()
        
        profile, _ = UserProfile.objects.get_or_create(user=bodeguero)
        profile.role = 'bodega'
        profile.nombres = 'Operador'
        profile.apellidos = 'Bodega'
        profile.estado = 'ACTIVO'
        profile.area = 'Bodega'
        profile.warehouse = warehouse1
        profile.save()
        
        sync_django_user_to_firebase(bodeguero, password=password)
        self.stdout.write(self.style.SUCCESS('  OK: Usuario bodeguero verificado'))
        
        # Vendedor
        vendedor, _ = User.objects.get_or_create(username='vendedor', defaults={'email': 'vendedor@lilis.com'})
        vendedor.email = 'vendedor@lilis.com'
        vendedor.first_name = 'Operador'
        vendedor.last_name = 'Ventas'
        vendedor.is_active = True
        vendedor.save()
        
        profile, _ = UserProfile.objects.get_or_create(user=vendedor)
        profile.role = 'ventas'
        profile.nombres = 'Operador'
        profile.apellidos = 'Ventas'
        profile.estado = 'ACTIVO'
        profile.area = 'Ventas'
        profile.save()
        
        sync_django_user_to_firebase(vendedor, password=password)
        self.stdout.write(self.style.SUCCESS('  OK: Usuario vendedor verificado'))

        self.stdout.write(self.style.SUCCESS('\n=== Datos de prueba cargados exitosamente! ==='))
        self.stdout.write(f'\nResumen:')
        self.stdout.write(f'  - {Warehouse.objects.count()} bodegas')
        self.stdout.write(f'  - {Zone.objects.count()} zonas')
        self.stdout.write(f'  - {Supplier.objects.count()} proveedores')
        self.stdout.write(f'  - {Product.objects.count()} productos')
        self.stdout.write(f'  - {ProductSupplier.objects.count()} relaciones producto-proveedor')
        self.stdout.write(f'  - {Inventory.objects.count()} registros de inventario')
        self.stdout.write(f'  - {Client.objects.count()} clientes')
        self.stdout.write(f'\nCredenciales demo:')
        self.stdout.write(f'  - Admin: admin / 123456')
        self.stdout.write(f'  - Bodeguero: bodeguero / 123456')
        self.stdout.write(f'  - Vendedor: vendedor / 123456')
