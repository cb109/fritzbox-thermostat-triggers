from django.contrib import admin
from django.utils import timezone

from fritzbox_thermostat_triggers.triggers.models import Thermostat
from fritzbox_thermostat_triggers.triggers.models import ThermostatLog
from fritzbox_thermostat_triggers.triggers.models import Trigger


class BaseModelAdmin(admin.ModelAdmin):
    save_as = True
    save_on_top = True


class ThermostatAdmin(BaseModelAdmin):
    list_display = (
        "name",
        "ain",
        "created_at",
        "updated_at",
    )
    search_fields = ("name", "ain", "id")


class ThermostatLogAdmin(BaseModelAdmin):
    list_display = (
        "thermostat",
        "trigger",
        "triggered_at",
        "temperature",
        "created_at",
        "updated_at",
    )


class TriggerAdmin(BaseModelAdmin):
    list_display = (
        "label",
        "temperature",
        "recurring",
        "time",
        "at_time",
        "enabled",
        "created_at",
        "updated_at",
    )
    autocomplete_fields = ("thermostat",)

    def at_time(self, trigger):
        if trigger.recurring:
            return trigger.get_recurring_time_label()
        return trigger.get_formatted_time()

    def recurring(self, trigger):
        return trigger.recurring

    recurring.boolean = True

    def label(self, trigger):
        return trigger.thermostat.name + (
            "" if not trigger.name else f": {trigger.name}"
        )


admin.site.site_header = "fritzbox thermostat triggers"
admin.site.register(Thermostat, ThermostatAdmin)
admin.site.register(ThermostatLog, ThermostatLogAdmin)
admin.site.register(Trigger, TriggerAdmin)
