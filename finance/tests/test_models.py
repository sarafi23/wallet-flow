from django.test import TestCase
from django.contrib.auth.models import User
from finance.models import Categoria, Transaccion, Wishlist, UserProfile
from decimal import Decimal
from datetime import date


class CategoriaModelTest(TestCase):
    """Tests para el modelo Categoria"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
    def test_crear_categoria(self):
        """Test de creación de categoría"""
        categoria = Categoria.objects.create(
            nombre='Comida',
            tipo='GASTO',
            icono='bi-cart'
        )
        self.assertEqual(categoria.nombre, 'Comida')
        self.assertEqual(categoria.tipo, 'GASTO')
        self.assertIn('Comida', str(categoria))


class TransaccionModelTest(TestCase):
    """Tests para el modelo Transaccion"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.categoria = Categoria.objects.create(
            nombre='Salario',
            tipo='INGRESO'
        )
        
    def test_crear_transaccion(self):
        """Test de creación de transacción"""
        transaccion = Transaccion.objects.create(
            usuario=self.user,
            categoria=self.categoria,
            monto=Decimal('5000.00'),
            descripcion='Salario mensual',
            fecha=date.today()
        )
        self.assertEqual(transaccion.monto, Decimal('5000.00'))
        self.assertIn('INGRESO', str(transaccion))
        self.assertTrue(transaccion.activo)


class WishlistModelTest(TestCase):
    """Tests para el modelo Wishlist (Metas de Ahorro)"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
    def test_crear_meta(self):
        """Test de creación de meta de ahorro"""
        meta = Wishlist.objects.create(
            usuario=self.user,
            item='Casa nueva',
            precio_objetivo=Decimal('500000.00'),
            ahorrado=Decimal('50000.00'),
            prioridad=3
        )
        self.assertEqual(meta.item, 'Casa nueva')
        self.assertEqual(meta.progreso(), 10)  # 50000/500000 * 100
        
    def test_progreso_cero(self):
        """Test de progreso cuando no hay ahorrado"""
        meta = Wishlist.objects.create(
            usuario=self.user,
            item='Vacaciones',
            precio_objetivo=Decimal('10000.00'),
            ahorrado=Decimal('0.00')
        )
        self.assertEqual(meta.progreso(), 0)
        
    def test_progreso_completo(self):
        """Test de progreso al 100%"""
        meta = Wishlist.objects.create(
            usuario=self.user,
            item='Computadora',
            precio_objetivo=Decimal('1500.00'),
            ahorrado=Decimal('1500.00')
        )
        self.assertEqual(meta.progreso(), 100)
        
    def test_falta_calculo(self):
        """Test de cuánto falta para completar la meta"""
        meta = Wishlist.objects.create(
            usuario=self.user,
            item='Moto',
            precio_objetivo=Decimal('20000.00'),
            ahorrado=Decimal('5000.00')
        )
        self.assertEqual(meta.falta(), Decimal('15000.00'))


class UserProfileModelTest(TestCase):
    """Tests para el modelo UserProfile"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
    def test_perfil_creado_automaticamente(self):
        """Test que el perfil se crea automáticamente vía signal"""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsNotNone(self.user.profile)
        
    def test_get_avatar_url_sin_imagen(self):
        """Test de URL de avatar cuando no hay imagen"""
        url = self.user.profile.get_avatar_url()
        self.assertIn('ui-avatars.com', url)
        self.assertIn(self.user.username, url)
        
    def test_get_full_name_con_datos(self):
        """Test de nombre completo cuando hay datos"""
        profile = self.user.profile
        profile.first_name = 'Juan'
        profile.last_name = 'Pérez'
        profile.save()
        
        self.assertEqual(profile.get_full_name(), 'Juan Pérez')
        
    def test_get_full_name_sin_datos(self):
        """Test de nombre completo sin datos devuelve username"""
        full_name = self.user.profile.get_full_name()
        self.assertEqual(full_name, 'testuser')


