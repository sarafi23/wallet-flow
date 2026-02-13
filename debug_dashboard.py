#!/usr/bin/env python
"""
Debug script to test dashboard data generation
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from finance.models import Transaccion, Categoria
from django.contrib.auth.models import User
from django.db.models import Sum

# Get or create test user
user = User.objects.first()
if not user:
    print("❌ No users found!")
    sys.exit(1)

print(f"✓ Testing with user: {user.username}\n")

# Get transactions
transacciones = Transaccion.objects.filter(usuario=user)
print(f"Total transactions: {transacciones.count()}")

# Calculate totals
total_ingresos = transacciones.filter(categoria__tipo='INGRESO').aggregate(Sum('monto'))['monto__sum'] or 0
total_gastos = transacciones.filter(categoria__tipo='GASTO').aggregate(Sum('monto'))['monto__sum'] or 0
balance = total_ingresos - total_gastos

print(f"Ingresos: ${total_ingresos}")
print(f"Gastos: ${total_gastos}")
print(f"Balance: ${balance}\n")

# Get expense breakdown
categorias_gastos = Categoria.objects.filter(tipo='GASTO').order_by('nombre')
print("Gastos por categoría:")
gastos_por_categoria = []
for categoria in categorias_gastos:
    total = transacciones.filter(categoria=categoria).aggregate(Sum('monto'))['monto__sum'] or 0
    if total > 0:
        gastos_por_categoria.append({
            'nombre': categoria.nombre,
            'total': float(total),
            'color': categoria.color,
            'icono': categoria.icono
        })
        print(f"  - {categoria.nombre}: ${total} (color: {categoria.color})")

print(f"\nTotal categorías con gastos: {len(gastos_por_categoria)}")

if len(gastos_por_categoria) == 0:
    print("\n❌ No expense categories with data! Charts will be empty.")
else:
    print("\n✓ Data looks good for charts!")
    
# Test health score
health_score = 0
if total_ingresos > 0:
    savings_rate = (balance / total_ingresos) * 100 if total_ingresos > 0 else 0
    savings_score = min(savings_rate / 20 * 50, 50)
    expense_ratio = (total_gastos / total_ingresos) * 100 if total_ingresos > 0 else 100
    expense_score = max(30 - (expense_ratio - 50) / 30 * 30, 0) if expense_ratio > 50 else 30
    balance_score = 20 if balance > 0 else 0
    health_score = min(int(savings_score + expense_score + balance_score), 100)

print(f"\nHealth Score: {health_score}/100")
