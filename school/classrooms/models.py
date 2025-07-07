from django.db import models


class ClassroomQuerySet(models.QuerySet):
    def for_user(self, user, teacher_required=False):
        if user.is_superuser:
            return self
        classroomuser_objects = ClassroomUser.objects.filter(user=user)
        if teacher_required:
            classroomuser_objects = classroomuser_objects.filter(is_teacher=True)
        return self.filter(id__in=classroomuser_objects.values("classroom"))


class Classroom(models.Model):
    id: int

    name = models.CharField(max_length=100)
    join_code = models.CharField(max_length=8, blank=True, null=True, unique=True)
    is_public = models.BooleanField(default=False)

    objects = ClassroomQuerySet.as_manager()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ClassroomUser(models.Model):
    id: int

    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    classroom_id: int
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    user_id: int
    is_teacher = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_teacher", "user__last_name", "user__first_name"]
        unique_together = (("classroom", "user"),)

    def __str__(self):
        return f"{self.user} in {self.classroom} ({'teacher' if self.is_teacher else 'student'})"
