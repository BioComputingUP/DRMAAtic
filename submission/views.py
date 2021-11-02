import mimetypes

from django.http import FileResponse
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from submission_lib.manage import get_job_status
from .authentication import *
from .permissions import *
from .serializers import *


class ScriptViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Script.objects.all()
    serializer_class = ScriptSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    parser_classes = (FormParser, MultiPartParser)  # set parsers if not set in settings. Edited
    authentication_classes = [BearerAuthentication]
    permission_classes = [IsOwner]

    def retrieve(self, request, *args, **kwargs):
        task = self.get_object()
        if task.drm_job_id is not None:
            task.status = get_job_status(str(task.drm_job_id))
            task.save()
        serializer = self.get_serializer(task)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(methods=['GET'], detail=True)
    def download(self, request, **kwargs):
        att = self.get_object()
        file_handle = att.file.open()

        mimetype, _ = mimetypes.guess_type(att.file.path)
        response = FileResponse(file_handle, content_type=mimetype)
        response['Content-Length'] = att.file.size
        response['Content-Disposition'] = "attachment; filename={}".format(att.filename)
        return response


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
                {'user_source': user.source, 'user_unsername': user.username, 'access_token': access_token.hash})
