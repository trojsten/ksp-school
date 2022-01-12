from judge_client.client import JudgeClient


def get_judge_client() -> JudgeClient:
    return JudgeClient("aaa", "localhost", 8001)
