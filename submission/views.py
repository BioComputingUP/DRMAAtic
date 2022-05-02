from rest_framework import mixins, viewsets
from rest_framework.response import Response

from .authentication import *
from .serializers import *

logger = logging.getLogger(__name__)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = ExternalUserSerializer
    lookup_field = "username"


# Define token view
class TokenViewSet(viewsets.ViewSet, mixins.RetrieveModelMixin):
    # Define authentication class
    serializer_class = InternalTokenSerializer
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
