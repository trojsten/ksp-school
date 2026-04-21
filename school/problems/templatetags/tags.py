from typing import Any

from django import template
from django.template.defaulttags import querystring

register = template.Library()


@register.simple_tag(takes_context=True)
def tagquery(
    context, name: str, active_tags: set[Any], tag: Any, *args, **kwargs
) -> str:
    if tag in active_tags:
        new_tags = active_tags - {tag}
    else:
        new_tags = active_tags | {tag}
    kwargs[name] = list(new_tags)

    return querystring(context, *args, **kwargs)
