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

    def __str__(self):
        return f"Set {self.thermostat.name} at {self.time} to {self.temperature}"
