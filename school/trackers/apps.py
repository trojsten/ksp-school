from django.apps import AppConfig


class TrackersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "school.trackers"

    def ready(self):
        # See https://docs.djangoproject.com/en/4.0/topics/signals/#connecting-receiver-functions
        from . import signals  # noqa
