from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class DRMJobTemplate(models.Model):
    class DRMQueue(models.Choices):
        LOCAL = "local"
        SUPER = "super"
        # TODO: add the queues

    class DRMEmailType(models.Choices):
        ALL = "ALL"

    # Name of the job, should describe the environment of execution e.g. 2cpus_local
    name = models.CharField(max_length=50, null=False, blank=False, unique=True)
    # Name of the stdout file
    stdout_file = models.CharField(max_length=50, default="log.o", null=False, blank=False)
    # Name of the stderr file
    stderr_file = models.CharField(max_length=50, default="log.e", null=False, blank=False)
    # Name of the queue where the scripts has to run
    queue = models.CharField(max_length=20, choices=DRMQueue.choices, default=DRMQueue.LOCAL, null=False, blank=False)
    # Number of cpus for the task
    cpus_per_task = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(64)])
    n_tasks = models.PositiveIntegerField(default=1)
    mem_per_node = models.CharField(max_length=20, null=True, blank=True)
    mem_per_cpu = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
