from dataclasses import dataclass
from typing import List, Optional

from school.courses.models import Lesson, LessonItem
from school.trackers.models import LessonItemTracker, LessonTracker
from school.users.models import User


@dataclass
class LessonWithTracker:
    lesson: Lesson
    tracker: Optional[LessonTracker]


def get_lessons_with_trackers(
    lessons: List[Lesson], user: User
) -> List[LessonWithTracker]:
    if not user.is_authenticated:
        return [LessonWithTracker(l, None) for l in lessons]

    trackers = {
        t.lesson_id: t
        for t in LessonTracker.objects.filter(
            user=user, lesson_id__in=[x.id for x in lessons]
        )
    }

    return [LessonWithTracker(l, trackers.get(l.id)) for l in lessons]


@dataclass
class LessonItemWithTracker:
    item: LessonItem
    tracker: Optional[LessonItemTracker]


def get_items_with_trackers(
    items: List[LessonItem], user: User
) -> List[LessonItemWithTracker]:
    if not user.is_authenticated:
        return [LessonItemWithTracker(i, None) for i in items]

    trackers = {
        t.lesson_item_id: t
        for t in LessonItemTracker.objects.filter(
            user=user, lesson_item_id__in=[x.id for x in items]
        )
    }

    return [LessonItemWithTracker(i, trackers.get(i.id)) for i in items]
