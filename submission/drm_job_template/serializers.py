from rest_framework import serializers

from submission.drm_job_template.models import DRMJobTemplate


class DRMJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = DRMJobTemplate
        fields = "__all__"
