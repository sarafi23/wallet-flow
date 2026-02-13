from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Opciones para que el usuario elija si es Ingreso o Gasto
TYPE_CHOICES = (
    ('INGRESO', 'Ingreso'),
    ('GASTO', 'Gasto'),
)

class Categoria(models.Model):
    """Aquí guardamos cosas como: Comida, Bus, Netflix, Sueldo"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='categorias')
    nombre = models.CharField(max_length=50)
    icono = models.CharField(max_length=50, default='bi-tag', help_text="Bootstrap icon class (e.g., bi-cart)")
    color = models.CharField(max_length=7, default='#6366f1', help_text="Color hex code")
    tipo = models.CharField(max_length=10, choices=TYPE_CHOICES, default='GASTO')

    def __str__(self):
        tipo = self.tipo
        if self.usuario:
            return f"{self.usuario.username} - {self.nombre} ({tipo})"
        return f"{self.nombre} ({tipo})"
    
    class Meta:
        verbose_name_plural = 'Categorías'
        ordering = ['tipo', 'nombre']
        indexes = [
            models.Index(fields=['usuario', 'tipo']),
        ]

class Wishlist(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    item = models.CharField(max_length=100)
    precio_objetivo = models.DecimalField(max_digits=10, decimal_places=2)
    ahorrado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    enlace = models.URLField(blank=True, null=True, help_text="Link del producto (Amazon, etc.)")
    imagen_url = models.URLField(blank=True, null=True)
    prioridad = models.IntegerField(default=0, help_text="Mayor número = mayor prioridad")
    creado_en = models.DateTimeField(auto_now_add=True)
    
    def progreso(self):
        if self.precio_objetivo > 0:
            return min(int((self.ahorrado / self.precio_objetivo) * 100), 100)
        return 0
    
    def falta(self):
        """Cuánto dinero falta para alcanzar la meta"""
        return max(self.precio_objetivo - self.ahorrado, 0)

    def __str__(self):
        return f"{self.item} - {self.progreso()}%"
    
    class Meta:
        ordering = ['-prioridad', '-creado_en']
        verbose_name = 'Meta de Ahorro'
        verbose_name_plural = 'Metas de Ahorro'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.FileField(upload_to='avatars/', blank=True, null=True)
    
    # Extended profile information
    first_name = models.CharField(max_length=50, blank=True, help_text="Nombre")
    last_name = models.CharField(max_length=50, blank=True, help_text="Apellidos")
    bio = models.TextField(blank=True, max_length=500, help_text="Información sobre ti")
    pronouns = models.CharField(max_length=50, blank=True, help_text="Pronombres (ej: él/ella, elle)")
    website = models.URLField(blank=True, help_text="Sitio web personal")
    
    # Contact info
    telefono = models.CharField(max_length=20, blank=True, help_text="Teléfono")
    fecha_nacimiento = models.DateField(null=True, blank=True, help_text="Fecha de nacimiento")
    ubicacion = models.CharField(max_length=100, blank=True, help_text="Ciudad, País")
    ocupacion = models.CharField(max_length=100, blank=True, help_text="Trabajo o estudios")
    
    # Social media
    linkedin = models.URLField(blank=True, help_text="Perfil de LinkedIn")
    instagram = models.CharField(max_length=50, blank=True, help_text="Usuario de Instagram")
    
    # Financial settings
    meta_ingreso_mensual = models.DecimalField(max_digits=10, decimal_places=2, default=2000, help_text="Meta de ingreso mensual esperado")
    meta_ahorro_mensual = models.IntegerField(default=20, help_text="Porcentaje de ahorro mensual objetivo")
    inicio_mes = models.IntegerField(default=1, help_text="Día de inicio del mes financiero (1 o 15)")
    
    # System preferences
    tema_oscuro = models.BooleanField(default=True, help_text="Preferencia de tema")
    moneda = models.CharField(max_length=3, default='USD', help_text="Código de moneda (USD, EUR, etc.)")
    
    def __str__(self):
        return f'{self.user.username} Profile'
    
    def get_avatar_url(self):
        """Retorna la URL del avatar o un placeholder"""
        if self.avatar:
            return self.avatar.url
        return f"https://ui-avatars.com/api/?name={self.user.username}&background=6366f1&color=fff&size=200"
    
    def get_full_name(self):
        """Retorna el nombre completo si existe, sino el username"""
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.user.username


    
    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'


class Transaccion(models.Model):
    """Una transacción (ingreso o gasto)"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transacciones')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, related_name='transacciones')
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    descripcion = models.CharField(max_length=200, blank=True)
    fecha = models.DateField(default=timezone.now)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['usuario', 'fecha']),
            models.Index(fields=['categoria']),
            models.Index(fields=['activo']),
        ]
    
    def __str__(self):
        tipo = self.categoria.tipo if self.categoria else 'N/A'
        return f"{self.descripcion or 'Sin descripción'} - ${self.monto} ({tipo})"