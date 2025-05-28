from django.db import models


class Page(models.Model):
    id: int

    name = models.CharField(max_length=64)
    slug = models.CharField(max_length=64, unique=True)
    content = models.TextField()

    class Meta:
        verbose_name = "stránka"
        verbose_name_plural = "stránky"

    def __str__(self):
        return self.name
