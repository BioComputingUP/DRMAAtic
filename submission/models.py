import uuid

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy
from rest_framework import serializers

from submission_lib.manage import get_job_status


class Admin(AbstractUser):
    # Update names
    class Meta:
        verbose_name = gettext_lazy('admin')
        verbose_name_plural = gettext_lazy('admins')

    @staticmethod
    def is_admin():
        return True

    @property
    def is_authenticated(self):
        return True


class Group(models.Model):
    name = models.CharField(max_length=50)
    has_full_access = models.BooleanField(default=False, blank=False, null=False)
    throttling_rate = models.CharField(max_length=30, default="10/s", null=False, blank=False)
    token_renewal_time = models.CharField(default="1 day", null=False, blank=False, max_length=40)

    def __str__(self):
        return self.name


# Define external user (logs in from external source)
class User(models.Model):
    # Hardcode external sources
    ORCID = 'ORCID'

    # Define source choices
    SOURCES = [
            (ORCID, 'ORCID')
    ]

    # Define source
    source = models.CharField(max_length=50, choices=SOURCES)
    # Define username
    username = models.CharField(max_length=100)

    name = models.CharField(max_length=20, blank=True, null=True)
    surname = models.CharField(max_length=20, blank=True, null=True)

    # Define (optional) email
    email = models.EmailField(blank=True, null=True)
    # Define (optional) telephone
    phone = models.CharField(max_length=100, blank=True, null=True)
    # Defines whether the user is enabled
    active = models.BooleanField(default=True, blank=False, null=False)

    token_renewal_time = models.CharField(max_length=40, blank=True, null=True)

    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=False, blank=False)

    def __str__(self):
        return self.username

    def is_admin(self):
        return self.group.has_full_access

    @property
    def is_authenticated(self):
        return True

    @property
    def throttling_rate(self):
        return self.group.throttling_rate

    @property
    def get_token_renewal_time(self):
        if self.token_renewal_time is not None and self.token_renewal_time != '':
            return self.token_renewal_time
        else:
            return self.group.token_renewal_time

    # Metadata
    class Meta:
        # Force source, username to be unique
        unique_together = ('source', 'username')


# Define internal token (associated to external user)
class Token(models.Model):
    # Define hash
    hash = models.CharField(max_length=1000, editable=False)
    # Defines when the token has been created
    created = models.DateTimeField(blank=False, null=False, editable=False)
    # Defines expiration time
    expires = models.DateTimeField(blank=False, null=False, editable=False)
    # Define foreign key constraint
    user = models.ForeignKey(User, to_field='id', related_name='has_user', on_delete=models.CASCADE, editable=False)

    # user = models.ForeignObject(ExternalUser, from_fields=['source', 'username'], to_fields=['source', 'username'], related_name='has_user', on_delete=models.CASCADE)


class DRMJobTemplate(models.Model):
    class DRMQueue(models.Choices):
        LOCAL = "local"
        SUPER = "super"
        # TODO: add the queues

    class DRMEmailType(models.Choices):
        ALL = "ALL"

    # Name of the job, should describe the environment of execution e.g. 2cpus_qlocal
    name = models.CharField(max_length=50, null=False, blank=False, unique=True)
    # Name of the stdout file
    stdout_file = models.CharField(max_length=50, default="log.o", null=False, blank=False)
    stderr_file = models.CharField(max_length=50, default="log.e", null=False, blank=False)
    # Name of the stderr file
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


class Script(models.Model):
    # Create your models here.
    # Identifier name of the script
    name = models.CharField(max_length=100, null=False, blank=False, unique=True)
    # Name of the command to execute (example.sh)
    # Link to the DRM job template that will run the script
    command = models.CharField(max_length=100, null=False, blank=False)
    job = models.ForeignKey(DRMJobTemplate, on_delete=models.SET_NULL, null=True)

    is_array = models.BooleanField(default=False)
    begin_index = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(1)])
    end_index = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(1)])
    step_index = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(1)])

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


