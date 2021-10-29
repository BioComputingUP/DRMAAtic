import logging

from rest_framework import serializers
from rest_framework.fields import ReadOnlyField

from submission_lib.manage import start_job
from .models import DRMJobTemplate, Script, Task
from .serializers_utils import *

logger = logging.getLogger(__name__)


class DRMJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = DRMJobTemplate
        fields = "__all__"


class ParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = ["flag", "type", "default", "description", "private", "required"]

    def validate(self, attrs):
        if attrs["private"] and attrs["required"]:
            raise serializers.ValidationError("Private and Required fields can't be set together")
        if attrs["name"] == "task_name":
            raise serializers.ValidationError("task_name cannot be set as name of a parameter")
        return attrs


class ScriptSerializer(serializers.ModelSerializer):
    param = ParameterSerializer(many=True, read_only=True)

    class Meta:
        model = Script
        fields = ["name", "command", "job", "param"]


class TaskParameterSerializer(serializers.ModelSerializer):
    name = ReadOnlyField(source='param.name')

    class Meta:
        model = TaskParameter
        fields = ["name", "value"]


class TaskSerializer(serializers.ModelSerializer):
    params = TaskParameterSerializer(many=True, read_only=True)
    status = serializers.CharField(read_only=True)
    drm_job_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Task
        fields = ["id", "task_name", "status", "drm_job_id", "creation_date", "update_date", "params"]

    def create(self, validated_data):
        # Check if user passed the params keyword
        if "task_name" not in validated_data.keys():
            raise exceptions.NotAcceptable("The task_name parameter needs to be specified")

        # Create the task with the name
        task = Task.objects.create(task_name=validated_data["task_name"])

        create_task_folder(task.pk)

        parameters_of_task = Parameter.objects.filter(script=task.task_name)

        task_params = get_params(self.initial_data, task, parameters_of_task)
        formatted_params = format_task_params(task_params)

        logger.info(formatted_params)
        drm_params = DRMJobTemplate.objects.get(name=task.task_name.job).__dict__

        j_id, name = start_job(**drm_params, task_name=task.task_name.name,
                               command=task.task_name.command,
                               script_args=formatted_params,
                               working_dir=str(task.pk))
        if j_id is None:
            # If the start of the job had some problem then j_id is none, set the status of the task as rejected
            task.status = Task.Status.REJECTED.value
        else:
            # Otherwise we associate the job id of the DRM and set the status to CREATED
            task.drm_job_id = j_id
            task.status = Task.Status.CREATED.value

        # Must save the instance since it has been modified with the new status/job_id
        task.save()
        return task
