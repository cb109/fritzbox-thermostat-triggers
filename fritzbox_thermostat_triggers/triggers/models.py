from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Thermostat(BaseModel):
    ain = models.CharField(max_length=64)
    name = models.CharField(max_length=128, default="", blank=True)

    def __str__(self):
        return f"{self.name} (AIN: '{self.ain}')"


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

    @property
    def recur_on_label(self):
        return (", ").join(
            [
                label
                for idx, label in enumerate(self.weekday_labels)
                if self.recurs_for_weekday_index(idx)
            ]
        )

    def __str__(self):
        return f"Set {self.thermostat.name} at {self.time} to {self.temperature}"
