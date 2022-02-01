import os.path
import zipfile
from typing import Callable, List

import frontmatter
from django.conf import settings
from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from school.courses.models import Course
from school.trackers.utils import recalculate_course


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


class RecalculateProgressView(ImportView):
    def post(self, request, *args, **kwargs):
        for course in Course.objects.all():
            recalculate_course(course)

        return JsonResponse({"ok": True})
