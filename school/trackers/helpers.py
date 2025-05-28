from dataclasses import dataclass
from typing import List, Optional

from school.courses.models import Course, CourseGroup, Lesson, LessonItem
from school.trackers.models import CourseTracker, LessonItemTracker, LessonTracker
from school.users.models import User


@dataclass
class LessonWithTracker:
    lesson: Lesson
    tracker: Optional[LessonTracker]


def get_lessons_with_trackers(
    lessons: List[Lesson], user: User
) -> List[LessonWithTracker]:
    if not user.is_authenticated:
        return [LessonWithTracker(lesson, None) for lesson in lessons]

    trackers = {
        t.lesson_id: t
        for t in LessonTracker.objects.filter(
            user=user, lesson_id__in=[x.id for x in lessons]
        )
    }

    return [LessonWithTracker(lesson, trackers.get(lesson.id)) for lesson in lessons]


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


@dataclass
class CourseWithTracker:
    course: Course
    tracker: Optional[CourseTracker]


def get_courses_with_trackers(
    courses: List[Course], user: User
) -> List[CourseWithTracker]:
    if not user.is_authenticated:
        return [CourseWithTracker(i, None) for i in courses]

    trackers = {
        t.course_id: t
        for t in CourseTracker.objects.filter(
            user=user, course_id__in=[x.id for x in courses]
        )
    }

    return [CourseWithTracker(i, trackers.get(i.id)) for i in courses]


@dataclass
class CourseGroupWithTracker:
    group: CourseGroup
    courses: List[CourseWithTracker]


def get_course_groups_with_trackers(
    groups: List[CourseGroup], user: User
) -> List[CourseGroupWithTracker]:
    return [
        CourseGroupWithTracker(i, get_courses_with_trackers(i.courses.all(), user))
        for i in groups
    ]
