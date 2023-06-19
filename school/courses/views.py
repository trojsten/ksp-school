from itertools import groupby

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView, TemplateView

from school.courses.models import Course, CourseGroup, Lesson, LessonItem
from school.problems.models import Submit
from school.trackers.helpers import (
    get_course_groups_with_trackers,
    get_items_with_trackers,
    get_lessons_with_trackers,
)
from school.trackers.models import LessonTracker, TrackerState
from school.trackers.utils import get_or_create_trackers, mark_completed


class CoursesListView(ListView):
    template_name = "courses/list.html"

    def get_queryset(self):
        return CourseGroup.objects.order_by("order").prefetch_related("courses").all()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["groups"] = get_course_groups_with_trackers(
            self.object_list, self.request.user
        )
        return ctx


class CourseView(DetailView):
    template_name = "courses/detail.html"
    model = Course

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        lessons = get_lessons_with_trackers(
            Lesson.objects.filter(course=self.object).order_by("layer", "order").all(),
            self.request.user,
        )

        layers = []
        for _, layer_lessons in groupby(lessons, key=lambda x: x.lesson.layer):
            layers.append(list(layer_lessons))

        ctx["layers"] = layers
        ctx["done"] = all(
            all(
                lesson.tracker is not None
                and lesson.tracker.state == TrackerState.COMPLETE
                for lesson in layer
            )
            for layer in layers
        )
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
            self.item: LessonItem = get_object_or_404(
                self.lesson.lessonitem_set, slug=kwargs["item"]
            )
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
                problem=self.item.problem,
                user=self.request.user,
                lesson_item=self.item,
            )

        # Tracking:
        tracker = None
        if self.request.user.is_authenticated:
            if self.item.lesson_material:
                _, tracker, _ = mark_completed(self.item, self.request.user)
            else:
                _, tracker, _ = get_or_create_trackers(self.item, self.request.user)

        ctx.update(
            {
                "lesson": self.lesson,
                "tracker": tracker,
                "item": self.item,
                "items": get_items_with_trackers(items, self.request.user),
                "submits": submits,
                "previous_item": previous_item,
                "next_item": next_item,
            }
        )
        return ctx
