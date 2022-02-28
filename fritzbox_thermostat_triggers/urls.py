from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView

from fritzbox_thermostat_triggers.triggers import views

urlpatterns = [
    path("triggers/", views.triggers, name="triggers"),
    path("admin/", admin.site.urls),
    path("", RedirectView.as_view(url="triggers/")),
]
