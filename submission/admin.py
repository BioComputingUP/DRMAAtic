import uuid

from django.contrib.admin import display
from django.contrib.auth import admin as auth

# noinspection PyUnresolvedReferences
from .drm_job_template.admin import *
from .models import *
# noinspection PyUnresolvedReferences
from .parameter.admin import *
from .script.admin import *
# noinspection PyUnresolvedReferences
from .task.admin import *

# Register user in the admin web interface, using the default interface
admin.site.register(Admin, auth.UserAdmin)


# Register external user in the admin web interface
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # Define columns to show
    list_display = ('username', 'source', 'group', 'email', 'phone', 'active')


class GroupForm(forms.ModelForm):
    def clean(self):
        if timeparse(self.cleaned_data["token_renewal_time"]) is None:
            raise forms.ValidationError({'token_renewal_time': "Invalid time"})


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    # Define columns to show
    # list_display = ('name', 'has_full_access', 'throttling_rate_burst', 'throttling_rate_sustained', 'token_renewal_time')
    form = GroupForm


# Register token in the admin web interface
@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    model = Token
    list_filter = [
            "user__username",
    ]
    search_fields = [
            "user__username",
    ]
    # Define columns to show
    list_display = ('get_short_hash', 'get_user_source', 'get_user_name', 'created', 'expires')
    # Define readonly fields

    def get_changeform_initial_data(self, request):
        return {'hash': uuid.uuid4()}

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
