from django import template

register = template.Library()


@register.simple_tag()
def percent(value, max_value):
    return f"{float(value) / float(max_value) * 100:0.2f}"
