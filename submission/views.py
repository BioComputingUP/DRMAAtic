from rest_framework import viewsets
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


class ParamsViewSet(viewsets.ModelViewSet):
    queryset = Parameter.objects.all()
    serializer_class = ParameterSerializer
