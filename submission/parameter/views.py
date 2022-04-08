from rest_framework import viewsets

from submission.parameter.models import Parameter
from submission.parameter.serializers import ParameterSerializer


class ParamsViewSet(viewsets.ModelViewSet):
    queryset = Parameter.objects.all()
    serializer_class = ParameterSerializer
