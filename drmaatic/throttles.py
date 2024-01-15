import logging
from datetime import timedelta

from django.core.cache import cache
from django.utils import timezone
from rest_framework.throttling import AnonRateThrottle, SimpleRateThrottle

from drmaatic.models import Group
from drmaatic.task.models import Task

logger = logging.getLogger(__name__)


class IPRateThrottleBurst(AnonRateThrottle):
    scope = 'ipBurst'
    THROTTLE_RATES = {'ipBurst': '10/s'}

    ident = None

    def get_cache_key(self, request, view):
        if request.user is not None:
            return None  # Only throttle unauthenticated requests.

        anon_throttle = Group.anonymous

        self.num_requests, self.duration = self.parse_rate(anon_throttle.throttling_rate_burst)

        self.ident = self.get_ident(request)

        return self.cache_format % {
            'scope': self.scope,
            'ident': self.ident
        }

    def throttle_failure(self):
        logger.warning(f'Request was throttled for {self.ident}')


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
        logger.warning(f'Request was throttled for {self.ident}')


class TokenBucketThrottle(SimpleRateThrottle):
    TOKENS_CACHE_PREFIX = "bucket_tokens_"
    CACHE_TIMEOUT = 100000

    wait_time = timedelta(seconds=0)

    ident = None

    def get_rate(self):
        return '1000/d'

    def get_user_tokens_key(self, user, is_anonymous):
        if not is_anonymous:
            return f"{self.TOKENS_CACHE_PREFIX}{user.pk}"
        else:
            return f"{self.TOKENS_CACHE_PREFIX}{user}"

    def get_max_tokens(self, user, is_anonymous):
        if not is_anonymous:
            return user.group.execution_token_max_amount
        else:
            return Group.anonymous.execution_token_max_amount

    def get_user_tokens(self, user, is_anonymous):
        user_tokens_key = self.get_user_tokens_key(user, is_anonymous)
        max_tokens = self.get_max_tokens(user, is_anonymous)
        return cache.get(user_tokens_key, max_tokens)

    def regenerate_tokens(self, user, is_anonymous):
        user_tokens_key = self.get_user_tokens_key(user, is_anonymous)
        max_tokens = self.get_max_tokens(user, is_anonymous)
        last_regen_time_key = f"{self.TOKENS_CACHE_PREFIX}{user if is_anonymous else user.pk}_last_regen"

        if not cache.get(last_regen_time_key):
            cache.set(last_regen_time_key, timezone.now(), self.CACHE_TIMEOUT)
        last_regen_time = cache.get(last_regen_time_key, timezone.now())
        time_since_last_regen = (timezone.now() - last_regen_time).total_seconds()

        current_tokens = self.get_user_tokens(user, is_anonymous)

        token_regen_interval = user.group.execution_token_regen_time if not is_anonymous else Group.anonymous.execution_token_regen_time
        token_regen_amount = user.group.execution_token_regen_amount if not is_anonymous else Group.anonymous.execution_token_regen_amount

        if time_since_last_regen >= token_regen_interval:
            cache.set(last_regen_time_key, timezone.now(), self.CACHE_TIMEOUT)

            current_tokens = self.get_user_tokens(user, is_anonymous)
            regenerated_tokens = int(time_since_last_regen / token_regen_interval) * token_regen_amount

            new_tokens = min(max_tokens, current_tokens + regenerated_tokens)
            cache.set(user_tokens_key, new_tokens, None)
        else:
            self.wait_time = timedelta(seconds=token_regen_interval - time_since_last_regen)

    def deduct_tokens(self, user, is_anon, tokens):
        user_tokens_key = self.get_user_tokens_key(user, is_anon)
        current_tokens = self.get_user_tokens(user, is_anon)
        new_tokens = max(0, current_tokens - tokens)
        cache.set(user_tokens_key, new_tokens, None)

    def get_request_user(self, request):
        anonymous_request = False
        if request.user is not None and request.user.is_authenticated:
            user = request.user
        else:
            user = self.get_ident(request=request)
            anonymous_request = True
        return user, anonymous_request

    def allow_request(self, request, view):
        user, anonymous_request = self.get_request_user(request)

        self.ident = user.username if not anonymous_request else user
        self.regenerate_tokens(user, is_anonymous=anonymous_request)

        available_tokens = self.get_user_tokens(user, is_anonymous=anonymous_request)
        request.available_execution_tokens = available_tokens

        try:
            task = Task.objects.get(name=request.data['task'])
            required_tokens = task.required_tokens
        except (Task.DoesNotExist, KeyError):
            return True

        if available_tokens >= required_tokens:
            self.deduct_tokens(user, anonymous_request, required_tokens)
            request.tokens = available_tokens
            return self.throttle_success()

        return self.throttle_failure()

    def wait(self):
        return self.wait_time.seconds

    def throttle_success(self):
        return True

    def throttle_failure(self):
        logger.warning(f'Request was throttled for {self.ident}')
