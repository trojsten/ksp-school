import dataclasses

from django.conf import settings
from django.db import models
from judge_client.client import Protocol

from school.problems import constants
from school.problems.services import get_judge_client


class Tag(models.Model):
    class Meta:
        verbose_name = "tag"
        verbose_name_plural = "tagy"

    name = models.CharField(verbose_name="názov", max_length=256)

    def __str__(self):
        return self.name


class Problem(models.Model):
    class ProblemDifficulty(models.TextChoices):
        EASY = "easy", "easy"
        MEDIUM = "medium", "medium"
        HARD = "hard", "hard"
        UNKNOWN = "unknown", "unknown"

    class Meta:
        verbose_name = "úloha"
        verbose_name_plural = "úlohy"

    name = models.CharField(verbose_name="názov", max_length=64)
    content = models.TextField(verbose_name="zadanie", blank=True)
    difficulty = models.CharField(
        verbose_name="obtiažnosť",
        choices=ProblemDifficulty.choices,
        default=ProblemDifficulty.UNKNOWN,
    )
    detail_visible = models.BooleanField(
        verbose_name="viditeľnosť detailov testovania", default=False
    )
    testovac_id = models.CharField(
        verbose_name="ID úlohy pre testovač", max_length=128, unique=True
    )
    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return self.name


class Submit(models.Model):
    class Meta:
        verbose_name = "submit"
        verbose_name_plural = "submity"
        ordering = ("-created_at",)

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

    lesson_item = models.ForeignKey(
        "courses.LessonItem",
        blank=True,
        null=True,
        verbose_name="časť lekcie",
        on_delete=models.SET_NULL,
    )

    @property
    def protocol_object(self) -> Protocol:
        client = get_judge_client()
        return client.parse_protocol(self.protocol, 100)

    @property
    def result_pretty(self):
        return constants.TESTOVAC_MESSAGES[self.result]

    @property
    def result_color(self):
        return constants.TESTOVAC_COLORS[self.result]

    def send_to_testovac(self):
        client = get_judge_client()
        client.submit(
            f"SCHOOL-{self.id}",
            f"SCHOOL-{self.user_id}",
            self.problem.testovac_id,
            self.code,
            self.language,
        )

    def __str__(self):
        return f"Submit {self.id}"
