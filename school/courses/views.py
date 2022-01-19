from itertools import groupby

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView, TemplateView

from school.courses.models import Course, CourseGroup, Lesson
from school.problems.models import Submit


class CoursesListView(ListView):
    template_name = "courses/list.html"

    def get_queryset(self):
        return (
            CourseGroup.objects.order_by("order")
            .filter(courses__isnull=False)
            .prefetch_related("courses")
            .all()
        )


class CourseView(DetailView):
    template_name = "courses/detail.html"
    model = Course

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        lessons = (
            Lesson.objects.filter(course=self.object).order_by("layer", "order").all()
        )
        layers = []
        for _, layer_lessons in groupby(lessons, key=lambda x: x.layer):
            layers.append(list(layer_lessons))

        ctx["layers"] = layers
        return ctx


class LessonView(TemplateView):
    template_name = "courses/lesson.html"

    def dispatch(self, request, *args, **kwargs):
        self.lesson = get_object_or_404(
            Lesson,
            slug=kwargs["lesson"],
            course__slug=kwargs["course"],
        )

        if "item" in kwargs:
            self.item = get_object_or_404(self.lesson.items(), slug=kwargs["item"])
        else:
            first_item = self.lesson.lessonitem_set.order_by("order").first()
            if not first_item:
                raise Http404()

            return redirect(
                "lesson",
                course=kwargs["course"],
                lesson=self.lesson.slug,
                item=first_item.slug,
            )

        return super(LessonView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        items = self.lesson.items().all()
        next_item = next(iter(filter(lambda x: x.order > self.item.order, items)), None)
        previous_item = next(
            iter(filter(lambda x: x.order < self.item.order, reversed(items))), None
        )

        submits = None
        if self.item.problem and self.request.user.is_authenticated:
            submits = Submit.objects.filter(
                problem=self.item.problem, user=self.request.user
            ).all()

        ctx.update(
            {
                "lesson": self.lesson,
                "item": self.item,
                "items": items,
                "submits": submits,
                "previous_item": previous_item,
                "next_item": next_item,
            }
        )
        return ctx
