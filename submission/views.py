from rest_framework import generics

from .models import Script
from .serializers import ScriptSerializer


class ScriptList(generics.ListCreateAPIView):
    queryset = Script.objects.all()
    serializer_class = ScriptSerializer
