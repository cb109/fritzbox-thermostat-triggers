from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from fritzbox_thermostat_triggers.triggers.models import Trigger


@login_required
def triggers(request):
    triggers = Trigger.objects.filter(triggered=False).order_by(
        "thermostat__name", "temperature"
    )
    return render(request, "triggers/triggers.html", {"triggers": triggers})
