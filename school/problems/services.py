from django.conf import settings
from judge_client.client import JudgeClient


def get_judge_client() -> JudgeClient:
    return JudgeClient(
        settings.TESTOVAC_CLIENT, settings.TESTOVAC_HOST, settings.TESTOVAC_PORT
    )
