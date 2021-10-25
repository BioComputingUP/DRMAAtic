from rest_framework import exceptions, serializers
from rest_framework.fields import ReadOnlyField

from .models import *


class DRMJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = DRMJob
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


class TaskSerializer(serializers.ModelSerializer):
    params = TaskParameterSerializer(many=True, read_only=True)
    custom_params = serializers.DictField(child=serializers.CharField(), write_only=True, required=False)
    status = serializers.ReadOnlyField()

    class Meta:
        model = Task
        fields = ["name", "status", "creation_date", "update_date", "params", "custom_params"]

    def create(self, validated_data):
        user_param = dict()
        # Check if user passed the params keyword
        if "custom_params" in validated_data.keys():
            user_param = validated_data.pop('custom_params')
        # Create the task with the name
        task = Task.objects.create(**validated_data)
        parameters_of_task = Parameter.objects.filter(script=task.name)

        for task_param in parameters_of_task:
            # Param not private and user has set it
            if not task_param.private and task_param.name in user_param.keys():
                param = Parameter.objects.get(script=task.name, name=task_param.name)
                TaskParameter.objects.create(task=task, param=param, value=user_param[task_param.name])
            # Param is required and user did not set it
            elif task_param.required and task_param.name not in user_param.keys():
                raise exceptions.NotAcceptable(
                        "The parameter {} must be specified for the {} task".format(task_param.name, task.name))
            # Param is private and hase to be set
            elif task_param.private:
                param = Parameter.objects.get(script=task.name, name=task_param.name)
                TaskParameter.objects.create(task=task, param=param, value=task_param.default)

        return task
