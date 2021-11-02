import mimetypes

from django.http import FileResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from submission_lib.manage import get_job_status
from .serializers import *


class ScriptViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Script.objects.all()
    serializer_class = ScriptSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    parser_classes = (FormParser, MultiPartParser)  # set parsers if not set in settings. Edited

    def retrieve(self, request, *args, **kwargs):
        task = self.get_object()
        if task.drm_job_id is not None:
            task.status = get_job_status(str(task.drm_job_id))
            task.save()
        serializer = self.get_serializer(task)
        return Response(serializer.data)

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
