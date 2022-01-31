import os.path
import zipfile

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from school.courses.models import LessonMaterial
from school.imports.forms import MaterialForm


@method_decorator(csrf_exempt, name="dispatch")
class ImportMaterialsView(View):
    def post(self, request, *args, **kwargs):
        form = MaterialForm(request.POST, request.FILES)

        if form.is_valid():
            imported = 0
            ids = []
            with zipfile.ZipFile(form.cleaned_data["materials"]) as z:
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
