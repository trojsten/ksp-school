import os.path
import zipfile

from django.core.files.storage import Storage, storages
from django.http import JsonResponse

from school.imports.forms import ZipImportForm
from school.imports.views import ImportView


class ImportAssetsView(ImportView):
    def post(self, request, *args, **kwargs):
        form = ZipImportForm(request.POST, request.FILES)

        if not form.is_valid():
            data = form.errors.as_json()
            return JsonResponse({"errors": data, "ok": False}, status=400)

        storage: Storage = storages["default"]
        uploaded_files = set()
        with zipfile.ZipFile(form.cleaned_data["file"]) as z:
            for file in z.filelist:
                storage.save(os.path.join("assets", file.filename), z.open(file))
                uploaded_files.add(file.filename)

        dirs, files = storage.listdir("assets")  # type: list, list
        file_set = set(files)
        while len(dirs):
            dir = dirs.pop()
            ndirs, nfiles = storage.listdir(os.path.join("assets", dir))
            dirs.extend([os.path.join(dir, x) for x in ndirs])
            file_set.update([os.path.join(dir, x) for x in nfiles])

        for old in file_set - uploaded_files:
            storage.delete(os.path.join("assets", old))

        return JsonResponse({"ok": True, "imported": len(uploaded_files)})
