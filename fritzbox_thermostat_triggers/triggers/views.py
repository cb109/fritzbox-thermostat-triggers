from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse

from fritzbox_thermostat_triggers.triggers.models import Trigger


@login_required
@require_http_methods(("GET",))
def list_triggers(request):
    triggers = Trigger.objects.order_by(
        "time", "thermostat__name", "temperature"
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


@login_required
@require_http_methods(("GET",))
def trigger_card(request, pk: int):
    trigger = Trigger.objects.get(id=pk)
    return render(
        request,
        "triggers/_trigger_card.html",
        {
            "trigger": trigger,
        },
    )


@login_required
@require_http_methods(("POST",))
def toggle_trigger(request, pk: int):
    trigger = Trigger.objects.get(id=pk)
    trigger.enabled = not trigger.enabled
    trigger.save(update_fields=["enabled"])
    return HttpResponse()
