from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import FormView, TemplateView

from school.classrooms.forms import JoinForm
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


class ClassroomJoinView(LoginRequiredMixin, FormView):
    template_name = "classrooms/join.html"
    form_class = JoinForm

    def form_valid(self, form):
        classroom = form.cleaned_data["classroom"]
        ClassroomUser.objects.create(user=self.request.user, classroom=classroom)

        return redirect("classrooms_list")  # TODO: classroom detail
