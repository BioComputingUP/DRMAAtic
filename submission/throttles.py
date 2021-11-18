# Dependencies
from rest_framework.settings import api_settings
from rest_framework.throttling import AnonRateThrottle, BaseThrottle, SimpleRateThrottle


class IPRateThrottle(AnonRateThrottle):
    THROTTLE_RATES = {'anon': '100/second'}

    def get_cache_key(self, request, view):
        if request.user is not None:
            return None  # Only throttle unauthenticated requests.

        return self.cache_format % {
                'scope': self.scope,
                'ident': self.get_ident(request)
        }


class UserBasedThrottle(SimpleRateThrottle):
    scope = 'user'

    def get_cache_key(self, request, view):
        if request.user is not None and request.user.is_authenticated:
            self.num_requests, self.duration = self.parse_rate(request.user.throttling_rate)
            ident = request.user.pk
        else:
            return None

        return self.cache_format % {
                'scope': self.scope,
                'ident': ident
        }


# TODO Define throttling for authenticated user
class CustomThrottle(BaseThrottle):

    def allow_request(self, request, view):
        """
        Return `True` if the request should be allowed, `False` otherwise.
        """
        # Retrieve request identity
        identity = self.get_ident(request)
        # Just return true
        return True

    def get_ident(self, request):
        """
        Identify the machine making the request by parsing HTTP_X_FORWARDED_FOR
        if present and number of proxies is > 0. If not use all of
        HTTP_X_FORWARDED_FOR if it is available, if not use REMOTE_ADDR.
        """
        # Retrieve HTTP_X_FORWARDED_FOR from request
        # NOTE this field is used to track all the nodes (client, proxy #1, proxy#2, ...)
        # through which the message passed. The rightmost IP in this field is related to
        # the latest traversed proxy, not the IP of the request. The latter can be found
        # within the actual HTTP header.
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        # Retrieve REMOTE_ADDR from request
        # NOTE this field is set by the server (through the socket) and is not returned
        # directly within the HTTP packet. This means that this information can be
        # considered as reliable (differently from HTTP_X_FORWARDED_FOR). Note also that
        # REMOTE_HOST returns the hostname of the 
        remote_addr = request.META.get('REMOTE_ADDR')
        # Define number of proxies
        num_proxies = api_settings.NUM_PROXIES

        # Case number of proxies is set
        if num_proxies is not None:
            # Case maximum distance is null
            if num_proxies == 0 or xff is None:
                # Just return IP of last node
                return remote_addr
            # Split addresses in XFF header
            addrs = xff.split(',')
            # Define client address
            # NOTE Client address is defined as the first traversed node
            # or as the node at the maximum allowed distance
            client_addr = addrs[-min(num_proxies, len(addrs))]
            # Strip client address, keep a string in `a.b.c.d` format
            return client_addr.strip()
        # Otherwise
        return ''.join(xff.split()) if xff else remote_addr
