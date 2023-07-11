from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from school.classrooms.models import Classroom, ClassroomUser


class ClassroomListView(LoginRequiredMixin, TemplateView):
    template_name = "classrooms/list.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx["mine"] = Classroom.objects.filter(
            id__in=ClassroomUser.objects.filter(user=self.request.user).values(
                "classroom"
            )
        )
        ctx["public"] = Classroom.objects.filter(is_public=True).exclude(
            id__in=ctx["mine"]
        )

        return ctx
