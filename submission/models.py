from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import timedelta, timezone


# Define custom user model
class User(AbstractUser):
    pass


# Define external user (logs in from external source)
class ExternalUser(models.Model):
    
    # Hardcode external sources
    ORCID = 'ORCID'

    # Define source choices
    SOURCES = (
        (ORCID, 'ORCID')
    )

    # Define source
    source = models.Choices(choices=SOURCES)
    # Define username
    username = models.CharField(max_length=100)
    # Define (optional) email
    email = models.CharField(blank=True, null=True)
    # Define (optional) telephone
    phone = models.CharField(max_length=100, blank=True, null=True)

    # Metadata
    class Meta:
        # Force source, username to be unique
        unique_together = ('source', 'username')


# Define internal token (associated to external user)
class InternalToken(models.Model):
    # Define hash
    hash = models.CharField(max_length=1000)
    # Defines when the token has been created
    created = models.DateTimeField(auto_now_add=True)
    # Defines expiration time
    expires = models.DateTimeField(default=lambda: timezone.now() + timedelta(days=30), blank=True, null=True)
    # Define associated user source
    source = models.ForeignKey(ExternalUser, to_field='source', on_delete=models.CASCADE)
    # Define associated user ID
    username = models.ForeignKey(ExternalUser, to_field='username', on_delete=models.CASCADE)
    # Define foreign key constraint
    user = models.ForeignObject(ExternalUser, from_fields=['source', 'username'], to_fields=['source', 'username'])

    # Define default method for creating a token
    def generate_hash(self, *args, **kwargs):
        # TODO Create token
        raise NotImplementedError