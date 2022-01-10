import logging

from rest_framework.fields import ReadOnlyField

from server.settings import SUBMISSION_SCRIPT_DIR
from submission_lib.manage import start_job
from .models import *
from .utils import *

logger = logging.getLogger(__name__)


class DRMJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = DRMJobTemplate
        fields = "__all__"


class ParameterSerializer(serializers.ModelSerializer):
    """
    Serializes the parameters of a script. Validates the data in input in order to ensure that everything is ok
    """

    class Meta:
        model = Parameter
        fields = ["name", "flag", "type", "default", "description", "private", "required"]

    def to_representation(self, instance):
        user = getattr(self.context.get('request'), 'user', None)
        if not instance.private:
            return super().to_representation(instance)
        else:
            try:
                if user is not None and user.is_admin():
                    return super().to_representation(instance)
                else:
                    return None
            except AttributeError:
                return None

    def validate(self, attrs):
        # Private and required cannot be set together
        if attrs["private"] and attrs["required"]:
            raise serializers.ValidationError("Private and Required fields can't be set together")
        # Special flag for the task that needs to be executed
        if attrs["name"] == "task_name":
            raise serializers.ValidationError("task_name cannot be set as name of a parameter")
        # Special flag to refer to another task already submitted (via uuid)
        if attrs["name"] == "parent_task":
            raise serializers.ValidationError("parent_task cannot be set as name of a parameter")
        return attrs


class ScriptSerializer(serializers.ModelSerializer):
    param = ParameterSerializer(many=True, read_only=True)
    job = serializers.CharField(source="job.name")

    # Array task fields
    is_array = serializers.ReadOnlyField()
    begin_index = serializers.ReadOnlyField()
    end_index = serializers.ReadOnlyField()
    step_index = serializers.ReadOnlyField()

    class Meta:
        model = Script
        fields = ["name", "command", "job", "is_array", "begin_index", "end_index", "step_index", "param"]

    def validate(self, attrs):
        # Private and required cannot be set together
        if attrs["is_array"] and (
                attrs["begin_index"] is None or attrs["end_index"] is None or attrs["step_index"] is None):
            raise serializers.ValidationError(
                    "When is_array is defined, begin_index, end_index and step_index have to be defined")
        return attrs

    def to_representation(self, instance):
        """
        Modify the task representation removing k:v pairs with v=None and null items in the param list
        """
        data = super().to_representation(instance)
        data["param"] = [p for p in data["param"] if p is not None]
        return {k: v for k, v in data.items() if v is not None}


class TaskParameterSerializer(serializers.ModelSerializer):
    """
    Serializes a parameter associated to a task, removing private parameters for non-admin users
    """
    name = ReadOnlyField(source='param.name')

    def to_representation(self, instance):
        user = getattr(self.context.get('request'), 'user', None)
        if (instance.param.private and user is not None and user.is_admin()) or not instance.param.private:
            return super().to_representation(instance)
        else:
            return None

    class Meta:
        model = TaskParameter
        fields = ["name", "value"]


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

    class Meta:
        model = Task
        fields = ["uuid", "task_name", "parent_task", "creation_date", "status", "params"]

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

        The task can be associated to an user if a user is passed.

        A task can have a parent if necessary, in this case the working directory of the new task is the same as the parent task.
        """

        # Check if user passed the params keyword
        if "task_name" not in validated_data.keys():
            raise exceptions.NotAcceptable("The task_name parameter needs to be specified")

        parent_task = None
        if "parent_task" in validated_data.keys():
            parent_task = validated_data["parent_task"]

        # Create the task with the name
        task = Task.objects.create(task_name=validated_data["task_name"], user=validated_data.get("user"),
                                   parent_task=parent_task)

        log_ip(self.context.get('request'))

        if task.parent_task is None:
            create_task_folder(str(task.uuid))

        parameters_of_task = Parameter.objects.filter(script=task.task_name)

        task_params = get_params(self.initial_data, task, parameters_of_task)
        formatted_params = format_task_params(task_params)

        drm_params = DRMJobTemplate.objects.get(name=task.task_name.job).__dict__

        p_task = get_ancestor(task)

        j_id, name = start_job(**drm_params,
                               task_name=task.task_name.name,
                               script_dir=SUBMISSION_SCRIPT_DIR,
                               out_dir=SUBMISSION_OUTPUT_DIR,
                               command=task.task_name.command,
                               script_args=formatted_params,
                               working_dir=p_task.uuid,
                               dependency=parent_task.drm_job_id if parent_task is not None else None,
                               is_array=task.task_name.is_array,
                               begin_index=task.task_name.begin_index,
                               end_index=task.task_name.end_index,
                               step_index=task.task_name.step_index,
                               account=task.user.group.name if task.user is not None else None)
        if j_id is None:
            # If the start of the job had some problem then j_id is none, set the status of the task as rejected
            task.status = Task.Status.REJECTED.value
        else:
            # Otherwise we associate the job id of the DRM and set the status to CREATED
            task.drm_job_id = j_id
            task.status = Task.Status.CREATED.value

        # Must save the instance since it has been modified with the new status/job_id
        task.save()
        return task


class SuperTaskSerializer(TaskSerializer):
    """
    Task serializer for admin users with more info regarding the task
    """
    drm_job_id = serializers.CharField(read_only=True)
    user = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Task
        fields = ["uuid", "task_name", "parent_task", "status", "drm_job_id", "user", "creation_date", "update_date",
                  "params"]


class ExternalUserSerializer(serializers.ModelSerializer):
    is_admin = serializers.BooleanField(source="group.has_full_access")

    class Meta:
        model = User
        fields = ["is_admin"]


class InternalTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = '__all__'
