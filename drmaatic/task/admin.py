from django import forms
from django.contrib import admin
from pytimeparse.timeparse import timeparse

from drmaatic.parameter.admin import ParamAdminInline
from drmaatic.task.models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = '__all__'

    def clean_cpus(self):
        # Get the queue and check that for that queue the number of cpus is not exceeded
        queues = self.cleaned_data.get("_queues")
        if queues:
            max_cpus = max([q.max_cpu for q in queues.all()])
            if self.cleaned_data["cpus"] > max_cpus:
                raise forms.ValidationError(f"Number of CPUs exceeds the maximum for the queues {max_cpus}")

        return self.cleaned_data["cpus"]

    def clean_mem(self):
        # Get the queue and check that for that queue the amount of memory is not exceeded
        queues = self.cleaned_data.get("_queues")
        if queues:
            max_mem = max([q.max_mem for q in queues.all()])
            if self.cleaned_data["mem"] > max_mem:
                raise forms.ValidationError(f"Amount of memory exceeds the maximum for the queues {max_mem}MB")

        return self.cleaned_data["mem"]

    def clean__max_clock_time(self):
        time = timeparse(self.cleaned_data["_max_clock_time"])
        if time is None:
            raise forms.ValidationError({'_max_clock_time': "Invalid time"})
        if time < 60:
            raise forms.ValidationError({'_max_clock_time': "Minimum time is 1 minute"})
        return self.cleaned_data["_max_clock_time"]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    fields = (('name', 'command', 'required_tokens'), ('_queues', 'cpus', 'mem'), 'is_output_public', "_max_clock_time", "groups",
              ('is_array', 'begin_index', 'end_index', 'step_index'))
    list_display = ('name', 'command', "required_tokens", "queues", "is_output_public")
    search_fields = ('name', 'command')
    list_filter = ('_queues' , 'is_output_public', 'groups')
    ordering = ('command', 'name')

    form = TaskForm

    save_as = True

    inlines = [ParamAdminInline, ]
