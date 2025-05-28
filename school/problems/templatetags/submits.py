from itertools import groupby
from operator import attrgetter
from typing import List

from django import template

from school.problems.constants import VERDICT_ICONS
from school.problems.models import Submit

register = template.Library()


@register.inclusion_tag("problems/tags/thermometers.html", takes_context=True)
def thermometers(context, submit: Submit):
    protocol = submit.protocol_object

    if not protocol.tests:
        return

    batch_tests = groupby(
        sorted(protocol.tests, key=attrgetter("batch")), key=lambda test: test.batch
    )
    batches = []

    for _, tests in batch_tests:
        tests = list(tests)
        for t in tests:
            t.verdict.human_name = t.verdict.get_human_name("sk")
            t.verdict.icon = VERDICT_ICONS.get(t.verdict, "circle")
        detail_visible = [
            submit.problem.detail_visible
            or context["request"].user.is_staff
            or "sample" in test.name
            for test in tests
        ]
        batches.append(
            {
                "score": int(
                    100 * sum(map(lambda test: test.score, tests)) // len(tests)
                ),
                "name": tests[0].batch,
                "tests": list(zip(tests, detail_visible)),
            }
        )

    return {
        "submit": submit,
        "protocol": protocol,
        "batches": batches,
    }


@register.inclusion_tag("problems/tags/submit_list.html")
def submit_list(submits: List[Submit], lesson_item_id=None):
    return {"submits": submits, "lesson_item_id": lesson_item_id}


@register.inclusion_tag("problems/tags/submit_form.html")
def submit_form(problem, lesson_item_id=None):
    return {"problem": problem, "lesson_item_id": lesson_item_id}
