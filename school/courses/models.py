from django.db import models
from django.db.models import UniqueConstraint


class Course(models.Model):
    class Meta:
        verbose_name = "kurz"
        verbose_name_plural = "kurzy"

    name = models.CharField(max_length=64)
    slug = models.CharField(max_length=64, unique=True)
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
    slug = models.CharField(max_length=64)
    layer = models.IntegerField()
    order = models.IntegerField()

    def __str__(self):
        return self.name
