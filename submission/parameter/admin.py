from django import forms
from django.contrib import admin

from submission.parameter.models import Parameter, JobParameter


class ParamForm(forms.ModelForm):
    name = forms.CharField(required=True, max_length=40, label="Name", help_text="Name of the parameter, this is the name that is used in the POST of the job")
    flag = forms.CharField(required=False, max_length=40, label="Flag", help_text="Flag to be used in the command line")
    default = forms.CharField(required=False, max_length=40, label="Default", help_text="Default value of the parameter")
    type = forms.ChoiceField(required=True, choices=Parameter.Type.choices, initial=Parameter.Type.STRING.value , label="Type", help_text="Type of the parameter")

    private = forms.BooleanField(required=False, label="Private", help_text="If checked, the parameter can be seen only by the admin, always passed in the command line")
    required = forms.BooleanField(required=False, label="Required", help_text="If checked, the parameter is required in the POST of the job")

    def clean(self):
        if self.cleaned_data["private"] and self.cleaned_data["required"]:
            raise forms.ValidationError({'private' : "Cannot be set with required",
                                         'required': "Cannot be set with private"})
        if self.cleaned_data["name"] == "task":
            raise forms.ValidationError({'name': "name cannot be set to 'task'"})


class ParamAdminInline(admin.TabularInline):
    model = Parameter
    form = ParamForm

    extra = 1


class JobParamAdminInline(admin.TabularInline):
    model = JobParameter

    readonly_fields = ('param', 'value')

    extra = 0
    can_delete = False
    show_change_link = False
    max_num = 0
