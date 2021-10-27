# Import token authentication
from datetime import datetime
from rest_framework.authentication import BaseAuthentication, get_authorization_header
# Define translation utils
from django.utils.translation import gettext_lazy as _
# Define authentication exception
from rest_framework.exceptions import AuthenticationFailed
# Import status codes
from rest_framework import status
# Import models
from .models import *
# Import requests
import requests
# Import JSON web tokens
import jwt
# # Import regular expression
# import re


# Extend token autentication in order to create Bearer authentication
class BearerAuthentication(BaseAuthentication):
    # Define user model
    user = ExternalUser
    # Define token model
    token = InternalToken
    # Define keyword as Bearer
    keyword = 'Bearer'
    # Define secret
    secret = 'This is not really secret'

    # Override authenticate method
    def authenticate(self, request):
        # Initialize user and token
        user, token = None, None
        # Try authenticating
        try:
            # Authenticate token
            token = self.authenticate_token(request)
            # Define user
            user = token.user 
            # Return both user and token
            return user, token
        # Catch authentication exceptions
        except:
            raise AuthenticationFailed(_('Issued token is not valid'))

    # Authenticate token against database
    def authenticate_token(self, request):
        # Split authentication binary header (token key, value)
        header = get_authorization_header(request).split()
        # Retrieve authentication key
        keyword = header[0] if len(header) > 0 else None
        # Case keyword specified is not the expected one
        if (keyword != self.keyword):
            raise AuthenticationFailed(_('Authentication header is not correctly formatted'))
        # Retrieve authentication value (token)
        hash = header[1].decode() if len(header) > 1 else None
        # Retrieve token from database
        token = self.token.objects.get(hash=hash)
        # Retrieve user from token
        user = self.user.get(user=token.user)
        # Decode payload from token
        payload = jwt.decode(token, self.secret, algorithm='HS256')
        # Case user id in payload does not match expected
        if (payload.get('iss', '') != user.id):
            raise AuthenticationFailed(_('User data is corrupted'))
        

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
    def authenticate_user(self, request):
        # Define username
        username = request.parser_context.get('kwargs', {}).get('pk', '')
        # Define current user
        # NOTE might raise not-found exception
        user = self.user.objects.get(username=username)
        # TODO Check that user is active
        # Return user
        return user
        
    # Authenticate token
    def authenticate_token(self, request, user):
        # Split authentication binary header (token key, value)
        header = get_authorization_header(request).split()
        # Retrieve authentication key
        keyword = header[0] if len(header) > 0 else None
        # Retrieve authentication token
        hash = header[1].decode() if len(header) > 1 else None
        # Case keyword does not match expected one
        if (keyword != self.keyword):
            # Just raise authentication error
            raise AuthenticationFailed(_('Authentication header is not valid'))
        # Define authentication endpoint (user username a s orcid ID)
        url = self.url.format(user.username)
        # Make a request against authorization URL
        response = requests.get(url, { **self.header, keyword: hash }, **self.request)
        # Case response return 200 OK
        if not status.is_success(response.status_code):
            # Just raise authentication error
            raise AuthenticationFailed(_('Issued token is not valid'))
        # Define creation time
        created = datetime.now()
        # Define expiration time
        expires = timezone.now() + timedelta(days=30)
        # Create a new hash
        hash = jwt.encode({'iss': created, 'exp': expires, 'iss': user.id }, secret=self.secret, algorithm='HS256')
        # Create token from user
        token, _ = self.token.objects.get_or_create(user=user, defaults={ 'hash': hash, 'created': created, 'expires': expires })
        # Return user's token
        return token

