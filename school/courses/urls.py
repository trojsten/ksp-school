from django.urls import include, path

from school.courses.views import CoursesListView, CourseView

urlpatterns = [
    path("courses/", CoursesListView.as_view(), name="course_list"),
    path("courses/<slug>/", CourseView.as_view(), name="course_detail"),
]
