from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Sum, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Transaccion, Wishlist, UserProfile, Categoria
from .forms import TransaccionForm, WishlistForm
import urllib.request
import re
from urllib.parse import urlparse
from datetime import datetime, timedelta
from calendar import monthrange

def home(request):
    return render(request, 'finance/landing.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'¡Bienvenido a Wallet Flow, {user.username}! Tu cuenta ha sido creada exitosamente.')
            return redirect('dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserCreationForm()
    return render(request, 'finance/register.html', {'form': form})

@login_required
def dashboard(request):
    # Get date filters from query params
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    mes_filtro = request.GET.get('mes')
    anio_filtro = request.GET.get('anio')
    
    # Base queryset
    transacciones_base = Transaccion.objects.filter(usuario=request.user)
    wishlist = Wishlist.objects.filter(usuario=request.user)
    
    # Apply filters
    if mes_filtro and anio_filtro:
        try:
            mes = int(mes_filtro)
            anio = int(anio_filtro)
            _, last_day = monthrange(anio, mes)
            fecha_inicio = datetime(anio, mes, 1).date()
            fecha_fin = datetime(anio, mes, last_day).date()
        except (ValueError, TypeError):
            pass
    
    if fecha_inicio:
        try:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            transacciones_base = transacciones_base.filter(fecha__gte=fecha_inicio)
        except ValueError:
            pass
    
    if fecha_fin:
        try:
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            transacciones_base = transacciones_base.filter(fecha__lte=fecha_fin)
        except ValueError:
            pass
    
    transacciones = transacciones_base.order_by('-fecha')
    
    # Pagination
    paginator = Paginator(transacciones, 20)  # 20 items per page
    page = request.GET.get('page', 1)
    
    try:
        transacciones_paginated = paginator.page(page)
    except PageNotAnInteger:
        transacciones_paginated = paginator.page(1)
    except EmptyPage:
        transacciones_paginated = paginator.page(paginator.num_pages)
    
    # Ensure user profile exists
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    # Calculate totals - ALWAYS use ALL transactions (ignore filters)
    all_transacciones_for_totals = Transaccion.objects.filter(usuario=request.user)
    total_ingresos = all_transacciones_for_totals.filter(
        categoria__isnull=False,
        categoria__tipo='INGRESO'
    ).aggregate(Sum('monto'))['monto__sum'] or 0
    
    total_gastos = all_transacciones_for_totals.filter(
        categoria__isnull=False,
        categoria__tipo='GASTO'
    ).aggregate(Sum('monto'))['monto__sum'] or 0
    
    balance = total_ingresos - total_gastos

    # 1. Inicializar formularios vacíos por defecto
    form_transaccion = TransaccionForm()
    form_wishlist = WishlistForm()

    if request.method == 'POST':
        if 'btn_transaccion' in request.POST:
            # 2. Si se envía transacción, llenamos ese form con los datos
            form_transaccion = TransaccionForm(request.POST)
            if form_transaccion.is_valid():
                t = form_transaccion.save(commit=False)
                t.usuario = request.user
                t.save()
                messages.success(request, 'Movimiento registrado correctamente.')
                return redirect('dashboard')
            else:
                messages.error(request, 'Error al registrar el movimiento.')


        elif 'btn_wishlist' in request.POST:
            form_wishlist = WishlistForm(request.POST)
            if form_wishlist.is_valid():
                w = form_wishlist.save(commit=False)
                w.usuario = request.user
                
                # Auto-scrape image if link provided with security checks
                if w.enlace:
                    try:
                        # Validate domain
                        parsed_url = urlparse(w.enlace)
                        allowed_domains = ['amazon.com', 'amazon.es', 'mercadolibre.com', 'ebay.com', 'aliexpress.com']
                        
                        if any(domain in parsed_url.netloc for domain in allowed_domains):
                            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                            req = urllib.request.Request(w.enlace, headers=headers)
                            
                            with urllib.request.urlopen(req, timeout=10) as response:
                                html = response.read().decode('utf-8', errors='ignore')
                                # Search for og:image meta tag
                                match = re.search(r'<meta\s+property=["\']og:image["\']\s+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
                                if match:
                                    w.imagen_url = match.group(1)
                                    messages.success(request, 'Meta añadida con éxito. Imagen obtenida automáticamente.')
                                else:
                                    messages.info(request, 'Meta añadida. No se pudo obtener la imagen automáticamente.')
                        else:
                            messages.warning(request, 'Meta añadida. El dominio no está en la lista de sitios permitidos para scraping.')
                    except Exception as e:
                        messages.warning(request, f'Meta añadida. No se pudo obtener la imagen: {str(e)}')
                else:
                    messages.success(request, 'Meta añadida con éxito.')

                w.save()
                return redirect('dashboard')
            else:
                for field, errors in form_wishlist.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')

        elif 'btn_profile' in request.POST:
            # Handle profile update with extended fields
            try:
                if request.FILES.get('avatar'):
                    profile.avatar = request.FILES['avatar']
                
                # Update basic profile fields
                profile.first_name = request.POST.get('first_name', '')
                profile.last_name = request.POST.get('last_name', '')
                profile.bio = request.POST.get('bio', '')
                profile.pronouns = request.POST.get('pronouns', '')
                profile.website = request.POST.get('website', '')
                
                # Update contact info
                profile.telefono = request.POST.get('telefono', '')
                profile.ubicacion = request.POST.get('ubicacion', '')
                profile.ocupacion = request.POST.get('ocupacion', '')
                profile.linkedin = request.POST.get('linkedin', '')
                profile.instagram = request.POST.get('instagram', '')
                
                # Try to parse date
                fecha_nac = request.POST.get('fecha_nacimiento', '')
                if fecha_nac:
                    from datetime import datetime
                    try:
                        profile.fecha_nacimiento = datetime.strptime(fecha_nac, '%Y-%m-%d').date()
                    except:
                        profile.fecha_nacimiento = None
                
                # Update financial settings
                try:
                    profile.meta_ingreso_mensual = float(request.POST.get('meta_ingreso_mensual', 2000))
                except:
                    profile.meta_ingreso_mensual = 2000
                
                try:
                    profile.meta_ahorro_mensual = int(request.POST.get('meta_ahorro_mensual', 20))
                except:
                    profile.meta_ahorro_mensual = 20
                
                try:
                    profile.inicio_mes = int(request.POST.get('inicio_mes', 1))
                except:
                    profile.inicio_mes = 1
                
                profile.moneda = request.POST.get('moneda', 'USD')
                
                # Update user email
                user.email = request.POST.get('email', '')
                user.save()
                
                profile.save()
                messages.success(request, 'Perfil actualizado correctamente.')
            except Exception as e:
                messages.error(request, f'Error al actualizar el perfil: {str(e)}')
            return redirect('dashboard')

        elif 'btn_categoria' in request.POST:
            # Handle category creation
            try:
                nombre = request.POST.get('nombre_categoria', '').strip()
                tipo = request.POST.get('tipo_categoria', 'GASTO')
                color = request.POST.get('color_categoria', '#6366f1')
                icono_input = request.POST.get('icono_categoria', '').strip()
                
                if nombre:
                    # Auto-detect icon based on emoji in name
                    icono = icono_input if icono_input else 'bi-tag'
                    
                    # Comprehensive emoji to icon mappings
                    emoji_map = {
                        # Comida y Restaurantes
                        '🍔': 'bi-cart', '🍕': 'bi-cup-hot', '🍜': 'bi-cup-hot',
                        '🥗': 'bi-cup-hot', '🍣': 'bi-cup-hot', '☕': 'bi-cup-hot',
                        '🍺': 'bi-cup-straw', '🍷': 'bi-cup', '🍩': 'bi-cookie',
                        '🧁': 'bi-cup-hot', '🥐': 'bi-cup-hot', '🍳': 'bi-cup-hot',
                        '🍽️': 'bi-cup-hot', '🥡': 'bi-cup-hot',
                        
                        # Transporte
                        '🚗': 'bi-car-front', '🚌': 'bi-bus-front', '🚕': 'bi-taxi-front',
                        '🚑': 'bi-ambulance', '🚒': 'bi-truck', '🚜': 'bi-tractor',
                        '⛽': 'bi-fuel-pump', '🅿️': 'bi-p-circle', '🚲': 'bi-bicycle',
                        '✈️': 'bi-airplane', '🚢': 'bi-boat', '🚝': 'bi-train',
                        
                        # Vivienda
                        '🏠': 'bi-house', '🏨': 'bi-building', '🏪': 'bi-shop',
                        '🏗️': 'bi-build', '🔑': 'bi-key', '🚪': 'bi-door-open',
                        '🛋️': 'bi-lamp', '🛏️': 'bi-bed', '🚿': 'bi-droplet',
                        '🧹': 'bi-stars', '🪣': 'bi-bucket', '🧺': 'bi-basket',
                        
                        # Tecnología y Trabajo
                        '💻': 'bi-laptop', '🖥️': 'bi-pc-display', '📱': 'bi-phone',
                        '📞': 'bi-telephone', '📺': 'bi-tv', '🎮': 'bi-controller',
                        '📷': 'bi-camera', '🎧': 'bi-headphones', '⌚': 'bi-smartwatch',
                        '💼': 'bi-briefcase', '📊': 'bi-bar-chart', '📈': 'bi-graph-up-arrow',
                        '📉': 'bi-graph-down-arrow', '💰': 'bi-cash-coin', '💵': 'bi-cash',
                        
                        # Entretenimiento
                        '🎬': 'bi-film', '🎵': 'bi-music-note-beamed', '🎤': 'bi-mic',
                        '🎭': 'bi-palette', '🎪': 'bi-tent', '🎢': 'bi-joystick',
                        '⚽': 'bi-trophy', '🏀': 'bi-disc', '🎱': 'bi-circle',
                        '🎯': 'bi-bullseye', '♟️': 'bi-dice-5', '🃏': 'bi-suit-club',
                        '🎰': 'bi-suit-diamond', '🎲': 'bi-dice-3',
                        
                        # Salud
                        '🏥': 'bi-hospital', '💊': 'bi-capsule', '🦷': 'bi-activity',
                        '👩‍⚕️': 'bi-person', '💉': 'bi-droplet-half', '🩺': 'bi-stethoscope',
                        '🧘': 'bi-person', '🏋️': 'bi-person', '🚴': 'bi-bicycle',
                        
                        # Educación
                        '📚': 'bi-book', '🎓': 'bi-mortarboard', '📖': 'bi-book-half',
                        '✏️': 'bi-pencil', '📝': 'bi-file-text', '🔬': 'bi-eyeglasses',
                        '💻': 'bi-laptop', '🎨': 'bi-palette',
                        
                        # Comunicación
                        '📧': 'bi-envelope', '📨': 'bi-inbox', '📩': 'bi-send',
                        '📲': 'bi-chat-dots', '💬': 'bi-chat-text', '📢': 'bi-soundwave',
                        '🔔': 'bi-bell', '📺': 'bi-tv',
                        
                        # Compras
                        '🛒': 'bi-cart', '🛍️': 'bi-bag', '👕': 'bi-shop-window',
                        '👟': 'bi-shoe', '💄': 'bi-brush', '🕶️': 'bi-eyeglasses',
                        '🧢': 'bi-hat', '🧤': 'bi-gloves', '🧣': 'bi-scarf',
                        '🎁': 'bi-gift', '💍': 'bi-gem', '🌸': 'bi-flower1',
                        
                        # Servicios
                        '💡': 'bi-lightbulb', '📄': 'bi-file-text', '🧾': 'bi-receipt',
                        '📦': 'bi-box', '📮': 'bi-postcard', '🔧': 'bi-tools',
                        '🔨': 'bi-hammer', '🪛': 'bi-wrench', '⚙️': 'bi-gear',
                        '🧰': 'bi-tools', '🔩': 'bi-nut', '🔌': 'bi-plug',
                        
                        # Banca y Finanzas
                        '🏦': 'bi-bank', '💳': 'bi-credit-card', '🏧': 'bi-cash-coin',
                        '💹': 'bi-graph-up-arrow', '📉': 'bi-graph-down', '💱': 'bi-currency-exchange',
                        '🔐': 'bi-shield-lock', '🔒': 'bi-lock', '🔓': 'bi-unlock',
                        
                        # Mascotas y Familia
                        '🐕': 'bi-inbox', '🐈': 'bi-inbox', '🐠': 'bi-inbox',
                        '👶': 'bi-person', '👨‍👩‍👧': 'bi-people', '🏠': 'bi-house-heart',
                        
                        # Otros
                        '🌟': 'bi-star', '⭐': 'bi-star-fill', '🔥': 'bi-fire',
                        '💎': 'bi-gem', '🎊': 'bi-stars', '🎉': 'bi-emoji-smile',
                        '❄️': 'bi-snow', '☀️': 'bi-brightness-high', '🌧️': 'bi-cloud-rain',
                        '⏰': 'bi-alarm', '⌛': 'bi-hourglass', '📅': 'bi-calendar-event',
                    }
                    
                    # Check for emoji in name and get matching icon
                    for emoji, icon in emoji_map.items():
                        if emoji in nombre:
                            icono = icon
                            break
                    
                    Categoria.objects.create(
                        usuario=request.user,
                        nombre=nombre,
                        tipo=tipo,
                        icono=icono,
                        color=color
                    )
                    messages.success(request, f'Categoría "{nombre}" creada correctamente.')
                else:
                    messages.error(request, 'El nombre de la categoría es obligatorio.')
            except Exception as e:
                messages.error(request, f'Error al crear la categoría: {str(e)}')
            return redirect('dashboard')

        elif 'btn_delete_categoria' in request.POST:
            # Handle category deletion (only user's own categories)
            try:
                categoria_id = request.POST.get('categoria_id')
                categoria = Categoria.objects.get(id=categoria_id, usuario=request.user)
                nombre = categoria.nombre
                categoria.delete()
                messages.success(request, f'Categoría "{nombre}" eliminada correctamente.')
            except Categoria.DoesNotExist:
                messages.error(request, 'La categoría no existe o no tienes permiso para eliminarla.')
            except Exception as e:
                messages.error(request, f'Error al eliminar la categoría: {str(e)}')
            return redirect('dashboard')


    # Get all categories for this user
    categorias_ingresos = Categoria.objects.filter(usuario=request.user, tipo='INGRESO').order_by('nombre')
    categorias_gastos = Categoria.objects.filter(usuario=request.user, tipo='GASTO').order_by('nombre')

    # Calculate breakdown by category
    gastos_por_categoria = []
    for categoria in categorias_gastos:
        total = transacciones.filter(
            categoria=categoria
        ).aggregate(Sum('monto'))['monto__sum'] or 0
        
        if total > 0:  # Only include categories with actual spending
            pct = round((float(total) / float(total_gastos)) * 100) if total_gastos > 0 else 0
            gastos_por_categoria.append({
                'nombre': categoria.nombre,
                'total': float(total),
                'color': categoria.color,
                'icono': categoria.icono,
                'porcentaje': pct
            })
    
    # Sort by total descending (highest first)
    gastos_por_categoria = sorted(gastos_por_categoria, key=lambda x: x['total'], reverse=True)
    
    ingresos_por_categoria = []
    for categoria in categorias_ingresos:
        total = transacciones.filter(
            categoria=categoria
        ).aggregate(Sum('monto'))['monto__sum'] or 0
        
        if total > 0:  # Only include categories with actual income
            ingresos_por_categoria.append({
                'nombre': categoria.nombre,
                'total': float(total),
                'color': categoria.color,
                'icono': categoria.icono
            })
    
    # Calculate financial health score (0-100)
    health_score = 0
    if total_ingresos > 0:
        # Factor 1: Savings rate (50% weight) - ideal is 20% or more
        savings_rate = (balance / total_ingresos) * 100 if total_ingresos > 0 else 0
        savings_score = min(savings_rate / 20 * 50, 50)  # Max 50 points
        
        # Factor 2: Expense ratio (30% weight) - expenses should be < 80% of income
        expense_ratio = (total_gastos / total_ingresos) * 100 if total_ingresos > 0 else 100
        expense_score = max(30 - (expense_ratio - 50) / 30 * 30, 0) if expense_ratio > 50 else 30
        
        # Factor 3: Positive balance (20% weight)
        balance_score = 20 if balance > 0 else 0
        
        health_score = min(int(savings_score + expense_score + balance_score), 100)
    
    # Determine health status
    if health_score >= 80:
        health_status = "Excelente"
        health_color = "#10b981"
    elif health_score >= 60:
        health_status = "Bueno"
        health_color = "#22c55e"
    elif health_score >= 40:
        health_status = "Regular"
        health_color = "#f59e0b"
    else:
        health_status = "Necesita Atención"
        health_color = "#ef4444"

    # Calculate monthly trends - show last 12 months
    from datetime import datetime, timedelta
    from django.db.models.functions import TruncMonth
    
    # Calculate monthly trends for chart - ALL AVAILABLE MONTHS
    from datetime import datetime, timedelta
    from django.db.models.functions import TruncMonth
    from calendar import monthrange
    
    # Get ALL transactions grouped by month
    all_transacciones_for_chart = Transaccion.objects.filter(usuario=request.user)
    
    # Get all months that have any data
    monthly_data = all_transacciones_for_chart.annotate(
        month=TruncMonth('fecha')
    ).values('month').annotate(
        ingresos=Sum('monto', filter=Q(categoria__tipo='INGRESO')),
        gastos=Sum('monto', filter=Q(categoria__tipo='GASTO'))
    ).order_by('month')
    
    # Format for chart - use all available months
    monthly_labels = []
    monthly_ingresos = []
    monthly_gastos = []
    
    for data in monthly_data:
        month_name = data['month'].strftime('%b %Y')  # Jan 2025, Feb 2025, etc.
        monthly_labels.append(month_name)
        monthly_ingresos.append(float(data['ingresos'] or 0))
        monthly_gastos.append(float(data['gastos'] or 0))
    
    # If no data, show empty chart
    if not monthly_labels:
        monthly_labels = ['Sin datos']
        monthly_ingresos = [0]
        monthly_gastos = [0]

    # Calculate percentages
    if total_ingresos > 0:
        gasto_porcentaje = round((float(total_gastos) / float(total_ingresos)) * 100)
        ahorro_porcentaje = round((float(balance) / float(total_ingresos)) * 100)
    else:
        gasto_porcentaje = 0
        ahorro_porcentaje = 0
    
    # Calculate expenses by day of month (1-31)
    from django.db.models import Count
    expenses_by_day = {}
    for day in range(1, 32):
        day_expenses = transacciones.filter(
            categoria__tipo='GASTO',
            fecha__day=day
        ).aggregate(Sum('monto'))['monto__sum'] or 0
        expenses_by_day[day] = float(day_expenses)
    
    context = {
        'transacciones': transacciones_paginated,
        'wishlist': wishlist,
        'total_ingresos': total_ingresos,
        'total_gastos': total_gastos,
        'balance': balance,
        'form_transaccion': form_transaccion,
        'form_wishlist': form_wishlist,
        'user_profile': profile,
        'categorias_ingresos': categorias_ingresos,
        'categorias_gastos': categorias_gastos,
        'gastos_por_categoria': gastos_por_categoria,
        'ingresos_por_categoria': ingresos_por_categoria,
        'health_score': health_score,
        'health_status': health_status,
        'health_color': health_color,
        'monthly_labels': monthly_labels,
        'monthly_ingresos': monthly_ingresos,
        'monthly_gastos': monthly_gastos,
        # Calculated percentages
        'gasto_porcentaje': gasto_porcentaje,
        'ahorro_porcentaje': ahorro_porcentaje,
        # Date filters
        'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d') if fecha_inicio else '',
        'fecha_fin': fecha_fin.strftime('%Y-%m-%d') if fecha_fin else '',
        'mes_filtro': mes_filtro if 'mes_filtro' in locals() else '',
        'anio_filtro': anio_filtro if 'anio_filtro' in locals() else '',
        'expenses_by_day': expenses_by_day,
    }
    return render(request, 'finance/dashboard.html', context)


@login_required
def export_excel(request):
    from django.http import HttpResponse
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter
    from datetime import datetime
    
    # Get transactions
    transacciones = Transaccion.objects.filter(
        usuario=request.user
    ).select_related('categoria').order_by('-fecha')
    
    # Create workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Resumen Financiero"
    
    # Styles
    header_font = Font(bold=True, color="FFFFFF", size=12)
    header_fill = PatternFill(start_color="6366F1", end_color="6366F1", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center")
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # Title
    ws.merge_cells('A1:E1')
    ws['A1'] = f"Wallet Flow - Reporte Financiero"
    ws['A1'].font = Font(bold=True, size=16)
    ws['A1'].alignment = Alignment(horizontal="center")
    
    # Date
    ws.merge_cells('A2:E2')
    ws['A2'] = f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    ws['A2'].alignment = Alignment(horizontal="center")
    ws['A2'].font = Font(italic=True, size=10)
    
    # Summary section
    total_ingresos = sum(t.monto for t in transacciones.filter(categoria__tipo='INGRESO'))
    total_gastos = sum(t.monto for t in transacciones.filter(categoria__tipo='GASTO'))
    balance = total_ingresos - total_gastos
    
    ws['A4'] = "RESUMEN"
    ws['A4'].font = Font(bold=True, size=14)
    
    ws['A5'] = "Total Ingresos:"
    ws['B5'] = f"${total_ingresos:,.2f}"
    ws['B5'].font = Font(color="10B981", bold=True)
    
    ws['A6'] = "Total Gastos:"
    ws['B6'] = f"${total_gastos:,.2f}"
    ws['B6'].font = Font(color="EF4444", bold=True)
    
    ws['A7'] = "Balance:"
    ws['B7'] = f"${balance:,.2f}"
    ws['B7'].font = Font(color="6366F1", bold=True)
    
    # Transaction table
    row = 10
    headers = ["Fecha", "Descripción", "Categoría", "Tipo", "Monto"]
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=row, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = thin_border
    
    # Data
    for t in transacciones:
        row += 1
        ws.cell(row=row, column=1, value=t.fecha.strftime('%d/%m/%Y'))
        ws.cell(row=row, column=2, value=t.descripcion or t.categoria.nombre)
        ws.cell(row=row, column=3, value=t.categoria.nombre)
        ws.cell(row=row, column=4, value="Ingreso" if t.categoria.tipo == 'INGRESO' else "Gasto")
        
        monto_cell = ws.cell(row=row, column=5)
        if t.categoria.tipo == 'INGRESO':
            monto_cell.value = t.monto
            monto_cell.font = Font(color="10B981")
        else:
            monto_cell.value = -t.monto
            monto_cell.font = Font(color="EF4444")
        
        for col in range(1, 6):
            ws.cell(row=row, column=col).border = thin_border
    
    # Adjust column widths
    ws.column_dimensions['A'].width = 12
    ws.column_dimensions['B'].width = 30
    ws.column_dimensions['C'].width = 20
    ws.column_dimensions['D'].width = 10
    ws.column_dimensions['E'].width = 15
    
    # Response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="walletflow_reporte_{datetime.now().strftime("%Y%m%d")}.xlsx"'
    wb.save(response)
    return response


@login_required
def export_pdf(request):
    from django.http import HttpResponse
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from datetime import datetime
    
    # Get data
    transacciones = Transaccion.objects.filter(
        usuario=request.user
    ).select_related('categoria').order_by('-fecha')[:50]
    
    total_ingresos = sum(t.monto for t in transacciones.filter(categoria__tipo='INGRESO'))
    total_gastos = sum(t.monto for t in transacciones.filter(categoria__tipo='GASTO'))
    balance = total_ingresos - total_gastos
    
    # Create PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="walletflow_reporte_{datetime.now().strftime("%Y%m%d")}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#6366f1'),
        spaceAfter=30
    )
    elements.append(Paragraph("Wallet Flow - Reporte Financiero", title_style))
    
    # Date
    elements.append(Paragraph(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Summary
    summary_data = [
        ['RESUMEN', ''],
        ['Total Ingresos:', f"${float(total_ingresos):,.2f}"],
        ['Total Gastos:', f"${float(total_gastos):,.2f}"],
        ['Balance:', f"${float(balance):,.2f}"]
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366f1')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TEXTCOLOR', (0, 1), (-1, 1), colors.HexColor('#10b981')),
        ('TEXTCOLOR', (0, 2), (-1, 2), colors.HexColor('#ef4444')),
        ('TEXTCOLOR', (0, 3), (-1, 3), colors.HexColor('#6366f1')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 30))
    
    # Transactions table
    elements.append(Paragraph("Transacciones", styles['Heading2']))
    elements.append(Spacer(1, 10))
    
    data = [['Fecha', 'Descripción', 'Categoría', 'Tipo', 'Monto']]
    
    for t in transacciones:
        tipo_str = "Ingreso" if t.categoria.tipo == 'INGRESO' else "Gasto"
        monto_str = f"${float(t.monto):,.2f}"
        data.append([
            t.fecha.strftime('%d/%m/%Y'),
            t.descripcion or t.categoria.nombre,
            t.categoria.nombre,
            tipo_str,
            monto_str
        ])
    
    table = Table(data, colWidths=[1*inch, 2*inch, 1.5*inch, 1*inch, 1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366f1')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(table)
    
    # Build PDF
    doc.build(elements)
    return response


@login_required
def agregar_dinero_meta(request, wishlist_id):
    """Vista para agregar dinero a una meta de ahorro"""
    from django.shortcuts import get_object_or_404
    from .models import Wishlist
    from decimal import Decimal
    
    # Obtener la meta
    meta = get_object_or_404(Wishlist, id=wishlist_id, usuario=request.user)
    
    if request.method == 'POST':
        try:
            monto = Decimal(request.POST.get('monto', '0'))
            
            if monto <= 0:
                messages.error(request, 'El monto debe ser mayor a 0')
            else:
                # Agregar el dinero a la meta
                meta.ahorrado += monto
                
                # Verificar si se completó la meta
                if meta.ahorrado >= meta.precio_objetivo:
                    messages.success(request, f'¡Felicitaciones! Has completado la meta de {meta.item} 🎉')
                else:
                    messages.success(request, f'Agregaste ${monto} a tu meta. ¡Vas por buen camino! 💪')
                
                meta.save()
                
        except Exception as e:
            messages.error(request, f'Error al agregar dinero: {str(e)}')
    
    return redirect('dashboard')