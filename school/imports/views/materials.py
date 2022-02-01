from django.http import JsonResponse

from school.courses.models import LessonMaterial
from school.imports.forms import ZipImportForm
from school.imports.views import ImportView, _import_markdowns


class ImportMaterialsView(ImportView):
    def post(self, request, *args, **kwargs):
        form = ZipImportForm(request.POST, request.FILES)

        if not form.is_valid():
            data = form.errors.as_json()
            return JsonResponse({"errors": data, "ok": False}, status=400)

        ids = _import_markdowns(
            form.cleaned_data["file"],
            lambda name, meta, body: LessonMaterial.objects.update_or_create(
                material_id=name,
                defaults={
                    "name": meta.get("name", "???"),
                    "content": body,
                },
            ),
        )

        orphans = list(
            LessonMaterial.objects.exclude(material_id__in=ids).values_list(
                "material_id", flat=True
            )
        )

        return JsonResponse({"ok": True, "imported": len(ids), "orphans": orphans})
