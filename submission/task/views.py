import mimetypes
import os

from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import exceptions, filters, status, viewsets
from rest_framework.decorators import action, throttle_classes
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.settings import api_settings

from server.settings import SUBMISSION_OUTPUT_DIR
from submission.authentication import BearerAuthentication
from submission.permissions import IsOutputAccessible, IsOwner, IsSuper
from submission.task.models import Task, TaskFilterSet
from submission.task.serializers import SuperTaskSerializer, TaskSerializer
from submission.throttles import *
from submission.utils import request_by_admin
from submission_lib.manage import terminate_job


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    parser_classes = (FormParser, MultiPartParser)

    authentication_classes = [api_settings.DEFAULT_AUTHENTICATION_CLASSES[0], BearerAuthentication]
    permission_classes = [IsOwner | IsSuper]
    lookup_field = "uuid"

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filter_class = TaskFilterSet
    filterset_fields = ["status", "task_name__name"]

    paginate_by = 5
    max_page_size = 10

    def get_serializer_class(self):
        if self.request.user and self.request.user.is_admin():
            return SuperTaskSerializer
        else:
            return TaskSerializer

    def get_permissions(self):
        if self.action == "file":
            return [permission() for permission in [IsOutputAccessible]]
        else:
            return super().get_permissions()

    def get_throttles(self):
        if self.action == "create":
            _throttle_classes = [IPRateThrottleBurst, IPRateThrottleSustained, UserBasedThrottleBurst, UserBasedThrottleSustained]
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
            # If UUIDs are passed in query params then return only those tasks
            uuids = uuids.split(',')

            if request_by_admin(request):
                # If the request is made by an admin, then return all the requested tasks
                queryset = queryset.filter(uuid__in=uuids)
            else:
                # Else return only the tasks owned by the user that are not deleted
                queryset = queryset.filter(uuid__in=uuids, user=request.user, deleted=False)

            for task in queryset:
                task.update_drm_status()

            return self.get_response(queryset)

        elif request.user is not None:
            # If the request is made by a user, then return all the tasks owned by the user

            if not request_by_admin(request):
                # If the user is not an admin, only return tasks that are not deleted and belong to the user
                queryset = queryset.filter(user=request.user)
                queryset = queryset.filter(deleted=False)

            # Update the drm status of the task
            for task in queryset:
                task.update_drm_status()

            return self.get_response(queryset)
        else:
            # If the request is made by an anonymous user, no content is returned
            return Response(status=status.HTTP_204_NO_CONTENT)

    @throttle_classes([IPRateThrottleBurst, UserBasedThrottleBurst])
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve the task and update the status of the DRM job
        """
        task = self.get_object()
        # Update the drm status before returning the task
        task.update_drm_status()

        if not task.deleted or request_by_admin(request):
            serializer = self.get_serializer(task)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        """
        Destroy the task, stopping it in DRM, but preserving it in the database
        """
        task: Task = self.get_object()

        if not task.has_finished():
            terminate_job(task.drm_job_id)

        task.delete_from_user()

        task.delete_from_file_system()

        # The task is not removed from the ws nor from the database
        # self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['GET'], detail=True)
    def download(self, request, **kwargs):
        task = self.get_object()

        task.update_drm_status()

        if task.has_finished():
            p_task = task.get_first_ancestor()

            zip_file = os.path.join(SUBMISSION_OUTPUT_DIR, str(p_task.uuid), "{}.zip".format(p_task.uuid))
            try:
                file_handle = open(zip_file, "rb")

                mimetype, _ = mimetypes.guess_type(zip_file)
                response = FileResponse(file_handle, content_type=mimetype)
                response['Content-Length'] = os.path.getsize(zip_file)
                response['Content-Disposition'] = "attachment; filename={}".format("{}.zip".format(p_task.uuid))
                return response
            except FileNotFoundError:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'status': 'Output files not available, check task status'},
                            status=status.HTTP_404_NOT_FOUND)

    @action(methods=['GET'], detail=True)
    def file(self, request, path, **kwargs):
        task = self.get_object()

        p_task = task.get_first_ancestor()

        root = os.path.join(SUBMISSION_OUTPUT_DIR, str(p_task.uuid))
        files = [os.path.join(dp.replace(root, ''), f).lstrip('/') for dp, dn, fn in os.walk(root) for f in fn]

        if path:
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

        return Response(files)
