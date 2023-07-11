from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import DetailView, FormView, TemplateView

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

        return redirect("classrooms_detail", pk=classroom.id)


class ClassroomMixin:
    def get_queryset(self):
        return Classroom.objects.for_user(self.request.user)


class TeacherRequiredMixin:
    def get_queryset(self):
        return Classroom.objects.for_user(self.request.user, teacher_required=True)


class ClassroomDetailView(LoginRequiredMixin, ClassroomMixin, DetailView):
    template_name = "classrooms/detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["is_teacher"] = (
            self.request.user.is_superuser
            or ClassroomUser.objects.filter(
                classroom=self.object, user=self.request.user, is_teacher=True
            ).exists()
        )
        return ctx


class ClassroomResultsView(LoginRequiredMixin, TeacherRequiredMixin, DetailView):
    template_name = "classrooms/teacher/results.html"
