from django.db.models.signals import post_save
from django.dispatch import receiver

from school.courses import trackers
from school.problems.models import Submit


@receiver(post_save, sender=Submit)
def submit_update_receiver(sender, instance: Submit, **kwargs):
    """
    This will update tracker for submits created from lesson.
    We only care about item completion, so we only update on OK result.
    """

    if instance.result != "OK" or instance.lesson_item_id is None:
        return

    trackers.mark_completed(instance.lesson_item, instance.user)
