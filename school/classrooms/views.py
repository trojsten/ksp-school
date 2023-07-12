from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.utils.functional import cached_property
from django.views.generic import DetailView, FormView, TemplateView

from school.classrooms.forms import JoinForm
from school.classrooms.models import Classroom, ClassroomUser
from school.classrooms.results import get_course_results
from school.courses.models import Course, LessonItem
from school.problems.models import Submit
from school.users.models import User


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

    @cached_property
    def course(self):
        if "course" not in self.kwargs:
            return Course.objects.first()
        return get_object_or_404(Course, slug=self.kwargs["course"])

    def get_results(self):
        students = User.objects.filter(
            id__in=ClassroomUser.objects.filter(
                classroom=self.object, is_teacher=False
            ).values("user")
        )
        print(students)
        return get_course_results(self.course, students)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["course"] = self.course
        ctx["results"] = self.get_results()
        return ctx
