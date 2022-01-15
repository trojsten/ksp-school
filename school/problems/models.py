from django.conf import settings
from django.db import models
from judge_client.client import Protocol

from school.problems.services import get_judge_client


class Problem(models.Model):
    class Meta:
        verbose_name = "úloha"
        verbose_name_plural = "úlohy"

    name = models.CharField(verbose_name="názov", max_length=64)
    content = models.TextField(verbose_name="zadanie", blank=True)
    testovac_id = models.CharField(verbose_name="ID úlohy pre testovač", max_length=128)

    def __str__(self):
        return self.name


class Submit(models.Model):
    class Meta:
        verbose_name = "submit"
        verbose_name_plural = "submity"

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, verbose_name="úloha")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="používateľ"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="čas", db_index=True
    )

    code = models.TextField(blank=True, verbose_name="odovzdaný program")
    language = models.CharField(max_length=16, verbose_name="jazyk")
    protocol = models.TextField(blank=True, verbose_name="protokol")
    result = models.CharField(blank=True, max_length=16, verbose_name="verdikt")

    @property
    def protocol_object(self) -> Protocol:
        client = get_judge_client()
        return client.parse_protocol(self.protocol, 100)
