from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView

from fritzbox_thermostat_triggers.triggers import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("logs/", views.list_logs, name="list-logs"),
    path("nothing/", views.nothing),
    path("triggers/", views.list_triggers, name="list-triggers"),
    path("trigger/<int:pk>/card", views.trigger_card),
    path("trigger/<int:pk>/toggle", views.toggle_trigger),
    path("trigger/<int:pk>/execute", views.execute_trigger, name="execute-trigger"),
    path("trigger/<int:pk>/clone", views.clone_trigger, name="clone-trigger"),
    path("trigger/<int:pk>/delete", views.delete_trigger, name="delete-trigger"),
    path("ui/toggle/theme", views.toggle_theme),
    path("ui/toggle/once", views.toggle_once_expanded),
    path("ui/toggle/weekly", views.toggle_weekly_expanded),
    path("", RedirectView.as_view(url="triggers/")),
]
