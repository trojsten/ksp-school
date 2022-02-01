import os.path
import zipfile

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from school.courses.models import LessonMaterial
from school.imports.forms import ZipImportForm


@method_decorator(csrf_exempt, name="dispatch")
class ImportView(View):
    def dispatch(self, request: HttpRequest, *args, **kwargs):
        token = request.headers.get("X-Token", None)
        if token != settings.SCHOOL_IMPORT_TOKEN:
            return JsonResponse({"ok": False}, status=403)

        return super().dispatch(request, *args, **kwargs)


class ImportMaterialsView(ImportView):
    def post(self, request, *args, **kwargs):
        form = ZipImportForm(request.POST, request.FILES)

        if form.is_valid():
            imported = 0
            ids = []
            with zipfile.ZipFile(form.cleaned_data["file"]) as z:
                for file in z.filelist:
                    name, ext = os.path.splitext(os.path.basename(file.filename))
                    if ext.lower() != ".md":
                        continue

                    content = z.read(file).decode()
                    LessonMaterial.objects.update_or_create(
                        material_id=name,
                        defaults={
                            "content": content,
                            "name": content.splitlines()[0].strip("# \t"),
                        },
                    )
                    ids.append(name)
                    imported += 1

                orphans = list(
                    LessonMaterial.objects.exclude(material_id__in=ids).values_list(
                        "material_id", flat=True
                    )
                )

            return JsonResponse({"ok": True, "imported": imported, "orphans": orphans})
        else:
            data = form.errors.as_json()
            return JsonResponse({"errors": data, "ok": False}, status=400)
