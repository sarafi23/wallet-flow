"""
Generate balanced realistic transaction data for Jan 2025 - Jan 2026
With consistent ~$2000/month income
"""
import os
import django
import random
from datetime import date, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from finance.models import Transaccion, Categoria

User = get_user_model()

def generate_transactions():
    user = User.objects.first()
    if not user:
        print("No user found!")
        return
    
    Transaccion.objects.filter(usuario=user).delete()
    print("Cleared existing transactions")
    
    # Get categories
    cats = {}
    cat_names = [
        ('salario', '💰 Salario'),
        ('freelance', '💻 Freelance'),
        ('propinas', '💵 Propinas'),
        ('bonos', '🎁 Bonos'),
        ('venta', '💸 Venta'),
        ('alquiler', '🏠 Alquiler'),
        ('comida', '🍔 Comida'),
        ('supermercado', '🛒 Supermercado'),
        ('transporte', '🚌 Transporte'),
        ('gasolina', '⛽ Gasolina'),
        ('servicios', '💡 Servicios'),
        ('internet', '📱 Internet'),
        ('telefono', '📞 Teléfono'),
        ('entretenimiento', '🎬 Cine/Series'),
        ('cafe', '☕ Café'),
        ('cerveza', '🍺 Cerveza/Bares'),
        ('gimnasio', '🧘 Gimnasio'),
        ('ropa', '👕 Ropa'),
        ('medico', '🏥 Médico'),
        ('farmacia', '💊 Farmacia'),
        ('cursos', '📚 Cursos'),
        ('regalos', '🎁 Regalos'),
        ('viajes', '✈️ Viajes'),
        ('reparaciones', '🔧 Reparaciones'),
        ('streaming', '📺 Streaming'),
    ]
    
    for key, name in cat_names:
        try:
            cats[key] = Categoria.objects.get(usuario=user, nombre=name)
        except Categoria.DoesNotExist:
            print(f"Category not found: {name}")
    
    # Months to generate
    months = [
        (2025, 1), (2025, 2), (2025, 3), (2025, 4), (2025, 5), (2025, 6),
        (2025, 7), (2025, 8), (2025, 9), (2025, 10), (2025, 11), (2025, 12),
        (2026, 1),
    ]
    
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan']
    
    for idx, (year, month_num) in enumerate(months):
        first_day = date(year, month_num, 1)
        
        # ============ INCOME - Consistent $2000 base ============
        # Salary 1st - $1000
        Transaccion.objects.create(
            usuario=user, categoria=cats['salario'], monto=Decimal('1000.00'),
            descripcion='💰 Salario quincena 1', fecha=first_day + timedelta(days=14)
        )
        
        # Salary 2nd - $1000
        Transaccion.objects.create(
            usuario=user, categoria=cats['salario'], monto=Decimal('1000.00'),
            descripcion='💰 Salario quincena 2', fecha=first_day + timedelta(days=28)
        )
        
        # Extra income - random $50-150 (70% chance)
        if random.random() < 0.7:
            extra = random.randint(50, 150)
            cat = random.choice([cats['freelance'], cats['propinas'], cats['bonos']])
            desc = random.choice(['💻 Proyecto freelance', '💵 Propinas', '🎁 Bono'])
            Transaccion.objects.create(
                usuario=user, categoria=cat, monto=Decimal(str(extra)),
                descripcion=desc, fecha=first_day + timedelta(days=random.randint(5, 25))
            )
        
        # ============ EXPENSES ============
        
        # Rent - $600
        Transaccion.objects.create(
            usuario=user, categoria=cats['alquiler'], monto=Decimal('600.00'),
            descripcion='🏠 Alquiler mensual', fecha=first_day
        )
        
        # Grocery - 2 times, $130-170 each
        Transaccion.objects.create(
            usuario=user, categoria=cats['supermercado'], monto=Decimal(str(random.randint(130, 170))),
            descripcion='🛒 Supermercado', fecha=first_day + timedelta(days=random.randint(3, 10))
        )
        Transaccion.objects.create(
            usuario=user, categoria=cats['supermercado'], monto=Decimal(str(random.randint(130, 170))),
            descripcion='🛒 Supermercado', fecha=first_day + timedelta(days=random.randint(18, 25))
        )
        
        # Food - 3-4 times, $25-50 each
        for _ in range(random.randint(3, 4)):
            Transaccion.objects.create(
                usuario=user, categoria=cats['comida'], monto=Decimal(str(random.randint(25, 50))),
                descripcion='🍔 Comida fuera', fecha=first_day + timedelta(days=random.randint(1, 28))
            )
        
        # Coffee - 3-4 times, $12-18 each
        for _ in range(random.randint(3, 4)):
            Transaccion.objects.create(
                usuario=user, categoria=cats['cafe'], monto=Decimal(str(random.randint(12, 18))),
                descripcion='☕ Café', fecha=first_day + timedelta(days=random.randint(1, 28))
            )
        
        # Gas - $50-70
        Transaccion.objects.create(
            usuario=user, categoria=cats['gasolina'], monto=Decimal(str(random.randint(50, 70))),
            descripcion='⛽ Gasolina', fecha=first_day + timedelta(days=random.randint(5, 15))
        )
        
        # Transport - $35-50
        Transaccion.objects.create(
            usuario=user, categoria=cats['transporte'], monto=Decimal(str(random.randint(35, 50))),
            descripcion='🚌 Transporte', fecha=first_day + timedelta(days=random.randint(5, 20))
        )
        
        # Utilities - $75-90
        Transaccion.objects.create(
            usuario=user, categoria=cats['servicios'], monto=Decimal(str(random.randint(75, 90))),
            descripcion='💡 Servicios', fecha=first_day + timedelta(days=random.randint(3, 10))
        )
        
        # Internet - $48-55
        Transaccion.objects.create(
            usuario=user, categoria=cats['internet'], monto=Decimal(str(random.randint(48, 55))),
            descripcion='📱 Internet', fecha=first_day + timedelta(days=2)
        )
        
        # Phone - $28-35
        Transaccion.objects.create(
            usuario=user, categoria=cats['telefono'], monto=Decimal(str(random.randint(28, 35))),
            descripcion='📞 Teléfono', fecha=first_day + timedelta(days=2)
        )
        
        # Gym - $38-45
        Transaccion.objects.create(
            usuario=user, categoria=cats['gimnasio'], monto=Decimal(str(random.randint(38, 45))),
            descripcion='🧘 Gimnasio', fecha=first_day + timedelta(days=random.randint(3, 10))
        )
        
        # Entertainment - $20-40
        Transaccion.objects.create(
            usuario=user, categoria=cats['entretenimiento'], monto=Decimal(str(random.randint(20, 40))),
            descripcion='🎬 Cine', fecha=first_day + timedelta(days=random.randint(10, 20))
        )
        
        # Streaming
        Transaccion.objects.create(
            usuario=user, categoria=cats['streaming'], monto=Decimal('15.00'),
            descripcion='📺 Streaming', fecha=first_day + timedelta(days=5)
        )
        
        # Beer/Bars - $40-70 (70% chance)
        if random.random() < 0.7:
            Transaccion.objects.create(
                usuario=user, categoria=cats['cerveza'], monto=Decimal(str(random.randint(40, 70))),
                descripcion='🍺 Salida', fecha=first_day + timedelta(days=random.randint(15, 25))
            )
        
        # Clothes - every 3 months
        if idx in [2, 5, 8, 11]:
            Transaccion.objects.create(
                usuario=user, categoria=cats['ropa'], monto=Decimal(str(random.randint(50, 100))),
                descripcion='👕 Ropa', fecha=first_day + timedelta(days=random.randint(10, 20))
            )
        
        # Medical - occasional
        if random.random() < 0.2:
            Transaccion.objects.create(
                usuario=user, categoria=cats['medico'], monto=Decimal(str(random.randint(50, 90))),
                descripcion='🏥 Médico', fecha=first_day + timedelta(days=random.randint(10, 20))
            )
        
        # Courses - some months
        if idx in [1, 4, 7, 10]:
            Transaccion.objects.create(
                usuario=user, categoria=cats['cursos'], monto=Decimal(str(random.randint(40, 70))),
                descripcion='📚 Curso', fecha=first_day + timedelta(days=random.randint(15, 25))
            )
        
        # Gifts - special months
        if idx in [1, 4, 10, 11]:
            Transaccion.objects.create(
                usuario=user, categoria=cats['regalos'], monto=Decimal(str(random.randint(50, 90))),
                descripcion='🎁 Regalos', fecha=first_day + timedelta(days=random.randint(10, 20))
            )
        
        # Travel - July and December
        if idx in [6, 11]:
            Transaccion.objects.create(
                usuario=user, categoria=cats['viajes'], monto=Decimal(str(random.randint(250, 450))),
                descripcion='✈️ Viaje', fecha=first_day + timedelta(days=random.randint(20, 28))
            )
        
        print(f"Generated: {month_names[idx]} {year}")
    
    # Summary
    total_income = sum(t.monto for t in Transaccion.objects.filter(usuario=user, categoria__tipo='INGRESO'))
    total_expense = sum(t.monto for t in Transaccion.objects.filter(usuario=user, categoria__tipo='GASTO'))
    
    print(f"\n{'='*50}")
    print(f"Total Income: ${total_income:,.2f} (${total_income/13:,.0f}/mes)")
    print(f"Total Expenses: ${total_expense:,.2f} (${total_expense/13:,.0f}/mes)")
    print(f"Balance: ${total_income - total_expense:,.2f}")
    print(f"Transactions: {Transaccion.objects.filter(usuario=user).count()}")
    print(f"{'='*50}")

if __name__ == '__main__':
    generate_transactions()
