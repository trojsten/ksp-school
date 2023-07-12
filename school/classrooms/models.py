from django.db import models


class ClassroomQuerySet(models.QuerySet):
    def for_user(self, user, teacher_required=False):
        if user.is_superuser:
            return self
        qs = self.filter(classroomuser__user=user)
        if teacher_required:
            qs = qs.filter(classroomuser__is_teacher=True)
        return qs


class Classroom(models.Model):
    name = models.CharField(max_length=100)
    join_code = models.CharField(max_length=8, blank=True, null=True, unique=True)
    is_public = models.BooleanField(default=False)

    objects = ClassroomQuerySet.as_manager()

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
