from itertools import groupby

from django.shortcuts import render
from django.views.generic import DetailView, ListView

from school.courses.models import Course, CourseGroup, Lesson


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
