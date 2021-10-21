# Import default user model
from django.contrib.auth.models import User
# Import token authentication
from rest_framework.authentication import TokenAuthentication, get_authorization_header
# Import model for token
from rest_framework.authtoken.models import Token
# Define translation utils
from django.utils.translation import gettext_lazy as _
# Import response
from rest_framework.response import Response
# Import status codes
from rest_framework import status
# Import exceptions
from rest_framework import exceptions
# Import requests
import requests
# Import regular expression
import re


# Extend token autentication in order to create Bearer authentication
class BearerAuthentication(TokenAuthentication):

    # Define keyword as Bearer
    keyword = 'Bearer'


# Extend Bearer token authentication to exchange it with an external service
class RemoteAuthentication(BearerAuthentication):

    # Define URL to remote service
    # url = r'https://orcid.org/v3.0/{0:s}/record'  # Production
    url = r'https://pub.sandbox.orcid.org/v3.0/{0:s}/record'  # Development

    # Define headers
    headers = {
        'Content-Type': 'application/json',
        'Bearer': '',  # Must be set on the fly
    }

    # Define request parameters
    request = {
        # Authentication request timeout
        'timeout': 100
    }

    # Override authenticate method
    def authenticate(self, request):
        """ Remote authentication
        
        This authentication exchanges an external access token with an internal one.
        Both ORCID ID and access token must be issued. Then, access token will be used
        to authenticate given orcid ID.
        """
        # Initialize user and token
        user, token = None, None
        # Authenticate user
        user = self.authenticate_user(request)
        # Authenticate token
        token = self.authenticate_token(request, user)
        # Return both user and token
        return user, token

    # Authenticate user
    def authenticate_user(self, request: any) -> User:
        # Retrieve user ID (orcid ID)
        user_id = request.parser_context.get('kwargs', {}).get('pk', '')
        # Check that both orcid ID is valid
        valid_id = bool(re.match('^([0-9a-z]{4}-){3}([0-9a-z]{4})$', user_id, re.IGNORECASE))
        # Case orcid ID is not valid
        if not valid_id:
            # Raise authentication error
            raise exceptions.AuthenticationFailed(_('Issued ORCID ID is not valid'))
        # Define current User
        user = User.objects.get(username=user_id)
        # Case user is not available
        if user is None:
            # Raise authentication error
            raise exceptions.AuthenticationFailed(_('No user is associated with given ORCID ID'))
        # TODO Check that user is active
        # Return user
        return user
        
    # Authenticate token
    def authenticate_token(self, request: any, user: User) -> Token:
        # Split authentication header (token key, value)
        auth_header = get_authorization_header(request).split()
        # Retrieve authentication key
        auth_key = auth_header[0] if len(auth_header) > 0 else None
        # Retrieve authentication token
        auth_token = auth_header[1].decode() if len(auth_header) > 1 else None
        # Check authentication header
        if ((auth_key != self.keyword.lower().encode()) or (auth_token is None)):
            # Raise error
            raise exceptions.AuthenticationFailed(_('Issued authentication header is not valid'))
        # Define authentication endpoint (user username a s orcid ID)
        auth_url = self.url.format(user.username)
        # Define authentication header
        auth_header = { **self.header, self.keyword: auth_token }
        # Make a request against authorization URL
        response = requests.get(auth_url, auth_header **self.request)
        # Case response return 200 OK
        if not status.is_success(response.status_code):
            # Raise error
            raise exceptions.AuthenticationFailed(_('Issued token is not valid'))
        # Define token model
        Token = self.get_model()
        # Create token from user
        token = Token.objects.get_or_create(user=user)
        # Return user's token
        return token

