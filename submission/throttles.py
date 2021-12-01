# Dependencies
from rest_framework.throttling import AnonRateThrottle, SimpleRateThrottle


class IPRateThrottle(AnonRateThrottle):
    THROTTLE_RATES = {'anon': '20/second'}

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
