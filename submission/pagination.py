from rest_framework.pagination import PageNumberPagination

from django.conf import settings


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = settings.MAX_PAGE_SIZE
