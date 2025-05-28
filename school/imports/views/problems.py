from django.http import JsonResponse

from school.imports.forms import ZipImportForm
from school.imports.views import ImportView, _import_markdowns
from school.problems.models import Problem, Tag


class ImportProblemsView(ImportView):
    def post(self, request, *args, **kwargs):
        def import_problems(name, meta, body):
            problem, _ = Problem.objects.update_or_create(
                slug=name,
                defaults={
                    "name": meta.get("name", "???"),
                    "content": body,
                    "difficulty": meta.get(
                        "difficulty", Problem.ProblemDifficulty.UNKNOWN
                    ),
                    "detail_visible": meta.get("detail_visible", False),
                },
            )

            problem.tags.clear()

            for tag in meta.get("tags", []):
                problem.tags.add(Tag.objects.update_or_create(name=tag)[0])

        form = ZipImportForm(request.POST, request.FILES)

        if not form.is_valid():
            data = form.errors.as_json()
            return JsonResponse({"errors": data, "ok": False}, status=400)

        ids = _import_markdowns(
            form.cleaned_data["file"],
            import_problems,
        )

        orphans = list(
            Problem.objects.exclude(slug__in=ids).values_list("slug", flat=True)
        )

        return JsonResponse({"ok": True, "imported": len(ids), "orphans": orphans})
