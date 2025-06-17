import enum

from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint


class TrackerState(enum.Enum):
    STARTED = enum.auto()
    COMPLETE = enum.auto()
    FASTFORWARD = enum.auto()


class Tracker(models.Model):
    id: int
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+"
    )
    user_id: int
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True

    @property
    def state(self) -> TrackerState:
        raise NotImplementedError()


class LessonItemTracker(Tracker):
    lesson_item = models.ForeignKey(
        "courses.LessonItem", on_delete=models.CASCADE, related_name="+"
    )
    lesson_item_id: int

    class Meta(Tracker.Meta):
        constraints = [
            UniqueConstraint(
                fields=["lesson_item", "user"], name="tracker_item_user_unique"
            )
        ]

    def __str__(self):
        return f"{self.lesson_item} tracker for {self.user}"

    @property
    def state(self) -> TrackerState:
        if self.completed_at is not None:
            return TrackerState.COMPLETE

        return TrackerState.STARTED


class LessonTracker(Tracker):
    lesson = models.ForeignKey(
        "courses.Lesson", on_delete=models.CASCADE, related_name="+"
    )
    lesson_id: int
    total = models.IntegerField()
    completed = models.IntegerField(default=0)
    fastforward = models.BooleanField(default=False)

    class Meta(Tracker.Meta):
        constraints = [
            UniqueConstraint(
                fields=["lesson", "user"], name="tracker_lesson_user_unique"
            )
        ]

    def __str__(self):
        return f"{self.lesson} tracker for {self.user}"

    @property
    def state(self) -> TrackerState:
        if self.completed == self.total:
            return TrackerState.COMPLETE

        if self.fastforward:
            return TrackerState.FASTFORWARD

        return TrackerState.STARTED


class CourseTracker(Tracker):
    course = models.ForeignKey(
        "courses.Course", on_delete=models.CASCADE, related_name="+"
    )
    course_id: int
    total = models.IntegerField()
    completed = models.IntegerField(default=0)

    class Meta(Tracker.Meta):
        constraints = [
            UniqueConstraint(
                fields=["course", "user"], name="tracker_course_user_unique"
            )
        ]

    def __str__(self):
        return f"{self.course} tracker for {self.user}"

    @property
    def state(self) -> TrackerState:
        if self.completed == self.total:
            return TrackerState.COMPLETE

        return TrackerState.STARTED
