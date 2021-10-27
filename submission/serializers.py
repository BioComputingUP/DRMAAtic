# Import serializers library
from rest_framework import serializers
# Import custom models
from submission.models import *


class ExternalUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExternalUser
        fields = '__ALL__'


class InternalTokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = InternalToken
        fields = '__ALL__'