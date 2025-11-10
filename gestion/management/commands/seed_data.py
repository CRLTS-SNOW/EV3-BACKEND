# gestion/management/commands/seed_data.py

import random
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User

# Importa todos tus modelos
from ...models import Supplier, Warehouse, Zone, Product, Inventory, UserProfile
from ...firebase_service import sync_django_user_to_firebase, initialize_firebase

class Command(BaseCommand):
    help = 'Carga la BD con datos de prueba (incluyendo ROLES de usuario)'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Limpiando la base de datos...')
        # Limpiamos solo productos, proveedores y bodegas, pero NO usuarios
        Warehouse.objects.all().delete()
        Supplier.objects.all().delete()
        Product.objects.all().delete()

        # Inicializar Firebase
        self.stdout.write('Inicializando Firebase...')
        initialize_firebase()

        # --- 1. Crear o obtener los 3 USUARIOS con sus ROLES ---
        self.stdout.write('Verificando usuarios y perfiles de rol...')

        # Usuario 1: Administrador
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@demo.com',
                'is_superuser': True,
                'is_staff': True
            }
        )
        password = '123'
        if created:
            admin_user.set_password(password)
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f'Usuario admin creado.'))
            # Sincronizar con Firebase
            firebase_user = sync_django_user_to_firebase(admin_user, password=password)
            if firebase_user:
                self.stdout.write(self.style.SUCCESS(f'  -> Usuario admin sincronizado con Firebase (UID: {firebase_user.uid})'))
            else:
                self.stdout.write(self.style.WARNING(f'  ADVERTENCIA: No se pudo sincronizar usuario admin con Firebase'))
        else:
            self.stdout.write(self.style.WARNING(f'Usuario admin ya existe, se conserva.'))
            # Sincronizar con Firebase si no existe
            if admin_user.email:
                firebase_user = sync_django_user_to_firebase(admin_user, password=password)
                if firebase_user:
                    self.stdout.write(self.style.SUCCESS(f'  -> Usuario admin sincronizado con Firebase (UID: {firebase_user.uid})'))
        
        # Asegurar que tiene perfil
        admin_profile, created = UserProfile.objects.get_or_create(
            user=admin_user,
            defaults={'role': 'admin'}
        )
        if not created and admin_profile.role != 'admin':
            admin_profile.role = 'admin'
            admin_profile.save()

        # Usuario 2: Operador de Bodega
        bodega_user, created = User.objects.get_or_create(
            username='bodeguero',
            defaults={
                'email': 'bodega@demo.com',
                'is_staff': True
            }
        )
        password = '123'
        if created:
            bodega_user.set_password(password)
            bodega_user.save()
            self.stdout.write(self.style.SUCCESS(f'Usuario bodeguero creado.'))
            # Sincronizar con Firebase
            if bodega_user.email:
                firebase_user = sync_django_user_to_firebase(bodega_user, password=password)
                if firebase_user:
                    self.stdout.write(self.style.SUCCESS(f'  -> Usuario bodeguero sincronizado con Firebase (UID: {firebase_user.uid})'))
                else:
                    self.stdout.write(self.style.WARNING(f'  ADVERTENCIA: No se pudo sincronizar usuario bodeguero con Firebase'))
        else:
            self.stdout.write(self.style.WARNING(f'Usuario bodeguero ya existe, se conserva.'))
            # Sincronizar con Firebase si no existe
            if bodega_user.email:
                firebase_user = sync_django_user_to_firebase(bodega_user, password=password)
                if firebase_user:
                    self.stdout.write(self.style.SUCCESS(f'  -> Usuario bodeguero sincronizado con Firebase (UID: {firebase_user.uid})'))
        
        # Usuario 3: Operador de Ventas
        ventas_user, created = User.objects.get_or_create(
            username='vendedor',
            defaults={
                'email': 'ventas@demo.com',
                'is_staff': True
            }
        )
        password = '123'
        if created:
            ventas_user.set_password(password)
            ventas_user.save()
            self.stdout.write(self.style.SUCCESS(f'Usuario vendedor creado.'))
            # Sincronizar con Firebase
            if ventas_user.email:
                firebase_user = sync_django_user_to_firebase(ventas_user, password=password)
                if firebase_user:
                    self.stdout.write(self.style.SUCCESS(f'  -> Usuario vendedor sincronizado con Firebase (UID: {firebase_user.uid})'))
                else:
                    self.stdout.write(self.style.WARNING(f'  ADVERTENCIA: No se pudo sincronizar usuario vendedor con Firebase'))
        else:
            self.stdout.write(self.style.WARNING(f'Usuario vendedor ya existe, se conserva.'))
            # Sincronizar con Firebase si no existe
            if ventas_user.email:
                firebase_user = sync_django_user_to_firebase(ventas_user, password=password)
                if firebase_user:
                    self.stdout.write(self.style.SUCCESS(f'  -> Usuario vendedor sincronizado con Firebase (UID: {firebase_user.uid})'))
        
        # Asegurar que tiene perfil
        ventas_profile, created = UserProfile.objects.get_or_create(
            user=ventas_user,
            defaults={'role': 'ventas'}
        )
        if not created and ventas_profile.role != 'ventas':
            ventas_profile.role = 'ventas'
            ventas_profile.save()

        # --- 2. Crear Proveedores y Bodegas ---
        self.stdout.write('Creando 3 proveedores y 2 bodegas...')
        supplier1 = Supplier.objects.create(
            name='Chocolates del Sur', 
            email='contacto@chocosur.cl',
            phone='+56 9 1234 5678'
        )
        supplier2 = Supplier.objects.create(
            name='Alfajores de la Montaña', 
            email='ventas@alfajores.cl',
            phone='+56 9 2345 6789'
        )
        supplier3 = Supplier.objects.create(
            name='Dulces Artesanales', 
            email='info@dulcesartesanales.cl',
            phone='+56 9 3456 7890'
        )
        
        warehouse1 = Warehouse.objects.create(name='Bodega Central (Refrigerados)')
        zone1A = Zone.objects.create(warehouse=warehouse1, name='Zona A (Refrigerados)')
        zone1B = Zone.objects.create(warehouse=warehouse1, name='Zona B (Secos)')
        
        warehouse2 = Warehouse.objects.create(name='Bodega Despacho (RM)')
        zone2A = Zone.objects.create(warehouse=warehouse2, name='Zona A (Despacho)')

        # Asignamos al 'bodeguero' a la Bodega Central
        bodega_profile, created = UserProfile.objects.get_or_create(
            user=bodega_user,
            defaults={
                'role': 'bodega',
                'warehouse': warehouse1
            }
        )
        if not created:
            # Si ya existe, actualizar warehouse
            bodega_profile.role = 'bodega'
            bodega_profile.warehouse = warehouse1
            bodega_profile.save()

        # --- 3. Crear 100 Productos y asignarlos a TODOS los proveedores ---
        self.stdout.write('Creando 100 productos y asignándolos a todos los proveedores...')
        product_names = [
            # Chocolates y confites (1-15)
            'Chocolate Blanco 100g', 'Chocolate Negro 70%', 'Chocolate con Leche', 
            'Chocolate Amargo 85%', 'Chocolates Rellenos', 'Bombones Surtidos',
            'Trufas de Chocolate', 'Barra Chocolate Almendras', 'Chocolate Blanco Frambuesa',
            'Chocolate Negro Naranja', 'Chocolate con Avellanas', 'Chocolate Blanco Coco',
            'Tableta Chocolate 200g', 'Chocolate con Caramelo', 'Chocolate Blanco Vainilla',
            
            # Alfajores (16-25)
            'Alfajor Manjar Nuez', 'Alfajor Maicena', 'Alfajor Chocolate', 
            'Alfajor Frutilla', 'Alfajor Doble Crema', 'Alfajor Vainilla',
            'Alfajor Limón', 'Alfajor Menta', 'Alfajor Café', 'Alfajor Miel',
            
            # Tortas y pasteles (26-40)
            'Torta Mil Hojas', 'Torta de Zanahoria', 'Torta Tres Leches',
            'Torta Selva Negra', 'Torta Opera', 'Torta Red Velvet',
            'Cheesecake Maracuyá', 'Cheesecake Frutilla', 'Pie de Limón',
            'Pie de Manzana', 'Torta de Naranja', 'Torta de Piña',
            'Torta de Chocolate', 'Torta de Vainilla', 'Torta de Fresa',
            
            # Kuchenes y queques (41-55)
            'Kuchen de Frambuesa', 'Kuchen de Manzana', 'Kuchen de Arándanos',
            'Queque Vainilla', 'Queque Chocolate', 'Queque Limón',
            'Queque Naranja', 'Queque Zanahoria', 'Queque Plátano',
            'Queque Manzana', 'Kuchen de Durazno', 'Kuchen de Cereza',
            'Queque de Coco', 'Queque de Maracuyá', 'Queque de Vainilla Especial',
            
            # Galletas y masas (56-75)
            'Galletas de Vainilla', 'Galletas de Chocolate', 'Galletas de Mantequilla',
            'Galletas de Avena', 'Galletas de Jengibre', 'Cookies Chocolate Chip',
            'Brownie Cacao 80%', 'Brownie Nuez', 'Muffin de Chocolate',
            'Muffin de Arándanos', 'Galletas de Coco', 'Galletas de Limón',
            'Cookies de Avena', 'Galletas de Menta', 'Cookies de Vainilla',
            'Brownie con Crema', 'Muffin de Vainilla', 'Muffin de Zanahoria',
            'Galletas de Canela', 'Cookies Doble Chocolate',
            
            # Helados y postres fríos (76-85)
            'Helado Vainilla', 'Helado Chocolate', 'Helado Frutilla',
            'Paletas Heladas', 'Helado de Coco', 'Helado de Menta',
            'Helado de Limón', 'Helado de Naranja', 'Helado de Frambuesa',
            'Helado de Mango',
            
            # Postres tradicionales (86-95)
            'Churros con Chocolate', 'Empanadas Dulces', 'Panqueques con Manjar',
            'Waffles con Miel', 'Donas Glaseadas', 'Rollos de Canela',
            'Suspiros', 'Calzones Rotos', 'Sopaipillas Pasadas',
            'Berlines con Manjar',
            
            # Productos especiales (96-100)
            'Trufas de Chocolate Premium', 'Bombones de Lujo', 'Caja Regalo Chocolates',
            'Caja Regalo Alfajores', 'Selección Premium Dulces'
        ]
        
        suppliers_list = [supplier1, supplier2, supplier3]
        
        # Crear TODOS los productos para CADA proveedor (se repiten entre proveedores)
        product_counter = 1
        for supplier_idx, supplier in enumerate(suppliers_list):
            self.stdout.write(f'  Asignando productos a {supplier.name}...')
            for i, name in enumerate(product_names):
                # Crear el producto con un SKU único por proveedor
                # Formato: SKU-{proveedor_id}-{número_producto}
                product = Product.objects.create(
                    name=name,
                    sku=f'SKU-{supplier.id}-{str(i+1).zfill(3)}',
                    supplier=supplier,
                    price=random.randint(1500, 20000)
                )
                
                # Crear stock inicial solo para los productos del primer proveedor
                # para evitar duplicar stock innecesariamente
                if supplier_idx == 0:
                    Inventory.objects.create(
                        product=product,
                        zone=zone1A,
                        quantity=random.randint(50, 150)
                    )
                    Inventory.objects.create(
                        product=product,
                        zone=zone2A,
                        quantity=random.randint(20, 60)
                    )
                
                product_counter += 1

        self.stdout.write(self.style.SUCCESS('¡Semilla de prueba con ROLES cargada con éxito!'))