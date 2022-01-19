from django import template
from django.utils.safestring import mark_safe
from pygments import highlight as pyg_highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer

register = template.Library()


@register.simple_tag()
def highlight(code, language):
    try:
        lexer = get_lexer_by_name(language)
    except ValueError:
        lexer = guess_lexer(code)

    return mark_safe(pyg_highlight(code, lexer, HtmlFormatter()))
