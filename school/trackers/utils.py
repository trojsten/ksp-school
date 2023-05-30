from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone

from school.courses.models import Course, Lesson, LessonItem
from school.trackers.models import (
    CourseTracker,
    LessonItemTracker,
    LessonTracker,
    TrackerState,
)
from school.users.models import User


@transaction.atomic
def get_or_create_trackers(
    item: LessonItem, user: User
) -> tuple[LessonItemTracker, LessonTracker, CourseTracker]:
    item_tracker, _ = LessonItemTracker.objects.get_or_create(
        lesson_item=item, user=user
    )

    lesson_tracker = LessonTracker.objects.filter(lesson=item.lesson, user=user).first()
    if not lesson_tracker:
        lesson_tracker = LessonTracker(lesson=item.lesson, user=user)
        lesson_tracker.total = LessonItem.objects.filter(lesson=item.lesson).count()
        lesson_tracker.started_at = item_tracker.started_at
        lesson_tracker.save()

    course_tracker = CourseTracker.objects.filter(
        course=item.lesson.course, user=user
    ).first()
    if not course_tracker:
        course_tracker = CourseTracker(course=item.lesson.course, user=user)
        course_tracker.total = Lesson.objects.filter(course=item.lesson.course).count()
        course_tracker.started_at = item_tracker.started_at
        course_tracker.save()

    return item_tracker, lesson_tracker, course_tracker


@transaction.atomic
def mark_completed(
    item: LessonItem, user: User
) -> tuple[LessonItemTracker, LessonTracker, CourseTracker]:
    item_tracker, lesson_tracker, course_tracker = get_or_create_trackers(item, user)

    # We only update the tracker if it was not completed before,
    if item_tracker.completed_at is not None:
        return item_tracker, lesson_tracker, course_tracker

    item_tracker.completed_at = timezone.now()
    item_tracker.save()

    old_state = lesson_tracker.state
    lesson_tracker.completed += 1
    new_state = lesson_tracker.state

    # LessonTracker state did not change.
    if old_state == new_state:
        lesson_tracker.save()
        return item_tracker, lesson_tracker, course_tracker

    # We have completed the Lesson (FF -> COMPLETE or STARTED -> COMPLETE)
    if new_state == TrackerState.COMPLETE:
        lesson_tracker.completed_at = item_tracker.completed_at

    # It was not tracked in CourseTracker before (STARTED -> COMPLETE)
    if old_state == TrackerState.STARTED and new_state == TrackerState.COMPLETE:
        course_tracker.completed += 1

        if course_tracker.state == TrackerState.COMPLETE:
            course_tracker.completed_at = item_tracker.completed_at

        course_tracker.save()

    lesson_tracker.save()
    return item_tracker, lesson_tracker, course_tracker


def recalculate_lesson(lesson: Lesson):
    LessonTracker.objects.filter(lesson=lesson).update(
        total=LessonItem.objects.filter(lesson=lesson).count()
    )

    completed_count = {
        x["user_id"]: x["completed"]
        for x in LessonItemTracker.objects.filter(lesson_item__lesson=lesson)
        .values("user_id")
        .annotate(completed=Count("id", filter=Q(completed_at__isnull=False)))
    }

    trackers = LessonTracker.objects.filter(lesson=lesson)
    for tracker in trackers:
        tracker.completed = completed_count.get(tracker.user_id, 0)
        if tracker.completed != tracker.total and not tracker.fastforward:
            tracker.completed_at = None
        if tracker.completed == tracker.total and tracker.completed_at is None:
            tracker.completed_at = timezone.now()

    LessonTracker.objects.bulk_update(trackers, ["completed", "completed_at"])


def recalculate_course(course: Course):
    CourseTracker.objects.filter(course=course).update(
        total=Lesson.objects.filter(course=course).count()
    )

    # First, recalculate all lessons.
    for lesson in course.lesson_set.all():
        recalculate_lesson(lesson)

    # Then update course based on updated data.
    completed_count = {
        x["user_id"]: x["completed"]
        for x in LessonTracker.objects.filter(lesson__course=course)
        .values("user_id")
        .annotate(completed=Count("id", filter=Q(completed_at__isnull=False)))
    }

    trackers = CourseTracker.objects.filter(course=course)
    for tracker in trackers:
        tracker.completed = completed_count.get(tracker.user_id, 0)
        if tracker.completed != tracker.total:
            tracker.completed_at = None
        if tracker.completed == tracker.total and tracker.completed_at is None:
            tracker.completed_at = timezone.now()

    CourseTracker.objects.bulk_update(trackers, ["completed", "completed_at"])
