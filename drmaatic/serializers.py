from rest_framework import serializers

from .models import *
from drmaatic.utils import *

logger = logging.getLogger(__name__)


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["name", ]


class ExternalUserSerializer(serializers.ModelSerializer):
    is_admin = serializers.BooleanField(source="group.has_full_access")

    class Meta:
        model = User
        fields = ["is_admin"]


class InternalTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = '__all__'
