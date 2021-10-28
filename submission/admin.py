from django.contrib import admin
from django.contrib.admin.decorators import display
from django.contrib.auth import admin as auth
from .models import ExternalUser, InternalToken, User


# Register user in the admin web interface, using the default interface
admin.site.register(User, auth.UserAdmin)


# Register external user in the admin web interface
@admin.register(ExternalUser)
class ExternalUserAdmin(admin.ModelAdmin):
    # Define columns to show
    list_display = ('source', 'username', 'email', 'phone', 'active')


# Register token in the admin web interface
@admin.register(InternalToken)
class InternalTokenAdmin(admin.ModelAdmin):
    # Define columns to show
    list_display = ('get_short_hash', 'get_user_source', 'get_user_name', 'created', 'expires')
    # Define readonly fields
    readonly_fields = ('hash', 'created', 'expires', 'user')

    # Show short hash
    @display(ordering='hash', description='Hashed token')
    def get_short_hash(self, obj):
        return '...{:s}'.format(obj.hash[-7::])

    # Add user's source
    @display(ordering='user_source', description='User source')
    def get_user_source(self, obj):
        return obj.user.source
    
    # Add user's username
    @display(ordering='user_name', description='Username')
    def get_user_name(self, obj):
        return obj.user.username