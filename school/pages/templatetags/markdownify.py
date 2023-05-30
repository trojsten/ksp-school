from django import template
from django.utils.safestring import mark_safe
from markdown import markdown

from school.pages.markdown_extensions import *

register = template.Library()


@register.filter
def markdownify(content):
    return mark_safe(
        markdown(
            content,
            extensions=[
                "abbr",
                "admonition",
                "attr_list",
                "fenced_code",
                "codehilite",
                "footnotes",
                "md_in_html",
                "sane_lists",
                "tables",
                KspSchoolExtension(),
            ],
        )
    )
