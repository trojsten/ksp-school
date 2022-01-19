import os.path

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotAllowed, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import DetailView, FormView
from judge_client.client import JudgeConnectionError

from school.courses.models import LessonItem
from school.problems import forms
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

        url = None
        if "liid" in self.request.GET:
            item = LessonItem.objects.filter(pk=self.request.GET["liid"]).first()
            if item:
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

        ctx["back_url"] = url
        ctx["submits"] = Submit.objects.all()
        ctx["lesson_item_id"] = self.request.GET.get("liid", None)
        return ctx


class SubmitCreateView(LoginRequiredMixin, FormView):
    http_method_names = ["post"]
    form_class = forms.SubmitForm

    def dispatch(self, request, *args, **kwargs):
        self.problem = get_object_or_404(Problem, testovac_id=kwargs["problem"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        submit = Submit()
        submit.user = self.request.user
        submit.code = form.cleaned_data["file"].read().decode()
        submit.problem = self.problem
        submit.language = os.path.splitext(form.cleaned_data["file"].name)[1][1:]
        submit.save()

        try:
            submit.send_to_testovac()
        except JudgeConnectionError:
            submit.result = "CONNERR"
            submit.save()

        url = reverse("submit_detail", args=[self.problem.testovac_id, submit.id])
        if "liid" in self.request.GET:
            url += f"?liid={self.request.GET['liid']}"
        return HttpResponseRedirect(url)

    def form_invalid(self, form):
        # TODO: Redirect back.
        return JsonResponse(form.errors)
