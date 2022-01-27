import enum

from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint


class TrackerState(enum.Enum):
    STARTED = enum.auto()
    COMPLETE = enum.auto()
    FASTFORWARD = enum.auto()


class Tracker(models.Model):
    class Meta:
        abstract = True

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+"
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    @property
    def state(self) -> TrackerState:
        raise NotImplementedError()


class LessonItemTracker(Tracker):
    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["lesson_item", "user"], name="tracker_item_user_unique"
            )
        ]

    lesson_item = models.ForeignKey(
        "courses.LessonItem", on_delete=models.CASCADE, related_name="+"
    )

    @property
    def state(self) -> TrackerState:
        if self.completed_at is not None:
            return TrackerState.COMPLETE

        return TrackerState.COMPLETE


class LessonTracker(Tracker):
    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["lesson", "user"], name="tracker_lesson_user_unique"
            )
        ]

    lesson = models.ForeignKey(
        "courses.Lesson", on_delete=models.CASCADE, related_name="+"
    )
    total = models.IntegerField()
    completed = models.IntegerField(default=0)
    fastforward = models.BooleanField(default=False)

    @property
    def state(self) -> TrackerState:
        if self.completed == self.total:
            return TrackerState.COMPLETE

        if self.fastforward:
            return TrackerState.FASTFORWARD

        return TrackerState.STARTED


class CourseTracker(Tracker):
    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["course", "user"], name="tracker_course_user_unique"
            )
        ]

    course = models.ForeignKey(
        "courses.Course", on_delete=models.CASCADE, related_name="+"
    )
    total = models.IntegerField()
    completed = models.IntegerField(default=0)

    @property
    def state(self) -> TrackerState:
        if self.completed == self.total:
            return TrackerState.COMPLETE

        return TrackerState.STARTED
