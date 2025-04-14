from django import template
from django.db.models import Sum, F

register = template.Library()

@register.filter
def sum_items_price(items):
    return items.aggregate(
        total=Sum(F('product__price') * F('quantity'))
    )['total'] or 0