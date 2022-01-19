from itertools import groupby
from typing import List

from django import template
from django.urls import reverse
from judge_client.client import ProtocolTest

from school.problems.models import Submit

register = template.Library()


@register.inclusion_tag("problems/thermometers.html")
def thermometers(submit: Submit):
    protocol = submit.protocol_object

    def get_test_batch(test: ProtocolTest):
        num, _ = test.name.split(".", 1)
        try:
            return int(num)
        except ValueError:
            return test.name

    batch_tests = groupby(protocol.tests, key=get_test_batch)
    batches = []

    for _, tests in batch_tests:
        tests = list(tests)
        batches.append(
            {
                "score": 100
                * len(list(filter(lambda x: x.result == "OK", tests)))
                // len(tests),
                "tests": tests,
            }
        )

    return {"submit": submit, "protocol": protocol, "batches": batches}


@register.inclusion_tag("problems/submit_list.html")
def submit_list(submits: List[Submit], lesson_item_id=None):
    return {"submits": submits, "lesson_item_id": lesson_item_id}


@register.inclusion_tag("problems/tags/submit_form.html")
def submit_form(problem, lesson_item_id=None):
    return {"problem": problem, "lesson_item_id": lesson_item_id}
