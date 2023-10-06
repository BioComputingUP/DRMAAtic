import logging
import re
from datetime import timedelta

import jwt
import requests
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from jwt import ExpiredSignatureError
from rest_framework import status
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed

from django.conf import settings
from drmaatic.models import Token, User, Group

logger = logging.getLogger(__name__)


# Extend token authentication in order to create Bearer authentication
class BearerAuthentication(BaseAuthentication):
    # Override authenticate method
    def authenticate(self, request):
        # Authenticate token
        try:
            # Authenticate token
            token = self.authenticate_token(request)
            # In case no header for authentication was provided
            if token is None:
                return None, None
            # Define user
            user = token.user
            # Catch authentication exceptions
        except AuthenticationFailed as e:
            # Unset both user and token
            raise e

        # Return both user and token
        return user, token

    def authenticate_token(self, request):
        header = get_authorization_header(request)
        match = re.match(r'^Bearer (.+)$', header.decode())
        if not match:
            return None

        jwt_token = match.group(1)
        try:
            token = Token.objects.get(hash=jwt_token)
        except Token.DoesNotExist:
            raise AuthenticationFailed(_('JWT token does not exist'))

        if token.expires < timezone.now():
            logger.warning("Is trying to use an expired token", extra={'ip': token.user.username})
            raise AuthenticationFailed(_('Authentication token expired'))

        if token.user.active:
            # Decode payload from token
            if token.user.source == 'INTERNAL':
                return token
            else:
                try:
                    jwt.decode(jwt_token, settings.SECRET_KEY,
                               algorithms=['HS256', ],
                               audience=token.user.source,
                               issuer=settings.DRMAATIC_WS_URL,
                               options={'verify_exp': True})
                except ExpiredSignatureError:
                    raise AuthenticationFailed(_('Authentication JWT token expired'))
                except (InvalidKeyError, InvalidSignatureError, InvalidAudienceError, Exception):
                    logger.warning("Is trying to use an invalid token", extra={'ip': token.user.username})
                    raise AuthenticationFailed(_('Authentication JWT token is not valid'))

                return token

        raise AuthenticationFailed(_('User is forbidden'))


# Extend Bearer token authentication to exchange it with an external service
class SocialProviderAuthentication(BearerAuthentication):
    # Define URL to remote service
    verification_url = settings.ORCID_AUTH_URL
    allowed_providers = ['orcid']
    provider = None

    # Override authenticate method
    def authenticate(self, request):
        """ Remote authentication
        
        This authentication exchanges an external access token with an internal one.
        Both ORCID ID and access token must be issued. Then, access token will be used
        to authenticate given orcid ID.
        """

        self.provider = request.resolver_match.kwargs.get('provider')
        if self.provider not in self.allowed_providers:
            raise AuthenticationFailed(_(f'Provider \'{self.provider}\' is not a valid provider'))

        try:
            user, token = None, None
            if self.provider == 'orcid':
                # Authenticate token
                user, token = self.authenticate_orcid_access_token(request)
            # Return both user and token
            return user, token
        # Catch any exception
        except Exception as e:
            raise AuthenticationFailed(e)

    def authenticate_orcid_access_token(self, request):
        from django.utils.translation import gettext_lazy as _

        header = get_authorization_header(request)
        match = re.match(r'^Bearer (.+)$', header.decode())
        if not match:
            raise AuthenticationFailed(_('Authentication header is not valid'))
        access_token = match.group(1)
        response = requests.get(self.verification_url, headers={'Authorization': f'Bearer {access_token}'})

        if not status.is_success(response.status_code):
            # Just raise authentication error
            raise AuthenticationFailed(_('Issued token is not valid'))

        user, _ = User.objects.get_or_create(username=response.json()['sub'],
                                             name=response.json()['given_name'],
                                             surname=response.json()['family_name'],
                                             defaults={'source': User.ORCID, 'active': True, 'group': Group.registered})
        # Check that user is active
        if not user.active:
            # Just raise authentication error
            raise AuthenticationFailed(_('User is forbidden'))

        # Define creation time
        created = timezone.now()
        # Define expiration time
        expires = created + timedelta(seconds=user.get_token_renewal_time_seconds)
        # Create a new hash
        jwt_token = jwt.encode({
            'nbf': created,
            'aud': user.source,
            'exp': expires,
            'iss': settings.DRMAATIC_WS_URL,
            'sub': user.username,
            'name': user.name,
            'surname': user.surname
        }, settings.SECRET_KEY, algorithm='HS256')
        # Create token from user
        token = Token.objects.create(user=user, hash=jwt_token, created=created, expires=expires)
        # Return user's token
        return user, token
