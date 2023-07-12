from django.contrib import admin

from school.classrooms.models import Classroom, ClassroomUser


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ["name", "is_public"]


@admin.register(ClassroomUser)
class ClassroomUserAdmin(admin.ModelAdmin):
    list_display = ["user", "classroom", "is_teacher"]
