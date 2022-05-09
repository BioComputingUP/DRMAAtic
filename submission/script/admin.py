from django import forms
from django.contrib import admin
from pytimeparse.timeparse import timeparse

from submission.parameter.admin import ParamAdminInline
from submission.script.models import Script


class ScriptForm(forms.ModelForm):
    def clean(self):
        if timeparse(self.cleaned_data["_max_clock_time"]) is None:
            raise forms.ValidationError({'_max_clock_time': "Invalid time"})

        # Time is parsed in seconds, min time is 1 minute (60 seconds)
        if timeparse(self.cleaned_data["_max_clock_time"]) < 60:
            raise forms.ValidationError({'_max_clock_time': "Minimum time is 1 minute"})


@admin.register(Script)
class ScriptAdmin(admin.ModelAdmin):
    fields = (('name', 'command'), ('job', 'is_output_visible'), "_max_clock_time", "groups",
              ('is_array', 'begin_index', 'end_index', 'step_index'))
    list_display = ('name', 'command', "is_output_visible")
    form = ScriptForm

    inlines = [ParamAdminInline, ]
