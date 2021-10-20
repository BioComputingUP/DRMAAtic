from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


# TODO: If we want we can create a model for the queues instead of hard-coding them as choices
# class DRMQueue(models.Model):
#     name = models.CharField(max_length=20, null=False, blank=False)

# Create your models here.
class DRMJob(models.Model):
    class DRMQueue(models.Choices):
        LOCAL = "local"
        # TODO: add the queues

    class DRMEmailType(models.Choices):
        ALL = "ALL"

    # Name of the job, should describe the environment of execution e.g. 2cpus_qlocal
    name = models.CharField(max_length=50, null=False, blank=False, unique=True)
    # Name of the stout file
    stdout_file = models.CharField(max_length=50, default="log.o", null=False, blank=False)
    # Name of the sterr file
    stderr_file = models.CharField(max_length=50, default="log.e", null=False, blank=False)
    # Name of the queue where the scripts has to run
    queue = models.CharField(max_length=20, choices=DRMQueue.choices, default=DRMQueue.LOCAL, null=False, blank=False)
    # Number of cpus for the task
    cpus_per_task = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(64)])

    # email_type = models.CharField(
    #         max_length=10,
    #         choices=DRMEmailType.choices,
    #         default=DRMEmailType.ALL,
    #         null=True,
    #         blank=True
    # )
    # email_addr = models.EmailField(blank=True, null=True)
    # account = models.CharField(max_length=30)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


# Create your models here.
class Script(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False, unique=True)
    command = models.CharField(max_length=100, null=False, blank=False)

    job = models.ForeignKey(DRMJob, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


# Define parameter in script
class Parameter(models.Model):
    class Type(models.Choices):
        ANY = 'any'
        INTEGER = 'int'
        FLOAT = 'float'
        STRING = 'string'
        BOOL = 'bool'
        FILE = 'file'

    # # Define parameter name
    # name = models.
    # Define substitution flag
    flag = models.CharField(max_length=100, blank=True, default='')
    # Define parameter type
    type = models.CharField(max_length=100, choices=Type.choices, blank=True, default=Type.ANY)
    # Define default value
    default = models.CharField(max_length=1000, blank=True)
    # Define parameter description
    description = models.CharField(max_length=300, blank=True, default='')

    script = models.ForeignKey(Script, related_name="param", on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return "{} {}".format(self.flag, self.default).strip()
