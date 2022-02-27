def _patch_pushover_old_ConfigParser_import():
    import sys  # noqa
    import configparser  # noqa

    sys.modules["ConfigParser"] = configparser


_patch_pushover_old_ConfigParser_import()  # noqa

from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from pushover import Client
from pyfritzhome import Fritzhome
from fritzbox_thermostat_triggers.triggers.models import Thermostat
from fritzbox_thermostat_triggers.triggers.models import ThermostatLog
from fritzbox_thermostat_triggers.triggers.models import Trigger


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


def send_push_notification(message, title=None):
    if not settings.PUSHOVER_USER_KEY or not settings.PUSHOVER_API_TOKEN:
        return
    client = Client(
        settings.PUSHOVER_USER_KEY,
        api_token=settings.PUSHOVER_API_TOKEN,
    )
    client.send_message(message, title=title)


def change_thermostat_target_temperature(
    thermostat: Thermostat,
    new_target_temperature: float,
    trigger: Trigger,
    no_op: bool = False,
    notify: bool = True,
):
    ThermostatLog.objects.create(
        no_op=no_op,
        temperature=new_target_temperature,
        thermostat=thermostat,
        trigger=trigger,
    )
    if no_op:
        return

    fritzbox = get_fritzbox_connection()
    fritzbox.set_target_temperature(thermostat.ain, new_target_temperature)

    if notify:
        message = (
            f"{thermostat.name} is now set to "
            f"{describe_temperature(new_target_temperature)}"
        )
        send_push_notification(
            message,
            title=(
                f"{thermostat.name} -> "
                f"{describe_temperature(new_target_temperature)}"
            ),
        )


class Command(BaseCommand):
    def handle(self, *args, **options):
        now = timezone.localtime()
        within_last_hour = now - timedelta(minutes=60)

        for device in get_fritzbox_thermostat_devices():
            # Create new Device if found.
            thermostat, created = Thermostat.objects.get_or_create(ain=device.ain)

            # Update name to reflect eventual changes from the fritzbox admin UI.
            if created or thermostat.name != device.name:
                thermostat.name = device.name
                thermostat.save(update_fields=["name"])

            # Trigger untriggered Triggers that need triggering, d'uh!
            for trigger in Trigger.objects.filter(
                triggered=False,
                thermostat=thermostat,
                time__gte=within_last_hour,
                time__lte=now,
            ):
                no_op = False
                if temperatures_equal(device.target_temperature, trigger.temperature):
                    # Nothing to do: Spare the device request to save battery life.
                    no_op = True

                change_thermostat_target_temperature(
                    new_target_temperature=trigger.temperature,
                    no_op=no_op,
                    thermostat=thermostat,
                    trigger=trigger,
                )
