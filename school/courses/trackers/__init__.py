from django.utils import timezone

from school.courses.models import LessonItem, Tracker
from school.users.models import User


def mark_started(item: LessonItem, user: User):
    Tracker.objects.get_or_create(lesson_item=item, user=user)


def mark_completed(item: LessonItem, user: User):
    obj, _ = Tracker.objects.get_or_create(lesson_item=item, user=user)

    if not obj.completed_at:
        obj.completed_at = timezone.now()
        obj.save()
