from django import forms
from django.contrib import admin

from submission.parameter.models import Parameter, TaskParameter


class ParamForm(forms.ModelForm):
    def clean(self):
        if self.cleaned_data["private"] and self.cleaned_data["required"]:
            raise forms.ValidationError({'private' : "Cannot be set with required",
                                         'required': "Cannot be set with private"})
        if self.cleaned_data["name"] == "task_name":
            raise forms.ValidationError({'name': "name cannot be set to 'task_name'"})


class ParamAdminInline(admin.TabularInline):
    model = Parameter
    form = ParamForm


class TaskParamAdminInline(admin.TabularInline):
    model = TaskParameter
