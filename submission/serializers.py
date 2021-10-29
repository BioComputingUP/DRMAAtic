# Import serializers library
from rest_framework import serializers
# Import custom models
from submission.models import *


class ExternalUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'


class InternalTokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = Token
        fields = '__all__'


class TestJobSerializer(serializers.ModelSerializer):

    class Meta:
        model = TestJob
        fields = '__all__'