from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def divide(value, arg):
    """Divide value by arg"""
    try:
        if arg == 0:
            return 0
        return float(value) / float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def multiply(value, arg):
    """Multiply value by arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def sub(value, arg):
    """Subtract arg from value"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def percentage(value, total):
    """Calculate percentage"""
    try:
        if total == 0 or total == Decimal('0'):
            return 0
        return (float(value) / float(total)) * 100
    except (ValueError, TypeError):
        return 0

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    try:
        return dictionary.get(int(key), 0)
    except (AttributeError, TypeError):
        return 0
