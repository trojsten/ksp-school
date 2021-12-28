from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import UniqueConstraint


class Course(models.Model):
    class Meta:
        verbose_name = "kurz"
        verbose_name_plural = "kurzy"

    name = models.CharField(max_length=64)
    slug = models.SlugField(unique=True)
    image = models.ImageField(blank=True, null=True)
    short_description = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class CourseGroup(models.Model):
    class Meta:
        verbose_name = "skupina kurzov"
        verbose_name_plural = "skupiny kurzov"

    name = models.CharField(max_length=64)
    order = models.IntegerField()
    courses = models.ManyToManyField(Course, blank=True)

    def __str__(self):
        return self.name


class Lesson(models.Model):
    class Meta:
        verbose_name = "lekcia"
        verbose_name_plural = "lekcie"
        constraints = [
            UniqueConstraint(fields=["course", "slug"], name="unique_course_slug"),
        ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    slug = models.SlugField()
    layer = models.IntegerField()
    order = models.IntegerField()

    def __str__(self):
        return self.name

    def items(self):
        """
        Builds QuerySet for retrieving all lesson items with related data
        :return: QuerySet
        """
        return self.lessonitem_set.order_by("order").select_related("lesson_material")


class LessonMaterial(models.Model):
    class Meta:
        verbose_name = "učebný text"
        verbose_name_plural = "učebné texty"

    name = models.CharField(max_length=64)
    content = models.TextField(blank=True)

    def __str__(self):
        return self.name


class LessonItem(models.Model):
    class Meta:
        verbose_name = "časť lekcie"
        verbose_name_plural = "časti lekcie"
        constraints = [
            UniqueConstraint(fields=["lesson", "order"], name="unique_lesson_order"),
            UniqueConstraint(fields=["lesson", "slug"], name="unique_lesson_slug"),
        ]

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    order = models.IntegerField()
    slug = models.SlugField(max_length=64)

    lesson_material = models.ForeignKey(
        LessonMaterial, on_delete=models.CASCADE, blank=True, null=True
    )
    # problem = models.ForeignKey("...", on_delete=models.CASCADE, blank=True, null=True)

    @property
    def name(self):
        if self.lesson_material:
            return self.lesson_material.name
        return "???"
