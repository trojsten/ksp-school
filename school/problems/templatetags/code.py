from django import template
from django.db.models.fields.files import FieldFile
from django.utils.safestring import mark_safe
from pygments import highlight as pyg_highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer

from school.utils import get_extension

register = template.Library()


@register.simple_tag()
def highlight(file: FieldFile | str, language: str | None = None):
    try:
        if isinstance(file, str):
            code = file
        else:
            with file.open("r") as f:
                code = f.read()
    except UnicodeDecodeError:
        return mark_safe(
            "<div><br>Nemožno zobraziť binárny súbor, skúste si ho stiahnuť.</div>"
        )

    if not language:
        assert isinstance(file, FieldFile)
        language = get_extension(file.name or "")

    try:
        lexer = get_lexer_by_name(language.lstrip("."))
    except ValueError:
        lexer = guess_lexer(code)

    return mark_safe(pyg_highlight(code, lexer, HtmlFormatter()))
