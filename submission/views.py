# Import custom permissions
from submission.authentication import BearerAuthentication, RemoteAuthentication
# Define token model
from rest_framework.authtoken.models import Token
# Define user model
from django.contrib.auth.models import User
# Import response
from rest_framework.response import Response
# Import renderers
from rest_framework import renderers
# Import viewsets
from rest_framework import viewsets


# Define token view
class TokenView(viewsets.ViewSet):
    
    # Define authentication class
    authentication_classes = [RemoteAuthentication]

    # Retrieve internal authorization token
    def retrieve(self, request, pk):
        # Define current authenticated user
        user = request.user
        # Define token
        access_token = request.auth
        # # Get/create internal access token
        # access_token = Token.objects.get_or_create(user=user)
        # # Return current access token
        # return Response({ 'access_token': access_token.key, 'orcid_id': user.username })
        return Response({ 'orcid_id': user.username })