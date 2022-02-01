from django.urls import path

from school.imports.views import ImportMaterialsView

urlpatterns = [
    path("materials/", ImportMaterialsView.as_view()),
]
