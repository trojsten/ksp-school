from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import DetailView

from school.courses.models import LessonItem
from school.problems.models import Submit


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
        return ctx
