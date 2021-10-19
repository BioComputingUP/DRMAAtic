# Define URLs module
from django.urls import path, include
# Define router
from rest_framework.routers import DefaultRouter
# Define suffix patterns
from rest_framework.urlpatterns import format_suffix_patterns

# Register routes
router = DefaultRouter()
router.register(r'token', views.TokenViewSet)
# router.register(r'job', views.JobViewSet)  # TODO Implement views for jobs
router.register(r'script', views.ScriptViewSet)


# Define URL patterns
urlpatterns = [
    path('', include(router.urls))
]