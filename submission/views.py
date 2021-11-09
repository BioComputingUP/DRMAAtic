import mimetypes
import os.path

from django.http import FileResponse
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from submission_lib.manage import terminate_job
from .authentication import *
from .permissions import *
from .serializers import *


class ScriptViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Script.objects.all()
    serializer_class = ScriptSerializer
    lookup_field = "name"


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    # serializer_class = TaskSerializer
    parser_classes = (FormParser, MultiPartParser)
    authentication_classes = [BearerAuthentication]
    permission_classes = [IsOwner | IsSuper]
    lookup_field = "uuid"

    def get_serializer_class(self):
        if self.request.user and self.request.user.is_admin():
            return SuperTaskSerializer
        else:
            return TaskSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        if request.user is not None:
            queryset = self.filter_queryset(self.get_queryset())

            if not request.user.is_admin():
                queryset = queryset.filter(user=request.user)

            # Update the drm status of the task
            for task in queryset:
                task.update_drm_status()

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, *args, **kwargs):
        """
        Retreive the task and update the status of the DRM job
        """
        task = self.get_object()
        # Update the drm status before returning the task
        task.update_drm_status()

        serializer = self.get_serializer(task)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Destroy the task, stopping it in DRM, but preserving it in the ws
        """
        instance: Task = self.get_object()

        terminate_job(instance.drm_job_id)

        # The task is not removed from the ws nor from the database
        # self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['GET'], detail=True)
    def download(self, request, **kwargs):
        task = self.get_object()

        if task.drm_job_id is not None:
            task.status = get_job_status(str(task.drm_job_id))
            task.save()

        if task.status == Task.Status.DONE.value and not task.has_finished():
            p_task = get_ancestor(task)

            zip_file = os.path.join(BASE_DIR, "downloads/{}.zip".format(p_task.uuid, p_task.uuid))
            file_handle = open(zip_file, "rb")

            mimetype, _ = mimetypes.guess_type(zip_file)
            response = FileResponse(file_handle, content_type=mimetype)
            response['Content-Length'] = os.path.getsize(zip_file)
            response['Content-Disposition'] = "attachment; filename={}".format("{}.zip".format(p_task.uuid))
            return response
        else:
            return Response({'status': 'Output files not available, check task status'},
                            status=status.HTTP_404_NOT_FOUND)

    @action(methods=['GET'], detail=True)
    def file(self, request, path, **kwargs):
        task = self.get_object()

        p_task = get_ancestor(task)

        root = os.path.join(BASE_DIR, "outputs/{}/".format(p_task.uuid))
        files = [os.path.join(dp.replace(root, ''), f) for dp, dn, fn in os.walk(root) for f in fn]

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


class ParamsViewSet(viewsets.ModelViewSet):
    queryset = Parameter.objects.all()
    serializer_class = ParameterSerializer


# Define token view
class TokenViewSet(viewsets.ViewSet, mixins.RetrieveModelMixin):
    # Define authentication class
    authentication_classes = [RemoteAuthentication]

    # Retrieve internal authorization token
    def retrieve(self, request, *args, **kwargs):
        # Define current authenticated user
        user = request.user
        # Define token
        access_token = request.auth
        # return Response({ 'access_token': access_token.key, 'orcid_id': user.username })
        return Response(
                {'user_source': user.source, 'user_name': user.username, 'access_token': access_token.hash})
