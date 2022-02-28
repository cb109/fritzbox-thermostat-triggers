from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from fritzbox_thermostat_triggers.triggers.models import Trigger


@login_required
def triggers(request):
    triggers = Trigger.objects.filter(enabled=True).order_by(
        "thermostat__name", "temperature"
    )
    onetime_triggers = [trigger for trigger in triggers if not trigger.recurring]
    recurring_triggers = [trigger for trigger in triggers if trigger.recurring]
    return render(
        request,
        "triggers/triggers.html",
        {
            "onetime_triggers": onetime_triggers,
            "recurring_triggers": recurring_triggers,
        },
    )
