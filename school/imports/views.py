import json
import os.path
import zipfile
from typing import Callable, List

import fastjsonschema
import frontmatter
import yaml
from django.conf import settings
from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from school.courses.models import Course, Lesson, LessonItem, LessonMaterial
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


class ImportCoursesView(ImportView):
    def post(self, request, *args, **kwargs):
        form = ZipImportForm(request.POST, request.FILES)

        if not form.is_valid():
            data = form.errors.as_json()
            return JsonResponse({"errors": data, "ok": False}, status=400)

        with open(os.path.join(os.path.dirname(__file__), "courses.schema.json")) as f:
            validate = fastjsonschema.compile(json.load(f))

        ids = []
        with zipfile.ZipFile(form.cleaned_data["file"]) as z:
            for file in z.filelist:
                name, ext = os.path.splitext(os.path.basename(file.filename))
                if ext.lower() not in [".yaml", ".yml"]:
                    continue

                data = yaml.safe_load(z.read(file))
                try:
                    data = validate(data)
                except fastjsonschema.JsonSchemaException as e:
                    return JsonResponse({"errors": str(e), "ok": False}, status=400)

                course, _ = Course.objects.update_or_create(
                    slug=name,
                    defaults={
                        "name": data["name"],
                        "short_description": data["short_description"],
                        "description": data["description"],
                    },
                )

                touched_lessons = []
                for i, layer in enumerate(data["lessons"]):
                    for o, lesson in enumerate(layer):
                        lesson_object, _ = Lesson.objects.update_or_create(
                            course=course,
                            slug=lesson["slug"],
                            defaults={
                                "layer": i,
                                "order": o,
                                "name": lesson["name"],
                            },
                        )
                        touched_lessons.append(lesson_object.id)

                        touched_items = []
                        for p, item in enumerate(lesson["content"]):
                            material = None
                            problem = None

                            if item["material"]:
                                material = LessonMaterial.objects.get(
                                    material_id=item["material"]
                                )

                            if item["problem"]:
                                problem = Problem.objects.get(
                                    testovac_id=item["problem"]
                                )

                            item_object, _ = LessonItem.objects.update_or_create(
                                lesson=lesson_object,
                                slug=item["slug"],
                                defaults={
                                    "order": p,
                                    "lesson_material": material,
                                    "problem": problem,
                                },
                            )
                            touched_items.append(item_object.id)

                        LessonItem.objects.filter(lesson=lesson_object).exclude(
                            id__in=touched_items
                        ).delete()

                Lesson.objects.filter(course=course).exclude(
                    id__in=touched_lessons
                ).delete()

                ids.append(name)

        orphans = list(
            Course.objects.exclude(slug__in=ids).values_list("slug", flat=True)
        )

        return JsonResponse({"ok": True, "imported": len(ids), "orphans": orphans})
