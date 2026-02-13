from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from finance import views, api_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Public pages
    path('', views.home, name='home'), 
    
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='finance/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    
    # Password Change
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='finance/password_change.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='finance/password_change_done.html'), name='password_change_done'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # API - Chart Data (existing)
    path('api/chart-data/', api_views.chart_data_api, name='chart_data_api'),
    
    # API - Dashboard Data
    path('api/dashboard/', api_views.api_dashboard_data, name='api_dashboard'),
    
    # API - Transactions
    path('api/transacciones/', api_views.api_transaccion_create, name='api_transaccion_create'),
    path('api/transacciones/<int:transaccion_id>/', api_views.api_transaccion_delete, name='api_transaccion_delete'),
    
    # API - Categories
    path('api/categorias/', api_views.api_categorias, name='api_categorias'),
    path('api/categorias/crear/', api_views.api_categoria_create, name='api_categoria_create'),
    
    # API - Wishlist
    path('api/wishlist/', api_views.api_wishlist, name='api_wishlist'),
    path('api/wishlist/crear/', api_views.api_wishlist_create, name='api_wishlist_create'),
    path('api/wishlist/<int:wishlist_id>/', api_views.api_wishlist_update, name='api_wishlist_update'),
    
    # API - Monthly Data
    path('api/monthly/', api_views.api_monthly_data, name='api_monthly_data'),
    
    # Export
    path('export/excel/', views.export_excel, name='export_excel'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
    
    # Wishlist - Agregar dinero
    path('metas/<int:wishlist_id>/agregar-dinero/', views.agregar_dinero_meta, name='agregar_dinero_meta'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)