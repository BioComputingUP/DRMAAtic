from django import forms
from django.contrib import admin

from .models import *


@admin.register(DRMJob)
class DRMJobtAdmin(admin.ModelAdmin):
    list_display = ('name', 'cpus_per_task', 'queue')


class ParamForm(forms.ModelForm):
    def clean(self):
        if self.cleaned_data["private"] and self.cleaned_data["required"]:
            raise forms.ValidationError({'private': "Cannot be set with required", 'required': "Cannot be set with private"})


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
    list_display = ('id', 'name', 'status', 'creation_date')
    inlines = [TaskParamAdminInline]
