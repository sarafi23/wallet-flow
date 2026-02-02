from django.contrib import admin
from .models import Categoria, Transaccion

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'icono')

@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'categoria', 'monto', 'fecha')
    list_filter = ('fecha', 'categoria')