from rest_framework import serializers

from .models import DRMJob, Script


class DRMJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = DRMJob
        fields = "id"


class ScriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Script
        fields = ["id", "__all__"]
