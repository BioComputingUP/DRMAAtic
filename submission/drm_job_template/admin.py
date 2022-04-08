from django.contrib import admin

from submission.drm_job_template.models import DRMJobTemplate


@admin.register(DRMJobTemplate)
class DRMJobtAdmin(admin.ModelAdmin):
    list_display = ('name', 'cpus_per_task', 'queue')
