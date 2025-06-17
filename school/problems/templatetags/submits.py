from typing import List

from django import template
from django.utils.safestring import mark_safe

from school.problems.models import Submit
from school.problems.utils import get_judge_client

register = template.Library()


@register.inclusion_tag("problems/tags/submit_list.html")
def submit_list(submits: List[Submit], lesson_item_id=None):
    return {"submits": submits, "lesson_item_id": lesson_item_id}


@register.inclusion_tag("problems/tags/submit_form.html")
def submit_form(problem, lesson_item_id=None):
    return {"problem": problem, "lesson_item_id": lesson_item_id}


@register.simple_tag()
def judge_embed_script():
    judge_client = get_judge_client()
    return mark_safe(f'<script async src="{judge_client.embed_script_url}"></script>')
