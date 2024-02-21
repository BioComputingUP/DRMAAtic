import jwt
from django.contrib.admin import display
from django.contrib.admin.widgets import AdminSplitDateTime
from django.contrib.auth import admin as auth
from django.utils import timezone
from django.core.cache import cache

from drmaatic.models import *
# noinspection PyUnresolvedReferences
from drmaatic.job.admin import *
# noinspection PyUnresolvedReferences
from drmaatic.parameter.admin import *
# noinspection PyUnresolvedReferences
from drmaatic.queue.admin import *
# noinspection PyUnresolvedReferences
from drmaatic.task.admin import *
from drmaatic.throttles import TokenBucketThrottle

# Register user in the admin web interface, using the default interface
admin.site.register(Admin, auth.UserAdmin)


class ExpiredDateFilter(admin.SimpleListFilter):
    title = 'Expired'
    parameter_name = 'expired'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        expired_tokens = []
        non_expired_tokens = []
        for token in queryset:
            try:
                decoded_token = jwt.decode(token.jwt, algorithms=['HS256', ], options={'verify_signature': False})
                expiration_date = timezone.datetime.fromtimestamp(decoded_token['exp'])
                (
                    expired_tokens if expiration_date.timestamp() < timezone.now().timestamp() else non_expired_tokens).append(
                    token.pk)
            except jwt.DecodeError:
                pass
        return queryset.filter(pk__in=expired_tokens if self.value() == 'yes' else non_expired_tokens)


class UsernameFilter(admin.SimpleListFilter):
    title = 'Username'
    parameter_name = 'username'

    def lookups(self, request, model_admin):
        return [(user.username, user.username) for user in User.objects.all()]

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        username_pks = dict()
        for token in queryset:
            try:
                decoded_token = jwt.decode(token.jwt, algorithms=['HS256', ], options={'verify_signature': False})
                username = decoded_token['sub']
                username_pks[username] = username_pks.get(username, []) + [token.pk]
            except jwt.DecodeError:
                pass
        return queryset.filter(pk__in=username_pks[self.value()] if self.value() in username_pks else [])


# Register external user in the admin web interface
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # Define columns to show
    list_display = ('username', 'source', 'group', 'name', 'surname', 'active')
    list_filter = ('source', 'group', 'active')


class GroupForm(forms.ModelForm):
    def clean_token_renewal_time(self):
        if timeparse(self.cleaned_data["token_renewal_time"]) is None:
            raise forms.ValidationError("Invalid time")
        return self.cleaned_data["token_renewal_time"]

    def clean_throttling_rate_burst(self):
        def parse_rate(rate):
            num, period = rate.split('/')
            num_requests = int(num)
            duration = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}[period[0]]
            return num_requests, duration

        try:
            parse_rate(self.cleaned_data["throttling_rate_burst"])
        except:
            raise forms.ValidationError("Invalid rate, expected format: <number>/<s|m|h|d>")
        return self.cleaned_data["throttling_rate_burst"]

    def clean__cpu_credit_regen_time(self):
        if timeparse(self.cleaned_data["_cpu_credit_regen_time"]) is None:
            raise forms.ValidationError("Invalid time")
        return self.cleaned_data["_cpu_credit_regen_time"]

    def clean_cpu_credit_max_amount(self):
        if self.cleaned_data["cpu_credit_max_amount"] < 0:
            raise forms.ValidationError("Invalid amount")
        return self.cleaned_data["cpu_credit_max_amount"]

    def clean_cpu_credit_regen_amount(self):
        if self.cleaned_data["cpu_credit_regen_amount"] < 0:
            raise forms.ValidationError("Invalid amount")
        return self.cleaned_data["cpu_credit_regen_amount"]

    def save(self, commit=True):
        super().save(commit=commit)
        # If the cpu_credit_max_amount is changed, invalidate the cache
        if 'cpu_credit_max_amount' in self.changed_data:
            cache_keys_to_invalidate = [key.split(':')[-1] for key in cache._cache.keys() if TokenBucketThrottle.TOKENS_CACHE_PREFIX in key]
            cache.delete_many(cache_keys_to_invalidate)
        return self.instance


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    # Define columns to show
    list_display = ('name', 'has_full_access', 'throttling_rate_burst',
                    'token_renewal_time', 'cpu_credit_max_amount', 'cpu_credit_regen_amount',
                    '_cpu_credit_regen_time')
    form = GroupForm


