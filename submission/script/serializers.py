from pytimeparse.timeparse import timeparse
from rest_framework import serializers

from submission.parameter.serializers import ParameterSerializer
from submission.script.models import Script
from submission.serializers import GroupSerializer


class ScriptSerializer(serializers.ModelSerializer):
    param = ParameterSerializer(many=True, read_only=True)

    class Meta:
        model = Script
        fields = ["name", "param"]

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
        data = super().to_representation(instance)

        data["param"] = [p for p in data["param"] if p is not None]
        return {k: v for k, v in data.items() if v is not None}


class SuperScriptSerializer(ScriptSerializer):
    """
    Serializes the script of a task, with permissions of see every field.
    """
    job = serializers.CharField(source="job.name")

    groups = GroupSerializer(many=True, read_only=True)

    # Array task fields
    is_array = serializers.ReadOnlyField()
    begin_index = serializers.ReadOnlyField()
    end_index = serializers.ReadOnlyField()
    step_index = serializers.ReadOnlyField()

    max_clock_time = serializers.CharField(source="_max_clock_time")

    def validate(self, attrs):
        super(SuperScriptSerializer, self).validate(attrs)

    class Meta:
        model = Script
        fields = ["name", "command", "job", "groups", "is_output_visible", "max_clock_time", "is_array", "begin_index",
                  "end_index", "step_index",
                  "param"]
