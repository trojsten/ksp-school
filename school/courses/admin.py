from django.contrib import admin

from school.courses.models import (
    Course,
    CourseGroup,
    Lesson,
    LessonItem,
    LessonMaterial,
)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    pass


@admin.register(CourseGroup)
class CourseGroupAdmin(admin.ModelAdmin):
    pass


class LessonItemInline(admin.TabularInline):
    model = LessonItem
    ordering = ["order"]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    inlines = [LessonItemInline]


@admin.register(LessonMaterial)
class LessonMaterialAdmin(admin.ModelAdmin):
    list_display = ["name", "material_id"]
    search_fields = ["name", "material_id"]
