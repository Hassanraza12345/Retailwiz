# api_integration/templatetags/math_filters.py

from django import template

register = template.Library()

@register.filter 
def apply_discount(price, discount_percentage):
    discount_amount = price * (discount_percentage / 100)
    final_price = price - discount_amount
    return final_price

@register.filter 
def discount_amount(price, discount_percentage):
    discount_amount = price * (discount_percentage / 100)
    return discount_amount

@register.filter(name='multiply')
def multiply(value, arg):
    try:
        return value * arg
    except (ValueError, TypeError):
        return None