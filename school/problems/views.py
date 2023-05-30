import os.path

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotAllowed, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, FormView
from judge_client.client import JudgeConnectionError

from school.courses.models import LessonItem
from school.problems import forms
from school.problems.forms import ProtocolForm
from school.problems.models import Problem, Submit


class SubmitDetailView(LoginRequiredMixin, DetailView):
    template_name = "problems/submit_detail.html"
    pk_url_kwarg = "submit"

    def get_queryset(self):
        # TODO: Permissions
        return Submit.objects.filter(
            user=self.request.user, problem__testovac_id=self.kwargs["problem"]
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        submits = Submit.objects.filter(
            problem__testovac_id=self.kwargs["problem"], user=self.request.user
        ).select_related("lesson_item__lesson__course")

        url = None
        if "liid" in self.request.GET:
            item = get_object_or_404(
                LessonItem,
                id=self.request.GET["liid"],
                problem__testovac_id=self.kwargs["problem"],
            )
            submits = submits.filter(lesson_item=item)
            url = reverse(
                "lesson",
                kwargs={
                    "course": item.lesson.course.slug,
                    "lesson": item.lesson.slug,
                    "item": item.slug,
                },
            )

        if url is None:
            url = ""

        ctx.update(
            {
                "back_url": url,
                "submits": submits,
                "lesson_item_id": self.request.GET.get("liid", None),
            }
        )
        return ctx


class SubmitCreateView(LoginRequiredMixin, FormView):
    http_method_names = ["post"]
    form_class = forms.SubmitForm

    def dispatch(self, request, *args, **kwargs):
        self.problem = get_object_or_404(Problem, testovac_id=kwargs["problem"])

        self.item = None
        if "liid" in request.GET:
            self.item = get_object_or_404(
                LessonItem, id=request.GET["liid"], problem=self.problem
            )

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        submit = Submit()
        submit.user = self.request.user
        submit.code = form.cleaned_data["file"].read().decode()
        submit.language = os.path.splitext(form.cleaned_data["file"].name)[1][1:]
        submit.problem = self.problem
        submit.lesson_item = self.item
        submit.save()

        try:
            submit.send_to_testovac()
        except JudgeConnectionError:
            submit.result = "CONNERR"
            submit.save()

        url = reverse("submit_detail", args=[self.problem.testovac_id, submit.id])
        if self.item:
            url += f"?liid={self.item.id}"
        return HttpResponseRedirect(url)

    def form_invalid(self, form):
        # TODO: Redirect back.
        return JsonResponse(form.errors)


@method_decorator(csrf_exempt, name="dispatch")
class UploadProtocolView(View):
    def post(self, request, *args, **kwargs):
        if not settings.TESTOVAC_TOKEN:
            return JsonResponse(
                {"errors": "Protocol upload is disabled.", "ok": False}, status=403
            )

        if settings.TESTOVAC_TOKEN != request.headers.get("X-Token", None):
            return JsonResponse(
                {"errors": "Wrong access token.", "ok": False}, status=403
            )

        form = ProtocolForm(request.POST, request.FILES)

        if not form.is_valid():
            data = form.errors.as_json()
            return JsonResponse({"errors": data, "ok": False}, status=400)

        submit = get_object_or_404(Submit, id=form.cleaned_data["submit"])
        submit.protocol = form.cleaned_data["protocol"].read().decode("utf-8")
        submit.result = submit.protocol_object.result
        submit.save()

        return JsonResponse({"ok": True})
