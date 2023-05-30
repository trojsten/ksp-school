from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

import school.pages.views as pages

urlpatterns = [
    path("admin/", admin.site.urls),
    path("oidc/", include("mozilla_django_oidc.urls")),
    path("", pages.HomepageView.as_view()),
    path("pages/<slug>/", pages.PageView.as_view()),
    path("", include("school.courses.urls")),
    path("", include("school.problems.urls")),
    path("api/import/", include("school.imports.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns.append(path("__debug__/", include("debug_toolbar.urls")))
