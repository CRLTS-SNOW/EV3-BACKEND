# gestion/management/commands/seed_5000_reposteria.py

import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
import time

from ...models import (
    Supplier, Warehouse, Zone, Product, Inventory, ProductSupplier
)

class Command(BaseCommand):
    help = 'Genera 5000 productos genéricos relacionados con repostería'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Limpiar productos existentes antes de crear nuevos',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('=== Generando 5000 productos de repostería ===\n')
        
        # Verificar que existan bodegas, zonas y proveedores
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
        
        # Categorías de repostería
        categorias_reposteria = [
            'Alfajores', 'Dulce de Leche', 'Chocolate', 'Tortas', 'Pasteles',
            'Galletas', 'Brownies', 'Muffins', 'Cupcakes', 'Cheesecakes',
            'Pies', 'Tartas', 'Flanes', 'Pudines', 'Mousses',
            'Crema Pastelera', 'Merengue', 'Ganache', 'Buttercream', 'Fondant',
            'Leche Condensada', 'Leche Evaporada', 'Crema de Leche', 'Mantequilla',
            'Harinas', 'Azúcares', 'Endulzantes', 'Especias', 'Extractos',
            'Colorantes', 'Decoraciones', 'Frutas en Conserva', 'Mermeladas',
            'Miel', 'Jarabes', 'Licores para Repostería', 'Coberturas', 'Glaseados'
        ]
        
        # Productos base por categoría
        productos_base = {
            'Alfajores': [
                'Alfajor de Maicena', 'Alfajor de Chocolate', 'Alfajor de Manjar',
                'Alfajor de Dulce de Leche', 'Alfajor de Frutilla', 'Alfajor de Vainilla',
                'Alfajor de Coco', 'Alfajor de Nuez', 'Alfajor de Miel',
                'Alfajor de Limón', 'Alfajor de Naranja', 'Alfajor de Frambuesa'
            ],
            'Dulce de Leche': [
                'Dulce de Leche Tradicional', 'Dulce de Leche Repostero',
                'Dulce de Leche Premium', 'Dulce de Leche Light',
                'Dulce de Leche con Chocolate', 'Dulce de Leche con Coco',
                'Dulce de Leche con Nuez', 'Dulce de Leche con Pasas'
            ],
            'Chocolate': [
                'Chocolate para Repostería', 'Chocolate Amargo', 'Chocolate Semi-amargo',
                'Chocolate con Leche', 'Chocolate Blanco', 'Chocolate en Polvo',
                'Chocolate para Derretir', 'Chocolate en Chips', 'Cacao en Polvo',
                'Chocolate para Cobertura', 'Chocolate para Decorar'
            ],
            'Tortas': [
                'Torta de Chocolate', 'Torta de Vainilla', 'Torta de Zanahoria',
                'Torta Tres Leches', 'Torta de Limón', 'Torta de Naranja',
                'Torta de Fresa', 'Torta de Manzana', 'Torta de Plátano',
                'Torta de Coco', 'Torta de Nuez', 'Torta de Café'
            ],
            'Pasteles': [
                'Pastel de Chocolate', 'Pastel de Vainilla', 'Pastel de Fresa',
                'Pastel de Limón', 'Pastel de Naranja', 'Pastel de Manzana',
                'Pastel de Durazno', 'Pastel de Frutos Rojos', 'Pastel de Coco'
            ],
            'Galletas': [
                'Galleta de Vainilla', 'Galleta de Chocolate', 'Galleta de Mantequilla',
                'Galleta de Avena', 'Galleta de Jengibre', 'Galleta de Canela',
                'Galleta de Limón', 'Galleta de Naranja', 'Galleta de Coco',
                'Galleta de Nuez', 'Galleta de Avena y Pasas'
            ],
            'Brownies': [
                'Brownie de Chocolate', 'Brownie de Nuez', 'Brownie de Menta',
                'Brownie de Caramelo', 'Brownie de Frambuesa', 'Brownie Blondie'
            ],
            'Muffins': [
                'Muffin de Chocolate', 'Muffin de Arándanos', 'Muffin de Plátano',
                'Muffin de Vainilla', 'Muffin de Limón', 'Muffin de Naranja',
                'Muffin de Manzana', 'Muffin de Zanahoria', 'Muffin de Nuez'
            ],
            'Cupcakes': [
                'Cupcake de Chocolate', 'Cupcake de Vainilla', 'Cupcake de Fresa',
                'Cupcake de Limón', 'Cupcake de Naranja', 'Cupcake de Red Velvet',
                'Cupcake de Caramelo', 'Cupcake de Coco', 'Cupcake de Menta'
            ],
            'Cheesecakes': [
                'Cheesecake de Fresa', 'Cheesecake de Limón', 'Cheesecake de Chocolate',
                'Cheesecake de Frutos Rojos', 'Cheesecake de Caramelo', 'Cheesecake de Coco'
            ],
            'Pies': [
                'Pie de Limón', 'Pie de Manzana', 'Pie de Durazno',
                'Pie de Cereza', 'Pie de Fresa', 'Pie de Arándanos',
                'Pie de Pera', 'Pie de Calabaza', 'Pie de Nuez'
            ],
            'Tartas': [
                'Tarta de Limón', 'Tarta de Fresa', 'Tarta de Manzana',
                'Tarta de Durazno', 'Tarta de Frutos Rojos', 'Tarta de Chocolate',
                'Tarta de Coco', 'Tarta de Nuez'
            ],
            'Flanes': [
                'Flan de Vainilla', 'Flan de Chocolate', 'Flan de Coco',
                'Flan de Caramelo', 'Flan de Café', 'Flan de Naranja'
            ],
            'Pudines': [
                'Pudín de Vainilla', 'Pudín de Chocolate', 'Pudín de Arroz',
                'Pudín de Pan', 'Pudín de Coco', 'Pudín de Plátano'
            ],
            'Mousses': [
                'Mousse de Chocolate', 'Mousse de Limón', 'Mousse de Fresa',
                'Mousse de Mango', 'Mousse de Maracuyá', 'Mousse de Vainilla'
            ],
            'Crema Pastelera': [
                'Crema Pastelera de Vainilla', 'Crema Pastelera de Chocolate',
                'Crema Pastelera de Limón', 'Crema Pastelera de Café'
            ],
            'Merengue': [
                'Merengue Italiano', 'Merengue Suizo', 'Merengue Francés',
                'Merengue de Limón', 'Merengue de Vainilla'
            ],
            'Ganache': [
                'Ganache de Chocolate Negro', 'Ganache de Chocolate con Leche',
                'Ganache de Chocolate Blanco', 'Ganache de Caramelo'
            ],
            'Buttercream': [
                'Buttercream de Vainilla', 'Buttercream de Chocolate',
                'Buttercream de Limón', 'Buttercream de Fresa', 'Buttercream de Café'
            ],
            'Fondant': [
                'Fondant Blanco', 'Fondant de Colores', 'Fondant de Chocolate',
                'Fondant Elástico', 'Fondant para Decorar'
            ],
            'Leche Condensada': [
                'Leche Condensada', 'Leche Condensada Light', 'Leche Condensada Azucarada'
            ],
            'Leche Evaporada': [
                'Leche Evaporada', 'Leche Evaporada Light', 'Leche Evaporada Entera'
            ],
            'Crema de Leche': [
                'Crema de Leche para Batir', 'Crema de Leche para Cocinar',
                'Crema de Leche Espesa', 'Crema de Leche Light'
            ],
            'Mantequilla': [
                'Mantequilla sin Sal', 'Mantequilla con Sal', 'Mantequilla Clarificada',
                'Mantequilla para Repostería'
            ],
            'Harinas': [
                'Harina de Trigo', 'Harina de Maíz', 'Harina de Arroz',
                'Harina de Almendras', 'Harina de Coco', 'Harina de Avena',
                'Harina Leudante', 'Harina Integral', 'Harina de Pastelería'
            ],
            'Azúcares': [
                'Azúcar Blanca', 'Azúcar Morena', 'Azúcar Glass',
                'Azúcar Mascabado', 'Azúcar de Coco', 'Azúcar de Caña'
            ],
            'Endulzantes': [
                'Stevia', 'Eritritol', 'Xilitol', 'Miel de Agave',
                'Sirope de Arce', 'Sirope de Maíz'
            ],
            'Especias': [
                'Canela en Polvo', 'Nuez Moscada', 'Clavo de Olor',
                'Jengibre en Polvo', 'Cardamomo', 'Anís', 'Vainilla en Polvo'
            ],
            'Extractos': [
                'Extracto de Vainilla', 'Extracto de Almendra', 'Extracto de Limón',
                'Extracto de Naranja', 'Extracto de Menta', 'Extracto de Coco',
                'Extracto de Café', 'Extracto de Rón'
            ],
            'Colorantes': [
                'Colorante Alimentario Rojo', 'Colorante Alimentario Azul',
                'Colorante Alimentario Verde', 'Colorante Alimentario Amarillo',
                'Colorante Alimentario Rosa', 'Colorante Alimentario Morado',
                'Colorante en Gel', 'Colorante en Polvo', 'Colorante Natural'
            ],
            'Decoraciones': [
                'Sprinkles Multicolor', 'Sprinkles de Chocolate', 'Perlas de Azúcar',
                'Confites', 'Chispas de Chocolate', 'Chispas de Colores',
                'Fondant Decorativo', 'Flores de Azúcar', 'Figuras de Azúcar'
            ],
            'Frutas en Conserva': [
                'Duraznos en Conserva', 'Piña en Conserva', 'Cerezas en Conserva',
                'Frutas Mixtas en Conserva', 'Arándanos en Conserva'
            ],
            'Mermeladas': [
                'Mermelada de Fresa', 'Mermelada de Durazno', 'Mermelada de Arándanos',
                'Mermelada de Frambuesa', 'Mermelada de Naranja', 'Mermelada de Limón'
            ],
            'Miel': [
                'Miel de Abeja', 'Miel de Eucalipto', 'Miel de Trébol',
                'Miel de Flores', 'Miel de Manuka'
            ],
            'Jarabes': [
                'Jarabe de Arce', 'Jarabe de Maíz', 'Jarabe de Agave',
                'Jarabe de Chocolate', 'Jarabe de Caramelo'
            ],
            'Licores para Repostería': [
                'Rón para Repostería', 'Brandy para Repostería', 'Amaretto',
                'Baileys', 'Kahlúa', 'Grand Marnier'
            ],
            'Coberturas': [
                'Cobertura de Chocolate', 'Cobertura de Vainilla',
                'Cobertura de Fresa', 'Cobertura de Caramelo'
            ],
            'Glaseados': [
                'Glaseado Real', 'Glaseado de Chocolate', 'Glaseado de Limón',
                'Glaseado de Vainilla', 'Glaseado de Colores'
            ]
        }
        
        # Marcas genéricas
        marcas = [
            'Lili\'s', 'Dulce Artesanal', 'Repostería Premium', 'Dulcería Clásica',
            'Sabores Tradicionales', 'Dulce Casero', 'Repostería Selecta',
            'Dulces Artesanales', 'Repostería Fina', 'Dulcería Premium',
            'Sabores del Sur', 'Dulce Tradicional', 'Repostería Gourmet',
            'Dulces Premium', 'Artesanía Dulce', 'Repostería Especial',
            'Dulcería Artesanal', 'Sabores Únicos', 'Repostería Clásica'
        ]
        
        # Unidades de medida
        unidades_compra = ['KG', 'GR', 'LT', 'ML', 'UN', 'PAQ']
        unidades_venta = ['KG', 'GR', 'LT', 'ML', 'UN', 'PAQ']
        
        # Generar productos
        self.stdout.write('Generando productos...')
        start_time = time.time()
        products_created = 0
        sku_counter = Product.objects.count() + 1
        
        # Calcular cuántos productos por categoría (distribución aproximada)
        productos_por_categoria = {}
        productos_restantes = 5000
        categorias_disponibles = list(categorias_reposteria)
        
        for categoria in categorias_reposteria:
            if categoria in productos_base:
                cantidad_base = len(productos_base[categoria])
                # Asignar más productos a categorías con más variantes base
                productos_por_categoria[categoria] = min(cantidad_base * 15, productos_restantes // len(categorias_disponibles) + random.randint(10, 50))
                productos_restantes -= productos_por_categoria[categoria]
            else:
                productos_por_categoria[categoria] = productos_restantes // len(categorias_disponibles)
                productos_restantes -= productos_por_categoria[categoria]
        
        # Ajustar para llegar exactamente a 5000
        if productos_restantes > 0:
            categorias_con_productos = [c for c in categorias_reposteria if productos_por_categoria.get(c, 0) > 0]
            if categorias_con_productos:
                categoria_extra = random.choice(categorias_con_productos)
                productos_por_categoria[categoria_extra] += productos_restantes
        
        # Crear productos
        productos_a_crear = []
        batch_size = 100
        
        for categoria in categorias_reposteria:
            cantidad = productos_por_categoria.get(categoria, 0)
            if cantidad == 0:
                continue
                
            nombres_categoria = productos_base.get(categoria, [f'Producto {categoria}'])
            
            for i in range(cantidad):
                # Seleccionar nombre base
                nombre_base = random.choice(nombres_categoria)
                
                # Variaciones de nombre
                variaciones = ['', 'Premium', 'Clásico', 'Especial', 'Deluxe', 'Original', 
                             'Tradicional', 'Artisanal', 'Selecto', 'Gourmet', 'Fino']
                variacion = random.choice(variaciones)
                
                if variacion:
                    nombre = f"{nombre_base} {variacion}"
                else:
                    nombre = nombre_base
                
                # Agregar número si es necesario para evitar duplicados exactos
                if random.random() < 0.3:  # 30% de probabilidad
                    nombre += f" {random.randint(1, 99)}"
                
                # Generar SKU único
                sku = f'REP-{str(sku_counter).zfill(6)}'
                sku_counter += 1
                
                # Generar EAN/UPC (opcional, 70% de probabilidad)
                ean_upc = None
                if random.random() < 0.7:
                    ean_upc = f'{random.randint(1000000000000, 9999999999999)}'
                
                # Precios y costos (valores enteros)
                costo_estandar = Decimal(str(random.randint(100, 5000)))
                costo_promedio = Decimal(str(int(costo_estandar * Decimal(str(random.uniform(0.95, 1.05))))))
                precio_venta = Decimal(str(int(costo_estandar * Decimal(str(random.uniform(1.5, 3.0))))))
                
                # Stock
                stock_minimo = random.randint(10, 100)
                stock_maximo = random.randint(200, 1000)
                punto_reorden = random.randint(stock_minimo, stock_maximo // 2)
                
                # Unidades
                uom_compra = random.choice(unidades_compra)
                uom_venta = random.choice(unidades_venta)
                factor_conversion = Decimal('1')
                if uom_compra != uom_venta:
                    if uom_compra == 'KG' and uom_venta == 'GR':
                        factor_conversion = Decimal('1000')
                    elif uom_compra == 'LT' and uom_venta == 'ML':
                        factor_conversion = Decimal('1000')
                
                # Impuesto IVA (19% en Chile) - se mantiene como decimal porque es un porcentaje
                impuesto_iva = Decimal('0.19')
                
                # Crear producto
                producto = Product(
                    sku=sku,
                    ean_upc=ean_upc,
                    name=nombre,
                    descripcion=f"Producto de repostería: {nombre}. Categoría: {categoria}.",
                    categoria=categoria,
                    marca=random.choice(marcas) if random.random() < 0.8 else None,
                    uom_compra=uom_compra,
                    uom_venta=uom_venta,
                    factor_conversion=factor_conversion,
                    costo_estandar=costo_estandar,
                    costo_promedio=costo_promedio,
                    precio_venta=precio_venta,
                    impuesto_iva=impuesto_iva,
                    stock_minimo=stock_minimo,
                    stock_maximo=stock_maximo,
                    punto_reorden=punto_reorden,
                    is_active=True
                )
                
                productos_a_crear.append(producto)
                products_created += 1
                
                # Crear en lotes para mejor rendimiento
                if len(productos_a_crear) >= batch_size:
                    Product.objects.bulk_create(productos_a_crear)
                    productos_a_crear = []
                    self.stdout.write(f'  Creados {products_created} productos...', ending='\r')
        
        # Crear productos restantes
        if productos_a_crear:
            Product.objects.bulk_create(productos_a_crear)
        
        elapsed_time = time.time() - start_time
        self.stdout.write(f'\n✅ Creados {products_created} productos en {elapsed_time:.2f} segundos\n')
        
        # Crear inventario para algunos productos
        self.stdout.write('Creando inventario inicial...')
        productos_creados = Product.objects.filter(sku__startswith='REP-').order_by('?')[:1000]  # Inventario para 1000 productos aleatorios
        
        inventario_a_crear = []
        for producto in productos_creados:
            zona = random.choice(zones_list)
            cantidad = random.randint(producto.stock_minimo, producto.stock_maximo)
            
            inventario, created = Inventory.objects.get_or_create(
                product=producto,
                zone=zona,
                defaults={'quantity': cantidad}
            )
            
            if not created:
                inventario.quantity += cantidad
                inventario.save()
        
        self.stdout.write(self.style.SUCCESS(f'✅ Inventario creado para {len(productos_creados)} productos\n'))
        
        # Crear relaciones con proveedores para algunos productos
        self.stdout.write('Creando relaciones con proveedores...')
        productos_con_proveedor = Product.objects.filter(sku__startswith='REP-').order_by('?')[:500]  # 500 productos con proveedor
        
        relaciones_a_crear = []
        for producto in productos_con_proveedor:
            proveedor = random.choice(suppliers_list)
            # Costo entero basado en el costo estándar del producto
            costo = Decimal(str(int(producto.costo_estandar * Decimal(str(random.uniform(0.9, 1.1))))))
            
            relacion, created = ProductSupplier.objects.get_or_create(
                product=producto,
                supplier=proveedor,
                defaults={
                    'costo': costo,
                    'lead_time_dias': random.randint(3, 15),
                    'min_lote': Decimal(str(random.randint(10, 100))),
                    'descuento_pct': Decimal(str(random.randint(0, 15))),  # Entero también
                    'preferente': random.random() < 0.2  # 20% son preferentes
                }
            )
        
        self.stdout.write(self.style.SUCCESS(f'✅ Relaciones con proveedores creadas para {len(productos_con_proveedor)} productos\n'))
        
        self.stdout.write(self.style.SUCCESS(f'\n=== Completado ==='))
        self.stdout.write(f'Total productos creados: {products_created}')
        self.stdout.write(f'Tiempo total: {elapsed_time:.2f} segundos')
        self.stdout.write(f'Promedio: {products_created / elapsed_time:.2f} productos/segundo')

