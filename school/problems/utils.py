from django.conf import settings
from django.contrib.auth.models import User
from django.core.files import File
from judge_client.client import JudgeClient, Submit


def get_judge_client() -> JudgeClient:
    return JudgeClient(settings.JUDGE_TOKEN, settings.JUDGE_URL)


def enqueue_judge_submit(
    namespace: str | None, task: str, user: User, file: File
) -> Submit:
    judge = get_judge_client()

    return judge.submit(
        namespace=namespace,
        task=task,
        external_user_id=user.username,
        filename=file.name or "",
        program=file.read(),
    )
