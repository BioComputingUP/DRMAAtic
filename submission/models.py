from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db import models


# Define custom user model
class Admin(AbstractUser):
    # Update names
    class Meta:
        verbose_name = _('admin')
        verbose_name_plural = _('admins')


# Define external user (logs in from external source)
class User(models.Model):
    
    # Hardcode external sources
    ORCID = 'ORCID'

    # Define source choices
    SOURCES = [
        (ORCID, 'ORCID')
    ]

    # Define source
    source = models.CharField(max_length=100, choices=SOURCES)
    # Define username
    username = models.CharField(max_length=100)
    # Define (optional) email
    email = models.EmailField(blank=True, null=True)
    # Define (optional) telephone
    phone = models.CharField(max_length=100, blank=True, null=True)
    # Defines whether the user is enabled
    active = models.BooleanField(default=True, blank=False, null=False)

    # Metadata
    class Meta:
        # Force source, username to be unique
        unique_together = ('source', 'username')


# Define internal token (associated to external user)
class Token(models.Model):
    # Define hash
    hash = models.CharField(max_length=1000, editable=False)
    # Defines when the token has been created
    created = models.DateTimeField(blank=False, null=False, editable=False)
    # Defines expiration time
    expires = models.DateTimeField(blank=False, null=False, editable=False)
    # # Define associated user source
    # source = models.ForeignKey(ExternalUser, to_field='source', related_name='has_source', on_delete=models.CASCADE)
    # # Define associated user ID
    # username = models.ForeignKey(ExternalUser, to_field='username', related_name='has_username', on_delete=models.CASCADE)
    # Define foreign key constraint
    user = models.ForeignKey(User, to_field='id', related_name='has_user', on_delete=models.CASCADE, editable=False)
    # user = models.ForeignObject(ExternalUser, from_fields=['source', 'username'], to_fields=['source', 'username'], related_name='has_user', on_delete=models.CASCADE)

    @staticmethod
    def generate_hash(*args, **kwargs):
        # TODO Create token
        raise NotImplementedError


# Define a test job
class TestJob(models.Model):
    # Define created datetime
    created = models.DateTimeField(auto_now_add=True, editable=False)
    # Define foreign key to user
    user = models.ForeignKey(User, related_name='owned_by', blank=True, null=True, on_delete=models.CASCADE)

