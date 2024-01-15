import mimetypes
import os

from django.http import FileResponse, HttpResponseNotFound
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import exceptions, filters, status, viewsets
from rest_framework.decorators import action, throttle_classes
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.settings import api_settings

from django.conf import settings
from drmaatic.authentication import BearerAuthentication
from drmaatic.job.models import Job, JobFilterSet
from drmaatic.job.serializers import SuperJobSerializer, JobSerializer
from drmaatic.permissions import IsOutputAccessible, IsOwner, IsSuper
from drmaatic.throttles import *
from drmaatic.utils import request_by_admin
from drmaatic_lib.manage import terminate_job


class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    parser_classes = (FormParser, MultiPartParser)

    http_method_names = ['get', 'post', 'delete', 'put']

    authentication_classes = [api_settings.DEFAULT_AUTHENTICATION_CLASSES[0], BearerAuthentication]
    permission_classes = [IsOwner | IsSuper]
    lookup_field = "uuid"

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = JobFilterSet

    paginate_by = 5
    max_page_size = 10

    def get_serializer_class(self):
        if self.request.user and self.request.user.is_admin():
            return SuperJobSerializer
        else:
            return JobSerializer

    def get_permissions(self):
        if self.action == "file":
            return [permission() for permission in [IsOutputAccessible | IsOwner | IsSuper]]
        else:
            return super().get_permissions()

    def get_throttles(self):
        if self.action == "create":
            _throttle_classes = [
                TokenBucketThrottle]  # [IPRateThrottleBurst, IPRateThrottleSustained, UserBasedThrottleBurst,  UserBasedThrottleSustained]
        else:
            _throttle_classes = [IPRateThrottleBurst, UserBasedThrottleBurst]
        return [throttle() for throttle in _throttle_classes]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_response(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            # If pagination is enabled, return the paginated response
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            # If pagination is disabled, return the serialized data
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

    @throttle_classes([IPRateThrottleBurst, UserBasedThrottleBurst])
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        uuids = request.query_params.get('ids', '')

        if len(uuids) > 0:
            # If UUIDs are passed in query params then return only those jobs
            uuids = uuids.split(',')

            if request_by_admin(request):
                # If the request is made by an admin, then return all the requested jobs
                queryset = queryset.filter(uuid__in=uuids)
            else:
                # Else return only the jobs owned by the user that are not deleted
                queryset = queryset.filter(uuid__in=uuids, user=request.user, deleted=False)

            for job in queryset:
                job.update_drm_status()

            return self.get_response(queryset)

        elif request.user is not None:
            # If the request is made by a user, then return all the jobs owned by the user

            if not request_by_admin(request):
                # If the user is not an admin, only return jobs that are not deleted and belong to the user
                queryset = queryset.filter(user=request.user)
                queryset = queryset.filter(deleted=False)

            # Update the drm status of the job
            for job in queryset:
                job.update_drm_status()

            return self.get_response(queryset)
        else:
            # If the request is made by an anonymous user, no content is returned
            return Response(status=status.HTTP_204_NO_CONTENT)

    @throttle_classes([IPRateThrottleBurst, UserBasedThrottleBurst])
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve the job and update the status of the DRM job
        """
        job = self.get_object()
        # Update the drm status before returning the job
        job.update_drm_status()

        if not job.deleted or request_by_admin(request):
            serializer = self.get_serializer(job)
            return Response(serializer.data)
        else:
            return Response("Job not found", status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        """
        Destroy the job, stopping it in DRM, but preserving it in the database
        """
        job: Job = self.get_object()

        if not job.has_finished():
            terminate_job(job.drm_job_id)

        job.delete_from_user()

        job.delete_from_file_system()

        # The job is not removed from the ws nor from the database
        # self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['PUT'], detail=True, description="Stop a job from running")
    def stop(self, request, *args, **kwargs):
        """
        Stop the job, stopping it in DRM, but preserving it in the database
        """
        job: Job = self.get_object()

        if not job.has_finished():
            terminate_job(job.drm_job_id)
            job.status = Job.Status.STOPPED.value
            job.save()
            return Response(data={'detail': 'Job successfully stopped'}, status=status.HTTP_200_OK)
        else:
            return Response(data={'detail': 'Job is not running'}, status=status.HTTP_409_CONFLICT)

    @action(methods=['GET'], detail=True)
    def download(self, request, **kwargs):
        job = self.get_object()

        job.update_drm_status()

        if job.has_finished():
            p_job = job.get_first_ancestor()

            zip_file = os.path.join(settings.DRMAATIC_JOB_OUTPUT_DIR, str(p_job.uuid), "{}.zip".format(p_job.uuid))
            try:
                file_handle = open(zip_file, "rb")

                mimetype, _ = mimetypes.guess_type(zip_file)
                response = FileResponse(file_handle, content_type=mimetype)
                response['Content-Length'] = os.path.getsize(zip_file)
                response['Content-Disposition'] = "attachment; filename={}".format("{}.zip".format(p_job.uuid))
                return response
            except FileNotFoundError:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            return Response('Output files not available, check job status', status=status.HTTP_404_NOT_FOUND)

    @action(methods=['GET'], detail=True)
    def file(self, request, path, **kwargs):
        job: Job = self.get_object()

        p_job: Job = job.get_first_ancestor()

        root = os.path.join(settings.DRMAATIC_JOB_OUTPUT_DIR, str(p_job.uuid))
        files = [os.path.join(dp.replace(root, ''), f).lstrip('/') for dp, dn, fn in os.walk(root) for f in fn]

        if not request_by_admin(request):
            to_remove = []
            for i, file in enumerate(files):
                out_file = f"{str(job.uuid)[:8]}_out.txt"
                err_file = f"{str(job.uuid)[:8]}_err.txt"
                if file == out_file or file == err_file:
                    to_remove.append(i)

            for i in reversed(to_remove):
                files.pop(i)

        if not path:  # We return the list of files in the job directory
            return Response(files)
        else:  # The requested file is returned, if it exists
            if path in files:
                file = os.path.join(root, path)
                file_handle = open(file, "rb")
                mimetype, _ = mimetypes.guess_type(file)
                response = FileResponse(file_handle, content_type=mimetype or 'text/plain', )
                response['Content-Length'] = os.path.getsize(file)
                response['Content-Disposition'] = "inline"  # ; filename={}".format(os.path.basename(file))
                return response
            else:
                raise exceptions.NotFound()

    @action(methods=['GET'], detail=True)
    def status(self, request, **kwargs):
        job = self.get_object()
        job.update_drm_status()

        return Response(job.status)

    @action(methods=['PUT'], detail=True, description="Associate a job to a user if the job has no user")
    def assign_ownership(self, request, **kwargs):
        job = self.get_object()
        user = request.user

        job_already_owned = job.user is not None
        user_is_valid = user is not None and user.is_authenticated

        if job_already_owned:
            return Response("Job already owned", status=status.HTTP_409_CONFLICT)
        elif not user_is_valid:
            return Response("User not valid", status=status.HTTP_400_BAD_REQUEST)
        else:
            job.user = user
            job.save()
            return Response("Job ownership granted", status=status.HTTP_200_OK)
