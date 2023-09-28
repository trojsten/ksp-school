from django.db.models.signals import post_save
from django.dispatch import receiver

from school.problems.models import Submit
from school.trackers.utils import mark_completed


@receiver(post_save, sender=Submit)
def submit_updated(sender, instance: Submit, **kwargs):
    # We only care about submits created in a Lesson
    if instance.lesson_item_id is None:
        return

    # We only care about OK submits
    if instance.result != "OK":
        return

    mark_completed(instance.lesson_item, instance.user, cycle=False)
