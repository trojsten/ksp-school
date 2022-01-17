from django.urls import path

from school.problems.views import SubmitDetailView

urlpatterns = [
    path(
        "problems/<problem>/submits/<submit>/",
        SubmitDetailView.as_view(),
        name="submit_detail",
    ),
]
