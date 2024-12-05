import logging
import threading
from typing import List

from django.contrib import admin
from django.db.models import BLANK_CHOICE_DASH, QuerySet
from django.utils.safestring import mark_safe
from rangefilter.filters import DateRangeFilter

from django.conf import settings
from drmaatic.job.models import Job
from drmaatic.parameter.admin import JobParamAdminInline
from drmaatic_lib.manage import terminate_job

logger = logging.getLogger(__name__)


def delete_jobs_from_file_system(jobs):
    for job in jobs:
        job.delete_from_file_system()


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('css/job-list-admin.css',)}

    readonly_fields = ('uuid', 'task', 'creation_date', '_sender_ip_addr',
                       '_drm_job_id', 'parent_job', 'dependencies', 'dependency_type', '_files_name')

    list_filter = [
        "task",
        "_status",
        "deleted",
        ("creation_date", DateRangeFilter),
        "user",
    ]
    search_fields = (
        "uuid",
        "task__name",
        "user__username",
        "creation_date",
        "_sender_ip_addr"
    )

    actions = ["delete_and_remove", "update_drm_status", "delete_folder"]

    list_display = ('uuid', 'task', '_status', 'outputs', 'deleted', 'creation_date', 'user', 'ip_address')

    list_per_page = 1000

    inlines = [JobParamAdminInline]

    def get_action_choices(self, request, default_choices=BLANK_CHOICE_DASH):
        choices = super(JobAdmin, self).get_action_choices(request, default_choices)
        choices.pop(0)
        choices.reverse()
        return choices

    def outputs(self, obj):
        out_file = "{}_out.txt".format(str(obj.uuid)[:8])
        err_file = "{}_err.txt".format(str(obj.uuid)[:8])

        base_url = f"{settings.DRMAATIC_WS_URL}/job/{obj.uuid}/file"
        return mark_safe(
            f'<a href="{base_url}/{out_file}" target="_blank">out</a> / <a href="{base_url}/{err_file}" target="_blank">err</a>  / <a href="{base_url}" target="_blank">files</a>'
        )

    outputs.short_description = 'outputs'

    def ip_address(self, obj):
        find_ip = f'https://whatismyipaddress.com/ip/{obj.sender_ip_addr}'
        return mark_safe(f'<a href="{find_ip}" target="_blank">{obj.sender_ip_addr}</a>')

    def delete_model(self, request, job):
        # Stop the job if it is running
        job.update_drm_status()
        if not job.has_finished() and job.drm_job_id:
            terminate_job(job.drm_job_id)
        # Delete job folder and all files
        job.delete_from_file_system()
        job.delete()

    # Overrides the default delete of bulk jobs from the admin interface with the setting of the deleted flag and removal of files from the file system
    def delete_queryset(self, request, queryset: QuerySet[Job]):
        for job in queryset:
            job.update_drm_status()
            # Stop the job if it is running
            if not job.has_finished() and job.drm_job_id:
                terminate_job(job.drm_job_id)
            job.deleted = True

        # Run a thread to delete all the jobs from the file system
        t = threading.Thread(target=delete_jobs_from_file_system, args=(queryset,), daemon=True)
        t.start()
        # Set the jobs to deleted
        Job.objects.abulk_update(queryset, ['deleted'], 1000)

    @admin.action(description="Delete and remove from database")
    def delete_and_remove(self, request, queryset):
        self.delete_queryset(request, queryset)
        queryset.delete()

    @admin.action(description="Delete jobs in filesystem")
    def delete_folder(self, request, queryset):
        logger.warning(f"Deleting {len(queryset)} jobs in filesystem")
        self.delete_queryset(request, queryset)

    @admin.action(description="Update DRM status")
    def update_drm_status(self, request, queryset):
        for job in queryset:
            job.update_drm_status()
