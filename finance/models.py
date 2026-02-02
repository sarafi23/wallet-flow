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
    nombre = models.CharField(max_length=50)
    icono = models.CharField(max_length=50, default='fa-tag', help_text="Clase para el ícono bonito")
    tipo = models.CharField(max_length=10, choices=TYPE_CHOICES, default='GASTO')

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"

class Transaccion(models.Model):
    """Aquí se guarda cada movimiento de dinero"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE) # Cada usuario ve solo SU dinero
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2) # Usamos Decimal para exactitud con dinero
    descripcion = models.CharField(max_length=200, blank=True)
    fecha = models.DateField(default=timezone.now)
    creado_en = models.DateTimeField(auto_now_add=True) # Para saber cuándo se registró realemente

    def __str__(self):
        return f"{self.usuario.username} - {self.monto}"

    class Meta:
        ordering = ['-fecha'] # Muestra primero lo más reciente