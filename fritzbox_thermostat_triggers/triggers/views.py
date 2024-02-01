from datetime import timedelta
from typing import Optional

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from fritzbox_thermostat_triggers.triggers.models import Trigger
from fritzbox_thermostat_triggers.triggers.models import ThermostatLog


@login_required
@require_http_methods(("GET",))
def list_triggers(request):
    alert : str = ""
    executed_trigger_id: Optional[str] = request.GET.get("executed", None)
    if executed_trigger_id:
        executed_trigger = Trigger.objects.get(id=executed_trigger_id)
        alert = f"Executed trigger: {executed_trigger}"

    theme: str = request.session.get("theme", "light") # Or 'dark'.
    once_expanded: bool = request.session.get("once:expanded", True)
    weekly_expanded: bool = request.session.get("weekly:expanded", True)

    triggers = Trigger.objects.order_by("thermostat__name", "time")
    onetime_triggers = [trigger for trigger in triggers if not trigger.recurring]
    recurring_triggers = [trigger for trigger in triggers if trigger.recurring]

    return render(
        request,
        "triggers/triggers.html",
        {
            "alert": alert,
            "once_expanded": once_expanded,
            "onetime_triggers": onetime_triggers,
            "recurring_triggers": recurring_triggers,
            "theme": theme,
            "weekly_expanded": weekly_expanded,
        },
    )


@login_required
@require_http_methods(("GET",))
def list_logs(request):
    theme : str = request.session.get("theme", "light") # Or 'dark'.
    logs = ThermostatLog.objects.order_by("-created_at")
    return render(
        request,
        "triggers/logs.html",
        {
            "theme": theme,
            "logs": logs,
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
    theme: str = request.session.get("theme", "light") # Or 'dark'.
    request.session["theme"] = "dark" if theme == "light" else "light"
    return redirect(request.META.get("HTTP_REFERER", "list-triggers"))


@login_required
@require_http_methods(("GET",))
def toggle_once_expanded(request):
    once_expanded: bool = request.session.get("once:expanded", True)
    request.session["once:expanded"] = not once_expanded
    return redirect(request.META.get("HTTP_REFERER", "list-triggers"))


@login_required
@require_http_methods(("GET",))
def toggle_weekly_expanded(request):
    weekly_expanded: bool = request.session.get("weekly:expanded", True)
    request.session["weekly:expanded"] = not weekly_expanded
    return redirect(request.META.get("HTTP_REFERER", "list-triggers"))


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


@login_required
@require_http_methods(("POST",))
def clone_trigger(request, pk: int):
    trigger = Trigger.objects.get(id=pk)
    trigger.id = None
    trigger.name = ((trigger.name or "") + " copy").strip()
    trigger.save()

    return redirect(request.META.get("HTTP_REFERER", "list-triggers"))


@login_required
@require_http_methods(("POST",))
def execute_trigger(request, pk: int):
    trigger = Trigger.objects.get(id=pk)
    trigger.execute()

    url: str = reverse("list-triggers") + f"?executed={pk}"
    return redirect(url)


@login_required
@require_http_methods(("POST",))
def delete_trigger(request, pk: int):
    trigger = Trigger.objects.get(id=pk)
    trigger.delete()

    return redirect(request.META.get("HTTP_REFERER", "list-triggers"))

@require_http_methods(("GET",))
def nothing(request):
    return HttpResponse("")
