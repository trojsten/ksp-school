from typing import Any

from django import template
from django.template.defaulttags import querystring
from django.urls import reverse

from school.problems.models import Problem, Tag

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


def _parse_tag(
    tag,
    background="bg-blue-900",
    highlighted_background="bg-blue-600",
    color="text-gray-400",
    highlighted_color="text-white",
    icon=None,
    link=None,
    tooltip=None,
    highlighted=False,
):
    if isinstance(tag, Tag) and not link:
        link = reverse("problem_list", query={"tags": tag})
        tag = tag.name

    if isinstance(tag, Problem.ProblemDifficulty):
        if link is None:
            link = reverse("problem_list", query={"difficulty": tag.value})
        match tag.value:
            case "basics":
                background = "bg-cyan-900"
                highlighted_background = "bg-cyan-600"
                color = "text-cyan-600"
                highlighted_color = "text-cyan-400"
                tooltip = "Úloha by mala byť zvládnuteľná začiatočníkmi."
            case "easy":
                background = "bg-green-900"
                highlighted_background = "bg-green-600"
                color = "text-green-600"
                highlighted_color = "text-green-400"
                tooltip = "Úloha by mala byť zvládnuteľná bez väčších problémov."
            case "medium":
                background = "bg-yellow-900"
                highlighted_background = "bg-yellow-600"
                color = "text-yellow-600"
                highlighted_color = "text-yellow-400"
                tooltip = "Úloha nemusí mať úplne priamočiare riešenie."
            case "hard":
                background = "bg-orange-900"
                highlighted_background = "bg-orange-600"
                color = "text-orange-600"
                highlighted_color = "text-orange-400"
                tooltip = "Úloha vyžaduje pokročilé vedomosti z iných kurzov."
            case "very-hard":
                background = "bg-red-900"
                highlighted_background = "bg-red-600"
                color = "text-red-600"
                highlighted_color = "text-red-400"
                tooltip = "Úloha vyžaduje pokročilé algoritmické myslenie a hľadanie neštandardných riešení."
            case "unknown":
                background = "bg-gray-900"
                highlighted_background = "bg-gray-600"
                color = "text-gray-600"
                highlighted_color = "text-gray-400"
                tooltip = "Here be dragons."
        tag = tag.label

    if highlighted:
        background = highlighted_background
        color = highlighted_color

    return {
        "tag": tag,
        "background": background,
        "color": color,
        "icon": icon,
        "link": link,
        "tooltip": tooltip,
    }


@register.inclusion_tag("problems/_partials/tag.html")
def render_tag(*args, **kwargs):
    return _parse_tag(*args, **kwargs)


@register.inclusion_tag("problems/_partials/icon.html")
def render_icon(*args, **kwargs):
    return _parse_tag(*args, **kwargs)
