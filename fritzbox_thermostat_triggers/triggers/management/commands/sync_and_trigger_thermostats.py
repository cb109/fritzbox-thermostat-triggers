from datetime import datetime
from datetime import timedelta
from typing import Optional
import http.client
import logging
import urllib.parse

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from pyfritzhome import Fritzhome
from fritzbox_thermostat_triggers.triggers.models import Thermostat
from fritzbox_thermostat_triggers.triggers.models import ThermostatLog
from fritzbox_thermostat_triggers.triggers.models import Trigger

logger = logging.getLogger(__name__)


def describe_temperature(temperature):
    """Return a string description of the given temperature."""
    if temperature == settings.TEMPERATURE_OFF:
        return "off"
    return f"{temperature} °C"


def temperatures_equal(t1, t2):
    """Handle 'off' reported as 126.5, but must be set as 0."""
    if t1 == settings.TEMPERATURE_OFF:
        t1 = 0
    if t2 == settings.TEMPERATURE_OFF:
        t2 = 0
    return t1 == t2


def get_fritzbox_connection(
    host=settings.FRITZBOX_HOST,
    user=settings.FRITZBOX_USER,
    password=settings.FRITZBOX_PASSWORD,
):
    fritzbox = Fritzhome(host, user, password)
    fritzbox.login()
    return fritzbox


def get_fritzbox_thermostat_devices():
    fritzbox = get_fritzbox_connection()
    return [device for device in fritzbox.get_devices() if device.has_thermostat]


def send_push_notification(message: str, title: Optional[str] = None):
    if not settings.PUSHOVER_USER_KEY or not settings.PUSHOVER_API_TOKEN:
        return

    # https://support.pushover.net/i44-example-code-and-pushover-libraries#python
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request(
        "POST",
        "/1/messages.json",
        urllib.parse.urlencode(
            {
                "message": message,
                "title": title,
                "token": settings.PUSHOVER_API_TOKEN,
                "user": settings.PUSHOVER_USER_KEY,
            }
        ),
        {"Content-type": "application/x-www-form-urlencoded"},
    )
    response = conn.getresponse()
    return response


def change_thermostat_target_temperature(
    thermostat: Thermostat,
    new_target_temperature: float,
    trigger: Trigger,
    no_op: bool = False,
    notify: bool = True,
    verbose: bool = False,
):
    ThermostatLog.objects.create(
        no_op=no_op,
        temperature=new_target_temperature,
        thermostat=thermostat,
        trigger=trigger,
    )

    if not trigger.recurring:
        if verbose:
            logger.info(f"Disabling non-recurring trigger {trigger}")
        trigger.enabled = False
        trigger.save(update_fields=["enabled"])

    if no_op:
        return

    fritzbox = get_fritzbox_connection()
    fritzbox.set_target_temperature(thermostat.ain, new_target_temperature)

    message = (
        f"Triggered: {thermostat.name} is now set to "
        f"{describe_temperature(new_target_temperature)}"
    )
    if verbose:
        logger.info(message)

    if notify:
        if verbose:
            logger.info("Sending PUSH notification")
        send_push_notification(
            message,
            title=(
                f"{thermostat.name} -> "
                f"{describe_temperature(new_target_temperature)}"
            ),
        )


query_any_recur_on = (
    Q(recur_on_monday=True)
    | Q(recur_on_tuesday=True)
    | Q(recur_on_wednesday=True)
    | Q(recur_on_thursday=True)
    | Q(recur_on_friday=True)
    | Q(recur_on_saturday=True)
    | Q(recur_on_sunday=True)
)


def get_soon_non_recurring_triggers(recently: datetime, now: datetime) -> list:
    return list(
        Trigger.objects.exclude(query_any_recur_on).filter(
            enabled=True, time__gte=recently, time__lte=now
        )
    )


def get_soon_recurring_triggers(recently: datetime, now: datetime) -> list:
    recurring_triggers = []

    for trigger in Trigger.objects.filter(query_any_recur_on, enabled=True).distinct():
        if not trigger.recurs_for_weekday_index(now.weekday()):
            continue

        # Ignore the specific date, check only time and weekday.
        trigger_time_only = trigger.get_normalized_time().time()

        if trigger_time_only < recently.time():
            continue
        if trigger_time_only > now.time():
            continue
        recurring_triggers.append(trigger)

    return recurring_triggers


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--minutes", action="store", default=1, dest="minutes", type=int
        )
        parser.add_argument(
            "--sync-only", action="store_true", default=False, dest="sync_only"
        )
        parser.add_argument(
            "--verbose", action="store_true", default=False, dest="verbose"
        )

    def handle(self, *args, **options):
        # This command is assumed to be run every minute as a cronjob.
        # Triggers are skipped if already executed within last interval.
        interval_minutes: int = options["minutes"]
        sync_only: bool = options["sync_only"]
        verbose: bool = options["verbose"]

        now = timezone.localtime()
        within_last_interval = now - timedelta(minutes=interval_minutes)

        non_recurring_triggers = get_soon_non_recurring_triggers(
            recently=within_last_interval, now=now
        )
        recurring_triggers = get_soon_recurring_triggers(
            recently=within_last_interval, now=now
        )
        triggers = non_recurring_triggers + recurring_triggers
        thermostats_fetched_already: bool = Thermostat.objects.count() > 0

        # Quick sanity check to save device battery life: If there are
        # no relevant Triggers at all, no need to talk to devices.
        if not sync_only and not triggers and thermostats_fetched_already:
            if verbose:
                logger.info("No Triggers found, Thermostats seem okay, do nothing")
            return

        for device in get_fritzbox_thermostat_devices():
            # Create new Device if found.
            thermostat, created = Thermostat.objects.get_or_create(ain=device.ain)
            if created and verbose:
                logger.info(f"New Thermostat created: {thermostat}")

            # Sync name to reflect eventual changes from the fritzbox admin UI.
            if created or thermostat.name != device.name:
                old_name = thermostat.name
                thermostat.name = device.name
                thermostat.save(update_fields=["name"])
                if verbose:
                    logger.info(
                        f"Thermostat name updated: {old_name} -> {thermostat.name}"
                    )

            if sync_only:
                continue

            # Trigger untriggered Triggers that need triggering, d'uh!
            thermostat_triggers = [t for t in triggers if t.thermostat == thermostat]
            for trigger in thermostat_triggers:
                if trigger.recurring and trigger.has_already_executed_within(interval_minutes):
                    if verbose:
                        logger.info(
                            f"Recurring {trigger} already executed recently, "
                            f"skipping it..."
                        )
                    continue

                no_op = False
                if temperatures_equal(device.target_temperature, trigger.temperature):
                    # Nothing to do: Spare the device request to save battery.
                    no_op = True
                    if verbose:
                        logger.info(
                            f"{trigger} target temperature {trigger.temperature} "
                            f"already reached on {device}, not sending actual "
                            f"request to save some battery..."
                        )

                change_thermostat_target_temperature(
                    new_target_temperature=trigger.temperature,
                    no_op=no_op,
                    thermostat=thermostat,
                    trigger=trigger,
                    verbose=verbose,
                )
