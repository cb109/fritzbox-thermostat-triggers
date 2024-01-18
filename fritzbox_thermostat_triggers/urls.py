from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView

from fritzbox_thermostat_triggers.triggers import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("triggers/", views.list_triggers, name="list-triggers"),
    path("theme/toggle", views.toggle_theme),
    path("trigger/<int:pk>/card", views.trigger_card),
    path("trigger/<int:pk>/toggle", views.toggle_trigger),
    # path("", RedirectView.as_view(url="triggers/")),
]
