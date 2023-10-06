from rest_framework import viewsets

from drmaatic.parameter.models import Parameter
from drmaatic.parameter.serializers import ParameterSerializer


class ParamsViewSet(viewsets.ModelViewSet):
    queryset = Parameter.objects.all()
    serializer_class = ParameterSerializer
