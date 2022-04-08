from rest_framework.pagination import PageNumberPagination

from server.settings import MAX_PAGE_SIZE


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = MAX_PAGE_SIZE
