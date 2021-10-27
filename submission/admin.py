from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


# Register user in the admin web interface, using the default interface
admin.site.register(User, UserAdmin)