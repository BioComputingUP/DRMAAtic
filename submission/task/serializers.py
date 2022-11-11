import logging

from rest_framework import exceptions, serializers

from server.settings import SUBMISSION_OUTPUT_DIR, SUBMISSION_SCRIPT_DIR
from submission.drm_job_template.models import DRMJobTemplate
from submission.parameter.models import Parameter
from submission.parameter.serializers import TaskParameterSerializer
from submission.script.models import Script
from submission.task.models import Task
from submission.utils import create_task_folder, format_task_params, get_ip, get_params
from submission_lib.manage import start_job

logger = logging.getLogger(__name__)


class TaskParentField(serializers.RelatedField):
    """
    Serializer for the nested relationship of a task with another task through the task UUID
    """

    def to_representation(self, instance):
        return instance.uuid

    def to_internal_value(self, value):
        p_task_uuid = value
        if p_task_uuid:
            try:
                task = self.queryset.get(uuid=p_task_uuid)
                return task
            except Task.DoesNotExist:
                raise serializers.ValidationError({
                        'parent_task': 'Specified task does not exists.'
                })
        return None


class TaskSerializer(serializers.ModelSerializer):
    params = TaskParameterSerializer(many=True, read_only=True, required=False)
    status = serializers.CharField(read_only=True)
    parent_task = TaskParentField(queryset=Task.objects.all(), required=False)
    descendants = serializers.SerializerMethodField(read_only=True, method_name='get_descendants')
    files_name = serializers.JSONField(required=False, read_only=True)

    task_description = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Task
        fields = ["uuid", "task_name", "task_description", "parent_task", "creation_date", "status",
                  "files_name", "params"]

    def get_descendants(self, task):
        """
        Get all the descendants of a task
        """
        descendants = []
        for child in Task.objects.filter(parent_task=task):
            descendants.append(child.uuid)
            next_descendants = self.get_descendants(child)
            if next_descendants:
                descendants.extend(next_descendants)

        return descendants if descendants else None

    def to_representation(self, instance):
        """
        Modify the task representation removing k:v pairs with v=None and null items in the param list
        """
        data = super().to_representation(instance)
        data["params"] = [p for p in data["params"] if p is not None]
        return {k: v for k, v in data.items() if v is not None}

    def create(self, validated_data):
        """
        Creates a new task in the ws and in the DRM

        After the creation of the task, the relative parameters (passed and private) are set, and linked to the created task.
        Once task and parameters are created, the task is sent to the DRM in order to be executed. The DRM returns an ID that is
        then associated to the task in order to check the status on the DRM.

        The task can be associated to a user if a user is passed.

        A task can have a parent if necessary, in this case the working directory of the new task is the same as the parent task.
        """

        # Check if user passed the params keyword
        if "task_name" not in validated_data.keys():
            raise exceptions.NotAcceptable("The task_name parameter needs to be specified")

        script = Script.objects.get(name=validated_data["task_name"])

        # Check if script has a group, then user must satisfy the group hierarchy
        if script.groups.count() > 0:
            user = validated_data.get("user")
            if not user or (user and not user.is_admin() and not script.groups.filter(name=user.group_name()).exists()):
                raise exceptions.NotFound(detail="Script not found")

        parent_task = None
        if "parent_task" in validated_data.keys():
            parent_task = validated_data["parent_task"]

        # Create the task with the name
        task = Task.objects.create(task_name=validated_data["task_name"], user=validated_data.get("user"),
                                   parent_task=parent_task)

        if "task_description" in validated_data.keys():
            task.task_description = validated_data["task_description"]

        task.sender_ip_addr = get_ip(self.context.get('request'))

        if task.parent_task is None:
            create_task_folder(str(task.uuid))

        parameters_of_task = Parameter.objects.filter(script=task.task_name)

        try:
            task_params, renamed_files = get_params(self.initial_data, task, parameters_of_task)
        except (exceptions.NotAcceptable, Exception) as e:
            task.delete_from_file_system()
            raise e

        # task.files_name = renamed_files

        formatted_params = format_task_params(task_params)

        drm_params = DRMJobTemplate.objects.get(name=task.task_name.job).__dict__

        p_task = task.get_first_ancestor()

        # Take the first 8 characters of the task uuid to use as outfile names
        out_file = "{}_out.txt".format(str(task.uuid)[:8])
        err_file = "{}_err.txt".format(str(task.uuid)[:8])

        try:
            j_id, name = start_job(**drm_params,
                                   task_name=task.task_name.name,
                                   # if the command is defined as absolute then do not add the submission script dir first
                                   script_dir='' if task.task_name.command[0] == '/' else SUBMISSION_SCRIPT_DIR,
                                   out_dir=SUBMISSION_OUTPUT_DIR,
                                   command=task.task_name.command,
                                   script_args=formatted_params,
                                   working_dir=p_task.uuid,
                                   dependency=parent_task.drm_job_id if parent_task is not None else None,
                                   clock_time_limit=bytes(task.task_name.max_clock_time, encoding='utf8'),
                                   is_array=task.task_name.is_array,
                                   begin_index=task.task_name.begin_index,
                                   end_index=task.task_name.end_index,
                                   step_index=task.task_name.step_index,
                                   account=task.user.group_name() if task.user else None,
                                   stdout_file=out_file,
                                   stderr_file=err_file)
        except Exception as e:
            task.delete_from_file_system()
            logger.warning(
                "Task {}, {}, something went wrong starting this job: {}".format(task.uuid, task.task_name.name, e),
                extra={'request': self.context.get('request')})
            raise exceptions.APIException(detail='An error occurred while starting the task')

        if j_id is None:
            # If the start of the job had some problem then j_id is none, set the status of the task as rejected
            task.status = Task.Status.REJECTED.value
            logger.warning("Task {}, {}, was rejected".format(task.uuid, task.task_name.name),
                           extra={'request': self.context.get('request')})

        else:
            # Otherwise, we associate the job id of the DRM and set the status to CREATED
            task.drm_job_id = j_id
            task.status = Task.Status.CREATED.value
            logger.info("Task {} ({}) was created, DRM {}".format(task.uuid, task.task_name.name, j_id),
                        extra={'request': self.context.get('request')})

        return task


class SuperTaskSerializer(TaskSerializer):
    """
    Task serializer for admin users with more info regarding the task
    """
    drm_job_id = serializers.CharField(read_only=True)
    user = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Task
        fields = ["uuid", "task_name", "task_description", "parent_task", "descendants", "sender_ip_addr", "status",
                  "deleted",
                  "drm_job_id", "files_name", "user", "creation_date", "update_date", "params"]
