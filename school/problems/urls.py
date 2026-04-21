from django.urls import path

from school.problems.views import (
    ProblemDetailView,
    ProblemListView,
    SubmitCreateView,
    SubmitDetailView,
    UploadProtocolView,
)

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
    path(
        "problems/protocol_upload/",
        UploadProtocolView.as_view(),
    ),
    path(
        "problems/",
        ProblemListView.as_view(),
        name="problem_list",
    ),
    path(
        "problems/<problem>/",
        ProblemDetailView.as_view(),
        name="problem_detail",
    ),
]
