from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, Categoria

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create a UserProfile when a new User is created"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the UserProfile when the User is saved"""
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()

@receiver(post_save, sender=User)
def create_default_categories(sender, instance, created, **kwargs):
    """Create default categories for new users (only if none exist)"""
    if created:
        # Check if user already has categories
        if Categoria.objects.filter(usuario=instance).exists():
            return
        
        # Default income categories with emojis
        income_categories = [
            {'nombre': '💰 Salario', 'icono': 'bi-cash-coin', 'tipo': 'INGRESO', 'color': '#10b981'},
            {'nombre': '💻 Freelance', 'icono': 'bi-laptop', 'tipo': 'INGRESO', 'color': '#3b82f6'},
            {'nombre': '📈 Inversiones', 'icono': 'bi-graph-up-arrow', 'tipo': 'INGRESO', 'color': '#8b5cf6'},
            {'nombre': '🎁 Bonos', 'icono': 'bi-gift', 'tipo': 'INGRESO', 'color': '#14b8a6'},
            {'nombre': '💵 Propinas', 'icono': 'bi-cash', 'tipo': 'INGRESO', 'color': '#22c55e'},
            {'nombre': '🏦 Intereses', 'icono': 'bi-bank', 'tipo': 'INGRESO', 'color': '#06b6d4'},
            {'nombre': '💰 Otros Ingresos', 'icono': 'bi-plus-circle', 'tipo': 'INGRESO', 'color': '#64748b'},
        ]
        
        # Default expense categories with emojis
        expense_categories = [
            # Comida
            {'nombre': '🍔 Comida', 'icono': 'bi-cart', 'tipo': 'GASTO', 'color': '#f59e0b'},
            {'nombre': '☕ Café', 'icono': 'bi-cup-hot', 'tipo': 'GASTO', 'color': '#d97706'},
            {'nombre': '🍺 Cerveza/Bares', 'icono': 'bi-cup-straw', 'tipo': 'GASTO', 'color': '#f97316'},
            
            # Transporte
            {'nombre': '🚗 Carro', 'icono': 'bi-car-front', 'tipo': 'GASTO', 'color': '#ec4899'},
            {'nombre': '🚌 Transporte', 'icono': 'bi-bus-front', 'tipo': 'GASTO', 'color': '#06b6d4'},
            {'nombre': '⛽ Gasolina', 'icono': 'bi-fuel-pump', 'tipo': 'GASTO', 'color': '#ef4444'},
            {'nombre': '✈️ Viajes', 'icono': 'bi-airplane', 'tipo': 'GASTO', 'color': '#8b5cf6'},
            
            # Vivienda
            {'nombre': '🏠 Alquiler', 'icono': 'bi-house', 'tipo': 'GASTO', 'color': '#6366f1'},
            {'nombre': '💡 Servicios', 'icono': 'bi-lightbulb', 'tipo': 'GASTO', 'color': '#eab308'},
            {'nombre': '📱 Internet', 'icono': 'bi-wifi', 'tipo': 'GASTO', 'color': '#3b82f6'},
            {'nombre': '📞 Teléfono', 'icono': 'bi-telephone', 'tipo': 'GASTO', 'color': '#10b981'},
            
            # Entretenimiento
            {'nombre': '🎮 Videojuegos', 'icono': 'bi-controller', 'tipo': 'GASTO', 'color': '#ef4444'},
            {'nombre': '🎬 Cine/Series', 'icono': 'bi-film', 'tipo': 'GASTO', 'color': '#ec4899'},
            {'nombre': '🎵 Música', 'icono': 'bi-music-note-beamed', 'tipo': 'GASTO', 'color': '#8b5cf6'},
            {'nombre': '⚽ Deportes', 'icono': 'bi-trophy', 'tipo': 'GASTO', 'color': '#f59e0b'},
            
            # Salud
            {'nombre': '🏥 Médico', 'icono': 'bi-hospital', 'tipo': 'GASTO', 'color': '#10b981'},
            {'nombre': '💊 Farmacia', 'icono': 'bi-capsule', 'tipo': 'GASTO', 'color': '#ef4444'},
            {'nombre': '🧘 Gimnasio', 'icono': 'bi-person', 'tipo': 'GASTO', 'color': '#14b8a6'},
            
            # Educación
            {'nombre': '📚 Cursos', 'icono': 'bi-book', 'tipo': 'GASTO', 'color': '#6366f1'},
            {'nombre': '🎓 Universidad', 'icono': 'bi-mortarboard', 'tipo': 'GASTO', 'color': '#8b5cf6'},
            {'nombre': '📖 Libros', 'icono': 'bi-book-half', 'tipo': 'GASTO', 'color': '#f59e0b'},
            
            # Shopping
            {'nombre': '🛒 Supermercado', 'icono': 'bi-cart', 'tipo': 'GASTO', 'color': '#22c55e'},
            {'nombre': '👕 Ropa', 'icono': 'bi-shop-window', 'tipo': 'GASTO', 'color': '#ec4899'},
            {'nombre': '🎁 Regalos', 'icono': 'bi-gift', 'tipo': 'GASTO', 'color': '#f43f5e'},
            
            # Otros
            {'nombre': '💳 Tarjetas', 'icono': 'bi-credit-card', 'tipo': 'GASTO', 'color': '#ef4444'},
            {'nombre': '📦 Envíos', 'icono': 'bi-box', 'tipo': 'GASTO', 'color': '#64748b'},
            {'nombre': '💸 Otros Gastos', 'icono': 'bi-three-dots', 'tipo': 'GASTO', 'color': '#64748b'},
        ]
        
        # Create categories for this specific user
        for cat_data in income_categories + expense_categories:
            Categoria.objects.create(usuario=instance, **cat_data)
