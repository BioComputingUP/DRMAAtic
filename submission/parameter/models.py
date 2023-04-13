from django.db import models
from rest_framework import serializers

from submission.task.models import Task


class Parameter(models.Model):
    class Type(models.TextChoices):
        INTEGER = 'int'
        FLOAT = 'float'
        STRING = 'string'
        BOOL = 'bool'
        FILE = 'file'

    # Define parameter name
    name = models.CharField(max_length=100, blank=False, null=False)
    # Define substitution flag
    flag = models.CharField(max_length=100, blank=True, default='', null=True)
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

    task = models.ForeignKey(Task, related_name="param", on_delete=models.CASCADE, null=True)

    def __str__(self):
        if self.flag:
            return "{} {} {}".format(self.name, self.flag, self.default).strip()
        else:
            return "{} {}".format(self.name, self.default).strip()

    class Meta:
        constraints = [models.UniqueConstraint(fields=["name", "task"], name="param_name")]


class JobParameter(models.Model):
    job = models.ForeignKey("Job", related_name="params", on_delete=models.CASCADE, null=True)
    param = models.ForeignKey(Parameter, on_delete=models.CASCADE)
    value = models.TextField(max_length=5000)

    def __str__(self):
        return "{} : {} ".format(self.param, self.value)

    # Override necessary to run validation when a model is created via create() method
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.validate_value(self.value)
        super(JobParameter, self).save()

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
