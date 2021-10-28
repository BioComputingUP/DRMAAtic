import logging
import os

from rest_framework import exceptions, serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import ReadOnlyField

from submission_lib.manage import start_job
from .models import DRMJobTemplate, Parameter, Script, Task, TaskParameter

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


def get_extension(param_name, file_name):
    if '.' not in file_name:
        raise exceptions.NotAcceptable("The file parameter {} must have a file extension".format(param_name))
    return file_name.split('.')[-1]


def get_params(user_param, task, parameters_of_task):
    created_params = set()
    for param in parameters_of_task:
        param = Parameter.objects.get(script=task.task_name, name=param.name)
        # Param not private and user has set it
        if not param.private and param.name in user_param.keys():
            # If the validation on the creation fails then the task (and all related param) will be deleted
            try:
                if param.type == Parameter.Type.FILE.value:
                    ext = get_extension(param.name, user_param[param.name].name)
                    file_pth = "/home/alessio/projects/submission_ws/outputs/{}/{}.{}".format(task.pk, param.name, ext)
                    with open(file_pth, "wb+") as f:
                        for chunk in user_param[param.name].chunks():
                            f.write(chunk)
                    new_param = TaskParameter.objects.create(task=task, param=param, value=file_pth)
                else:
                    new_param = TaskParameter.objects.create(task=task, param=param,
                                                             value=user_param[param.name])
                created_params.add(new_param)
            except ValidationError as e:
                task.delete()
                raise e
        # Param is required and user did not set it
        elif param.required and param.name not in user_param.keys():
            task.delete()  # The submitted task was not created with proper params, destroy it
            raise exceptions.NotAcceptable("The parameter {} must be specified for the {} task"
                                           .format(param.name, task.task_name))
        # Param is private and hase to be set
        elif param.private:
            new_param = TaskParameter.objects.create(task=task, param=param, value=param.default)
            created_params.add(new_param)
    return created_params


def create_task_folder(wd):
    # TODO : Change base path
    os.makedirs(os.path.join("/home/alessio/projects/submission_ws/outputs", str(wd)), exist_ok=True)


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
