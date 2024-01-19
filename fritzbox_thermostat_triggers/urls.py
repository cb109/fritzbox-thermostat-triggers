from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView

from fritzbox_thermostat_triggers.triggers import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("theme/toggle", views.toggle_theme),
    path("logs/", views.list_logs, name="list-logs"),
    path("triggers/", views.list_triggers, name="list-triggers"),
    path("trigger/<int:pk>/card", views.trigger_card),
    path("trigger/<int:pk>/toggle", views.toggle_trigger),
    path("", RedirectView.as_view(url="triggers/")),
]
