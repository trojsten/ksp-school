from django.contrib import admin

from school.problems.models import Problem, Submit, Tag


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ["name", "difficulty", "slug"]
    search_fields = ["name", "slug"]
    list_filter = ["difficulty"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Submit)
class SubmitAdmin(admin.ModelAdmin):
    list_display = ["problem", "user", "result", "created_at"]
    search_fields = ["problem__name", "user__username"]
    list_filter = ["result", "problem__slug"]
