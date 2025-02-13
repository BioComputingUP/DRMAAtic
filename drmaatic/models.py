from django.contrib.auth.models import AbstractUser
from django.db import models, OperationalError
from django.utils.translation import gettext_lazy
from pytimeparse.timeparse import timeparse


class classproperty(property):
    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()


from django.db import connections


def table_exists(table_name: str, connection_name: str) -> bool:
    return table_name in connections[connection_name].introspection.table_names()


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
    def group(self):
        return Group.anonymous


class Group(models.Model):
    name = models.CharField(max_length=50)
    has_full_access = models.BooleanField(default=False, blank=False, null=False)
    throttling_rate_burst = models.CharField(max_length=30, default="10/s", null=False, blank=False)
    token_renewal_time = models.CharField(default="1 day", null=False, blank=False, max_length=40, verbose_name="JWT renewal time")
    cpu_credit_max_amount = models.IntegerField(default=100, blank=False, null=False, verbose_name="CPU credit max amount")
    _cpu_credit_regen_time = models.CharField(default="30 seconds", null=False, blank=False, max_length=40, verbose_name="CPU credit regen time")
    cpu_credit_regen_amount = models.IntegerField(default=1, blank=False, null=False, verbose_name="CPU credit regen amount")

    @property
    def cpu_credit_regen_time(self):
        return timeparse(self._cpu_credit_regen_time)

    @classproperty
    def anonymous(self):
        try:
            return self.objects.get_or_create(name='anonymous', defaults={'throttling_rate_burst': '20/s',
                                                                          'token_renewal_time': '3 days',
                                                                          'cpu_credit_max_amount': 100})[0]
        except:
            return Group(name='anonymous', throttling_rate_burst='20/s', token_renewal_time='3 days',
                         cpu_credit_max_amount=100)

    @classproperty
    def registered(self):
        try:
            return self.objects.get_or_create(name='registered', defaults={'throttling_rate_burst': '30/s',
                                                                           'token_renewal_time': '5 days',
                                                                           'cpu_credit_max_amount': 200})[0]
        except:
            return Group(name='registered', throttling_rate_burst='30/s', token_renewal_time='5 days',
                         cpu_credit_max_amount=200)

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

    token_renewal_time = models.CharField(max_length=40, blank=True, null=True, verbose_name="JWT renewal time")

    group = models.ForeignKey('Group', on_delete=models.SET_DEFAULT, null=False, default=Group.registered.id)

    def __str__(self):
        return self.username

    def is_admin(self):
        return self.group.has_full_access

    def group_name(self):
        return self.group.name

    @property
    def is_authenticated(self):
        return True

    @property
    def throttling_rate_burst(self):
        if self.group:
            return self.group.throttling_rate_burst
        else:
            return Group.anonymous.throttling_rate_burst

    @property
    def get_token_renewal_time_seconds(self):
        if self.token_renewal_time is not None and self.token_renewal_time != '':
            return timeparse(self.token_renewal_time)
        elif self.group:
            return timeparse(self.group.token_renewal_time)
        else:
            return timeparse(Group.anonymous.token_renewal_time)

    # Metadata
    class Meta:
        # Force source, username to be unique
        unique_together = ('source', 'username')


# Define internal token (associated to external user)
class Token(models.Model):
    # Define hash
    jwt = models.CharField(max_length=1000)

    def __repr__(self):
        return self.jwt[-8:]

    def __str__(self):
        return self.jwt[-8:]
