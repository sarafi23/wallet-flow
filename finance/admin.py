from django.contrib import admin
from .models import Categoria, Transaccion, Wishlist, UserProfile

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'icono', 'usuario')
    list_filter = ('tipo',)
    search_fields = ('nombre',)
    list_select_related = ('usuario',)

@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'categoria', 'monto', 'fecha', 'creado_en')
    list_filter = ('fecha', 'categoria', 'usuario')
    search_fields = ('descripcion', 'usuario__username')
    date_hierarchy = 'fecha'

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'item', 'precio_objetivo', 'ahorrado', 'progreso')
    list_filter = ('usuario',)
    search_fields = ('item', 'usuario__username')
    
    def progreso(self, obj):
        return f"{obj.progreso()}%"
    progreso.short_description = 'Progreso'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio')
    search_fields = ('user__username', 'bio')