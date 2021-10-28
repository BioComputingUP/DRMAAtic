# Import serializers library
from rest_framework import serializers
# Import custom models
from submission.models import *


class ExternalUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExternalUser
        fields = '__all__'


class InternalTokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = InternalToken
        fields = '__all__'


class TestJobSerializer(serializers.ModelSerializer):

    class Meta:
        model = TestJob
        fields = '__all__'