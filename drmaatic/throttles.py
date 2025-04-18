import logging

from rest_framework import exceptions as rest_framework_exceptions
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

    def __init__(self):
        super().__init__()
        self.view_name = None
        self._user = None
        self.anonymous_request = False
        self.ident = None

    def get_rate(self):
        return '1000/d'

    @property
    def user(self):
        return self._user

    @property
    def user_id(self):
        if self.anonymous_request:
            return self._user
        return self._user.pk

    @user.setter
    def user(self, user):
        self._user = user

    @property
    def user_credit_key(self):
        return f"{self.TOKENS_CACHE_PREFIX}{self.user_id}"

    @property
    def user_current_credit(self):
        return cache.get(self.user_credit_key, self.max_tokens)

    @property
    def max_tokens(self):
        if not self.anonymous_request:
            return self.user.group.cpu_credit_max_amount
        else:
            return Group.anonymous.cpu_credit_max_amount

    @property
    def token_regen_interval(self):
        if not self.anonymous_request:
            return self.user.group.cpu_credit_regen_time
        else:
            return Group.anonymous.cpu_credit_regen_time

    @property
    def token_regen_amount(self):
        if not self.anonymous_request:
            return self.user.group.cpu_credit_regen_amount
        else:
            return Group.anonymous.cpu_credit_regen_amount

    @property
    def last_regen_time_key(self):
        return f"{self.TOKENS_CACHE_PREFIX}{self.user_id}_last_regen"

    def time_since_last_regen(self):
        """
        Calculate the time since the last regeneration of tokens
        :return: The time since the last regeneration of tokens, in seconds
        """
        if not cache.get(self.last_regen_time_key):
            cache.set(self.last_regen_time_key, timezone.now(), self.CACHE_TIMEOUT)
        last_regen_time = cache.get(self.last_regen_time_key, timezone.now())
        time_since_last_regen = (timezone.now() - last_regen_time).total_seconds()

        return time_since_last_regen

    def regenerate_tokens(self):
        max_tokens = self.max_tokens
        time_since_last_regen = self.time_since_last_regen()

        if time_since_last_regen >= self.token_regen_interval:
            cache.set(self.last_regen_time_key, timezone.now(), self.CACHE_TIMEOUT)

            regenerated_tokens = int(time_since_last_regen / self.token_regen_interval) * self.token_regen_amount

            new_tokens = min(max_tokens, self.user_current_credit + regenerated_tokens)
            cache.set(self.user_credit_key, new_tokens, None)
        else:
            self.wait_time = timedelta(seconds=self.token_regen_interval - time_since_last_regen)

    def deduct_tokens(self, tokens):
        new_tokens = max(0, self.user_current_credit - tokens)
        cache.set(self.user_credit_key, new_tokens, None)

    def extract_user_from_request(self, request):
        self.anonymous_request = False
        if request.user is not None and request.user.is_authenticated:
            self.user = request.user
            self.ident = request.user.username
        else:
            self.anonymous_request = True
            self.user = self.get_ident(request=request)
            self.ident = self.user

    def calculate_time_to_wait(self, tokens_requested) -> float:
        """
        Calculate the time to wait for the tokens to be available
        :param tokens_requested: The number of tokens requested
        :return: The time to wait, in seconds. If the time is infinite, then return float('inf')
        """
        # If the tokens requested exceed the maximum allowed, then wait time is infinite
        if tokens_requested > self.max_tokens:
            return float('inf')

        tokens_to_wait = tokens_requested - self.user_current_credit
        # If there are enough tokens, then no need to wait
        if tokens_to_wait <= 0:
            return 0
        # The time to wait is the number of tokens to wait divided by the number of tokens regenerated per interval, multiplied by the interval
        time_to_wait = (tokens_to_wait / self.token_regen_amount) * self.token_regen_interval - self.time_since_last_regen()
        return time_to_wait

    def allow_request(self, request, view):
        self.view_name = view.__class__.__name__
        self.extract_user_from_request(request)

        self.regenerate_tokens()

        request.available_cpu_credit = self.user_current_credit

        # If the request is for the view for retrieving the execution token, and the required parameter is present, then calculate the time to wait for
        # the tokens to be available, if ever
        if self.view_name == 'retrieve_cpu_credit' and 'required' in request.query_params:
            try:
                token_requested = int(request.query_params['required'])
            except ValueError:
                raise rest_framework_exceptions.ValidationError(
                    f"Invalid required token amount '{request.query_params['required']}'")
            if token_requested < 0:
                raise rest_framework_exceptions.ValidationError("The required token amount must be a positive integer")

            request.time_to_wait = self.calculate_time_to_wait(token_requested)
            return True

        try:
            task = Task.objects.get(name=request.data['task'])
            required_tokens = task.required_tokens
        except (Task.DoesNotExist, KeyError):
            return True

        if self.user_current_credit >= required_tokens:
            self.deduct_tokens(required_tokens)
            return self.throttle_success()

        return self.throttle_failure()

    def wait(self):
        return self.wait_time.seconds

    def throttle_success(self):
        return True

    def throttle_failure(self):
        logger.warning(f'Request was throttled for {self.ident}')
