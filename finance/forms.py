from django import forms
from .models import Transaccion, Wishlist
from decimal import Decimal

class TransaccionForm(forms.ModelForm):
    class Meta:
        model = Transaccion
        fields = ['categoria', 'monto', 'descripcion', 'fecha']
        widgets = {
            'fecha': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'style': 'width: 100%; padding: 0.75rem 1rem; background: var(--dark-bg-secondary); border: 1px solid var(--border); border-radius: var(--radius-md); color: var(--text);'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select',
                'style': 'width: 100%; padding: 0.75rem 1rem; background: var(--dark-bg-secondary); border: 1px solid var(--border); border-radius: var(--radius-md); color: var(--text);'
            }),
            'monto': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'style': 'width: 100%; padding: 0.75rem 1rem; background: var(--dark-bg-secondary); border: 1px solid var(--border); border-radius: var(--radius-md); color: var(--text);'
            }),
            'descripcion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Compra en supermercado',
                'style': 'width: 100%; padding: 0.75rem 1rem; background: var(--dark-bg-secondary); border: 1px solid var(--border); border-radius: var(--radius-md); color: var(--text);'
            }),
        }
        labels = {
            'categoria': 'Categoría',
            'monto': 'Monto',
            'descripcion': 'Descripción',
            'fecha': 'Fecha'
        }

    def clean_monto(self):
        monto = self.cleaned_data.get('monto')
        if monto is not None:
            if monto <= 0:
                raise forms.ValidationError('El monto debe ser mayor a 0')
            if monto > Decimal('1000000'):
                raise forms.ValidationError('El monto parece demasiado alto (máximo: $1,000,000)')
        return monto

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion', '').strip()
        if len(descripcion) > 200:
            raise forms.ValidationError('La descripción es demasiado larga (máximo 200 caracteres)')
        return descripcion


class WishlistForm(forms.ModelForm):
    class Meta:
        model = Wishlist
        fields = ['item', 'precio_objetivo', 'enlace']
        widgets = {
            'item': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. PlayStation 5',
                'style': 'width: 100%; padding: 0.75rem 1rem; background: var(--dark-bg-secondary); border: 1px solid var(--border); border-radius: var(--radius-md); color: var(--text);'
            }),
            'precio_objetivo': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'style': 'width: 100%; padding: 0.75rem 1rem; background: var(--dark-bg-secondary); border: 1px solid var(--border); border-radius: var(--radius-md); color: var(--text);'
            }),
            'enlace': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://amazon.com/...',
                'style': 'width: 100%; padding: 0.75rem 1rem; background: var(--dark-bg-secondary); border: 1px solid var(--border); border-radius: var(--radius-md); color: var(--text);'
            }),
        }
        labels = {
            'item': 'Nombre del objetivo',
            'precio_objetivo': 'Precio objetivo',
            'enlace': 'Enlace del producto (opcional)'
        }

    def clean_precio_objetivo(self):
        precio = self.cleaned_data.get('precio_objetivo')
        if precio is not None:
            if precio <= 0:
                raise forms.ValidationError('El precio debe ser mayor a 0')
            if precio > Decimal('1000000'):
                raise forms.ValidationError('El precio parece demasiado alto (máximo: $1,000,000)')
        return precio

    def clean_item(self):
        item = self.cleaned_data.get('item', '').strip()
        if len(item) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres')
        if len(item) > 100:
            raise forms.ValidationError('El nombre es demasiado largo (máximo 100 caracteres)')
        return item