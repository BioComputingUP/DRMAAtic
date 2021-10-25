from rest_framework import viewsets

from .serializers import *


class ScriptViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Script.objects.all()
    serializer_class = ScriptSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
