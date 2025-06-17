from django.db import models
from django.db.models import UniqueConstraint


class Course(models.Model):
    id: int

    name = models.CharField(max_length=64)
    order = models.IntegerField(default=0)
    slug = models.SlugField(unique=True)
    image = models.ImageField(blank=True, null=True)
    short_description = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    recommended_courses = models.ManyToManyField("Course", blank=True)

    class Meta:
        verbose_name = "kurz"
        verbose_name_plural = "kurzy"
        ordering = ["order"]

    def __str__(self):
        return self.name


class CourseGroup(models.Model):
    id: int

    name = models.CharField(max_length=64)
    order = models.IntegerField()
    courses = models.ManyToManyField(Course, blank=True)

    class Meta:
        verbose_name = "skupina kurzov"
        verbose_name_plural = "skupiny kurzov"
        ordering = ["order"]

    def __str__(self):
        return self.name


class Lesson(models.Model):
    id: int

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    course_id: int

    name = models.CharField(max_length=64)
    slug = models.SlugField()
    layer = models.IntegerField()
    order = models.IntegerField()

    class Meta:
        verbose_name = "lekcia"
        verbose_name_plural = "lekcie"
        constraints = [
            UniqueConstraint(fields=["course", "slug"], name="unique_course_slug"),
        ]
        ordering = ["layer", "order"]

    def __str__(self):
        return self.name

    def items(self):
        """
        Builds QuerySet for retrieving all lesson items with related data
        :return: QuerySet
        """
        return self.lessonitem_set.order_by("order").select_related(
            "lesson_material", "problem"
        )


class LessonMaterial(models.Model):
    id: int

    name = models.CharField(max_length=64)
    material_id = models.SlugField(unique=True)
    content = models.TextField(blank=True)

    class Meta:
        verbose_name = "učebný text"
        verbose_name_plural = "učebné texty"

    def __str__(self):
        return self.name


class LessonItem(models.Model):
    id: int

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    lesson_id: int

    order = models.IntegerField()
    slug = models.SlugField(max_length=64)

    lesson_material = models.ForeignKey(
        LessonMaterial, on_delete=models.CASCADE, blank=True, null=True
    )
    problem = models.ForeignKey(
        "problems.Problem", on_delete=models.CASCADE, blank=True, null=True
    )

    class Meta:
        verbose_name = "časť lekcie"
        verbose_name_plural = "časti lekcie"
        constraints = [
            UniqueConstraint(fields=["lesson", "slug"], name="unique_lesson_slug"),
        ]
        ordering = ["order"]

    def __str__(self):
        return self.name

    @property
    def name(self):
        if self.lesson_material:
            return self.lesson_material.name
        if self.problem:
            return self.problem.name
        return "???"
