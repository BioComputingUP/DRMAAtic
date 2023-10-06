from django.apps import AppConfig


class SubmissionConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'
    name = 'drmaatic'
    verbose_name = 'DRMAAtic - DRMAA enabled job scheduler with REST APIs'
