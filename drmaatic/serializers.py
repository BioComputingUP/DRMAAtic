from rest_framework import serializers

from .models import *
from drmaatic.utils import *

logger = logging.getLogger(__name__)


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["name", ]
