from datetime import datetime
from datetime import timedelta

from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


DATETIME_FULL_FORMAT = "%d.%m.%Y at %H:%M"
TIME_ONLY_FORMAT = "%H:%M"


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Thermostat(BaseModel):
    ain = models.CharField(max_length=64)
    name = models.CharField(max_length=128, default="", blank=True)

    def __str__(self):
        return self.name or self.ain


class ThermostatLog(BaseModel):
    thermostat = models.ForeignKey(
        "triggers.Thermostat", related_name="logs", on_delete=models.CASCADE
    )
    trigger = models.ForeignKey(
        "triggers.Trigger", null=True, related_name="logs", on_delete=models.CASCADE
    )
    triggered_at = models.TimeField(blank=True, null=True)
    temperature = models.FloatField()

    no_op = models.BooleanField(default=False)
    """When True, no actual request was sent as temperate already matched."""

    def __str__(self):
        return f"{self.thermostat}: {self.trigger}"


class Trigger(BaseModel):
    thermostat = models.ForeignKey("triggers.Thermostat", on_delete=models.CASCADE)
    name = models.CharField(max_length=128, default="", blank=True)
    time = models.DateTimeField()
    temperature = models.FloatField(
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(28.0),
        ],
    )
    enabled = models.BooleanField(default=True)

    recur_on_monday = models.BooleanField(default=False)
    recur_on_tuesday = models.BooleanField(default=False)
    recur_on_wednesday = models.BooleanField(default=False)
    recur_on_thursday = models.BooleanField(default=False)
    recur_on_friday = models.BooleanField(default=False)
    recur_on_saturday = models.BooleanField(default=False)
    recur_on_sunday = models.BooleanField(default=False)

    @property
    def weekday_flags(self):
        return (
            self.recur_on_monday,
            self.recur_on_tuesday,
            self.recur_on_wednesday,
            self.recur_on_thursday,
            self.recur_on_friday,
            self.recur_on_saturday,
            self.recur_on_sunday,
        )

    @property
    def weekday_labels(self):
        return (
            "Mon",
            "Tue",
            "Wed",
            "Thu",
            "Fri",
            "Sat",
            "Sun",
        )

    @property
    def recurring(self):
        return any(self.weekday_flags)

    def recurs_for_weekday_index(self, weekday_index: int) -> bool:
        idx_to_recurs = {idx: flag for idx, flag in enumerate(self.weekday_flags)}
        return idx_to_recurs[weekday_index]

    def get_normalized_time(self) -> datetime:
        return timezone.make_naive(self.time, timezone.get_current_timezone())

    def get_formatted_time(self, date_format: str = DATETIME_FULL_FORMAT) -> str:
        return self.get_normalized_time().strftime(date_format)

    def get_recurring_time_label(self) -> str:
        """Return str like 'Mon, Tue, Wed, Thu, Fri, Sat, Sun at 21:00'."""
        return (
            (", ").join(
                [
                    label
                    for idx, label in enumerate(self.weekday_labels)
                    if self.recurs_for_weekday_index(idx)
                ]
            )
            + " at "
            + self.get_formatted_time(TIME_ONLY_FORMAT)
        )

    def has_already_executed_within(self, minutes: int) -> bool:
        threshold = timezone.localtime() - timedelta(minutes=minutes)
        return self.logs.filter(triggered_at__gte=threshold)

    def __str__(self):
        formatted_time = self.get_formatted_time(TIME_ONLY_FORMAT)
        return f"{self.thermostat.name} at {formatted_time} -> {self.temperature}"
