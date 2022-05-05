# Dependencies
from rest_framework.throttling import AnonRateThrottle, SimpleRateThrottle

from submission.models import Group


def get_anon_user_throttle():
    anon = Group.objects.get_or_create(name='anon',
                                       defaults={'throttling_rate_burst'    : '20/s',
                                                 'throttling_rate_sustained': '100/d',
                                                 'token_renewal_time'       : '3 days'})[0]
    return anon


class IPRateThrottleBurst(AnonRateThrottle):
    THROTTLE_RATES = {'anon': '20/s'}

    def get_cache_key(self, request, view):
        anon_throttle = get_anon_user_throttle()

        self.num_requests, self.duration = self.parse_rate(anon_throttle.throttling_rate_burst)

        if request.user is not None:
            return None  # Only throttle unauthenticated requests.

        return self.cache_format % {
                'scope': self.scope,
                'ident': self.get_ident(request)
        }


class IPRateThrottleSustained(AnonRateThrottle):
    THROTTLE_RATES = {'anon': '20/s'}

    def get_cache_key(self, request, view):
        anon_throttle = get_anon_user_throttle()

        self.num_requests, self.duration = self.parse_rate(anon_throttle.throttling_rate_sustained)

        if request.user is not None:
            return None  # Only throttle unauthenticated requests.

        return self.cache_format % {
                'scope': self.scope,
                'ident': self.get_ident(request)
        }


class UserBasedThrottleBurst(SimpleRateThrottle):
    scope = 'user'

    def get_cache_key(self, request, view):
        if request.user is not None and request.user.is_authenticated:
            self.num_requests, self.duration = self.parse_rate(request.user.throttling_rate_burst)
            ident = request.user.pk
        else:
            return None

        return self.cache_format % {
                'scope': self.scope,
                'ident': ident
        }


class UserBasedThrottleSustained(SimpleRateThrottle):
    scope = 'user'

    def get_cache_key(self, request, view):
        if request.user is not None and request.user.is_authenticated:
            self.num_requests, self.duration = self.parse_rate(request.user.throttling_rate_sustained)
            ident = request.user.pk
        else:
            return None

        return self.cache_format % {
                'scope': self.scope,
                'ident': ident
        }
