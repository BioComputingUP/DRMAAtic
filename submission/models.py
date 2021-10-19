# Import fields
from rest_framework import fields
# Import models
from django.db import models


# Define parameter in script
class Parameter(models.Model):
    # Define substitution flag
    flag = models.CharField(blank=True, default='')
    # Define parameter type
    type = models.Choices(blank=True, default='any')  # TODO Implement choices
    # Define parameter description
    description = models.TextField(blank=False, default='')


# Define script model
class Script(models.Model):
    # Define script name
    name = models.CharField(max_length=100, blank=False)
    # Define script parameters
    params = fields.DictField(child=Parameter)
