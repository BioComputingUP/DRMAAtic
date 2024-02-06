import uuid

from django.contrib.admin import display
from django.contrib.auth import admin as auth
from django.utils import timezone

from drmaatic.models import *
# noinspection PyUnresolvedReferences
from drmaatic.job.admin import *
# noinspection PyUnresolvedReferences
from drmaatic.parameter.admin import *
# noinspection PyUnresolvedReferences
from drmaatic.queue.admin import *
# noinspection PyUnresolvedReferences
from drmaatic.task.admin import *

# Register user in the admin web interface, using the default interface
admin.site.register(Admin, auth.UserAdmin)


class ExpiredDateFilter(admin.SimpleListFilter):
    title = 'Expired'
    parameter_name = 'expired'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(expires__lt=timezone.now())
        elif self.value() == 'no':
            return queryset.exclude(expires__lt=timezone.now())


# Register external user in the admin web interface
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # Define columns to show
    list_display = ('username', 'source', 'group', 'name', 'surname', 'active')
    list_filter = ('source', 'group', 'active')


class GroupForm(forms.ModelForm):
    def clean(self):
        if timeparse(self.cleaned_data["token_renewal_time"]) is None:
            raise forms.ValidationError({'token_renewal_time': "Invalid time"})


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    # Define columns to show
    list_display = ('name', 'has_full_access', 'throttling_rate_burst',
                    'token_renewal_time', 'execution_token_max_amount', 'execution_token_regen_amount',
                    '_execution_token_regen_time')
    form = GroupForm


# Register token in the admin web interface
@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    model = Token
    list_filter = [
        "user__username",
        "created",
        ExpiredDateFilter
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
    @display(ordering='user__source', description='User source')
    def get_user_source(self, obj):
        return obj.user.source

    # Add user's username
    @display(ordering='user__name', description='Username')
    def get_user_name(self, obj):
        return obj.user.username
