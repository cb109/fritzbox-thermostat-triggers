from django.contrib import admin

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
        "time",
        "enabled",
        "recurring",
        "recur_on",
        "created_at",
        "updated_at",
    )

    def recurring(self, trigger):
        return trigger.recurring

    recurring.boolean = True

    def label(self, trigger):
        return trigger.thermostat.name + (
            "" if not trigger.name else f": {trigger.name}"
        )

    def recur_on(self, trigger):
        if not trigger.recurring:
            return ""
        return trigger.recur_on_label


admin.site.site_header = "fritzbox thermostat triggers"
admin.site.register(Thermostat, ThermostatAdmin)
admin.site.register(ThermostatLog, ThermostatLogAdmin)
admin.site.register(Trigger, TriggerAdmin)
