from django.contrib import admin
from django.db.models import BLANK_CHOICE_DASH
from django.utils.safestring import mark_safe
from rangefilter.filters import DateRangeFilter

from django.conf import settings
from submission.job.models import Job
from submission.parameter.admin import JobParamAdminInline
from submission_lib.manage import terminate_job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('css/mymodel_list.css',)}

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
        "job__name",
        "user__username",
        "creation_date",
    )

    actions = ["delete_and_remove", "update_drm_status"]

    list_display = ('uuid', 'task', '_status', 'outputs', 'deleted', 'creation_date', 'user', '_sender_ip_addr')

    inlines = [JobParamAdminInline]

    def get_action_choices(self, request, default_choices=BLANK_CHOICE_DASH):
        choices = super(JobAdmin, self).get_action_choices(request, default_choices)
        choices.pop(0)
        choices.reverse()
        return choices

    def outputs(self, obj):
        out_file = "{}_out.txt".format(str(obj.uuid)[:8])
        err_file = "{}_err.txt".format(str(obj.uuid)[:8])

        url = "{}/job/".format(settings.SUBMISSION_WS_URL)
        return mark_safe(
            f'<a href="{url}{obj.uuid}/file/{out_file}" target="_blank">out</a> / <a href="{url}{obj.uuid}/file/{err_file}" target="_blank">err</a>  / <a href="{url}{obj.uuid}/file" target="_blank">files</a>'
        )

    outputs.short_description = 'outputs'

    def delete_model(self, request, job):
        # Stop the job if it is running
        job.update_drm_status()
        if not job.has_finished() and job.drm_job_id:
            terminate_job(job.drm_job_id)
        # Delete job folder and all files
        job.delete_from_file_system()
        job.delete()

    # Overrides the default delete of bulk jobs from the admin interface with the setting of the deleted flag and removal of files from the file system
    def delete_queryset(self, request, queryset):
        for job in queryset:
            job.update_drm_status()
            # Stop the job if it is running
            if not job.has_finished() and job.drm_job_id:
                terminate_job(job.drm_job_id)
            # Delete job folder and all files
            job.delete_from_file_system()

        # Set the jobs to deleted
        queryset.update(deleted=True)

    @admin.action(description="Delete and remove from database")
    def delete_and_remove(self, request, queryset):
        self.delete_queryset(request, queryset)
        queryset.delete()

    @admin.action(description="Update DRM status")
    def update_drm_status(self, request, queryset):
        for job in queryset:
            job.update_drm_status()

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Update the drm status of the job
        # for job in queryset:
        #     job.update_drm_status()

        return queryset
