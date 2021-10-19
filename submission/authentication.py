# Import default user model
from django.contrib.auth.models import User
# Import token authentication
from rest_framework.authentication import TokenAuthentication
# Import model for token
from rest_framework.authtoken.models import Token
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

    # Override authenticate method
    def authenticate(self, request):
        """ Remote authentication
        
        This authentication exchanges an external access token with an internal one.
        Both ORCID ID and access token must be issued. Then, access token will be used
        to authenticate given orcid ID.
        """
        # Try to execute
        try:
            # Retrieve ORCID ID
            orcid_id = request.query_params.get('orcid-id', '')
            # Retrieve access token
            access_token = request.auth
            # Check that both ORCID ID is valid
            valid_id = bool(re.match('^([0-9a-z]{4}-){3}([0-9a-z]{4})$', re.IGNORECASE))
            # Check that token is valid
            valid_token = isinstance(access_token, Token)
            # Initialize response
            response = None
            # Case both id and access token are valid
            if ( valid_id and valid_token ):
                # Format url
                url = self.url.format(orcid_id)
                # Define header
                header = { **self.header, self.keyword: access_token.key }
                # Make a request against authorization URL
                response = requests.get(self.url, timeout=400)
                # Retrieve status code
                status_code = response.status_code
                # Case response return 200 OK
                if status.is_success(status_code):
                    # Cast response to JSON format
                    data = response.json()
                    # Cast response to Response format
                    response = Response(data, status=status.HTTP_200_OK)
                # Otherwise
                else:
                    # Unset response
                    response = None
            # Case response is set (and is valid!)
            if response is not None:
                # Get orcid object
                orcid_dict = response.data.get('orcid-identifier', {})
                # Retrieve identifier from response
                retrieved_id = orcid_dict.get('path', '')
                # Case retrieved id is valid
                if ( retrieved_id == orcid_id ):
                    # Retrun user
                    user = User.objects.get(username=orcid_id)
                    # Return user
                    return (user, None)
        # Catch user not exist
        except User.DoesNotExist:
            # Just raise authentication error
            raise exceptions.AuthenticationFailed('No such user')
        # Otherwise, just raise error
        except:
            # Just raise cateched error
            raise

