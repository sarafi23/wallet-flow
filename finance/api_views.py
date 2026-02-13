from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
from .models import Transaccion, Categoria, Wishlist
from django.db.models import Sum, Q
from django.db import transaction

@login_required
@require_http_methods(["GET"])
def chart_data_api(request):
    """API endpoint to get chart data as JSON"""
    user = request.user
    transacciones = Transaccion.objects.filter(usuario=user)
    
    # Calculate totals
    total_ingresos = transacciones.filter(categoria__tipo='INGRESO').aggregate(Sum('monto'))['monto__sum'] or 0
    total_gastos = transacciones.filter(categoria__tipo='GASTO').aggregate(Sum('monto'))['monto__sum'] or 0
    balance = total_ingresos - total_gastos
    
    # Expense breakdown - filter by user's categories
    categorias_gastos = Categoria.objects.filter(usuario=user, tipo='GASTO').order_by('nombre')
    gastos_por_categoria = []
    for categoria in categorias_gastos:
        total = transacciones.filter(categoria=categoria).aggregate(Sum('monto'))['monto__sum'] or 0
        if total > 0:
            gastos_por_categoria.append({
                'nombre': categoria.nombre,
                'total': float(total),
                'color': categoria.color
            })
    
    # Monthly trends
    from datetime import datetime, timedelta
    six_months_ago = datetime.now() - timedelta(days=180)
    from django.db.models.functions import TruncMonth
    monthly_data = transacciones.filter(fecha__gte=six_months_ago).annotate(
        month=TruncMonth('fecha')
    ).values('month').annotate(
        ingresos=Sum('monto', filter=Q(categoria__tipo='INGRESO')),
        gastos=Sum('monto', filter=Q(categoria__tipo='GASTO'))
    ).order_by('month')
    
    monthly_labels = []
    monthly_ingresos = []
    monthly_gastos = []
    
    for data in monthly_data:
        month_name = data['month'].strftime('%b')
        monthly_labels.append(month_name)
        monthly_ingresos.append(float(data['ingresos'] or 0))
        monthly_gastos.append(float(data['gastos'] or 0))
    
    # Health score
    health_score = 0
    health_color = "#ef4444"
    if total_ingresos > 0:
        savings_rate = (balance / total_ingresos) * 100
        savings_score = min(savings_rate / 20 * 50, 50)
        expense_ratio = (total_gastos / total_ingresos) * 100
        expense_score = max(30 - (expense_ratio - 50) / 30 * 30, 0) if expense_ratio > 50 else 30
        balance_score = 20 if balance > 0 else 0
        health_score = min(int(savings_score + expense_score + balance_score), 100)
        
        if health_score >= 80:
            health_color = "#10b981"
        elif health_score >= 60:
            health_color = "#22c55e"
        elif health_score >= 40:
            health_color = "#f59e0b"
    
    return JsonResponse({
        'gastos_por_categoria': gastos_por_categoria,
        'monthly': {
            'labels': monthly_labels,
            'ingresos': monthly_ingresos,
            'gastos': monthly_gastos
        },
        'health': {
            'score': health_score,
            'color': health_color
        },
        'totals': {
            'ingresos': float(total_ingresos),
            'gastos': float(total_gastos),
            'balance': float(balance)
        }
    })

