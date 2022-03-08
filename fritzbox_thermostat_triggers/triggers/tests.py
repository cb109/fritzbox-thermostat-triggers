from django.utils import timezone
import logging

from django.core.management import call_command
from model_bakery import baker

from fritzbox_thermostat_triggers.triggers.models import Thermostat
from fritzbox_thermostat_triggers.triggers.models import ThermostatLog

logger = logging.getLogger(__name__)


class MockedFritzbox:
    def login(*args, **kwargs):
        pass

    def set_target_temperature(*args, **kwargs):
        pass

    def get_devices(*args, **kwargs):
        pass


class MockedDevice:
    def __init__(self, ain, name, target_temperature):
        self.ain = ain
        self.name = name
        self.target_temperature = target_temperature
        self.has_thermostat = True


def mocked_send_push_notification(message, title=None):
    logger.debug(title)
    logger.debug(message)


def test_command_sync_and_trigger_thermostats(db, monkeypatch):
    # Setup
    device_livingroom = MockedDevice("11962 0785015", "Living Room", 21)
    device_kitchen = MockedDevice("11962 0785016", "Kitchen", 21)

    thermostat_livingroom = baker.make(
        "triggers.Thermostat", ain=device_livingroom.ain, name="Other name"
    )
    assert Thermostat.objects.count() == 1
    assert thermostat_livingroom.name != device_livingroom.name

    def mocked_get_fritzbox_connection():
        return MockedFritzbox()

    def mocked_get_fritzbox_thermostat_devices():
        return [
            device_livingroom,
            device_kitchen,
        ]

    monkeypatch.setattr(
        (
            "fritzbox_thermostat_triggers.triggers.management.commands."
            "sync_and_trigger_thermostats.send_push_notification"
        ),
        mocked_send_push_notification,
    )
    monkeypatch.setattr(
        (
            "fritzbox_thermostat_triggers.triggers.management.commands."
            "sync_and_trigger_thermostats.get_fritzbox_connection"
        ),
        mocked_get_fritzbox_connection,
    )
    monkeypatch.setattr(
        (
            "fritzbox_thermostat_triggers.triggers.management.commands."
            "sync_and_trigger_thermostats.get_fritzbox_thermostat_devices"
        ),
        mocked_get_fritzbox_thermostat_devices,
    )

    # Test
    call_command("sync_and_trigger_thermostats")

    # We did not specify Triggers and already have a Thermostat fetched,
    # so the script will have skipped additional syncing.
    assert Thermostat.objects.count() == 1

    # Creating an active Trigger will help with that.
    trigger = baker.make(
        "triggers.Trigger",
        thermostat=thermostat_livingroom,
        name="my trigger",
        temperature=0.0,
        time=timezone.now(),
    )
    assert ThermostatLog.objects.count() == 0

    call_command("sync_and_trigger_thermostats")

    # A new Device has been created by the sync, the existing one has
    # its name corrected.
    assert Thermostat.objects.count() == 2
    thermostat_livingroom.refresh_from_db()
    assert thermostat_livingroom.name == device_livingroom.name

    thermostat_kitchen = Thermostat.objects.last()
    assert thermostat_kitchen.ain == device_kitchen.ain
    assert thermostat_kitchen.name == device_kitchen.name

    # The Trigger has also been executed, logged and deactivated.
    trigger.refresh_from_db()
    assert not trigger.enabled
    assert ThermostatLog.objects.count() == 1

    log = ThermostatLog.objects.last()
    assert log.triggered_at is not None
    assert log.trigger == trigger
    assert not log.no_op

    # Ensure running the command multiple times in a short timespan
    # does not actually do anything.
    call_command("sync_and_trigger_thermostats")

    trigger.refresh_from_db()
    assert not trigger.enabled
    assert ThermostatLog.objects.count() == 1
