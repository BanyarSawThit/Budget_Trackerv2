from django import template

register = template.Library()

@register.filter
def convert(amount, rate):


    return round(amount * rate)
