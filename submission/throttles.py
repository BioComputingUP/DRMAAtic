# Dependencies
import logging

from rest_framework.throttling import AnonRateThrottle, SimpleRateThrottle

from submission.models import Group

logger = logging.getLogger(__name__)


def get_anon_user_throttle():
    anon = Group.objects.get_or_create(name='anon',
                                       defaults={'throttling_rate_burst'    : '20/s',
                                                 'throttling_rate_sustained': '100/d',
                                                 'token_renewal_time'       : '3 days'})[0]
    return anon


class IPRateThrottleBurst(AnonRateThrottle):
    scope = 'ipBurst'
    THROTTLE_RATES = {'ipBurst': '10/s'}

    ident = None

    def get_cache_key(self, request, view):
        if request.user is not None:
            return None  # Only throttle unauthenticated requests.

        anon_throttle = get_anon_user_throttle()

        self.num_requests, self.duration = self.parse_rate(anon_throttle.throttling_rate_burst)

        self.ident = self.get_ident(request)

        return self.cache_format % {
                'scope': self.scope,
                'ident': self.ident
        }

    def throttle_failure(self):
        logger.warning('Throttling failure for IP: %s', self.ident)


class IPRateThrottleSustained(AnonRateThrottle):
    scope = 'ipSustained'
    THROTTLE_RATES = {'ipSustained': '100/d'}

    ident = None

    def get_cache_key(self, request, view):
        if request.user is not None:
            return None  # Only throttle unauthenticated requests.

        anon_throttle = get_anon_user_throttle()

        self.num_requests, self.duration = self.parse_rate(anon_throttle.throttling_rate_sustained)

        self.ident = self.get_ident(request)

        return self.cache_format % {
                'scope': self.scope,
                'ident': self.ident
        }

    def throttle_failure(self):
        logger.warning('Throttling failure for user: %s', self.ident)


class UserBasedThrottleBurst(SimpleRateThrottle):
    scope = 'userBurst'
    THROTTLE_RATES = {'userBurst': '5/s'}

    ident = None

    def get_cache_key(self, request, view):
        if request.user is not None and request.user.is_authenticated:
            self.num_requests, self.duration = self.parse_rate(request.user.throttling_rate_burst)
            pk = request.user.pk
            self.ident = request.user.username
        else:
            return None

        return self.cache_format % {
                'scope': self.scope,
                'ident': pk
        }

    def throttle_failure(self):
        logger.warning('Throttling failure for user: %s', self.ident)


class UserBasedThrottleSustained(SimpleRateThrottle):
    scope = 'userSustained'
    THROTTLE_RATES = {'userSustained': '1000/d'}

    ident = None

    def get_cache_key(self, request, view):
        if request.user is not None and request.user.is_authenticated:
            self.num_requests, self.duration = self.parse_rate(request.user.throttling_rate_sustained)
            pk = request.user.pk
            self.ident = request.user.username
        else:
            return None

        return self.cache_format % {
                'scope': self.scope,
                'ident': pk
        }

    def throttle_failure(self):
        logger.warning('Throttling failure for IP: %s', self.ident)
