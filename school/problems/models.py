import secrets
from os import path

from django.conf import settings
from django.db import models
from django.urls import reverse
from judge_client.types import SubmitStatus, TestingStatus, Verdict

from school.utils import get_extension


def submit_file_filepath(instance: "Submit", filename):
    _, ext = path.splitext(filename)
    rnd_str = secrets.token_hex(16)
    return f"submits/{instance.problem_id}/{instance.user_id}_{rnd_str}{ext}"


class Tag(models.Model):
    id: int

    name = models.CharField(verbose_name="názov", max_length=256)

    class Meta:
        verbose_name = "tag"
        verbose_name_plural = "tagy"

    def __str__(self):
        return self.name


class Problem(models.Model):
    class ProblemDifficulty(models.TextChoices):
        EASY = "easy", "easy"
        MEDIUM = "medium", "medium"
        HARD = "hard", "hard"
        UNKNOWN = "unknown", "unknown"

    id: int

    name = models.CharField(verbose_name="názov", max_length=64)
    slug = models.SlugField(
        verbose_name="slug",
        max_length=64,
        unique=True,
    )
    content = models.TextField(verbose_name="zadanie", blank=True)
    difficulty = models.CharField(
        verbose_name="obtiažnosť",
        choices=ProblemDifficulty.choices,
        default=ProblemDifficulty.UNKNOWN,
    )
    detail_visible = models.BooleanField(
        verbose_name="viditeľnosť detailov testovania", default=False
    )
    judge_namespace = models.CharField(
        verbose_name="namespace v ktorom je úloha v Judgi",
        max_length=128,
        default="",
        blank=True,
    )
    judge_task = models.CharField(verbose_name="názov úlohy pre Judge", max_length=128)
    tags = models.ManyToManyField(Tag)

    class Meta:
        verbose_name = "úloha"
        verbose_name_plural = "úlohy"

        constraints = [
            models.UniqueConstraint(
                "judge_task",
                "judge_namespace",
                name="problem__judge_task_judge_namespace",
            )
        ]

    def __str__(self):
        return self.name


class Submit(models.Model):
    class JudgeTestingStatus(models.IntegerChoices):
        QUEUED = 0, "queued"
        FINISHED = 1, "finished"
        FAILED = 2, "failed"

    id: int

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, verbose_name="úloha")
    problem_id: int
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="používateľ"
    )
    user_id: int
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="čas", db_index=True
    )

    program = models.FileField(
        verbose_name="odovzdaný program",
        upload_to=submit_file_filepath,
        max_length=255,
    )

    status = models.SmallIntegerField(
        choices=JudgeTestingStatus.choices,
        verbose_name="status submitu na Judgi",
        default=JudgeTestingStatus.QUEUED,
    )
    testing_status = models.CharField(
        max_length=32, blank=True, default="", verbose_name="status testovania na Judgi"
    )

    result = models.CharField(blank=True, max_length=16, verbose_name="verdikt")
    public_id = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="public ID submitu",
        null=True,
        default=None,
        blank=True,
    )
    protocol_key = models.CharField(max_length=255, blank=True)

    lesson_item = models.ForeignKey(
        "courses.LessonItem",
        blank=True,
        null=True,
        verbose_name="časť lekcie",
        on_delete=models.SET_NULL,
    )
    lesson_item_id: int

    class Meta:
        verbose_name = "submit"
        verbose_name_plural = "submity"
        ordering = ("-created_at",)

    def __str__(self):
        return f"Submit {self.id}"

    def get_absolute_url(self):
        return reverse(
            "submit_detail",
            kwargs={"problem": self.problem.slug, "submit": self.id},
        )

    @property
    def language(self) -> str:
        return get_extension(self.program.path)

    @property
    def status_pretty(self) -> str:
        if self.result:
            return self.result_pretty

        if self.status == self.JudgeTestingStatus.QUEUED and self.testing_status:
            return TestingStatus(self.testing_status).get_human_name("sk")

        return SubmitStatus(self.status).get_human_name("sk")

    @property
    def result_pretty(self) -> str:
        return Verdict(self.result).get_human_name("sk")

    @property
    def result_color(self) -> str:
        if not self.result:
            return "gray"
        return Verdict(self.result).color
