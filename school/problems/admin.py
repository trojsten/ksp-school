from django.contrib import admin

from school.problems.models import Problem, Submit, Tag


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ["name", "difficulty", "detail_visible", "testovac_id"]
    search_fields = ["name", "testovac_id"]
    list_filter = ["difficulty", "detail_visible"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Submit)
class SubmitAdmin(admin.ModelAdmin):
    list_display = ["problem", "user", "result", "created_at"]
    search_fields = ["problem__name", "user__username"]
    list_filter = ["result", "language", "problem__testovac_id"]
