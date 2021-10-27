import logging

from rest_framework import exceptions
from rest_framework.exceptions import ValidationError
from rest_framework.fields import ReadOnlyField

from submission_lib.manage import start_job
from .models import *

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


def define_params_of_task(parameters_of_task, task, user_param):
    created_params = set()
    for task_param in parameters_of_task:
        param = Parameter.objects.get(script=task.name, name=task_param.name)
        # Param not private and user has set it
        if not task_param.private and task_param.name in user_param.keys():
            # If the validation on the creation fails then the task (and all related param) will be deleted
            try:
                new_param = TaskParameter.objects.create(task=task, param=param, value=user_param[task_param.name])
                created_params.add(new_param)
            except ValidationError as e:
                task.delete()
                raise e
        # Param is required and user did not set it
        elif task_param.required and task_param.name not in user_param.keys():
            task.delete()  # The submitted task was not created with proper params, destroy it
            raise exceptions.NotAcceptable("The parameter {} must be specified for the {} task"
                                           .format(task_param.name, task.name))
        # Param is private and hase to be set
        elif task_param.private:
            new_param = TaskParameter.objects.create(task=task, param=param, value=task_param.default)
            created_params.add(new_param)
    return created_params


def format_task_params(passed_params):
    formatted_params = []
    for passed_param in passed_params:
        # If the param is of type Bool and is positive, no value has to be passed, only the flag
        if passed_param.param.type == Parameter.Type.BOOL.value and passed_param.value:
            formatted_params.append("{}".format(passed_param.param.flag))
        else:
            # If at the end of the flag there is a '=' then no space is required between flag and value
            format_string = "{} {}"
            if passed_param.param.flag[-1] == "=":
                format_string = "{}{}"
            formatted_params.append(format_string.format(passed_param.param.flag, passed_param.value).strip())

    return formatted_params


class TaskSerializer(serializers.ModelSerializer):
    params = TaskParameterSerializer(many=True, read_only=True)
    custom_params = serializers.JSONField(write_only=True, required=False)
    status = serializers.CharField(read_only=True)
    drm_job_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Task
        fields = ["id", "name", "status", "drm_job_id", "creation_date", "update_date", "params", "custom_params"]

    def create(self, validated_data):
        user_param = dict()
        # Check if user passed the params keyword
        if "custom_params" in validated_data.keys():
            user_param = validated_data.pop('custom_params')
        # Create the task with the name
        task = Task.objects.create(**validated_data)
        parameters_of_task = Parameter.objects.filter(script=task.name)

        created_params = define_params_of_task(parameters_of_task, task, user_param)

        formatted_params = format_task_params(created_params)

        logger.info(formatted_params)
        drm_params = DRMJobTemplate.objects.get(name=task.name.job).__dict__

        j_id, name = start_job(**drm_params, task_name=task.name.name,
                               command=task.name.command,
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
