from datetime import timedelta

from django.core.validators import MinValueValidator
from django.db import models
from pytimeparse.timeparse import timeparse

from submission.drm_job_template.models import DRMJobTemplate


class Script(models.Model):
    # Create your models here.
    # Identifier name of the script
    name = models.CharField(max_length=100, null=False, blank=False, unique=True)
    # Name of the command to execute (example.sh)
    # Link to the DRM job template that will run the script
    command = models.CharField(max_length=500, null=False, blank=False)
    job = models.ForeignKey(DRMJobTemplate, on_delete=models.SET_NULL, null=True)

    _max_clock_time = models.CharField(default="7 days", max_length=100, blank=False)

    is_array = models.BooleanField(default=False)
    begin_index = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(1)])
    end_index = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(1)])
    step_index = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(1)])

    groups = models.ManyToManyField('Group', related_name="scripts", blank=True)

    is_output_visible = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @property
    def max_clock_time(self) -> [str, None]:
        def period(delta, pattern):
            d = {}
            d['h'], rem = divmod(delta.seconds, 3600)
            d['h'] += delta.days * 24
            d['m'], _ = divmod(rem, 60)
            return pattern.format(**d)

        time_in_seconds = timeparse(self._max_clock_time)
        delta_time = timedelta(seconds=time_in_seconds)
        return period(delta_time, "{h:>02d}:{m:>02d}")

    class Meta:
        ordering = ['name']