# Define parameter in script
class Parameter(models.Model):
    class Type(models.Choices):
        INTEGER = 'int'
        FLOAT = 'float'
        STRING = 'string'
        BOOL = 'bool'
        FILE = 'file'

    # Define parameter name
    name = models.CharField(max_length=100, blank=False, null=False)
    # Define substitution flag
    flag = models.CharField(max_length=100, blank=False, default='')
    # Define parameter type
    type = models.CharField(max_length=100, choices=Type.choices, blank=True, default=Type.STRING)
    # Define default value
    default = models.CharField(max_length=1000, blank=True)
    # Define parameter description
    description = models.CharField(max_length=300, blank=True, default='')
    # Define if parameter can be changed by users or only admin
    private = models.BooleanField(default=False, null=False, blank=False)
    # Define if parameter can be changed by users or only admin
    required = models.BooleanField(default=True, null=False, blank=False)

    script = models.ForeignKey(Script, related_name="param", on_delete=models.CASCADE, null=True)

    def __str__(self):
        return "{} {} {}".format(self.name, self.flag, self.default).strip()

    class Meta:
        constraints = [models.UniqueConstraint(fields=["name", "script"], name="param_name")]


class Task(models.Model):
    # The name of the task should be one of the script names
    task_name = models.ForeignKey(Script, to_field="name", on_delete=models.CASCADE, null=False)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    creation_date = models.DateTimeField(auto_now_add=True, auto_created=True)
    update_date = models.DateTimeField(auto_now=True, auto_created=True)

    class Status(models.Choices):
        REJECTED = "task has been rejected from the ws"
        RECEIVED = "task has been received from the ws"
        CREATED = "task has been created and sent to the DRM"
        UNDETERMINED = "process status cannot be determined"
        QUEUED_ACTIVE = "job is queued and active"
        SYSTEM_ON_HOLD = "job is queued and in system hold"
        USER_ON_HOLD = "job is queued and in user hold"
        USER_SYSTEM_ON_HOLD = "job is queued and in user and system hold"
        RUNNING = "job is running"
        SYSTEM_SUSPENDED = "job is system suspended"
        USER_SUSPENDED = "job is user suspended"
        DONE = "job finished normally"
        FAILED = "job finished, but failed"

    status = models.CharField(max_length=200, choices=Status.choices, blank=False, null=False, default=Status.RECEIVED)
    parent_task = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    drm_job_id = models.PositiveIntegerField(null=True, blank=True)

    # TODO : Add a reference to the user whose submitted the job

    def has_finished(self):
        return self.status in {self.Status.DONE.value, self.Status.FAILED.value}

    def update_drm_status(self):
        if self.drm_job_id is not None and not self.has_finished():
            self.status = get_job_status(str(self.drm_job_id))
            self.save()

    def __str__(self):
        return "{} : {}".format(self.pk, self.task_name.name)


class TaskParameter(models.Model):
    task = models.ForeignKey(Task, related_name="params", on_delete=models.CASCADE, null=True)
    param = models.ForeignKey(Parameter, on_delete=models.CASCADE)
    value = models.CharField(max_length=1000)

    def __str__(self):
        return "{} : {} ".format(self.param, self.value)

    # Override necessary to run validation when a model is created via create() method
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.validate_value(self.value)
        super(TaskParameter, self).save()

    # Validate the value passed in input, that has to be of the type specified in the Param
    def validate_value(self, value: str):
        try:
            if self.param.type == Parameter.Type.INTEGER.value:
                int(value)
            if self.param.type == Parameter.Type.BOOL.value:
                if isinstance(self.value, bool):
                    raise ValueError
            if self.param.type == Parameter.Type.FLOAT.value:
                float(value)
            # TODO : if self.param.type == Parameter.Type.FILE:

        except ValueError:
            raise serializers.ValidationError(
                    "The value for the {} parameter has to be of type {}".format(self.param.name, self.param.type))
        return value
