from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.settings import api_settings

from submission.authentication import BearerAuthentication
from submission.script.models import Script
from submission.script.serializers import ScriptSerializer, SuperScriptSerializer


class ScriptViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Script.objects.all()
    authentication_classes = [api_settings.DEFAULT_AUTHENTICATION_CLASSES[0], BearerAuthentication]
    serializer_class = ScriptSerializer
    lookup_field = "name"

    def get_serializer_class(self):
        if self.request.user and self.request.user.is_admin():
            return SuperScriptSerializer
        else:
            return ScriptSerializer

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

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        allowed_scripts = []
        for script in queryset:
            if script.groups.count() == 0:
                allowed_scripts.append(script.name)
            elif request.user and (request.user.is_admin() or script.groups.filter(name=request.user.group).exists()):
                allowed_scripts.append(script.name)

        queryset = queryset.filter(name__in=allowed_scripts)

        return self.get_response(queryset)

    def retrieve(self, request, *args, **kwargs):
        script = self.get_object()
        serializer = self.get_serializer(script)
        user = request.user

        if script.groups.count() == 0:
            return Response(serializer.data)
        elif user and (user.is_admin() or script.groups.filter(name=user.group).exists()):
            return Response(serializer.data)
        else:
            return Response(status=404)
