from datetime import timedelta

from django.core.validators import MinValueValidator
from django.db import models
from pytimeparse.timeparse import timeparse

from drmaatic.models import Group
from drmaatic.queue.models import Queue


class Task(models.Model):
    # Identifier name of the script
    name = models.CharField(max_length=100, null=False, blank=False, unique=True)
    # Name of the command to execute (example.sh)
    command = models.CharField(max_length=500, null=False, blank=False)

    required_tokens = models.IntegerField(default=1, validators=[MinValueValidator(0)])

    _max_clock_time = models.CharField(default="3 hours", max_length=100, blank=False)

    is_array = models.BooleanField(default=False)
    begin_index = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(1)])
    end_index = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(1)])
    step_index = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(1)])

    # Resources parameters
    queue = models.ForeignKey(Queue, on_delete=models.SET_NULL, null=True, blank=False)
    # Number of cpus for the task
    cpus = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)],
                                       verbose_name="CPUs per task")
    # Memory for the task
    mem = models.PositiveIntegerField(default=256, validators=[MinValueValidator(256)],
                                      verbose_name="Memory per task (MB)")

    groups = models.ManyToManyField(Group, related_name="groups", blank=True)

    is_output_public = models.BooleanField(default=False)

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
