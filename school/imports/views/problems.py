from django.http import JsonResponse

from school.imports.forms import ZipImportForm
from school.imports.views import ImportView, _import_markdowns
from school.problems.models import Problem


class ImportProblemsView(ImportView):
    def post(self, request, *args, **kwargs):
        form = ZipImportForm(request.POST, request.FILES)

        if not form.is_valid():
            data = form.errors.as_json()
            return JsonResponse({"errors": data, "ok": False}, status=400)

        ids = _import_markdowns(
            form.cleaned_data["file"],
            lambda name, meta, body: Problem.objects.update_or_create(
                testovac_id=name,
                defaults={
                    "name": meta.get("name", "???"),
                    "content": body,
                },
            ),
        )

        orphans = list(
            Problem.objects.exclude(testovac_id__in=ids).values_list(
                "testovac_id", flat=True
            )
        )

        return JsonResponse({"ok": True, "imported": len(ids), "orphans": orphans})
