from django.contrib import admin
from rangefilter.filters import DateRangeFilter

from submission.parameter.admin import TaskParamAdminInline
from submission.task.models import Task
from submission_lib.manage import terminate_job


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_filter = [
            "task_name",
            "_status",
            "deleted",
            ("creation_date", DateRangeFilter),
            "user",
    ]
    search_fields = (
            "task_name__name",
            "user__username",
            "creation_date",
    )

    actions = ["delete_and_remove"]

    list_display = ('uuid', 'task_name', '_status', 'deleted', 'creation_date', 'user', '_sender_ip_addr')
    inlines = [TaskParamAdminInline]

    def delete_model(self, request, task):
        # Stop the job if it is running
        task.update_drm_status()
        if not task.has_finished() and task.drm_job_id:
            terminate_job(task.drm_job_id)
        # Delete task folder and all files
        task.delete_from_file_system()
        task.delete()

    # Overrides the default delete of bulk tasks from the admin interface with the setting of the deleted flag and removal of files from the file system
    def delete_queryset(self, request, queryset):
        for task in queryset:
            task.update_drm_status()
            # Stop the job if it is running
            if not task.has_finished() and task.drm_job_id:
                terminate_job(task.drm_job_id)
            # Delete task folder and all files
            task.delete_from_file_system()

        # Set the tasks to deleted
        queryset.update(deleted=True)

    @admin.action(description="Delete and remove from database")
    def delete_and_remove(self, request, queryset):
        self.delete_queryset(request, queryset)
        queryset.delete()
