import json
import os
import zipfile

import fastjsonschema
import yaml
from django.http import JsonResponse

from school.courses.models import Course, Lesson, LessonItem, LessonMaterial
from school.imports.forms import ZipImportForm
from school.imports.views import ImportView
from school.problems.models import Problem


class ImportCoursesView(ImportView):
    def post(self, request, *args, **kwargs):
        form = ZipImportForm(request.POST, request.FILES)

        if not form.is_valid():
            data = form.errors.as_json()
            return JsonResponse({"errors": data, "ok": False}, status=400)

        with open(
            os.path.join(os.path.dirname(__file__), "..", "courses.schema.json")
        ) as f:
            validate = fastjsonschema.compile(json.load(f))

        recommended_courses = {}

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
                        "order": data["order"],
                    },
                )

                recommended_courses[course.id] = data["recommended_courses"]

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
                                material = LessonMaterial.objects.filter(
                                    material_id=item["material"]
                                ).first()
                                if material is None:
                                    return JsonResponse({"errors": f"Material '{item['material']}' don't exist.'", "ok": False}, status=400)

                            if item["problem"]:
                                problem = Problem.objects.filter(
                                    testovac_id=item["problem"]
                                ).first()
                                if problem is None:
                                    return JsonResponse({"errors": f"Problem '{item['material']}' don't exist.'", "ok": False}, status=400)

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

        for course_id in recommended_courses:
            Course.objects.get(id=course_id).recommended_courses.set(
                Course.objects.filter(slug__in=recommended_courses[course_id])
            )

        orphans = list(
            Course.objects.exclude(slug__in=ids).values_list("slug", flat=True)
        )

        return JsonResponse({"ok": True, "imported": len(ids), "orphans": orphans})
