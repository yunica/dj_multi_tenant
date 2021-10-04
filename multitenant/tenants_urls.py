from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("intranet/", include("intranet.urls", namespace="intranet")),
    path("admin/", admin.site.urls),
]
