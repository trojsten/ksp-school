from itertools import groupby

from django import template
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
