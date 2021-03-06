from django.contrib import admin

from school.problems.models import Problem, Submit


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    pass


@admin.register(Submit)
class SubmitAdmin(admin.ModelAdmin):
    list_display = ["problem", "user", "result", "created_at"]
    search_fields = ["problem__name", "user__username"]
