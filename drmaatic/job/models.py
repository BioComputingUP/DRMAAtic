import logging
import shutil
import uuid
from os.path import join

from django.db import models
from django_filters import CharFilter, ChoiceFilter
from django_filters.rest_framework import FilterSet

from django.conf import settings

from drmaatic.models import User
from drmaatic_lib.manage import get_job_status

logger = logging.getLogger(__name__)


class Job(models.Model):
    # The name of the job should be one of the task names
    task = models.ForeignKey('Task', on_delete=models.CASCADE, null=False)
    # Custom name that can be given to the job by the user
    _job_description = models.CharField(default=None, blank=True, max_length=200, null=True)

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    _sender_ip_addr = models.GenericIPAddressField(default=None, null=True, blank=True)

    creation_date = models.DateTimeField(auto_now_add=True, auto_created=True)
    update_date = models.DateTimeField(auto_now=True, auto_created=True)

    _files_name = models.JSONField(default=dict, null=False, blank=True)

    class Status(models.TextChoices):
        REJECTED = "job has been rejected from the ws"
        RECEIVED = "job has been received from the ws"
        CREATED = "job has been created and sent to the DRM"
        UNDETERMINED = "process status cannot be determined"
        QUEUED_ACTIVE = "job is queued and active"
        SYSTEM_ON_HOLD = "job is queued and in system hold"
        USER_ON_HOLD = "job is queued and in user hold"
        USER_SYSTEM_ON_HOLD = "job is queued and in user and system hold"
        RUNNING = "job is running"
        SYSTEM_SUSPENDED = "job is system suspended"
        USER_SUSPENDED = "job is user suspended"
        STOPPED = "job was stopped by the user"
        DONE = "job finished normally"
        FAILED = "job finished, but failed"

    class DependencyTypes(models.TextChoices):
        AFTER_ANY = "afterany"
        AFTER_OK = "afterok"
        AFTER_NOT_OK = "afternotok"

    _status = models.CharField(max_length=200, choices=Status.choices, blank=False, null=False, default=Status.RECEIVED)

    deleted = models.BooleanField(default=False, null=False, blank=False, editable=False)

    parent_job = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    _drm_job_id = models.PositiveIntegerField(null=True, blank=True)

    dependencies = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='dependents')
    dependency_type = models.CharField(max_length=20, choices=DependencyTypes.choices, blank=True, null=True,
                                       default=None)

    def has_finished(self):
        return self.status in {self.Status.DONE.value, self.Status.FAILED.value,
                               self.Status.STOPPED.value} or self.deleted

    def update_drm_status(self):
        if self.drm_job_id is not None and not self.has_finished():
            self.status = get_job_status(str(self.drm_job_id))

    def delete_from_user(self):
        self.deleted = True
        self.save()

    def delete(self, using=None, keep_parents=False):
        self.delete_from_file_system()
        super().delete(using, keep_parents)

    def get_first_ancestor(self):
        current_job = self
        while current_job.parent_job is not None:
            current_job = current_job.parent_job

        return current_job

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        self._status = status
        self.save(update_fields=['_status'])

    @property
    def drm_job_id(self):
        return self._drm_job_id

    @drm_job_id.setter
    def drm_job_id(self, job_id):
        self._drm_job_id = job_id
        self.save(update_fields=['_drm_job_id'])

    @property
    def job_description(self):
        return self._job_description

    @job_description.setter
    def job_description(self, description):
        self._job_description = description
        self.save(update_fields=['_job_description'])

    @property
    def sender_ip_addr(self):
        return self._sender_ip_addr

    @sender_ip_addr.setter
    def sender_ip_addr(self, ip_addr):
        self._sender_ip_addr = ip_addr
        self.save(update_fields=['_sender_ip_addr'])

    @property
    def files_name(self):
        return self._files_name

    @files_name.setter
    def files_name(self, files_name):
        self._files_name = files_name
        self.save(update_fields=['_files_name'])

    def __str__(self):
        return "{} - {}".format(self.uuid, self.task.name)

    def get_job_path(self):
        return join(settings.DRMAATIC_JOB_OUTPUT_DIR, str(self.uuid))

    def delete_from_file_system(self):
        if settings.REMOVE_JOB_FILES_ON_DELETE:
            try:
                shutil.rmtree(self.get_job_path(), ignore_errors=False)
            except Exception as e:
                logger.error(f"Error while deleting job {self.uuid} from the file system: {e}")

    class Meta:
        ordering = ['-creation_date']


class JobFilterSet(FilterSet):
    job_name = CharFilter(field_name='task__name', lookup_expr='iexact', label="Job name")
    description = CharFilter(field_name='_job_description', lookup_expr='icontains', label="Job description contains")
    status = ChoiceFilter(choices=Job.Status.choices, field_name="_status", lookup_expr='iexact', label="Status is")

    class Meta:
        model = Job
        fields = ['job_name', 'description', 'status']
