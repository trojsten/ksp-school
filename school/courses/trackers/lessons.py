import enum
from dataclasses import dataclass
from typing import List

from django.db.models import Count

from school.courses.models import Lesson, LessonItem, Tracker
from school.users.models import User


class LessonStatus(enum.Enum):
    NONE = 0
    STARTED = 1
    COMPLETE = 2
    FASTFORWARD = 3


@dataclass
class LessonWithProgress:
    lesson: Lesson
    completed: int
    total: int
    status: LessonStatus


def get_lessons_with_progress(
    lessons: List[Lesson], user: User
) -> List[LessonWithProgress]:
    if not user.is_authenticated:
        return [LessonWithProgress(l, 0, 0, LessonStatus.NONE) for l in lessons]

    out = []
    lesson_items = {
        x["lesson_id"]: x["id__count"]
        for x in LessonItem.objects.filter(lesson__in=lessons)
        .values("lesson_id")
        .annotate(Count("id"))
    }
    completed_items = {
        x["lesson_item__lesson_id"]: x["id__count"]
        for x in Tracker.objects.filter(
            user=user, lesson_item__lesson__in=lessons, completed_at__isnull=False
        )
        .values("lesson_item__lesson_id")
        .annotate(Count("id"))
    }

    for lesson in lessons:
        completed = completed_items[lesson.id] if lesson.id in completed_items else 0
        total = lesson_items[lesson.id] if lesson.id in lesson_items else 0
        status = LessonStatus.NONE
        if completed != 0:
            status = LessonStatus.STARTED

        if completed == total:
            status = LessonStatus.COMPLETE

            if lesson.slug == "ff":
                status = LessonStatus.FASTFORWARD

        out.append(LessonWithProgress(lesson, completed, total, status))

    return out
