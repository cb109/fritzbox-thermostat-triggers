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
        "type",
        "ain",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    search_fields = ("name", "ain", "id")

    def type(self, thermostat):
        if thermostat.ain.startswith("grp"):
            return "GROUP"
        return ""

class ThermostatLogAdmin(BaseModelAdmin):
    list_display = (
        "created_at",
        "thermostat",
        "trigger",
        "temperature",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )

class TriggerAdmin(BaseModelAdmin):
    list_display = (
        "label",
        "enabled",
        "temperature",
        "at_time",
        "recurring",
    )
    readonly_fields = (
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
        if trigger.name:
            return f"{trigger.name}: {trigger.thermostat.name}"
        return trigger.thermostat.name


admin.site.site_header = "Thermostat Triggers"
admin.site.register(Thermostat, ThermostatAdmin)
admin.site.register(ThermostatLog, ThermostatLogAdmin)
admin.site.register(Trigger, TriggerAdmin)
