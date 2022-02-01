from django.urls import path

from school.imports.views import (
    ImportCoursesView,
    ImportMaterialsView,
    ImportProblemsView,
)

urlpatterns = [
    path("materials/", ImportMaterialsView.as_view()),
    path("problems/", ImportProblemsView.as_view()),
    path("courses/", ImportCoursesView.as_view()),
]
