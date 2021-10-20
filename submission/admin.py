from django.contrib import admin

from .models import *


@admin.register(DRMJob)
class DRMJobtAdmin(admin.ModelAdmin):
    list_display = ('name', 'cpus_per_task', 'queue')


class ParamAdminInline(admin.TabularInline):
    model = Parameter


@admin.register(Script)
class ScriptAdmin(admin.ModelAdmin):
    fields = (('name', 'command'), 'job')
    list_display = ('name', 'command')

    inlines = [ParamAdminInline]
