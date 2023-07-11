from django.db import models


class Classroom(models.Model):
    name = models.CharField(max_length=100)
    join_code = models.CharField(max_length=8, blank=True, null=True, unique=True)
    is_public = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ClassroomUser(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    is_teacher = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_teacher", "user__last_name", "user__first_name"]
