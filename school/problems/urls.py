from django.urls import path

from school.problems.views import SubmitCreateView, SubmitDetailView

urlpatterns = [
    path(
        "problems/<problem>/submits/<submit>/",
        SubmitDetailView.as_view(),
        name="submit_detail",
    ),
    path(
        "problems/<problem>/submits/",
        SubmitCreateView.as_view(),
        name="submit_create",
    ),
]
