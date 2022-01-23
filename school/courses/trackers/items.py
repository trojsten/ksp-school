from dataclasses import dataclass
from typing import List

from school.courses.models import LessonItem, Tracker
from school.users.models import User


@dataclass
class LessonItemWithProgress:
    item: LessonItem
    completed: bool


@dataclass
class LessonItemProgress:
    items: List[LessonItemWithProgress]
    completed: int
    total: int


def get_items_progress(items: List[LessonItem], user: User) -> LessonItemProgress:
    if not user.is_authenticated:
        return LessonItemProgress(
            [LessonItemWithProgress(i, False) for i in items], 0, len(items)
        )

    progress_items = []
    completed_items = Tracker.objects.filter(
        user=user, lesson_item__in=items, completed_at__isnull=False
    ).values_list("lesson_item_id", flat=True)

    for item in items:
        progress_items.append(LessonItemWithProgress(item, item.id in completed_items))

    return LessonItemProgress(progress_items, len(completed_items), len(items))
