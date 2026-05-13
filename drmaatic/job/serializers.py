import logging
import os

from rest_framework import exceptions, serializers

from django.conf import settings
from drmaatic.job.models import Job
from drmaatic.parameter.models import Parameter
from drmaatic.parameter.serializers import TaskParameterSerializer
from drmaatic.task.models import Task
from drmaatic.utils import get_ip, process_parameters, create_job_folder, format_job_params, track_matomo_job_creation
from drmaatic_lib.manage import start_job

logger = logging.getLogger(__name__)


class JobParentField(serializers.RelatedField):
    """
    Serializer for the nested relationship of a task with another task through the task UUID
    """

    def to_representation(self, instance):
        return instance.uuid

    def to_internal_value(self, value):
        p_job_uuid = value
        if p_job_uuid:
            try:
                job = self.queryset.get(uuid=p_job_uuid)
                return job
            except Job.DoesNotExist:
                raise serializers.ValidationError({
                    'parent_job': 'Specified job does not exists.'
                })
        return None


class JobSerializer(serializers.ModelSerializer):
    task = serializers.CharField(required=True)

    params = TaskParameterSerializer(many=True, read_only=True, required=False)
    status = serializers.CharField(read_only=True)
    parent_job = JobParentField(queryset=Job.objects.all(), required=False)
    descendants = serializers.SerializerMethodField(read_only=True, method_name='get_descendants')
    # The dependencies are passed as a list of UUIDs separated by commas
    dependencies = serializers.CharField(required=False, write_only=True)
    depends_on = serializers.SlugRelatedField(many=True, read_only=True, required=False, slug_field='uuid',
                                              source='dependencies')
    files_name = serializers.JSONField(required=False, read_only=True)
    has_owner = serializers.SerializerMethodField(read_only=True, method_name='get_has_owner')

    job_description = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Job
        fields = ["uuid", "task", "descendants", "dependencies", "depends_on", "dependency_type", "has_owner",
                  "job_description", "parent_job", "creation_date", "status", "files_name", "params"]

    def get_has_owner(self, job):
        return job.user is not None

    def get_descendants(self, job):
        """
        Get all the descendants of a job
        """
        descendants = []
        for child in Job.objects.filter(parent_job=job):
            descendants.append(child.uuid)
            next_descendants = self.get_descendants(child)
            if next_descendants:
                descendants.extend(next_descendants)

        return descendants if descendants else None

    def to_representation(self, instance):
        """
        Modify the job representation removing k:v pairs with v=None and null items in the param list
        """
        data = super().to_representation(instance)
        data["params"] = [p for p in data["params"] if p is not None]
        return {k: v for k, v in data.items() if v is not None}

    def validate_task(self, task: str):
        """
        Check if the task is valid
        """
        try:
            task = Task.objects.get(name=task)
        except Task.DoesNotExist:
            raise exceptions.ValidationError({
                'task': f"Task '{task}' does not exist. Use GET /task to see available tasks."
            })
        except Exception as e:
            raise exceptions.ValidationError({
                'task': f"Error validating task '{task}': {str(e)}"
            })
        return task

    def create(self, validated_data):
        """
        Creates a new job in the ws and in the DRM

        After the creation of the job, the relative parameters (passed and private) are set, and linked to the created job.
        Once job and parameters are created, the job is sent to the DRM in order to be executed. The DRM returns an ID that is
        then associated to the job in order to check the status on the DRM.

        The job can be associated to a user if a user is passed.

        A job can have a parent if necessary, in this case the working directory of the new job is the same as the parent job.
        """


        

        # Check if user passed the params keyword
        task = validated_data["task"]

        # Check if script has a group, then user must satisfy the group hierarchy
        if task.groups.count() > 0:
            user = validated_data.get("user")
            if not user or (user and not user.is_admin() and not task.groups.filter(name=user.group_name()).exists()):
                raise exceptions.NotFound(detail="Task not found")

        parent_job = None
        if "parent_job" in validated_data.keys():
            parent_job = validated_data["parent_job"]

        # Create the job with the name
        job: Job = Job.objects.create(task=validated_data["task"], user=validated_data.get("user"),
                                      parent_job=parent_job)

        task: Task = job.task

        if "job_description" in validated_data.keys():
            job.job_description = validated_data["job_description"]

        job.sender_ip_addr = get_ip(self.context.get('request'))

        if job.parent_job is None:
            create_job_folder(str(job.uuid))

        parameters_of_job = Parameter.objects.filter(task=task)

        try:
            job_params, renamed_files = process_parameters(self.initial_data, job, parameters_of_job)
        except (exceptions.NotAcceptable, exceptions.ValidationError) as e:
            job.delete_from_file_system()
            raise e
        except Exception as e:
            job.delete_from_file_system()
            raise exceptions.ValidationError({'detail': f"Parameter processing error: {str(e)}"})

        # job.files_name = renamed_files

        formatted_params = format_job_params(job_params)

        drm_params = {
            'queue': task.queues,
            'cpus_per_task': str(task.cpus),
            'mem_per_node': task.mem,
        }

        p_job = job.get_first_ancestor()

        # Take the first 8 characters of the job uuid to use as outfile names
        out_file = "{}_out.txt".format(str(job.uuid)[:8])
        err_file = "{}_err.txt".format(str(job.uuid)[:8])

        # Get all the dependencies of the job and the type of dependency
        if "dependencies" in validated_data.keys():
            dep_uuids = validated_data["dependencies"].split(",")
            try:
                dep_jobs = []
                for dep_uuid in dep_uuids:
                    dep_uuid_clean = dep_uuid.strip()
                    try:
                        dep_job = Job.objects.get(uuid=dep_uuid_clean)
                        dep_jobs.append(dep_job)
                    except Job.DoesNotExist:
                        job.delete_from_file_system()
                        raise exceptions.ValidationError({
                            'dependencies': f"Dependency job '{dep_uuid_clean}' does not exist."
                        })
                job.dependencies.set(dep_jobs)
            except exceptions.ValidationError:
                raise
            except Exception as e:
                job.delete_from_file_system()
                raise exceptions.ValidationError({
                    'dependencies': f"Error processing dependencies: {str(e)}"
                })

            if "dependency_type" in validated_data.keys():
                dependency_type = validated_data["dependency_type"].strip()
                if dependency_type not in Job.DependencyTypes.values:
                    valid_types = ", ".join(Job.DependencyTypes.values)
                    raise exceptions.ValidationError({
                        'dependency_type': f"Invalid dependency_type '{dependency_type}'. Valid options: {valid_types}"
                    })
                job.dependency_type = dependency_type
            else:
                job.dependency_type = Job.DependencyTypes.AFTER_ANY

        dependencies = [t.drm_job_id for t in job.dependencies.all()] if job.dependencies.exists() else None
        dependency_type = job.dependency_type if dependencies else None

        # Validate command path before asking Slurm to submit the job.
        # This prevents opaque "slurm_submit_batch_job" errors when the script path is wrong.
        if task.command and task.command[0] != '/':
            submission_script = os.path.join(str(settings.DRMAATIC_TASK_SCRIPT_DIR), task.command)
            if not os.path.exists(submission_script):
                job.delete_from_file_system()
                raise exceptions.ValidationError({
                    'task': (
                        f"Task command '{task.command}' was not found under "
                        f"DRMAATIC_TASK_SCRIPT_DIR='{settings.DRMAATIC_TASK_SCRIPT_DIR}'. "
                        "Check task command and environment settings."
                    )
                })

        try:
            j_id, name = start_job(**drm_params,
                                   task_name=task.name,
                                   # if the command is defined as absolute then do not add the submission script dir first
                                   script_dir='' if task.command[0] == '/' else settings.DRMAATIC_TASK_SCRIPT_DIR,
                                   out_dir=settings.DRMAATIC_JOB_OUTPUT_DIR,
                                   command=task.command,
                                   script_args=formatted_params,
                                   working_dir=p_job.uuid,
                                   dependencies=dependencies,
                                   dependency_type=dependency_type,
                                   clock_time_limit=bytes(task.max_clock_time, encoding='utf8'),
                                   is_array=task.is_array,
                                   begin_index=task.begin_index,
                                   end_index=task.end_index,
                                   step_index=task.step_index,
                                   account=job.user.group_name() if job.user else None,
                                   stdout_file=out_file,
                                   stderr_file=err_file)
        except Exception as e:
            job.delete_from_file_system()
            error_detail = str(e).strip()
            logger.error(
                f"Job {job.uuid} ({task.name}) failed to start in DRM: {error_detail}",
                extra={'request': self.context.get('request')}, exc_info=True)
            job.status = Job.Status.FAILED.value
            job.save()
            raise exceptions.APIException(detail=error_detail)

        if j_id is None:
            # If the start of the job had some problem then j_id is none, set the status of the job as rejected
            job.status = Job.Status.REJECTED.value
            job.save()
            logger.warning(f"Job {job.uuid} ({task.name}) was rejected by DRM/SLURM. Check job status and error logs for details.",
                           extra={'request': self.context.get('request')})
            raise exceptions.APIException(detail=f"Job {job.uuid} was rejected by the DRM system. This may indicate resource constraints or invalid job parameters. Check with your system administrator.")

        else:
            # Otherwise, we associate the job id of the DRM and set the status to CREATED
            job.drm_job_id = j_id
            job.status = Job.Status.CREATED.value
            logger.info("Job {} ({}) was created, DRM {}".format(job.uuid, task.name, j_id),
                        extra={'request': self.context.get('request')})

        job.save()

        # If matomo is enabled, track the job creation
        if settings.MATOMO_API_TRACKING:
            track_matomo_job_creation(job, self.context.get('request'))

        return job


class SuperJobSerializer(JobSerializer):
    """
    Job serializer for admin users with more info regarding the job
    """
    drm_job_id = serializers.CharField(read_only=True)
    user = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Job
        fields = ["uuid", "task", "job_description", "parent_job", "descendants", "dependencies",
                  "depends_on",
                  "dependency_type",
                  "sender_ip_addr", "status", "deleted",
                  "drm_job_id", "files_name", "user", "creation_date", "update_date", "params"]
