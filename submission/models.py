from django.db import models

# Create your models here.

# Define parameter in script
class Parameter(models.Model):

    class Type(models.Choices):
        ANY = 'any'
        INTEGER = 'int'
        FLOAT = 'float'
        STRING = 'string'
        BOOL = 'bool'
        FILE = 'file'

    # # Define parameter name
    # name = models.
    # Define substitution flag
    flag = models.CharField(max_length=100, blank=True, default='')
    # Define parameter type
    type = models.CharField(max_length=100, choices=Type.choices, blank=True, default=Type.ANY)
    # Define default value
    default = models.CharField(max_length=1000)
    # Define parameter description
    description = models.TextField(blank=False, default='')

# Define script model
class Script(models.Model):
    # Define script name
    name = models.CharField(max_length=100, blank=False)
    # # Define script parameters
    # params = fields.DictField(child=Parameter)
