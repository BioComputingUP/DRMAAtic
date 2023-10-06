from rest_framework import serializers
from rest_framework.fields import ReadOnlyField

from drmaatic.parameter.models import Parameter, JobParameter
from drmaatic.utils import is_user_admin


class ParameterSerializer(serializers.ModelSerializer):
    """
    Serializes the parameters of a script. Validates the data in input in order to ensure that everything is ok
    """

    class Meta:
        model = Parameter
        fields = ["name", "type", "default", "description", "required"]

    def to_representation(self, parameter):
        # If the parameter is not private, return its representation
        if not parameter.private:
            return super().to_representation(parameter)
        # Private parameters are only returned if the user is an admin
        else:
            return None

    def validate(self, attrs):
        # Private and required cannot be set together
        if attrs["private"] and attrs["required"]:
            raise serializers.ValidationError("Private and Required fields can't be set together")
        # Special flag for the task that needs to be executed
        if attrs["name"] == "task":
            raise serializers.ValidationError("'task' cannot be set as name of a parameter")
        # Special flag to refer to another task already submitted (via uuid)
        if attrs["name"] == "parent_job":
            raise serializers.ValidationError("parent_job cannot be set as name of a parameter")
        return attrs


class SuperParameterSerializer(ParameterSerializer):
    """
    Serializes the parameters of a script for a superuser.
    """

    class Meta:
        model = Parameter
        fields = ["name", "flag", "type", "default", "description", "required"]

    def to_representation(self, parameter):
        return serializers.ModelSerializer.to_representation(self, parameter)


class TaskParameterSerializer(serializers.ModelSerializer):
    """
    Serializes a parameter associated to a task, removing private parameters for non-admin users
    """
    name = ReadOnlyField(source='param.name')

    def to_representation(self, task_parameter):
        if is_user_admin(self.context) or not task_parameter.param.private:
            return super().to_representation(task_parameter)
        else:
            return None

    class Meta:
        model = JobParameter
        fields = ["name", "value"]
