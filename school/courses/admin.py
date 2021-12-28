from django.contrib import admin

from school.courses.models import Course, CourseGroup, Lesson


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    pass


@admin.register(CourseGroup)
class CourseGroupAdmin(admin.ModelAdmin):
    pass


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    pass
