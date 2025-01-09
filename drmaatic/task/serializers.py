from pytimeparse.timeparse import timeparse
from rest_framework import serializers

from drmaatic.parameter.serializers import ParameterSerializer, SuperParameterSerializer
from drmaatic.serializers import GroupSerializer
from drmaatic.task.models import Task
from drmaatic.utils import is_user_admin


class TaskSerializer(serializers.ModelSerializer):
    param = ParameterSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = ["name", "required_tokens", "param"]

    def validate(self, attrs):
        if timeparse(attrs["_max_clock_time"]) is None:
            raise serializers.ValidationError("max_clock_time is not a valid time")

        # Private and required cannot be set together
        if attrs["is_array"] and (
                attrs["begin_index"] is None or attrs["end_index"] is None or attrs["step_index"] is None):
            raise serializers.ValidationError(
                "When is_array is defined, begin_index, end_index and step_index have to be defined")
        return attrs

    def to_representation(self, instance):
        """
        Modify the task representation removing k:v pairs with v=None and null items in the param list
        """
        if is_user_admin(self.context):
            self.fields['param'] = SuperParameterSerializer(many=True, read_only=True)
        else:
            self.fields['param'] = ParameterSerializer(many=True, read_only=True)

        data = super().to_representation(instance)

        data["param"] = [p for p in data["param"] if p is not None]
        return {k: v for k, v in data.items() if v is not None}


class SuperTaskSerializer(TaskSerializer):
    """
    Serializes the job of a task, with permissions of see every field.
    """
    groups = GroupSerializer(many=True, read_only=True)

    queues = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name", source="_queues")
    memory_mb = serializers.ReadOnlyField(source="mem")

    # Array task fields
    is_array = serializers.ReadOnlyField()
    begin_index = serializers.ReadOnlyField()
    end_index = serializers.ReadOnlyField()
    step_index = serializers.ReadOnlyField()

    max_clock_time = serializers.CharField(source="_max_clock_time")

    def validate(self, attrs):
        super(SuperTaskSerializer, self).validate(attrs)

    class Meta:
        model = Task
        fields = [
            "command", "name", "required_tokens", "groups", "queues", "cpus", "memory_mb", "is_array", "begin_index",
            "end_index", "step_index", "max_clock_time", "is_output_public", "param",
        ]
