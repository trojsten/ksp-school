from django.urls import include, path

from school.courses.views import CoursesListView, CourseView, LessonView

urlpatterns = [
    path("courses/", CoursesListView.as_view(), name="course_list"),
    path("courses/<slug>/", CourseView.as_view(), name="course_detail"),
    path("courses/<course>/<lesson>/", LessonView.as_view(), name="lesson"),
    path("courses/<course>/<lesson>/<item>/", LessonView.as_view(), name="lesson"),
]
