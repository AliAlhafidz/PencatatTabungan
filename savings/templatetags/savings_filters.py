from django import template
from decimal import Decimal

register = template.Library()

@register.filter(name='rupiah')
def rupiah(value):
    if value is None or value == '':
        return 'Rp 0'
    try:
        val = float(value)
        # format with dots as thousands separator
        formatted = f"{val:,.0f}".replace(',', '.')
        return f"Rp {formatted}"
    except (ValueError, TypeError):
        return f"Rp {value}"

@register.filter(name='thousands')
def thousands(value):
    if value is None or value == '':
        return '0'
    try:
        val = float(value)
        return f"{val:,.0f}".replace(',', '.')
    except (ValueError, TypeError):
        return str(value)

@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)
