from datetime import timedelta

import jwt
import requests
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from jwt import ExpiredSignatureError
from rest_framework import status
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed

from server.settings import ORCID_AUTH_URL, SECRET_KEY
from .models import Token, User


# Extend token authentication in order to create Bearer authentication
class BearerAuthentication(BaseAuthentication):
    # Define user model
    user = User
    # Define token model
    token = Token
    # Define keyword as Bearer
    keyword = 'Bearer'
    # Define secret
    # NOTE by default it is set as server's secret
    secret = SECRET_KEY

    def get_user_class(self):
        return self.user

    def get_token_class(self):
        return self.token

    # Override authenticate method
    def authenticate(self, request):
        # Try authenticating
        try:
            # Authenticate token
            token = self.authenticate_token(request)
            # Define user
            user = token.user
            # Catch authentication exceptions
        except AuthenticationFailed:
            # Unset both user and token
            user, token = None, None
            # raise AuthenticationFailed(_('Issued token is not valid'))
        # Return both user and token
        return user, token

    # Authenticate token against database
    def authenticate_token(self, request, user=None):
        # Define user and token classes
        user_class, token_class = self.get_user_class(), self.get_token_class()
        # Split authentication binary header (token key, value)
        header = get_authorization_header(request).split()
        # Retrieve authentication key
        keyword = header[0] if len(header) > 0 else None
        # Case keyword specified is not the expected one
        if keyword != self.keyword.encode():
            raise AuthenticationFailed(_('Authentication header is not correctly formatted'))
        # Retrieve authentication value (token)
        hash = header[1].decode() if len(header) > 1 else None
        # Retrieve token out of hash
        token = token_class.objects.get(hash=hash)
        # Decode payload from token
        try:
            payload = jwt.decode(hash, self.secret, algorithms=['HS256', ])
        except ExpiredSignatureError:
            raise AuthenticationFailed(_('Authentication token expired'))
        # # Retrieve user out payload
        # user = User.objects.get(id=payload.get('iss', ''))
        # Case retrieved user is not allowed
        if (token.user.id != payload.get('iss', None)) or not token.user.active:
            # Raise an authentication error
            raise AuthenticationFailed(_('User is forbidden'))
        # Define token
        return token


# Extend Bearer token authentication to exchange it with an external service
class RemoteAuthentication(BearerAuthentication):
    # Define URL to remote service
    url = ORCID_AUTH_URL
    # Define header
    header = {
            'Content-Type': 'application/json',
            'Bearer'      : '',  # Must be set on the fly
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
        # Try executing
        try:
            # Initialize user and token
            user, token = None, None
            # Authenticate user
            user = self.authenticate_user(request)
            # Authenticate token
            token = self.authenticate_token(request, user)
            # Return both user and token
            return user, token
        # Catch any exception
        except Exception as error:
            # Substitute with authentication exception
            raise AuthenticationFailed(_('Could not authenticate user'))

    # Authenticate user
    def authenticate_user(self, request):
        # Define username
        username = request.parser_context.get('kwargs', {}).get('pk', '')
        # Define current user
        # NOTE might raise not-found exception
        user, _ = self.user.objects.get_or_create(username=username,
                                                  defaults={'source': User.ORCID, 'active': True})
        # Check that user is active
        if not user.active:
            # Just raise authentication error
            raise AuthenticationFailed(_('User is forbidden'))
        # Return user
        return user

    # Authenticate token
    def authenticate_token(self, request, user=None):
        # Split authentication binary header (token key, value)
        header = get_authorization_header(request).split()
        # Retrieve authentication key
        keyword = header[0] if len(header) > 0 else None
        # Retrieve authentication token
        secret = header[1].decode() if len(header) > 1 else None
        # Case keyword does not match expected one
        if keyword != self.keyword.encode():
            # Just raise authentication error
            raise AuthenticationFailed(_('Authentication header is not valid'))
        # Define authentication endpoint (user username a s orcid ID)
        url = self.url.format(user.username)
        # Make a request against authorization URL
        response = requests.get(url, {**self.header, keyword: secret}, **self.request)

        # Case response return 200 OK
        if not status.is_success(response.status_code):
            # Just raise authentication error
            raise AuthenticationFailed(_('Issued token is not valid'))
        # Define creation time
        created = timezone.now()
        # Define expiration time
        expires = created + timedelta(seconds=user.get_token_renewal_time_seconds)
        # Create a new hash
        secret = jwt.encode({'nbf': created, 'exp': expires, 'iss': user.id}, self.secret, algorithm='HS256')
        # Create token from user
        token = self.token.objects.create(user=user, hash=secret, created=created, expires=expires)
        # Return user's token
        return token
