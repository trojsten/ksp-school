from django.urls import path

from school.imports.views.courses import ImportCoursesView
from school.imports.views.materials import ImportMaterialsView
from school.imports.views.problems import ImportProblemsView

urlpatterns = [
    path("materials/", ImportMaterialsView.as_view()),
    path("problems/", ImportProblemsView.as_view()),
    path("courses/", ImportCoursesView.as_view()),
]
