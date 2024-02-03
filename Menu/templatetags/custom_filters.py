# your_app/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def total_price(order_items):
    total = sum(item.price * item.quantity for item in order_items)
    return "{:.2f}".format(total)
