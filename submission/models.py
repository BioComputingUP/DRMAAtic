from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy
from pytimeparse.timeparse import timeparse


class Admin(AbstractUser):
    # Update names
    class Meta:
        verbose_name = gettext_lazy('admin')
        verbose_name_plural = gettext_lazy('admins')

    @staticmethod
    def is_admin():
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def throttling_rate_burst(self):
        return "1000/s"

    @property
    def throttling_rate_sustained(self):
        return "1000/s"


class Group(models.Model):
    name = models.CharField(max_length=50)
    has_full_access = models.BooleanField(default=False, blank=False, null=False)
    throttling_rate_burst = models.CharField(max_length=30, default="10/s", null=False, blank=False)
    throttling_rate_sustained = models.CharField(max_length=30, default="100/day", null=False, blank=False)
    token_renewal_time = models.CharField(default="1 day", null=False, blank=False, max_length=40)

    def __str__(self):
        return self.name


# Define external user (logs in from external source)
class User(models.Model):
    # Hardcode external sources
    ORCID = 'ORCID'

    # Define source choices
    SOURCES = [
            (ORCID, 'ORCID'),
            ('INTERNAL', 'INTERNAL')
    ]

    # Define source
    source = models.CharField(max_length=50, choices=SOURCES)
    # Define username
    username = models.CharField(max_length=100)

    name = models.CharField(max_length=20, blank=True, null=True)
    surname = models.CharField(max_length=20, blank=True, null=True)

    # Define (optional) email
    email = models.EmailField(blank=True, null=True)
    # Define (optional) telephone
    phone = models.CharField(max_length=100, blank=True, null=True)
    # Defines whether the user is enabled
    active = models.BooleanField(default=True, blank=False, null=False)

    token_renewal_time = models.CharField(max_length=40, blank=True, null=True)

    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)

    anon_user = Group.objects.get_or_create(name='anon',
                                            defaults={'throttling_rate_burst'    : '20/s',
                                                      'throttling_rate_sustained': '100/d',
                                                      'token_renewal_time'       : '3 days'})[0]

    def __str__(self):
        return self.username

    def is_admin(self):
        if self.group:
            return self.group.has_full_access
        return False

    def group_name(self):
        if self.group:
            return self.group.name
        return None

    @property
    def is_authenticated(self):
        return True

    @property
    def throttling_rate_burst(self):
        if self.group:
            return self.group.throttling_rate_burst
        else:
            return self.anon_user.throttling_rate_burst

    @property
    def throttling_rate_sustained(self):
        if self.group:
            return self.group.throttling_rate_sustained
        else:
            return self.anon_user.throttling_rate_sustained

    @property
    def get_token_renewal_time_seconds(self):
        if self.token_renewal_time is not None and self.token_renewal_time != '':
            return timeparse(self.token_renewal_time)
        elif self.group:
            return timeparse(self.group.token_renewal_time)
        else:
            return timeparse(self.anon_user.token_renewal_time)

    # Metadata
    class Meta:
        # Force source, username to be unique
        unique_together = ('source', 'username')


# Define internal token (associated to external user)
class Token(models.Model):
    # Define hash
    hash = models.CharField(max_length=1000)
    # Defines when the token has been created
    created = models.DateTimeField(blank=False, null=False)
    # Defines expiration time
    expires = models.DateTimeField(blank=False, null=False)
    # Define foreign key constraint
    user = models.ForeignKey(User, to_field='id', related_name='has_user', on_delete=models.CASCADE)
