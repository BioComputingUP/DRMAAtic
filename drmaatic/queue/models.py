from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Queue(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False, unique=True)
    max_cpu = models.PositiveIntegerField(default=16, validators=[MinValueValidator(1), MaxValueValidator(64)],
                                          verbose_name="Maximum CPUs per node")
    max_mem = models.PositiveIntegerField(default=1024, validators=[MinValueValidator(1), MaxValueValidator(96000)],
                                          verbose_name="Maximum memory (MB) per node")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
