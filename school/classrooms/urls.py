from django.urls import path

from school.classrooms import views

urlpatterns = [
    path("", views.ClassroomListView.as_view(), name="classrooms_list"),
    path("join/", views.ClassroomJoinView.as_view(), name="classrooms_join"),
]
