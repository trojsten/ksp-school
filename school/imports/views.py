import os.path
import zipfile
from typing import Callable, List

import frontmatter
from django.conf import settings
from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from school.courses.models import LessonMaterial
from school.imports.forms import ZipImportForm
from school.problems.models import Problem


@method_decorator(csrf_exempt, name="dispatch")
class ImportView(View):
    def dispatch(self, request: HttpRequest, *args, **kwargs):
        token = request.headers.get("X-Token", None)
        if token != settings.SCHOOL_IMPORT_TOKEN:
            return JsonResponse({"ok": False}, status=403)

        return super().dispatch(request, *args, **kwargs)


def _import_markdowns(infile, action: Callable[[str, dict, str], None]) -> List[str]:
    ids = []
    with zipfile.ZipFile(infile) as z:
        for file in z.filelist:
            name, ext = os.path.splitext(os.path.basename(file.filename))
            if ext.lower() != ".md":
                continue

            data = frontmatter.loads(z.read(file))
            action(name, data.metadata, data.content)
            ids.append(name)
    return ids


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
