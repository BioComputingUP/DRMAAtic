from django import forms
from django.contrib import admin
from django.contrib.admin import display
from django.contrib.auth import admin as auth

from .models import *


@admin.register(DRMJobTemplate)
class DRMJobtAdmin(admin.ModelAdmin):
    list_display = ('name', 'cpus_per_task', 'queue')


class ParamForm(forms.ModelForm):
    def clean(self):
        if self.cleaned_data["private"] and self.cleaned_data["required"]:
            raise forms.ValidationError(
                    {'private': "Cannot be set with required", 'required': "Cannot be set with private"})
        if self.cleaned_data["name"] == "task_name":
            raise forms.ValidationError({'name': "name cannot be set to 'task_name'"})


class ParamAdminInline(admin.TabularInline):
    model = Parameter
    form = ParamForm


@admin.register(Script)
class ScriptAdmin(admin.ModelAdmin):
    fields = (('name', 'command'), 'job', ('is_array', 'begin_index', 'end_index', 'step_index'))
    list_display = ('name', 'command')

    inlines = [ParamAdminInline]


class TaskParamAdminInline(admin.TabularInline):
    model = TaskParameter


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_filter = [
            "task_name",
            "status",
            "user"
    ]
    search_fields = (
            "task_name__name",
            "user__username",
    )

    list_display = ('uuid', 'task_name', 'status', 'creation_date', 'user')
    inlines = [TaskParamAdminInline]


# Register user in the admin web interface, using the default interface
admin.site.register(Admin, auth.UserAdmin)


# Register external user in the admin web interface
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # Define columns to show
    list_display = ('username', 'source', 'group', 'email', 'phone', 'active')


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    # Define columns to show
    list_display = ('name', 'has_full_access', 'throttling_rate', 'token_renewal_time')


# Register token in the admin web interface
@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_filter = [
            "user__username",
    ]
    search_fields = [
            "user__username",
    ]
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
