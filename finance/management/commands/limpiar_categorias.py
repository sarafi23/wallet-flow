from django.core.management.base import BaseCommand
from finance.models import Categoria, Transaccion

class Command(BaseCommand):
    help = 'Elimina categorías duplicadas y mantiene solo una de cada'

    def handle(self, *args, **options):
        # Encontrar categorías únicas por nombre
        categorias_unicas = {}
        
        for cat in Categoria.objects.all().order_by('id'):
            key = (cat.nombre, cat.tipo)
            if key not in categorias_unicas:
                categorias_unicas[key] = cat
                self.stdout.write(f"✓ Manteniendo: {cat.nombre} ({cat.tipo})")
            else:
                # Reasignar transacciones de esta categoría duplicada a la primera
                transacciones_afectadas = Transaccion.objects.filter(categoria=cat)
                count = transacciones_afectadas.count()
                if count > 0:
                    transacciones_afectadas.update(categoria=categorias_unicas[key])
                    self.stdout.write(f"  → Reasignadas {count} transacciones")
                
                # Eliminar el duplicado
                self.stdout.write(self.style.WARNING(f"✗ Eliminando duplicado: {cat.nombre} ({cat.tipo}) [ID: {cat.id}]"))
                cat.delete()
        
        self.stdout.write(self.style.SUCCESS(f'\n¡Limpieza completa! Categorías restantes: {Categoria.objects.count()}'))
