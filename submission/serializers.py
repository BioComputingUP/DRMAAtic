# Import serializers library
from rest_framework import serializers
# Import default user module
from django.contrib.auth.models import User
# Import custom models
from submission.models import Script, Parameter


# Define user serializer
class UserSerializer(serializers.ModelSerializer):
    
    # Define metadata
    class Meta:
        # Define related model
        model = User
        # Define fields to [de]serialize
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


# Define script serializer
class ScriptSerializer(serializers.ModelSerializer):
    # # Define parameters
    # params = serializers.NestedBoundField

    # Define metadata
    class Meta:
        # Define related model
        model = Script
        # Define fields to [de]serialize
        fields = ['name', 'params']
