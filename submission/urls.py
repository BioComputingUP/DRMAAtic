# Define URLs module
from django.urls import path, include
# Define router
from rest_framework.routers import DefaultRouter
# Define suffix patterns
from rest_framework.urlpatterns import format_suffix_patterns
# Define views
from .views import *


# Register routes
router = DefaultRouter()
router.register(r'token', TokenViewSet, basename='Token')
router.register(r'job', JobViewSet, basename='Job')


# Define URL patterns
urlpatterns = [
    path('', include(router.urls))
]