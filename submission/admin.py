from django import forms
from django.contrib import admin

from .models import *


@admin.register(DRMJobTemplate)
class DRMJobtAdmin(admin.ModelAdmin):
    list_display = ('name', 'cpus_per_task', 'queue')


class ParamForm(forms.ModelForm):
    def clean(self):
        if self.cleaned_data["private"] and self.cleaned_data["required"]:
            raise forms.ValidationError({'private': "Cannot be set with required", 'required': "Cannot be set with private"})
        if self.cleaned_data["name"] == "task_name":
            raise forms.ValidationError({'name': "name cannot be set to 'task_name'"})


class ParamAdminInline(admin.TabularInline):
    model = Parameter
    form = ParamForm


@admin.register(Script)
class ScriptAdmin(admin.ModelAdmin):
    fields = (('name', 'command'), 'job')
    list_display = ('name', 'command')

    inlines = [ParamAdminInline]


class TaskParamAdminInline(admin.TabularInline):
    model = TaskParameter


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'task_name', 'status', 'creation_date')
    inlines = [TaskParamAdminInline]
