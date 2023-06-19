from django.urls import path

from school.problems.views import (
    SubmitCreateView,
    SubmitDetailView,
    SubmitProtocolView,
    UploadProtocolView,
)

urlpatterns = [
    path(
        "problems/<problem>/submits/<submit>/",
        SubmitDetailView.as_view(),
        name="submit_detail",
    ),
    path(
        "problems/<problem>/submits/<submit>/protocol/",
        SubmitProtocolView.as_view(),
        name="submit_protocol",
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
]
