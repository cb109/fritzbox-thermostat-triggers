from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from fritzbox_thermostat_triggers.triggers.models import Trigger


@login_required
@require_http_methods(("GET",))
def list_triggers(request):
    theme : str = request.session.get("theme", "light") # Or 'dark'.

    triggers = Trigger.objects.order_by("thermostat__name", "time")
    onetime_triggers = [trigger for trigger in triggers if not trigger.recurring]
    recurring_triggers = [trigger for trigger in triggers if trigger.recurring]

    return render(
        request,
        "triggers/triggers.html",
        {
            "theme": theme,
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
@require_http_methods(("GET",))
def toggle_theme(request):
    theme : str = request.session.get("theme", "light") # Or 'dark'.
    request.session["theme"] = "dark" if theme == "light" else "light"
    return redirect("list-triggers")


@login_required
@require_http_methods(("POST",))
def toggle_trigger(request, pk: int):
    trigger = Trigger.objects.get(id=pk)
    trigger.enabled = not trigger.enabled

    ui_update_message : str = ""
    if trigger.enabled and not trigger.recurring and trigger.outdated:
        # Makes no sense to enable a trigger for the past,
        # update to a sensible new date, either today or tomorrow.
        old_time_naive = trigger.get_normalized_time()
        old_time_aware = timezone.make_aware(
            old_time_naive, timezone.get_current_timezone()
        )

        now = timezone.localtime()
        today_same_clock = now.replace(
            hour=old_time_aware.hour,
            minute=old_time_aware.minute,
            second=old_time_aware.second
        )
        tomorrow_same_clock = today_same_clock + timedelta(days=1)

        if now < today_same_clock and today_same_clock > old_time_aware:
            new_time = today_same_clock
            ui_update_message = "Time has been set to <b>today</b>"
        else:
            new_time = tomorrow_same_clock
            ui_update_message = "Time has been set to <b>tomorrow</b>"

        trigger.time = new_time

    trigger.save(update_fields=["enabled", "time"])

    return render(
        request,
        "triggers/_trigger_card.html",
        {
            "trigger": trigger,
            "message": ui_update_message,
        },
    )
