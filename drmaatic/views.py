from django.http import HttpResponse
from rest_framework.decorators import api_view, authentication_classes, renderer_classes, throttle_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from drmaatic.authentication import *
from .serializers import *
from .throttles import TokenBucketThrottle

logger = logging.getLogger(__name__)


@api_view(['GET'])
@renderer_classes([JSONRenderer])
@authentication_classes([SocialProviderAuthentication])
def retrieve_internal_token(request, **kwargs):
    # Define token
    internal_token: Token = request.auth
    return Response({'jwt': internal_token.jwt}, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([BearerAuthentication])
@throttle_classes([TokenBucketThrottle])
@renderer_classes([JSONRenderer])
def retrieve_cpu_credit(request):
    # If in the request there is a required number of tokens, then calculate in how many seconds the tokens will be available, if ever
    if 'required' in request.query_params:
        wait_time = request.time_to_wait
        wait_time_value = 'infinite' if wait_time == float('inf') else int(wait_time)
        return Response(data={'available_cpu_credit': request.available_cpu_credit,
                              'wait_time': wait_time_value},
                        status=status.HTTP_200_OK)

    # Based on the renderers, the response will be either JSON or plain text
    return Response(data={'available_cpu_credit': request.available_cpu_credit}, status=status.HTTP_200_OK)
