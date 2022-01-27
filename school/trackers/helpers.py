from dataclasses import dataclass
from typing import List, Optional

from school.courses.models import Lesson
from school.trackers.models import LessonTracker
from school.users.models import User


@dataclass
class LessonWithTracker:
    lesson: Lesson
    tracker: Optional[LessonTracker]


def get_lessons_with_trackers(
    lessons: List[Lesson], user: User
) -> List[LessonWithTracker]:
    trackers = {
        t.lesson_id: t
        for t in LessonTracker.objects.filter(
            user=user, lesson_id__in=[x.id for x in lessons]
        )
    }

    return [LessonWithTracker(l, trackers.get(l.id)) for l in lessons]
