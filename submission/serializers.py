from rest_framework import serializers

from .models import *


class DRMJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = DRMJob
        fields = "__all__"


class ParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = ["flag", "type", "default", "description"]


class ScriptSerializer(serializers.ModelSerializer):
    param = ParameterSerializer(many=True, read_only=True)

    class Meta:
        model = Script
        fields = ["name", "command", "job", "param"]
