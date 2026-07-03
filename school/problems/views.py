import json
from typing import Any

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Exists, OuterRef, Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, FormView, ListView
from django.views.generic.base import ContextMixin
from judge_client.exceptions import JudgeConnectionError, UnknownLanguageError

from school.courses.models import LessonItem
from school.problems import forms
from school.problems.models import Problem, Submit
from school.problems.utils import enqueue_judge_submit
from school.trackers.models import LessonItemTracker


class TagMixin(ContextMixin, View):
    @cached_property
    def tags(self):
        raise NotImplementedError()

    def get_active_tags(self):
        return set(self.request.GET.getlist("tags"))

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "tags": self.tags,
                "active_tags": self.get_active_tags(),
            }
        )
        return context


class ProblemListView(TagMixin, ListView):
    template_name = "problems/problem_list.html"
    context_object_name = "problems"

    def get_queryset(self):
        qs = Problem.objects.all().prefetch_related("tags")

        if self.request.user.is_authenticated:
            qs = qs.annotate(
                completed=Exists(
                    LessonItemTracker.objects.filter(
                        user=self.request.user,
                        lesson_item__problem_id=OuterRef("id"),
                        completed_at__isnull=False,
                    )
                )
            )

        if query := self.request.GET.get("q"):
            qs = qs.filter(Q(name__icontains=query) | Q(tags__name__in=query.split()))

        if active_tags := self.get_active_tags():
            qs = qs.filter(tags__name__in=active_tags)

        if self.active_difficulty:
            qs = qs.filter(difficulty=self.active_difficulty)

        if self.active_state and self.request.user.is_authenticated:
            qs = qs.filter(completed=self.active_state == "completed")

        return qs.order_by("name").distinct()

    @cached_property
    def tags(self):
        return (
            Problem.objects.exclude(tags__name__isnull=True)
            .values_list("tags__name", flat=True)
            .order_by("tags__name")
            .distinct()
        )

    @cached_property
    def active_difficulty(self):
        return self.request.GET.get("difficulty")

    @cached_property
    def active_state(self):
        return self.request.GET.get("state")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)

        ctx["user_authenticated"] = self.request.user.is_authenticated

        ctx["active_difficulty"] = self.active_difficulty
        ctx["difficulties"] = Problem.ProblemDifficulty
        ctx["active_state"] = self.active_state
        ctx["states"] = [
            (
                "Nedokončená",
                "started",
                "Nezačatá alebo nedokončená úloha.",
                "bg-orange-900",
                "bg-orange-600",
                self.active_state == "started",
            ),
            (
                "Dokončená",
                "completed",
                "Dokončená úloha.",
                "bg-green-900",
                "bg-green-600",
                self.active_state == "completed",
            ),
        ]

        return ctx


class ProblemDetailView(DetailView):
    template_name = "problems/problem_detail.html"
    context_object_name = "problem"
    slug_url_kwarg = "problem"

    def get_queryset(self):
        return Problem.objects.prefetch_related("tags")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            ctx["submits"] = Submit.objects.filter(
                problem=self.get_object(),
                user=self.request.user,
            )

        return ctx


class SubmitDetailView(LoginRequiredMixin, DetailView):
    template_name = "problems/submit_detail.html"
    pk_url_kwarg = "submit"

    def get_queryset(self):
        qs = Submit.objects.filter(problem__slug=self.kwargs["problem"])
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        submits = Submit.objects.filter(
            problem__slug=self.kwargs["problem"], user=self.request.user
        ).select_related("lesson_item__lesson__course")

        url = None
        if "liid" in self.request.GET:
            item = get_object_or_404(
                LessonItem,
                id=self.request.GET["liid"],
                problem__slug=self.kwargs["problem"],
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

        submit: Submit = self.get_object()

        ctx.update(
            {
                "back_url": url,
                "submits": submits,
                "lesson_item_id": self.request.GET.get("liid", None),
                "protocol_key": submit.protocol_key,
            }
        )
        return ctx


class SubmitCreateView(LoginRequiredMixin, FormView):
    http_method_names = ["post"]
    form_class = forms.SubmitForm
    template_name = "problems/submit_error.html"

    def dispatch(self, request, *args, **kwargs):
        self.problem = get_object_or_404(Problem, slug=kwargs["problem"])

        self.item = None
        if "liid" in request.GET:
            self.item = get_object_or_404(
                LessonItem, id=request.GET["liid"], problem=self.problem
            )

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        submit = Submit(
            user=self.request.user,
            program=form.cleaned_data["file"],
            problem=self.problem,
            lesson_item=self.item,
        )
        try:
            judge_submit = enqueue_judge_submit(
                self.problem.judge_namespace if self.problem.judge_namespace else None,
                self.problem.judge_task,
                self.request.user,
                form.cleaned_data["file"],
            )
            submit.public_id = judge_submit.public_id
            submit.protocol_key = judge_submit.protocol_key
        except UnknownLanguageError:
            form.add_error("file", "Nepodporovaný jazyk programu.")
            return self.form_invalid(form)
        except JudgeConnectionError:
            submit.result = "CONNERR"

        submit.save()

        url = reverse("submit_detail", args=[self.problem.slug, submit.id])
        if self.item:
            url += f"?liid={self.item.id}"
        return HttpResponseRedirect(url)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        submits = Submit.objects.filter(
            problem__slug=self.kwargs["problem"], user=self.request.user
        ).select_related("lesson_item__lesson__course")

        url = None
        if "liid" in self.request.GET:
            item = get_object_or_404(
                LessonItem,
                id=self.request.GET["liid"],
                problem__slug=self.kwargs["problem"],
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
                "problem": self.problem,
                "lesson_item_id": self.request.GET.get("liid", None),
            }
        )

        return ctx


@method_decorator(csrf_exempt, name="dispatch")
class UploadProtocolView(View):
    def post(self, request, *args, **kwargs):
        if not settings.JUDGE_TOKEN:
            return JsonResponse(
                {"errors": "Protocol upload is disabled.", "ok": False}, status=403
            )

        json_data = json.loads(self.request.body)

        if json_data["token"] != settings.JUDGE_TOKEN:
            return JsonResponse(
                {"errors": "Wrong access token.", "ok": False}, status=403
            )

        submit: Submit = get_object_or_404(Submit, public_id=json_data["public_id"])

        if "status" in json_data:
            submit.status = json_data["status"]
        if "testing_status" in json_data:
            submit.testing_status = json_data["testing_status"]

        if "final_verdict" in json_data["protocol"]:
            submit.result = json_data["protocol"]["final_verdict"]

        submit.save()

        return JsonResponse({"ok": True})
