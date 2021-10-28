# Import response
from rest_framework.response import Response
# Import viewsets
from rest_framework import viewsets
# Import custom serializers
from .serializers import *
# Import custom authentication
from .authentication import *
# Import custom permissions
from .permissions import *
# Import custom models
from .models import *


# Define token view
class TokenViewSet(viewsets.ViewSet):
    # Define authentication class
    authentication_classes = [RemoteAuthentication]

    # Retrieve internal authorization token
    def retrieve(self, request, pk=None):
        # Define current authenticated user
        user = request.user
        # Define token
        access_token = request.auth
        # return Response({ 'access_token': access_token.key, 'orcid_id': user.username })
        return Response({ 'user_source': user.source, 'user_unsername': user.username, 'access_token': access_token.hash })


# Example viewset for job
class JobViewSet(viewsets.ModelViewSet):
    # Define serializer
    serializer_class = TestJobSerializer
    # Define queryset
    queryset = TestJob.objects.all()
    # Define authentication
    authentication_classes = [BearerAuthentication]
    # Define permissions
    permission_classes = [IsOwner]

    # Retrieve status of a job
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    # Send single job
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # Create single job
    def perform_create(self, serializer):
        # Request can be accessed like this
        request = self.request
        # Then, user can be retrieved from it
        user = request.user or None
        # Finally, just save model with user
        serializer.save(user=user)

    # TODO Delete a job
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)