class TokenForm(forms.ModelForm):
    class Meta:
        model = Token
        exclude = ['jwt']
        readonly_fields = ['jwt', 'user', 'created', 'expires']

    # The hash is calculated after the form is saved
    user = forms.ModelChoiceField(queryset=User.objects.all(), label="User")
    created = forms.SplitDateTimeField(label="Not before", help_text="Token will be valid from this date",
                                       required=True,
                                       widget=AdminSplitDateTime)
    expires = forms.SplitDateTimeField(label="Expires", help_text="Token will be valid until this date",
                                       required=True,
                                       widget=AdminSplitDateTime)

    def get_initial_for_field(self, field, field_name):
        if field_name == 'created':
            return timezone.now()
        return super(TokenForm, self).get_initial_for_field(field, field_name)

    def clean(self):
        if self.cleaned_data["expires"] < self.cleaned_data["created"]:
            raise forms.ValidationError({'expires': "Invalid expiration date"})

        user = self.cleaned_data['user']
        created = self.cleaned_data['created']
        expires = self.cleaned_data['expires']
        jwt_token = jwt.encode({
            'nbf': int(created.timestamp()),
            'aud': user.source,
            'exp': int(expires.timestamp()),
            'iss': settings.DRMAATIC_WS_URL,
            'sub': user.username,
            'name': user.name,
            'surname': user.surname
        }, settings.SECRET_KEY, algorithm='HS256')
        self.cleaned_data['jwt'] = jwt_token

        return self.cleaned_data


# Register token in the admin web interface
@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    form = TokenForm

    readonly_fields = ('jwt',)

    # add_form_template =
    list_filter = [
        ExpiredDateFilter,
        UsernameFilter,
    ]
    # search_fields = [
    #     "user__username",
    # ]
    # Define columns to show
    list_display = ('get_short_jwt', 'get_user_source', 'get_user_name', 'get_created', 'get_expires', 'expired')

    def get_fields(self, request, token=None):
        if token is not None:
            decoded_jwt = jwt.decode(token.jwt, algorithms=['HS256'], options={'verify_signature': False})
            token.user = User.objects.get(username=decoded_jwt['sub'], source=decoded_jwt['aud'])
            token.created = timezone.datetime.fromtimestamp(decoded_jwt['nbf'])
            token.expires = timezone.datetime.fromtimestamp(decoded_jwt['exp'])
            return ['jwt', 'user', 'created', 'expires']
        return ['user', 'created', 'expires']

    def has_change_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        token = Token(jwt=form.cleaned_data['jwt'])
        token.save(force_insert=True)

    # Show short hash
    @display(ordering='jwt', description='Hashed token')
    def get_short_jwt(self, token):
        return '...{:s}'.format(token.jwt[-8:])

    # Add user's source
    @display(description='User source')
    def get_user_source(self, token):
        return jwt.decode(token.jwt, algorithms=['HS256', ], options={'verify_signature': False})['aud']

    # Add user's username
    @display(description='Username')
    def get_user_name(self, token):
        return jwt.decode(token.jwt, algorithms=['HS256', ], options={'verify_signature': False})['sub']

    @display(description='JWT token created')
    def get_created(self, obj):
        timestamp = jwt.decode(obj.jwt, algorithms=['HS256', ], options={'verify_signature': False})['nbf']
        return timezone.datetime.fromtimestamp(timestamp)

    @display(description='JWT token expiry')
    def get_expires(self, obj):
        timestamp = jwt.decode(obj.jwt, algorithms=['HS256', ], options={'verify_signature': False})['exp']
        return timezone.datetime.fromtimestamp(timestamp)

    @display(description='Expired', boolean=True)
    def expired(self, obj):
        timestamp = jwt.decode(obj.jwt, algorithms=['HS256', ], options={'verify_signature': False})['exp']
        return timestamp < timezone.now().timestamp()