@login_required
@require_http_methods(["GET"])
def api_dashboard_data(request):
    """Get dashboard summary data"""
    transacciones = Transaccion.objects.filter(usuario=request.user)
    wishlist = Wishlist.objects.filter(usuario=request.user)
    
    total_ingresos = transacciones.filter(
        categoria__isnull=False,
        categoria__tipo='INGRESO'
    ).aggregate(Sum('monto'))['monto__sum'] or 0
    
    total_gastos = transacciones.filter(
        categoria__isnull=False,
        categoria__tipo='GASTO'
    ).aggregate(Sum('monto'))['monto__sum'] or 0
    
    balance = total_ingresos - total_gastos
    
    recent_transactions = transacciones.order_by('-fecha')[:5]
    transactions_data = [{
        'id': t.id,
        'descripcion': t.descripcion,
        'monto': float(t.monto),
        'categoria': t.categoria.nombre if t.categoria else None,
        'categoria_color': t.categoria.color if t.categoria else '#6366f1',
        'categoria_icono': t.categoria.icono if t.categoria else 'bi-tag',
        'tipo': t.categoria.tipo if t.categoria else 'GASTO',
        'fecha': t.fecha.strftime('%Y-%m-%d'),
    } for t in recent_transactions]
    
    wishlist_data = [{
        'id': w.id,
        'item': w.item,
        'progreso': w.progreso(),
        'ahorrado': float(w.ahorrado),
        'objetivo': float(w.precio_objetivo),
        'imagen_url': w.imagen_url,
    } for w in wishlist[:3]]
    
    return JsonResponse({
        'balance': float(balance),
        'total_ingresos': float(total_ingresos),
        'total_gastos': float(total_gastos),
        'transacciones': transactions_data,
        'wishlist': wishlist_data,
    })

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def api_transaccion_create(request):
    """Create a new transaction via API"""
    try:
        data = json.loads(request.body)
        
        categoria_id = data.get('categoria_id')
        monto = data.get('monto')
        descripcion = data.get('descripcion', '')
        fecha = data.get('fecha')
        
        if not categoria_id or not monto:
            return JsonResponse({'error': 'Categoría y monto son requeridos'}, status=400)
        
        try:
            categoria = Categoria.objects.get(id=categoria_id, usuario=request.user)
        except Categoria.DoesNotExist:
            return JsonResponse({'error': 'Categoría no encontrada'}, status=404)
        
        with transaction.atomic():
            transaccion = Transaccion.objects.create(
                usuario=request.user,
                categoria=categoria,
                monto=monto,
                descripcion=descripcion,
                fecha=fecha
            )
        
        return JsonResponse({
            'success': True,
            'transaccion': {
                'id': transaccion.id,
                'monto': float(transaccion.monto),
                'descripcion': transaccion.descripcion,
                'fecha': transaccion.fecha.strftime('%Y-%m-%d'),
            }
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def api_transaccion_delete(request, transaccion_id):
    """Delete a transaction via API"""
    try:
        transaccion = Transaccion.objects.get(id=transaccion_id, usuario=request.user)
        transaccion.delete()
        return JsonResponse({'success': True})
    except Transaccion.DoesNotExist:
        return JsonResponse({'error': 'Transacción no encontrada'}, status=404)

@login_required
@require_http_methods(["GET"])
def api_categorias(request):
    """Get all categories for current user"""
    tipo = request.GET.get('tipo', None)
    
    categorias = Categoria.objects.filter(usuario=request.user)
    if tipo:
        categorias = categorias.filter(tipo=tipo)
    
    categorias_data = [{
        'id': c.id,
        'nombre': c.nombre,
        'icono': c.icono,
        'color': c.color,
        'tipo': c.tipo,
    } for c in categorias.order_by('nombre')]
    
    return JsonResponse({'categorias': categorias_data})

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def api_categoria_create(request):
    """Create a new category via API"""
    try:
        data = json.loads(request.body)
        
        nombre = data.get('nombre')
        tipo = data.get('tipo', 'GASTO')
        icono = data.get('icono', 'bi-tag')
        color = data.get('color', '#6366f1')
        
        if not nombre:
            return JsonResponse({'error': 'Nombre es requerido'}, status=400)
        
        categoria = Categoria.objects.create(
            usuario=request.user,
            nombre=nombre,
            tipo=tipo,
            icono=icono,
            color=color
        )
        
        return JsonResponse({
            'success': True,
            'categoria': {
                'id': categoria.id,
                'nombre': categoria.nombre,
                'icono': categoria.icono,
                'color': categoria.color,
                'tipo': categoria.tipo,
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["GET"])
def api_wishlist(request):
    """Get all wishlist items for current user"""
    wishlist = Wishlist.objects.filter(usuario=request.user)
    
    wishlist_data = [{
        'id': w.id,
        'item': w.item,
        'precio_objetivo': float(w.precio_objetivo),
        'ahorrado': float(w.ahorrado),
        'progreso': w.progreso(),
        'falta': float(w.falta()),
        'imagen_url': w.imagen_url,
        'enlace': w.enlace,
    } for w in wishlist]
    
    return JsonResponse({'wishlist': wishlist_data})

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def api_wishlist_create(request):
    """Create a new wishlist item via API"""
    try:
        data = json.loads(request.body)
        
        item = data.get('item')
        precio_objetivo = data.get('precio_objetivo')
        enlace = data.get('enlace', '')
        
        if not item or not precio_objetivo:
            return JsonResponse({'error': 'Item y precio objetivo son requeridos'}, status=400)
        
        wishlist = Wishlist.objects.create(
            usuario=request.user,
            item=item,
            precio_objetivo=precio_objetivo,
            enlace=enlace
        )
        
        return JsonResponse({
            'success': True,
            'wishlist': {
                'id': wishlist.id,
                'item': wishlist.item,
                'precio_objetivo': float(wishlist.precio_objetivo),
                'ahorrado': float(wishlist.ahorrado),
                'progreso': wishlist.progreso(),
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def api_wishlist_update(request, wishlist_id):
    """Update a wishlist item (add savings) via API"""
    try:
        data = json.loads(request.body)
        
        wishlist = Wishlist.objects.get(id=wishlist_id, usuario=request.user)
        
        if 'ahorrado' in data:
            wishlist.ahorrado = data['ahorrado']
        
        wishlist.save()
        
        return JsonResponse({
            'success': True,
            'wishlist': {
                'id': wishlist.id,
                'ahorrado': float(wishlist.ahorrado),
                'progreso': wishlist.progreso(),
                'falta': float(wishlist.falta()),
            }
        })
    except Wishlist.DoesNotExist:
        return JsonResponse({'error': 'Meta no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["GET"])
def api_monthly_data(request):
    """Get monthly data for charts"""
    from datetime import datetime, timedelta
    from django.db.models.functions import TruncMonth
    
    meses = int(request.GET.get('meses', 6))
    
    transacciones = Transaccion.objects.filter(usuario=request.user)
    six_months_ago = datetime.now() - timedelta(days=meses * 30)
    
    monthly_data = transacciones.filter(fecha__gte=six_months_ago).annotate(
        month=TruncMonth('fecha')
    ).values('month').annotate(
        ingresos=Sum('monto', filter=Q(categoria__tipo='INGRESO')),
        gastos=Sum('monto', filter=Q(categoria__tipo='GASTO'))
    ).order_by('month')
    
    data = [{
        'mes': m['month'].strftime('%Y-%m'),
        'mes_nombre': m['month'].strftime('%b'),
        'ingresos': float(m['ingresos'] or 0),
        'gastos': float(m['gastos'] or 0),
        'balance': float((m['ingresos'] or 0) - (m['gastos'] or 0)),
    } for m in monthly_data]
    
    return JsonResponse({'data': data})
